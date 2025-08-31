from sqlalchemy import text
from db import connection
import pandas as pd
import random


class Ordine :

    carrello: list[dict]  # si mette come attributo per evitare che il carrello si riazzeri ogni volta che viene chiamata da search_bar
    quanto_compro: dict

    def __init__(self):
        self.carrello = []
        self.quanto_compro = {}

    def aggiunta_carrello(self,results) -> None:

        ck: bool = False
        rimane :int = 0
        ck_se_presente : bool = False
        controllo_q: bool = False
        verifica_cod: bool = False
        quantity: int = 0
        codice_input: str = ''
        quanto_in_m:int

        # sezione dedicata al controllo del codice se è presente o meno nell'elenco trovato nella ricerca
        # Se ce più di un farmaco
        if len(results) > 1:
            while not ck:
                codice_input = input("\nInserire il codice del farmaco che si vuole acquistare: ")

                for prodotto in results.to_dict(orient="records"):
                    if codice_input == prodotto["codice_farmaco"]:
                        verifica_cod = True
                        break

                if not verifica_cod:
                    print("Il codice inserito non è valido, o non è presente tra quelli elencati")
                    ck=False
                else:
                    ck = True
        # Se ce n'è solo uno
        else:
            codice_input = (results.iloc[0]["codice_farmaco"])

        #ricerca se il prodotto era già stato aggiunto al carrello
        for contenuto in self.carrello :
            quanto_in_m=contenuto["quantità"]
            if codice_input == contenuto["codice_farmaco"]:
                ck_se_presente = True
                break


        # sezione di codice per controllare che la quantità che si vuole acquistare sia disponibile
        while not controllo_q: #  consente di riprovare se non è sufficente la quantità
            ck = False
            if ck_se_presente:
                rimane = quanto_in_m - self.quanto_compro[codice_input]
                print(" Il farmaco è stato precedentemente selezionato. ")
                print(f"Con la precedente selzione rimangono {rimane} campioni ")
                if rimane ==0:
                    print("Il prodotto è terminato non è possibile acquistarlo")
                    break

            while not ck:
                try:
                    quantity = int(input("Inserire la quantità di prodotto che si vuole acquistare : "))
                    if quantity == 0 :
                        print("non può assumere valore nullo, riprovare ")
                        ck = False
                    else :
                        ck = True
                except ValueError:
                    ck = False
                    print("il valore inserito non è compatibile, riprovare")

            if ck_se_presente:
                quantity = quantity + self.quanto_compro[codice_input]


            query = f"SELECT quantità FROM FarmaciMagazzino WHERE quantità < '{quantity}' AND codice = '{codice_input}' "
            q_trovato = pd.read_sql(query, connection)

            if q_trovato.empty:
                aggiungi_carrello = input("\nDigitare 'si' se si vuole aggiungere il prodotto al carrello, altrimenti digitare 'no': ")

                if aggiungi_carrello == "si":

                    # recupera la riga che contiene le informazioni del farmaco che si vuole acquistare
                    riga = results.loc[results["codice_farmaco"] == codice_input]
                    farmaco_dict = riga.iloc[0].to_dict()# prende la prima corrispondenza

                    if not ck_se_presente : # aggiunge al  carrelo solo se non ho messo nel carrello lo stesso prodotto
                        self.carrello.append(farmaco_dict)
                        self.quanto_compro[codice_input]= quantity
                    else :
                        self.quanto_compro[codice_input] = quantity

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

                controllo_q = True

            else: # non trova riscontri in magazzino
                if q_trovato.iloc[0, 0] == 0:
                    print("Il prodotto è terminato non è possibile acquistarlo")
                    controllo_q = True
                else:
                    print("La quantità di farmaco in magazzino non è sufficiente, riprovare  ")

    @staticmethod
    def associa_numero_ordine(indirizzo: str, id_utente :str) -> None:

        num_ordine: int

        num_ordine = random.randint(0, 1000000000)
        print(f"Fornire il seguente codice al momento del ritiro : {num_ordine}")

        new_ordine = pd.DataFrame(
            [[
                num_ordine,
                id_utente,
                indirizzo,
            ]],
            columns=[
                'numero_ordine',  # <-- niente spazio finale
                'codice_fiscale',
                'indirizzo',
            ]
        )
        new_ordine.to_sql('Ordine', connection, if_exists='append', index=False)
        connection.commit()

    def stampa_carrello(self)-> None:

        for prodotto in self.carrello:
            print(f" codice : {prodotto["codice_farmaco"]} ")
            print(f" nome : {prodotto["nome"]} ")
            print(f" quantità : {self.quanto_compro[prodotto["codice_farmaco"]]} ")
            print(f" prezzo : {self.quanto_compro[prodotto["codice_farmaco"]] * float(prodotto["prezzo"])} €")

    def update_database(self, id_utente :str)->None:

        for prodotto in self.carrello:
            # si modifica la quantità di prodotto in magazzino
            new_quantity = prodotto["quantità"] - self.quanto_compro[prodotto["codice_farmaco"]]
            query = f"UPDATE FarmaciMagazzino SET quantità = '{new_quantity}' WHERE codice = '{prodotto["codice_farmaco"]}' "
            connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
            connection.commit()
            # si elimina la ricetta utilizzata nell'acquisto
            query = f"DELETE FROM Ricetta WHERE codice_farmaco ='{prodotto["codice_farmaco"]}' AND codice_fiscale = '{id_utente}' "
            connection.execute(text(query))
            connection.commit()