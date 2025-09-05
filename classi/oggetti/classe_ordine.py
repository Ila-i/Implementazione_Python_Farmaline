from funzioni_generali.controlli_function import controlla_si_no
from classi.oggetti.classe_farmaco import Farmaco
from pandas import DataFrame
from sqlalchemy import text
from db import connection
import pandas as pd
import random


class Ordine :

    codice_ordine : int
    carrello: list[dict]
    quanto_compro: dict

    def __init__(self)->None:
        self.codice_ordine = random.randint(0, 1000000000) # si associa un numero random come codice
        self.carrello = []
        self.quanto_compro = {}

    def aggiungi_a_carrello(self, results: DataFrame ) -> None:

        """Permette di scegliere se aggiungere o meno un prodotto al carrello per poi acquistarlo"""
        codice_p : str
        quantity_p :int

        codice_p = Farmaco.controllo_codice_farmaco(results)

        # ricerca se il prodotto era già stato aggiunto al carrello
        ck_se_presente: bool = False  # in riferimento a un farmaco già presente nel carrello
        quanto_in_m: int = 0 # in riferimento alla quantità di un prodotto nel carrello

        for contenuto in self.carrello:
            quanto_in_m = contenuto["quantità"] # per prendere la quantità di prodotto nel magazzino
            if codice_p == contenuto["codice_farmaco"]:
                ck_se_presente = True
                break

        if not ck_se_presente:
            quantity_p = Farmaco.controllo_quanto_farmaco(codice_p,quanto_in_m, ck_se_presente)
        else:
            quantity_p = Farmaco.controllo_quanto_farmaco(codice_p,quanto_in_m, ck_se_presente, self.quanto_compro[codice_p])

        if quantity_p > 0:

            aggiungi_carrello:str = controlla_si_no("\nDigitare 'si' se si vuole aggiungere il prodotto al carrello, altrimenti digitare 'no': ")

            if aggiungi_carrello == "si":

                # recupera la riga che contiene le informazioni del farmaco che si vuole acquistare
                riga:DataFrame = results.loc[results["codice_farmaco"] == codice_p]
                farmaco_dict: dict = riga.iloc[0].to_dict()# prende la prima corrispondenza nel Dataframe

                if not ck_se_presente : # aggiunge al  carrello solo se non si è messo nel carrello lo stesso prodotto
                    self.carrello.append(farmaco_dict)
                    self.quanto_compro[codice_p]= quantity_p
                else :
                    self.quanto_compro[codice_p] = quantity_p# aggiorna la quantità di prodotto se già presente nel carrello

                print("Farmaco aggiunto al carrello.")

                # stampa del carrello
                print("Contenuto attuale del carrello:")
                if self.carrello:
                    self.stampa_carrello()

                else:
                    print("Il carrello è vuoto.")

            elif aggiungi_carrello == "no":
                print("Farmaco non aggiunto al carrello")
                print("Contenuto attuale del carrello:")

                #stampa del carrello
                if self.carrello:
                    self.stampa_carrello()

                else:
                    print("Il carrello è vuoto.")
            else:
                print("Operazione non valida.")

    def stampa_carrello(self)-> None:

        for prodotto in self.carrello:
            print(f" codice farmaco : {prodotto["codice_farmaco"]} ")
            print(f" nome : {prodotto["nome"]} ")
            print(f" quantità : {self.quanto_compro[prodotto["codice_farmaco"]]} ")
            print(f" prezzo : {self.quanto_compro[prodotto["codice_farmaco"]] * float(prodotto["prezzo"]):.2f} €")

    def update_quantity(self, id_utente :str)->None:

        """Agisce sul database andando a modificare le quantità dei faramci in magazzino dopo che il cliente ha effettuato il pagamento"""

        for prodotto in self.carrello:

            query: str
            # si modifica la quantità di prodotto in magazzino
            new_quantity:int = prodotto["quantità"] - self.quanto_compro[prodotto["codice_farmaco"]]
            query = f"UPDATE FarmaciMagazzino SET quantità = '{new_quantity}' WHERE codice_farmaco = '{prodotto["codice_farmaco"]}' "
            connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
            connection.commit()

            # si elimina la ricetta utilizzata nell'acquisto
            query = f"DELETE FROM Ricetta WHERE codice_farmaco ='{prodotto["codice_farmaco"]}' AND codice_fiscale = '{id_utente}' "
            connection.execute(text(query))
            connection.commit()

    def aggiungi_ordine_a_db(self, indirizzo: str, id_utente :str) -> None:

        new_ordine = pd.DataFrame(
            [[
                self.codice_ordine,
                id_utente,
                indirizzo,
            ]],
            columns=[
                'numero_ordine',
                'codice_fiscale',
                'indirizzo_consegna',
            ]
        )
        new_ordine.to_sql('Ordine', connection, if_exists='append', index=False)
        connection.commit()
