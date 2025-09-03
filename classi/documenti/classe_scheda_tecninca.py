from funzioni_generali.controlli_function import check_se_vuoto
from db import connection
import pandas as pd

class SchedaTecnica :

    indicazioni_terapeutiche : str
    composizione : str
    eccipienti : str
    controindicazioni : str
    posologia : str
    avvertenze : str
    effetti_indesiderati : str

    def __init__(self)->None:
        self.indicazioni_terapeutiche = check_se_vuoto("Inserire le indicazioni terapeutiche : ")
        self.composizione = check_se_vuoto("Inserire i componenti del farmaco : ")
        self.eccipienti = check_se_vuoto("Inserire gli eccipienti del farmaco : ")
        self.controindicazioni = check_se_vuoto("Inserire le controindicazioni : ")
        self.posologia = check_se_vuoto("Inserire la posologia : ")
        self.avvertenze = check_se_vuoto("Inserire le avvertenze : ")
        self.effetti_indesiderati = check_se_vuoto("Inserire gli effetti indesiderati : ")

    def aggiungi_scheda_a_db(self, cod :str )->None:

        scheda = pd.DataFrame(
            data=[[
                cod,
                self.indicazioni_terapeutiche,
                self.composizione,
                self.eccipienti,
                self.controindicazioni,
                self.posologia,
                self.avvertenze,
                self.effetti_indesiderati,
            ]],
            columns=[
                'codice_farmaco',
                'indicazioni_terapeutiche',
                'composizione',
                'eccipienti',
                'controindicazioni',
                'posologia',
                'avvertenze',
                'effetti_indesiderati',
            ]
        )

        scheda.to_sql('SchedaTecnica', connection, if_exists='append', index=False)
        connection.commit()