from sqlalchemy import text

from funzioni_generali.controlli_function import controlla, check_se_vuoto, check_scadenza
from datetime import datetime, date
from db import connection
import pandas as pd


class TesseraSanitaria :

    codice_fiscale: str
    sesso: str
    luogo_nascita: str
    provincia: str
    data_nascita: datetime.date
    data_scadenza: datetime.date
    numero_identificazione_tessera: str

    def __init__(self):

        ck: bool =False
        print( " Di seguito si inseriscano i dati della tessera sanitaria : ")
        self.codice_fiscale = controlla(" CODICE FISCALE :", 16) # nel codice fiscale si contano 16 caratteri alfanumerici
        self.sesso = controlla(" SESSO : ", 1)
        self.luogo_nascita = check_se_vuoto(" LUOGO DI NASCITA : ")
        self.provincia = controlla(" PROVINCIA : ", 2)
        #controllo che la data di nascita sia inserita correttamente
        while not ck:
            data_input = controlla(" DATA DI NASCITA (gg/mm/aaaa) : ", 10)
            try:
                self.data_nascita = datetime.strptime(data_input, "%d/%m/%Y").date()
                ck=True
            except ValueError:
                print("Data non valida!")
                ck=False
        #controllo che la data di scadenza sia inserita correttamente
        ck= False
        while not ck:
            data_input = controlla(" DATA DI SCADENZA (gg/mm/aaaa) : ", 10)
            try:
                self.data_scadenza = datetime.strptime(data_input, "%d/%m/%Y").date()
                ck = True
            except ValueError:
                print("Data non valida!")
                ck=False
        self.numero_identificazione_tessera = controlla(" NUMERO IDENTIFICAZIONE TESSERA : ", 20)# sulla tessera sanitaria fisica sono 20 caratteri alfanumerici

    def associazione_tessera_a_db(self)->None:
        new_tessera = pd.DataFrame(
            [[
                self.codice_fiscale,
                self.sesso,
                self.luogo_nascita,
                self.provincia,
                self.data_nascita,
                self.data_scadenza,
                self.numero_identificazione_tessera
            ]],
            columns=[
                'codice_fiscale',  # <-- niente spazio finale
                'sesso',
                'luogo_nascita',
                'provincia',
                'data_nascita',
                'data_scadenza',
                'numero_identificazione_tessera'
            ]
        )
        new_tessera.to_sql('TesseraSanitaria', connection, if_exists='append', index=False)
        connection.commit()

    @classmethod
    def check_se_ancora_valida(cls, codice_f: str )->None:

        new_date : datetime.date = date.today()
        query = f"SELECT data_scadenza FROM TesseraSanitaria WHERE codice_Fiscale= '{codice_f}'"
        data = pd.read_sql_query(query, connection)
        data_ck = data.iloc[0, 0]
        data_ck = datetime.strptime(data_ck, "%Y-%m-%d").date()
        data_ck = check_scadenza(data_ck)

        while not data_ck:

            print("La tessera sanitaria risulta scaduta. Vuoi aggiornare la data di scadenza ? Digitare si o no")
            verifica = input()

            if verifica == "si":

                ck : bool = False

                while not ck:
                    data_input = controlla("NUOVA DATA DI SCADENZA (gg/mm/aaaa) : ", 10)
                    try:
                        new_date = datetime.strptime(data_input, "%d/%m/%Y").date()
                        ck = True
                    except ValueError:
                        print("Data non valida!")
                        ck = False

                query = f"UPDATE TesseraSanitaria SET data_scadenza= '{new_date}' WHERE codice_Fiscale= '{codice_f}'"
                connection.execute(text(query))
                connection.commit()

            elif verifica == "no":

                print("Il profilo verrà eliminato")
                query = f"DELETE FROM TesseraSanitaria WHERE codice_Fiscale ='{codice_f}'"
                connection.execute(text(query))
                connection.commit()
                query = f"DELETE FROM ProfiloUtente WHERE id_cliente = '{codice_f}'"
                connection.execute(text(query))
                connection.commit()
                query = f"DELETE FROM Clienti WHERE  codice_fiscale = '{codice_f}'"
                connection.execute(text(query))
                connection.commit()
                return None

            else:
                print("operazione non valida")

            data_ck = check_scadenza(new_date)