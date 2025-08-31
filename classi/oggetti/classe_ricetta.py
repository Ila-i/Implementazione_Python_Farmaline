from funzioni_generali.random_function import create_random_string
from db import connection
from sqlalchemy import text
import pandas as pd
import string



class Ricetta :

    codice_ricetta : str
    id_utente :str
    codice_farmaco : str

    def __init__(self, id_u :str , cod_farmaco :str):
        self.id_utente = id_u
        self.codice_faramco = cod_farmaco
        self.codice_ricetta = ((create_random_string(4, string.digits)
                                + create_random_string(1, string.ascii_uppercase))
                                + ' '
                                + create_random_string(10, string.digits))

    @classmethod
    def verifica_dati_ricetta( cls, carrello : list[dict], quantity: dict, cod_fisc :str) -> int:

        count: int = 0
        nome_farma : str
        verifica_cod : bool = False

        for prodotto in carrello:
            #si ricerca tra i prodotti nel carrello quelli che necessitano di ricetta
            codice_val = prodotto["codice_farmaco"]
            nome_farma = prodotto["nome"]
            query = f" SELECT ricetta FROM FarmaciMagazzino WHERE codice = '{codice_val}' AND ricetta = 'si'"
            serve_ricetta = pd.read_sql_query(query, connection)  # può restituire si o rimanere vuoto

            if not serve_ricetta.empty:

                # controllo se l'utente è in possesso della ricetta per acquistare il farmaco
                query = f" SELECT codice_ricetta, codice_farmaco , nome_medico FROM Ricetta WHERE codice_farmaco ='{codice_val}' AND codice_fiscale = '{cod_fisc}'"
                ricetta_ck = pd.read_sql_query(query, connection)

                if ricetta_ck.empty:

                    print(f"Non è associata nessuna ricetta per {nome_farma} al profilo corrente, il prodotto con ricetta verrà eliminato dal carrello")
                    carrello.remove(prodotto)
                    del quantity[prodotto["codice_farmaco"]]



                if not ricetta_ck.empty:
                    if quantity[codice_val] > len(ricetta_ck):
                        print(f"La quantità di farmaco richiesta non corrisponde al numero di ricette ('{len(ricetta_ck)}') relative a quel farmaco, il prodotto verrà eliminato")
                        carrello.remove(prodotto)
                        del quantity[prodotto["codice_farmaco"]]
                    elif quantity[codice_val] < len(ricetta_ck):
                        if len(ricetta_ck) > 1:
                            #se sono state prescritte più ricette si stampa quelle associate e si fa scegliere all'utente quale usare
                            for ricetta in ricetta_ck.to_dict(orient="records"):
                                print(ricetta)
                        for i in range(quantity[codice_val]):
                            ck=False
                            while not ck:
                                codice_input = input("\nInserire il codice della ricetta che si vuole utilizzare : ")

                                for ricetta in ricetta_ck.to_dict(orient="records"):
                                    if codice_input == ricetta["codice_ricetta"]:
                                        verifica_cod = True
                                        query = f"DELETE FROM Ricetta WHERE codice_ricetta = '{codice_input}'"
                                        connection.execute(text(query))
                                        connection.commit()
                                        ck=True
                                        ricetta_ck = ricetta_ck[ricetta_ck["codice_ricetta"] != codice_input]
                                        #crea una serie booleana: True per le righe in cui codice_ricetta è diverso da quello scelto, False per la riga corrispondente al codice inserito dall'utente
                                        # ricetta_ck[...] -> filtra il DataFrame tenendo solo le righe dove la condizione è True ricetta_ck = ... -> riassegna il Dataframe filtrato a se stesso
                                        break

                                    if not verifica_cod:
                                        print("Il codice inserito non è valido, o non è presente tra quelli elencati")

                    elif quantity[codice_val] == len(ricetta_ck):

                        for codice in ricetta_ck["codice_ricetta"].tolist():
                            query =f"DELETE FROM Ricetta WHERE codice_ricetta = '{codice}'"
                            connection.execute(text(query))
                            connection.commit()


                    # 5) conteggio: quante unità/ricette sono state processate
                    count += 1

        return count

    def aggiungi_ricetta_a_db(self)->None:

        ricetta = pd.DataFrame(
            columns=[
                'codice_ricetta',
                'codice_fiscale',
                'codice_farmaco',
            ],
            data=[
                    self.codice_ricetta,
                    self.id_utente,
                    self.codice_farmaco
                ],
        )
        ricetta.to_sql('Ricetta', connection, if_exists='append', index=False)
        connection.commit()


