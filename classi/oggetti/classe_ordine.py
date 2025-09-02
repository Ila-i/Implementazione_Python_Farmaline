from pandas import DataFrame
from sqlalchemy import text

from classi.oggetti.classe_farmaco import Farmaco
from db import connection
import pandas as pd
import random

from funzioni_generali.controlli_function import controlla_si_no


class Ordine :

    codice_ordine : int
    carrello: list[dict]
    quanto_compro: dict

    def __init__(self)->None:
        self.codice_ordine = random.randint(0, 1000000000) # si associa un numero random come codice
        self.carrello = []
        self.quanto_compro = {}

    def aggiungi_a_carrello(self, results: DataFrame ) -> None:

        codice_p : str
        quantity_p :int=0

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

            aggiungi_carrello = controlla_si_no("\nDigitare 'si' se si vuole aggiungere il prodotto al carrello, altrimenti digitare 'no': ")

            if aggiungi_carrello == "si":

                # recupera la riga che contiene le informazioni del farmaco che si vuole acquistare
                riga = results.loc[results["codice_farmaco"] == codice_p]
                farmaco_dict = riga.iloc[0].to_dict()# prende la prima corrispondenza

                if not ck_se_presente : # aggiunge al  carrelo solo se non ho messo nel carrello lo stesso prodotto
                    self.carrello.append(farmaco_dict)
                    self.quanto_compro[codice_p]= quantity_p
                else :
                    self.quanto_compro[codice_p] = quantity_p

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
            print(f" codice : {prodotto["codice_farmaco"]} ")
            print(f" nome : {prodotto["nome"]} ")
            print(f" quantità : {self.quanto_compro[prodotto["codice_farmaco"]]} ")
            print(f" prezzo : {self.quanto_compro[prodotto["codice_farmaco"]] * float(prodotto["prezzo"])} €")

    def update_quantity(self, id_utente :str)->None:

        """Agisce sul database andando a modificare le quantità di prodotto aggiornate dal farmacista"""

        for prodotto in self.carrello:

            # si modifica la quantità di prodotto in magazzino
            new_quantity = prodotto["quantità"] - self.quanto_compro[prodotto["codice_farmaco"]]
            query = f"UPDATE FarmaciMagazzino SET quantità = '{new_quantity}' WHERE codice_farmaco = '{prodotto["codice_farmaco"]}' "
            connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
            connection.commit()

            # si elimina la ricetta utilizzata nell'acquisto
            query = f"DELETE FROM Ricetta WHERE codice_farmaco ='{prodotto["codice_farmaco"]}' AND codice_fiscale = '{id_utente}' "
            connection.execute(text(query))
            connection.commit()

    def aggiungi_ordine_a_db(self, indirizzo: str, id_utente :str) -> None:

        # agginge il nuovo ordine al database
        new_ordine = pd.DataFrame(
            [[
                self.codice_ordine,
                id_utente,
                indirizzo,
            ]],
            columns=[
                'numero_ordine',  # <-- niente spazio finale
                'codice_fiscale',
                'indirizzo_consegna',
            ]
        )
        new_ordine.to_sql('Ordine', connection, if_exists='append', index=False)
        connection.commit()
