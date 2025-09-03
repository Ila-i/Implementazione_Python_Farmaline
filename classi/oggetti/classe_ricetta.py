from funzioni_generali.random_function import create_random_string
from sqlalchemy import text
from db import connection
import pandas as pd
import string

class Ricetta :

    codice_ricetta : str
    id_utente :str
    codice_farmaco : str

    def __init__(self, id_u :str , cod_farmaco :str)->None:
        self.id_utente = id_u
        self.codice_farmaco = cod_farmaco
        #per assegnare un codice nella forma 1234A 1234567890 alle ricette
        self.codice_ricetta = ((create_random_string(4, string.digits)
                                + create_random_string(1, string.ascii_uppercase))
                                + ' '
                                + create_random_string(10, string.digits))

    @classmethod
    def verifica_dati_ricetta( cls, carrello : list[dict], quantity: dict, cod_fisc :str) -> int:

        count: int = 0

        # si ricerca tra i prodotti nel carrello quelli che necessitano di ricetta
        for prodotto in carrello:

            nome_farma: str

            codice_val = prodotto["codice_farmaco"]
            nome_farma = prodotto["nome"]
            query = f" SELECT serve_ricetta FROM FarmaciMagazzino WHERE codice_farmaco = '{codice_val}' AND serve_ricetta = 'si'"
            serve_ricetta = pd.read_sql_query(query, connection)  # può restituire la stringa "si" o rimanere vuoto

            # sezione dedicata al caso in cui il cliente sta acquistando farmaci che richiedono ricetta
            if not serve_ricetta.empty:

                # controllo se l'utente è in possesso della ricetta per acquistare il farmaco
                query = f" SELECT codice_ricetta FROM Ricetta WHERE codice_farmaco ='{codice_val}' AND codice_fiscale = '{cod_fisc}'"
                ricetta_ck = pd.read_sql_query(query, connection)

                if ricetta_ck.empty: # il cliente non ha ricette associate per quel farmaco

                    print(f"Non è associata nessuna ricetta per {nome_farma} al profilo corrente, il prodotto con ricetta verrà eliminato dal carrello")
                    carrello.remove(prodotto)
                    del quantity[codice_val]#codice_val è la chiave del dizionario quantity

                else: #il cliente ha ricette associate per quel farmaco

                    if quantity[codice_val] > len(ricetta_ck):# il numero di ricette è insufficiente per l'acquisto
                        print(f"La quantità di farmaco richiesta non corrisponde al numero di ricette ('{len(ricetta_ck)}') relative a quel farmaco, il prodotto verrà eliminato")
                        carrello.remove(prodotto)
                        del quantity[codice_val]

                    elif quantity[codice_val] < len(ricetta_ck): # il numero di ricette è superiore a quello necessario per l'acquisto

                        #se sono state prescritte più ricette si stampa l'elenco di quelle associate
                        for ricetta in ricetta_ck.to_dict(orient="records"):
                            print(ricetta)

                        # si fa scegliere all'utente quali ricette usare
                        for i in range(quantity[codice_val]):

                            ck=False

                            while not ck:

                                codice_input = input("\nInserire il codice della ricetta che si vuole utilizzare : ")

                                for ricetta in ricetta_ck.to_dict(orient="records"):

                                    if codice_input == ricetta["codice_ricetta"]:
                                        query = f"DELETE FROM Ricetta WHERE codice_ricetta = '{codice_input}'"
                                        connection.execute(text(query))
                                        connection.commit()
                                        ck=True

                                        query = f" SELECT codice_ricetta FROM Ricetta WHERE codice_farmaco ='{codice_val}' AND codice_fiscale = '{cod_fisc}'"
                                        ricetta_ck = pd.read_sql_query(query, connection)
                                        break

                                if not ck:
                                    print("Il codice inserito non è valido o non è presente tra quelli elencati")

                    elif quantity[codice_val] == len(ricetta_ck): # il numero di ricette è sufficente

                        for codice in ricetta_ck["codice_ricetta"].tolist():
                            query =f"DELETE FROM Ricetta WHERE codice_ricetta = '{codice}'"
                            connection.execute(text(query))
                            connection.commit()


                    # conta quanti farmaci con ricetta sono presenti nel carrello e si posso acquistare
                    count += 1

        return count

    def aggiungi_ricetta_a_db(self)->None:

        ricetta = pd.DataFrame(
            columns=[
                'codice_ricetta',
                'codice_fiscale',
                'codice_farmaco',
            ],
            data=[[
                    self.codice_ricetta,
                    self.id_utente,
                    self.codice_farmaco
                ]]
        )
        ricetta.to_sql('Ricetta', connection, if_exists='append', index=False)
        connection.commit()


