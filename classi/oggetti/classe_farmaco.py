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
        ck_prezzo: bool = False
        while not ck_prezzo:
            try:
                self.prezzo = float(input("Inserire il prezzo del prodotto in euro ( 0.00 ): "))
                ck_prezzo = True
            except ValueError:
                print("Il valore inserito non è compatibile, riprovare")

        self.scheda_tecnica= SchedaTecnica()

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
