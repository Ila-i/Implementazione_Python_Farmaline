from pandas import DataFrame

from funzioni_generali.random_function import create_random_string
from db import connection
import pandas as pd
import string

class Ricetta :

    codice_ricetta : str
    id_utente :str
    codice_farmaco : str
    matricola_medico :str

    def __init__(self, id_u :str , cod_farmaco :str, matricola :str)->None:
        self.id_utente = id_u
        self.codice_farmaco = cod_farmaco
        #per assegnare un codice nella forma 1234A 1234567890 alle ricette
        self.codice_ricetta = ((create_random_string(4, string.digits)
                                + create_random_string(1, string.ascii_uppercase))
                                + ' '
                                + create_random_string(10, string.digits))
        self.matricola_medico = matricola

    @classmethod
    def verifica_dati_ricetta( cls, carrello : list[dict], quantity: dict, cod_fisc :str) -> list[str]:

        ricette_usate : list[str] = []

        # si ricerca tra i prodotti nel carrello quelli che necessitano di ricetta
        for prodotto in carrello:

            codice_farma: str
            nome_farma: str

            codice_farma = prodotto["codice_farmaco"]
            nome_farma = prodotto["nome"]

            query:str = f" SELECT serve_ricetta FROM FarmaciMagazzino WHERE codice_farmaco = '{codice_farma}' AND serve_ricetta = 'si'"
            serve_ricetta: DataFrame = pd.read_sql_query(query, connection)

            # sezione dedicata al caso in cui il cliente sta acquistando farmaci che richiedono ricetta
            if not serve_ricetta.empty:

                # controllo se l'utente è in possesso della ricetta per acquistare il farmaco
                query = f" SELECT codice_ricetta FROM Ricetta WHERE codice_farmaco ='{codice_farma}' AND codice_fiscale = '{cod_fisc}'"
                ricetta_ck:DataFrame = pd.read_sql_query(query, connection)

                # il cliente non ha ricette associate per quel farmaco, si elimina il prodotto dal carrello
                if ricetta_ck.empty:
                    print(f"Non è associata nessuna ricetta per {nome_farma} al profilo corrente, il prodotto con ricetta verrà eliminato dal carrello")
                    carrello.remove(prodotto)
                    del quantity[codice_farma]

                # il cliente ha ricette associate per quel farmaco
                else:

                    # il numero di ricette è inferiore alla quantità di farmaco che si vuole acquistare, si elimina il prodotto dal carrello
                    if quantity[codice_farma] > len(ricetta_ck):
                        print(f"La quantità di farmaco richiesta non corrisponde al numero di ricette ('{len(ricetta_ck)}') relative a {nome_farma}, il prodotto verrà tolto dal carrello")
                        carrello.remove(prodotto)
                        del quantity[codice_farma]

                    # il numero di ricette è superiore alla quantità di farmaco che si vuole acquistare
                    elif quantity[codice_farma] < len(ricetta_ck):

                        #si stampa l'elenco delle ricette associate profilo con cui si sta effettuando l'acquisto
                        for ricetta in ricetta_ck.to_dict(orient="records"):
                            print(ricetta)

                        # si fa scegliere all'utente quali ricette usare
                        for i in range(quantity[codice_farma]):
                            ck=False
                            while not ck:
                                codice_input:str = input("\nInserire il codice della ricetta che si vuole utilizzare : ")

                                #si controlla che il codice inserito sia presente nell'elenco e non sia già stato selezionato
                                for ricetta in ricetta_ck.to_dict(orient="records"):
                                    if codice_input == ricetta["codice_ricetta"] :
                                        if ricette_usate:
                                            for ri_usate in ricette_usate:
                                                if codice_input != ri_usate:
                                                    ricette_usate.append(codice_input)
                                                    ck=True
                                                    break
                                        else :# se è la prima ricetta che viene inserita il controllo si fa solo sull' elenco di ricette
                                            ricette_usate.append(codice_input)
                                            ck=True
                                            break

                                if not ck:
                                    print("Il codice inserito non è valido o non è presente tra quelli elencati")

                    # il numero di ricette è pari alla quantità di farmaco che si vuole acquistare
                    elif quantity[codice_farma] == len(ricetta_ck):

                        for codice_r in ricetta_ck["codice_ricetta"].tolist():
                            ricette_usate.append(codice_r)

        return ricette_usate

    def aggiungi_ricetta_a_db(self)->None:

        ricetta = pd.DataFrame(
            columns=[
                'codice_ricetta',
                'codice_fiscale',
                'codice_farmaco',
                'matricola_medico'
            ],
            data=[[
                    self.codice_ricetta,
                    self.id_utente,
                    self.codice_farmaco,
                    self.matricola_medico
                ]]
        )
        ricetta.to_sql('Ricetta', connection, if_exists='append', index=False)
        connection.commit()


