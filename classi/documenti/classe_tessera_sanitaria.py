from funzioni_generali.controlli_function import controlla_lunghezza, check_se_vuoto, check_scadenza
from datetime import datetime, date
from sqlalchemy import text
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

        ck_d: bool =False # abbreviazione per check_data

        print( " Di seguito si inseriscano i dati della tessera sanitaria : ")
        self.codice_fiscale = controlla_lunghezza(" CODICE FISCALE( es. RSSMRA00A01H501C ):", 16) # nel codice fiscale si contano 16 caratteri alfanumerici
        self.sesso = controlla_lunghezza(" SESSO (es. X): ", 1)
        self.luogo_nascita = check_se_vuoto(" LUOGO DI NASCITA : ")
        self.provincia = controlla_lunghezza(" PROVINCIA ( es. RM): ", 2)
        #controllo che la data di nascita sia inserita correttamente
        while not ck_d:
            data_input = controlla_lunghezza(" DATA DI NASCITA (es. gg/mm/aaaa) : ", 10)
            try:
                self.data_nascita = datetime.strptime(data_input, "%d/%m/%Y").date()
                ck_d=True
            except ValueError:
                print("Data non valida!")
                ck_d=False
        #controllo che la data di scadenza sia inserita correttamente
        ck_d= False
        while not ck_d:
            data_input = controlla_lunghezza(" DATA DI SCADENZA (es. gg/mm/aaaa) : ", 10)
            try:
                self.data_scadenza = datetime.strptime(data_input, "%d/%m/%Y").date()
                ck_d = True
            except ValueError:
                print("Data non valida!")
                ck_d=False
        self.numero_identificazione_tessera = controlla_lunghezza(" NUMERO IDENTIFICAZIONE TESSERA (es. 12345678901234567890 ): ", 20)# sulla tessera sanitaria fisica sono 20 caratteri alfanumerici

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

        """Restiurse None solo se non viene aggiornata la data di scadenza della tessera"""

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
                    data_input = controlla_lunghezza("NUOVA DATA DI SCADENZA (gg/mm/aaaa) : ", 10)
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