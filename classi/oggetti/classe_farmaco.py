from pandas import DataFrame

from classi.documenti.classe_scheda_tecninca import SchedaTecnica
from funzioni_generali.controlli_function import check_se_vuoto, controlla_si_no
from db import connection
import pandas as pd

class Farmaco :

    nome : str
    serve_ricetta: str
    preparato_galenico: str
    prezzo: float
    quantity: int
    codice_farmaco: str
    scheda_tecnica : SchedaTecnica

    def __init__(self, codice:str)->None:

        self.nome = check_se_vuoto("Inserire il nome del farmaco : ")
        self.serve_ricetta = controlla_si_no("Il farmaco necessita di ricetta ? (digitare si o no) : ")
        self.preparato_galenico = controlla_si_no("È un preparato galenico ? (digitare si o no) : ")
        self.quantity = 0
        self.prezzo = 0.0
        self.codice_farmaco = codice

        #per controllare che la quantità inserita sia un valore valido
        while self.quantity <= 0:
            try:
                self.quantity = int(input("Inserire la quantità di farmaco che si vuole aggiungere in magazzino : "))
            except ValueError:
                print("Il valore inserito non è compatibile, riprovare")
            if self.quantity <= 0:
                print("Il parametro non può assumere valore negativo o nullo")

        # per controllare che il prezzo inserito sia un valore valido
        while self.prezzo <= 0:
            try:
                self.prezzo = float(input("Inserire il prezzo del prodotto in euro ( 0.00 ): "))
            except ValueError:
                print("Il valore inserito non è compatibile, riprovare")
            if self.prezzo <= 0:
                print("Il parametro non può assumere valore negativo o nullo")

        self.scheda_tecnica= SchedaTecnica()

    @classmethod
    def controllo_codice_farmaco(cls, results: DataFrame) -> str:

        """Controlla se il codice del faramco è presente o meno nell'elenco trovato durante la ricerca

        Restituisce il codice corretto """

        codice_input: str = ''
        # sezione dedicata al

        if len(results) > 1:  # Se ce più di un farmaco nell'elenco

            ck: bool = False

            while not ck:

                codice_input = input("\nInserire il codice del farmaco che si vuole acquistare: ")
                verifica_cod: bool = False

                for prodotto in results.to_dict(orient="records"):
                    if codice_input == prodotto["codice_farmaco"]:
                        verifica_cod = True
                        break

                if not verifica_cod:
                    print("Il codice inserito non è valido, o non è presente tra quelli elencati")
                    ck = False
                else:
                    ck = True

        else:  # Se ce solo un farmaco nell'elenco
            codice_input = (results.iloc[0]["codice_farmaco"])

        return codice_input

    @classmethod
    def controllo_quanto_farmaco(cls,codice_f :str,  quanto_in_m: int, ck_se_presente: bool , quanto_in_c:int = 0) -> int:

        """Controlla che la quantità di farmaco che si vuole acquistare sia disponibile in magazzino

        :param codice_f indica il codice del farmaco selezionato
        :param quanto_in_m indica la quantità di faramco nel magazzino
        :param ck_se_presente indica se il faramco era già stato selezionato
        :param quanto_in_c indica la quantà di farmaco gia presente nel carrello se precedentemente selezionato

        Restituisce la quantità corretta di farmaco nel caso in cui ci fosse una quanità sufficente in magazzino
        Restituisce 0 nel caso in cui il faramco fosse terminato"""

        controllo_q: bool = False

        while not controllo_q:  # consente di riprovare se non è sufficente la quantità

            quantity: int = 0

            # fornisce informazioni sulla quantità disponibile in magazzino tenendo conto di una precente selzione dello stesso farmaco
            if ck_se_presente:
                rimane = quanto_in_m - quanto_in_c
                print(" Il farmaco è stato precedentemente selezionato. ")
                print(f"Con la precedente selzione rimangono {rimane} campioni ")
                if rimane == 0:
                    print("Il prodotto è terminato non è possibile acquistarlo")
                    break

            # controllo sull'inserimento della quantità di prodotto che si vuole acquistare
            while quantity <=0:
                try:
                    quantity = int(input("Inserire la quantità di prodotto che si vuole acquistare : "))
                    if quantity <= 0:
                        print("non può assumere valore nullo o negativo, riprovare ")

                except ValueError:
                    print("il valore inserito non è compatibile, riprovare")

            if ck_se_presente:  # se già selezionato la nuova quantità viene aggiunta alla precedente
                quantity = quantity + quanto_in_c

            # controlla che la quantità che si vuole acquistare non sia superiore a quella disponibile in magazzino
            query = f"SELECT quantità FROM FarmaciMagazzino WHERE quantità < '{quantity}' AND codice_farmaco = '{codice_f}' "
            q_trovata = pd.read_sql(query, connection)

            if q_trovata.empty:  # nel magazzino c'è una quanittà di prodotto sufficiente
                return quantity

            else:  # non trova riscontri in magazzino
                # prende la quantità di prodotto dal database e controlla se è nulla o meno
                if q_trovata.iloc[0, 0] == 0:
                    print("Il prodotto è terminato non è possibile acquistarlo")
                    return 0
                else:
                    print("La quantità di farmaco in magazzino non è sufficiente, riprovare  ")

    def aggiungi_farmaco_a_db(self)->None:

        self.scheda_tecnica.aggiungi_scheda_a_db(self.codice_farmaco)

        farmaco = pd.DataFrame(
            columns=[
                'nome',
                'serve_ricetta',
                'preparato_galenico',
                'prezzo',
                'quantità',
                'codice_farmaco',
            ],
            data=[[
                self.nome,
                self.serve_ricetta,
                self.preparato_galenico,
                self.prezzo,
                self.quantity,
                self.codice_farmaco,
            ]]
        )
        farmaco.to_sql('FarmaciMagazzino', connection, if_exists='append', index=False)
        connection.commit()