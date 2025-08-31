from funzioni_generali.controlli_function import check_se_vuoto
from db import connection
import pandas as pd


class TesserinoProfessionale :

    ordine_di_appartenenza: str # indica il settore lavorativo a cui appartieni
    n_matricola : str # indica il numero di iscrizione all'albo di riferimento

    def __init__(self, ordine :str):
        self.ordine_di_appartenenza = ordine
        self.n_matricola =check_se_vuoto("Inserire il proprio numero di matricola : ")

    def aggiunta_tessera_a_db(self)->None:

        new_tesserino = pd.DataFrame(
            columns=[
                'ordine_appartenenza',
                'n_matricola'
            ],
            data=[
                self.ordine_di_appartenenza,
                self.n_matricola
            ]
        )
        new_tesserino.to_sql('TesserinoProfessionale', connection, if_exists='append', index=False)
        connection.commit()