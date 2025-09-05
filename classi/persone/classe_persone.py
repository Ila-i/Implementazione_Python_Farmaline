from funzioni_generali.controlli_function import check_scadenza, check_se_vuoto, controlla_lunghezza, check_nascita, controlla_si_no
from classi.documenti.classe_tesserino_professionale import TesserinoProfessionale
from classi.documenti.classe_tessera_sanitaria import TesseraSanitaria
from classi.oggetti.classe_farmaco import Farmaco
from classi.oggetti.classe_ricetta import Ricetta
from classi.oggetti.classe_ordine import Ordine
from abc import ABC, abstractmethod
from datetime import datetime, date
from dateutil.utils import today
from typing import Optional
from sqlalchemy import text
from pandas import DataFrame
from db import connection
import pandas as pd

class Persona (ABC) :

    nome: str
    cognome: str

    def __init__(self)->None:
        self.nome = check_se_vuoto("Inserire il proprio nome : ")
        self.cognome = check_se_vuoto("Inserire il proprio cognome : ")

    @classmethod
    def registrazione_utente(cls) -> bool:

        """Restituisce True se la registrazione è avvenuta correttamente
        Altrimenti vengono terminate le operazioni
        """

        print("Per registrarsi seguire le istruzioni mostrate di seguito")

        verifica: bool = False
        pearson: Persona
        controllo_op: Optional[str] #controllo operazione

        while not verifica:

            print("Digitare 1 se si desidera iscriversi come cliente")
            print("Digitare 2 se si desidera iscriversi come farmacista")
            print("Digitare 3 se si desidera iscriversi come medico")
            controllo_op= input()

            #registrazione cliente
            if controllo_op == '1':
                pearson = Cliente()
                return pearson.iscriversi()

            #registrazione farmacista
            elif controllo_op == '2':
                pearson = LavoratoreSanitario("farmacista")
                return pearson.iscriversi()

            #registrazione medico
            elif controllo_op == '3':
                pearson = LavoratoreSanitario("medico")
                return pearson.iscriversi()

            else:
                print("opzione non valida riprovare")

    @abstractmethod
    def iscriversi(self) -> bool:
        """Restituisce True se le operazioni sono andate a buon fine
        Restituisce False altrimenti"""
        ...

    @abstractmethod
    def crea_profilo(self) ->None:
        """Genera un profilo utente che viene aggiunto al database della farmacia """
        ...

    @abstractmethod
    def aggiungi_persona_a_db(self)-> None:
        ...

class ProfiloUtente(ABC):

    nome_utente: str
    password: str
    tipo_profilo: str
    id_utente :str

    def __init__(self, nome : str, password :str, id_u : str , tipo_p : str)-> None:
        self.nome_utente = nome
        self.password = password
        self.id_utente = id_u
        self.tipo_profilo = tipo_p

    @classmethod
    def accesso_utente(cls) -> str:

        """ Ritorna il nome utente quando l'operazione va a buon fine.
        Ritorna 2 se si vuole passare al processo di registazione.
        Ritorna exit per terminare le operazioni.
        """
        username: str
        tentativi: int = 3
        query : str

        print("INSERIMENTO DATI PER ACCESSO")

        # sezione dedicata al controllo del nome utente, si verifica se è presente nel database
        username = check_se_vuoto("Inserire il proprio nome utente : ")
        query = f"SELECT nome_utente, password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
        profile_check : DataFrame = pd.read_sql(query, connection)

        while profile_check.empty:

            username = check_se_vuoto(f" Il nome utente inserito non appartiente a un utente registrato, riprovare (tentativi rimasti {tentativi}): ")
            query = f"SELECT nome_utente, password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
            profile_check = pd.read_sql(query, connection)
            tentativi -= 1

            if tentativi == 0:
                ck_op : bool = False
                op: str  # abbreviazione per operazione

                while not ck_op :
                    print("Digitare 2 per iscriversi al servizio se non si è in possesso di un profilo utente già registrato")
                    print("Digitare exit se si vuole terminare le operazioni")
                    op = check_se_vuoto('')
                    if op== "2" or op=="exit":
                        return op
                    else :
                        print("operazione non valida, riprovare")


        # sezione dedicata al controllo password, si esegue questa sezione solo quando viene trovato il nome utente nel database
        if tentativi > 0:

            pw: str  # pw abbreviazione per password
            tentativi = 3

            pw = check_se_vuoto("Inserire la propria password : ")
            pw_check = str(profile_check.iloc[0, 1])

            while pw != pw_check:
                tentativi -= 1
                if tentativi > 0:
                    pw = check_se_vuoto(
                        f" La password inserita  per questo username è incorretta, riprovare (tentetivi rimasti {tentativi}): ")

                elif tentativi == 0:
                    print(f"La password inserita  per questo username è incorretta, tentativi rimasti {tentativi}")
                    print(f"Operazione fallita")
                    return "exit"

        return username

    @abstractmethod
    def aggiunta_profilo_utente_a_db(self) -> None:
        ...

    def controllo_nome_utente(self) -> bool:

        """Verifica che il nome utente inserito per la registrazione non sia già in uso

        Ritorna False quando il nome utente  è già in uso
        Ritorna True altrimenti
        """

        query: str  = f"SELECT * FROM ProfiloUtente WHERE nome_utente = '{self.nome_utente}'"
        profilo_esistente: DataFrame = pd.read_sql(query, connection)

        if not profilo_esistente.empty:
            print(f"Il nome utente '{self.nome_utente}' è già in uso. Scegliere un altro nome.")
            return False
        else:
            return True

    @classmethod
    def get_profilo(cls, username :str ) -> "ProfiloUtente": #"ProfiloUtente" usato per indicare che il metodo può restiture un oggetto della classe senza che venga istanziata

        """Restituisce il ProfiloUtente con cui si fa l'accesso se l'operazione si è conclusa correttamente
        Restituisce None altrimenti
        """

        query:str = f"SELECT password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
        profile : DataFrame = pd.read_sql_query(query, connection)

        pw: str = str(profile.iloc[0, 0])
        tipo_prof: str = str(profile.iloc[0, 1])

        if tipo_prof == "cliente":

            d_c: Optional[DataFrame, str]
            query = f"SELECT id_cliente FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_c = pd.read_sql_query(query, connection)
            id_c = str(id_c.iloc[0, 0])
            return ProfiloCliente(username, pw, id_c, tipo_prof)

        elif tipo_prof == "farmacista":

            id_f: Optional[DataFrame, str]
            query = f"SELECT id_sanitari FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_f = pd.read_sql_query(query, connection)
            id_f = str(id_f.iloc[0, 0])
            return ProfiloFarmacista(username, pw, id_f, tipo_prof)

        elif tipo_prof == "medico":

            id_m: Optional[DataFrame, str]
            query = f"SELECT id_sanitari FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_m = pd.read_sql_query(query, connection)
            id_m = str(id_m.iloc[0, 0])
            return ProfiloMedico(username, pw, id_m, tipo_prof)

        else:
            print("Operazione fallita")
            pass


class ProfilolavoratoreSanitario(ProfiloUtente) :

    def aggiunta_profilo_utente_a_db(self) -> None:

        new_profile = pd.DataFrame(
            columns=[
                'nome_utente',
                'password',
                'tipo_profilo',
                'id_sanitari'
            ],
            data=[[
                self.nome_utente,
                self.password,
                self.tipo_profilo,
                self.id_utente
            ]]
        )
        new_profile.to_sql('ProfiloUtente', connection, if_exists='append', index=False)
        connection.commit()

        print("Profilo utente aggiunto con successo.")

class ProfiloCliente(ProfiloUtente) :

    ordine : Ordine

    def __init__(self, nome: str, password: str, id_u: str, tipo_p: str)->None:
        super().__init__(nome,password,id_u,tipo_p)
        self.ordine=Ordine()

    def ricerca(self) -> None:

        """Permette di effettuare una ricerca di faramci nel magazzino tramite una barra di ricerca o tramite l'uso di filtri"""

        scelta_filtri: str
        query: str
        results: DataFrame #risultati che si ottengono dalla query

        print("BARRA DI RICERCA")
        scelta_filtri = controlla_si_no("Vuoi applicare dei filtri alla tua ricerca? (digitare si o no) : ")

        if scelta_filtri == "si":

            print("Indica almeno uno dei seguenti filtri, quando non si vuole mettere un filtro premere semplicemente invio")
            indicazioni_terapeutiche : str = input("Inserire la patologia da trattare : ")
            composizione : str = input("Indicare il principio attivo del farmaco : ")
            posologia : str= input("Indicare se si sta cercando farmaci per adulti, adolescenti o bambini: ")

            filters: list[str] = []

            if indicazioni_terapeutiche:
                filters.append(f"LOWER(s.indicazioni_terapeutiche) LIKE LOWER ('%{indicazioni_terapeutiche}%')")

            if composizione:
                filters.append(f"LOWER (s.composizione) LIKE LOWER ('%{composizione}%')")

            if posologia:
                filters.append(f"LOWER (s.posologia) LIKE LOWER ('%{posologia}%')")

            query= """
                    SELECT 
                        f.codice_farmaco, 
                        f.nome,
                        f.serve_ricetta,
                        f.preparato_galenico,
                        f.prezzo,
                        f.quantità,
                        s.indicazioni_terapeutiche,
                        s.composizione,
                        s.eccipienti,
                        s.controindicazioni,
                        s.posologia,
                        s.avvertenze,
                        s.effetti_indesiderati
                    FROM FarmaciMagazzino AS f
                    JOIN SchedaTecnica AS s
                      ON f.codice_farmaco = s.codice_farmaco 
                    """

            if filters:
                query += " WHERE " + " AND ".join(filters) # compone una stringa con le clausole WHERE e AND che viene aggiunta alla query per applicare i filtri inseriti dall'utente
                results = pd.read_sql(query, connection)

            else:
                print("Nessun filtro inserito. Ricerca annullata.")
                results = pd.DataFrame()  # equivalente a lista vuota

        elif scelta_filtri == "no":

            medicinale: str
            medicinale = input("Digitare il nome del farmaco che si sta cercando (premendo invio si visualizzano tutti i prodotti disponili in magazzino): ")

            query = f"""
                    SELECT
                        f.codice_farmaco,      -- alias univoco
                        f.nome,
                        f.serve_ricetta,
                        f.preparato_galenico,
                        f.prezzo,
                        f.quantità,
                        s.indicazioni_terapeutiche,
                        s.composizione,
                        s.eccipienti,
                        s.controindicazioni,
                        s.posologia,
                        s.avvertenze,
                        s.effetti_indesiderati
                    FROM FarmaciMagazzino AS f
                    JOIN SchedaTecnica AS s
                      ON f.codice_farmaco = s.codice_farmaco
                        WHERE LOWER(TRIM(f.nome)) LIKE LOWER('%{medicinale}%') -- TRIM dà più tolleranza sugli spazi 
                                """
            results = pd.read_sql(query, connection)

        else:
            print("Operazione non valida.")
            results = pd.DataFrame()  # equivalente a lista vuota

        # Stampa dei risultati
        if not results.empty:
            for farmaco in results.to_dict(orient="records"):
                print(farmaco)

            self.ordine.aggiungi_a_carrello(results)

        if results.empty:
            print("Nessun farmaco trovato.")

    def scelta_indirizzi(self) -> None:

        """Permette di selezionare l'indirizzo di consegna se non ci sono farmaci con ricetta nel carrello
         Altrimenti seleziona automaticamente l'idirizzo della farmacia fisica
         """

        ricette_usate: list[str] = Ricetta.verifica_dati_ricetta(self.ordine.carrello, self.ordine.quanto_compro, self.id_utente)

        if len(self.ordine.carrello) > 0 : # il carrello non è vuoto

            ck_op :bool = False
            scelta_ind: str
            indirizzo_farmacia : str = "Via Università di Santa Marta, 26"

            while not ck_op:

                # non ci sono farmaci con ricetta nel carrello, si può selezionare l'indirizzo di consegna
                if not ricette_usate :

                    print("Digitare 1 per ricevere l'ordine a domicilio ")
                    print("Digitare 2 per ritirare l'ordine nella farmacia fisica")
                    scelta_ind = input()

                # ci sono farmaci con ricetta nel carrello, non si può selezionare l'indirizzo di consegna
                else :
                    scelta_ind= "2"

                if scelta_ind == "1":

                    indirizzo_domicilio: str
                    indirizzo_domicilio = input("Inserire l'indirizzo di domicilio a cui si vuole ricevere l'ordine : ")
                    print(f"L'ordine sarà spedito presso {indirizzo_domicilio}")

                    self.pagare(indirizzo_domicilio, ricette_usate)
                    ck_op = True

                elif scelta_ind== "2":
                    print(f"L'ordine potrà essere ritirato entro 10 giorni presso la nostra sede fisica in {indirizzo_farmacia}")

                    self.pagare(indirizzo_farmacia, ricette_usate)
                    ck_op = True

                else:
                    print("operazione non valida, riprovare ")
        else : # le operazioni vengono terminate se il carrello risulta vuoto
            print("il carrello è vuoto , l'operazione di acquisto verrà terminata")

    def pagare(self, indirizzo: str, ricette_usate:list[str] ) -> None:

        """Permette di selezionare il metodo di pagamento con carta o con portafoglio digitale"""

        prezzo_tot: float = 0

        self.ordine.stampa_carrello()

        for prodotto in self.ordine.carrello:
            prezzo_tot = prezzo_tot + float(prodotto["prezzo"]) * self.ordine.quanto_compro[prodotto["codice_farmaco"]]

        print(f"Prezzo totale dell'ordine : {prezzo_tot:.2f} €")

        print("Digitare 1 se si desidera procedere al pagamento")
        print("Digitare exit se si desidera annullare l'operazione")
        scelta = input()

        if scelta == "1":

            metodo: str

            print("Scegliere metodo di pagamento")
            print("Digitare 1 per pagare con carta di credito o debito (American Express, Euro/Mastercard, Visa, Maestro)")
            print("Digitare 2 per pagare con portafoglio digitale (paypal , Google pay, Apple pay)")
            metodo = input()

            #pagamento con carta
            if metodo == "1":

                ck_data: bool = False
                data_scadenza : datetime.date = today()

                print("INSERIMENTO DATI CARTA")
                nome = check_se_vuoto("Inserire il nome dell'intestatario : ")
                cognome = check_se_vuoto("Inserire il cognome dell'intestatario : ")
                numero_carta = controlla_lunghezza("Inserire il numero della carta (es. 1234567890123456 ): ", 16)
                cvc = controlla_lunghezza("Inserire il CVC (es. 123 ): ", 3)
                while not ck_data :
                    data_input = controlla_lunghezza("Inserire la data di scadenza della carta(es. gg/mm/aaaa ): ", 10)

                    try:
                        data_scadenza = datetime.strptime(data_input, "%d/%m/%Y").date()
                        ck_data = True
                    except ValueError:
                        print("Data non valida!")
                        ck_data = False

                print("DATI DELLA CARTA")
                print(f"NOME : {nome}")
                print(f"COGNOME : {cognome}")
                print(f"NUMERO CARTA : {numero_carta}")
                print(f"DATA SCADENZA : {data_scadenza}")
                print(f"CVC : {cvc}")

                ck_data = check_scadenza(data_scadenza)

                if not ck_data:
                    print("Operazione fallita") # se la carta è scaduta
                else:
                    print("Operazione andata a buon fine")
                    self.ordine.aggiungi_ordine_a_db(indirizzo, self.id_utente)
                    self.ordine.update_database(ricette_usate)
                    print(f"Fornire il seguente codice al momento del ritiro : {self.ordine.codice_ordine}")

            #pagamento con portafoglio digitale
            elif metodo == "2":
                print("Operazione andata a buon fine")
                self.ordine.aggiungi_ordine_a_db(indirizzo, self.id_utente)
                self.ordine.update_database(ricette_usate)
                print(f"Fornire il seguente codice al momento del ritiro : {self.ordine.codice_ordine}")

            else :
                print("Opzione non valida")

        elif scelta == "exit":
            print("Operazione annullata")
        else:
            print("Opzione non valida")

    def aggiunta_profilo_utente_a_db(self) -> None:

        new_profile = pd.DataFrame(
            columns=[
                'nome_utente',
                'password',
                'tipo_profilo',
                'id_cliente'
            ],
            data=[[
                self.nome_utente,
                self.password,
                self.tipo_profilo,
                self.id_utente
            ]]
        )
        new_profile.to_sql('ProfiloUtente', connection, if_exists='append', index=False)
        connection.commit()

        print("Profilo utente aggiunto con successo.")

class ProfiloFarmacista(ProfilolavoratoreSanitario) :

    @staticmethod
    def verifica_ordine() -> None:

        """Consente al farmacista di verificare che l'ordine del cliente sia all'interno del database
         In caso positivo l'ordine viene eliminato dal database
         Altrimenti mostra un messaggio di 'operazione fallita'
         """

        cod_fisc: str
        n_ordine: str
        count: int = 3 # per contare il numero di tentativi di inserimento dei dati richiesti

        print("RICERCA ORDINE NEL DATABASE")

        cod_fisc = controlla_lunghezza("Inserire il codice fiscale del cliente( es. RSSMRA00A01H501C ) : ", 16 )
        n_ordine = check_se_vuoto("Inserire il numero dell'ordine : ")

        query:str = f"SELECT * FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo_consegna = 'Via Università di Santa Marta, 26' "
        trovato: DataFrame = pd.read_sql(query, connection) # rimane vuoto se non si trova l'ordine nel database

        while trovato.empty:

            print(f"Ordine non trovato, riprovare (tentativi rimasti {count})")
            cod_fisc = controlla_lunghezza("Inserire il codice fiscale del cliente ( es. RSSMRA00A01H501C )  : ", 16)
            n_ordine = check_se_vuoto("Inserire il numero dell'ordine : ")

            query = f"SELECT * FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo_consegna = 'Via Università di Santa Marta, 26' "
            trovato = pd.read_sql(query, connection)
            count -= 1

            if count == 0:
                print("Operazione fallita")
                return None

        if count > 0:
            print("Ordine trovato")
            print(str(trovato.iloc[0]))
            query = f"DELETE FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo_consegna = 'Via Università di Santa Marta, 26' "
            connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
            connection.commit()
            print("Ordine rimosso dal database")
        else:
            print("Errore")

    @staticmethod
    def aggiorna_magazzino() -> None:

        """Consente di aggiornare le quantità dei prodotti che stanno per terminare o sono già terminati"""

        controllo_scelta: bool = False

        # sezione di codice per cercare nel database se ci sono farmaci che stanno per terminare
        query: str = "SELECT codice_farmaco, nome, quantità FROM FarmaciMagazzino WHERE quantità <= 2 "
        riordinare: DataFrame = pd.read_sql(query, connection)

        if not riordinare.empty:
            print("ATTENZIONE!! I seguenti farmaci stanno per terminare o sono già terminati ")

            for farmaco in riordinare.to_dict(orient="records"):
                print(farmaco)
        else:
            print("Non ci sono prodotti che stanno per terminare o sono già terminati")
            return None

        # sezione di codice che permette di aggiornare le quantità di faramaci che stanno per terminare
        while not controllo_scelta:

            scelta_op: str

            print("Digitare 1 se si vuole aggiornare le quantità dei farmaci sopra elencati")
            print("Digiatre exit per terminare le operazioni")
            scelta_op = input()

            while scelta_op == "1":

                new_quantity: int = 0
                cod: str = input("Inserire il codice del farmaco che si vuole aggiornare : ")

                query = f"SELECT codice_farmaco FROM FarmaciMagazzino WHERE codice_farmaco = '{cod}' AND quantità <= 2 "
                ricerca: DataFrame = pd.read_sql(query, connection)

                if not ricerca.empty:

                    while new_quantity <= 0:
                        try:
                            new_quantity = int(input("Inserire la quantità aggiornata : "))
                        except ValueError:
                            print("Il valore inserito non è compatibile, riprovare ")

                        if new_quantity <= 0:
                            print("Il parametro non può assumere valore negativo o nullo")

                    query = f"UPDATE FarmaciMagazzino SET quantità = '{new_quantity}' WHERE codice_farmaco = '{cod}'"
                    connection.execute(text(query))
                    connection.commit()

                    query = "SELECT codice_farmaco, nome, quantità FROM FarmaciMagazzino WHERE quantità <= 2 "
                    new_elenco: DataFrame = pd.read_sql(query, connection)

                    if not new_elenco.empty:
                        print("ELENCO AGGIORNATO")
                        for farmaco in new_elenco.to_dict(orient="records"):
                            print(farmaco)
                    else:
                        return None

                    print("Digitare 1 se si desidera continuare ad aggiornare le quantità")
                    print("Digitare exit per terminare le operazioni")
                    scelta_op = input()

                    if scelta_op == 'exit' :
                        return None

                else:
                    print("Il codice inserito non è presente nella lista fornita , riprovare ")
                    scelta_op = "1"

            if scelta_op == "exit":
                return None

            else:
                print("Operazione non valida")
                controllo_scelta = False

    @staticmethod
    def aggiunta_farmaci() -> None:

        """Consente al faramcista di aggiungere nuove tipologie di farmaci in magazzino """

        print("Per aggiungere una nuova tipologia di medicinale in magazzino, seguire le istruzioni di seguito riportate ")

        query:str = "SELECT MAX(CAST(codice_farmaco AS INT)) FROM SchedaTecnica"
        cod: Optional[DataFrame,str] = pd.read_sql(query, connection)
        cod = str(cod.iloc[0, 0])

        if cod == "None":#caso di databse vuoto
            cod = "1"
        else :
            cod = str(int(cod) + 1)

        new_farmaco = Farmaco(cod)
        new_farmaco.aggiungi_farmaco_a_db()

class ProfiloMedico(ProfilolavoratoreSanitario) :

    @staticmethod
    def crea_ricetta(matricola_medico :str) -> bool:

        """Permette al medico di prescrivere una ricetta medica

        Ritorna True quando l'operazione si conclude correttamente
        Ritorna False altrimenti
        """

        print("Digitare il codice del farmaco che si vuole prescrivere, selezionando dal segunete elenco ")

        query:str = "SELECT codice_farmaco , nome FROM FarmaciMagazzino WHERE serve_ricetta = 'si' "
        elenco: DataFrame= pd.read_sql(query, connection)

        if not elenco.empty:

            ck_cod: bool = False# abbreviazione per check codice

            for farmaco in elenco.to_dict(orient="records"):
                print(farmaco)

            while not ck_cod:

                cod_farmaco : str = input()
                query = f"SELECT nome FROM FarmaciMagazzino WHERE codice_farmaco='{cod_farmaco}' AND serve_ricetta = 'si'"
                farma: DataFrame = pd.read_sql(query, connection)

                if not farma.empty:
                    cod_fisc:str = controlla_lunghezza("Inserire il codice fiscale del paziente a cui si sta prescrivendo il farmaco : ", 16)

                    new_ricetta = Ricetta(cod_fisc, cod_farmaco, matricola_medico)
                    new_ricetta.aggiungi_ricetta_a_db()

                    print(f"Fornire il seguente codice al paziente , CODICE RICETTA : {new_ricetta.codice_ricetta}")
                    return True

                else:
                    print("Il codice inserito non appartiente a nessun farmaco nell'elenco , riprovare: ")
                    ck_cod=False

        else:
            print("Non ci sono farmaci con ricetta da poter prescrivere in magazzino")
            return False

class LavoratoreSanitario (Persona) :#classe base

    t_p: TesserinoProfessionale  # t_p abbreviazione tesserino professionale

    def __init__(self, tipo_p :str )->None:
        super().__init__()
        self.t_p = TesserinoProfessionale(tipo_p)

    def iscriversi(self) -> bool:

        query:str = f"SELECT * FROM Sanitari WHERE matricola = '{self.t_p.n_matricola}'"
        lav_sani: DataFrame = pd.read_sql(query, connection)

        #sezione di codice per verificare che il codice inserito non appartenga a un'altra tessera sanitaria
        if not lav_sani.empty: # è un dataframe
            ck_scelta: bool = False
            print("La matricola inserita appartiene a un utente già registrato")

            while not ck_scelta:
                print("Digitare 1 se si vuole accedere al servizio")
                print("Digitare 2 se si vuole ritentare il processo di iscrizione")
                print("Digitare exit se si vuole terminare l'operazione")
                scelta = check_se_vuoto("")

                if scelta == "1":
                    return True
                elif scelta == "2":
                    self.t_p.n_matricola = input("Inserire il numero di matricola corretto : ")
                    return self.iscriversi()
                elif scelta== "exit":
                    return False
                else:
                    print("operazione non valida,riprovare ")
                    ck_scelta= False

        else:
            self.aggiungi_persona_a_db()
            # sezione per associazione profilo utente
            self.crea_profilo()
            return True

    def crea_profilo(self) ->None:

        print("CREAZIONE PROFILO UTENTE")
        nome:str = check_se_vuoto(" Inserire un nome utente : ")
        password:str = check_se_vuoto(" Inserire una password : ")

        profilo = ProfilolavoratoreSanitario(nome, password, self.t_p.n_matricola, self.t_p.ordine_di_appartenenza)

        ck_profilo:bool = profilo.controllo_nome_utente()

        while not ck_profilo:
            nuovo_nome:str = check_se_vuoto("Inserisci un altro nome utente: ")
            profilo.nome_utente = nuovo_nome
            ck_profilo = profilo.controllo_nome_utente()

        profilo.aggiunta_profilo_utente_a_db()

        print("registrazione effettuata con successo.")
        print(f"        Benvenuto {profilo.nome_utente} !")

    def aggiungi_persona_a_db(self)-> None:

        self.t_p.aggiungi_tessera_a_db()

        new_lav_sani= pd.DataFrame(
            columns=[
                'nome',
                'cognome',
                'professione',
                'matricola'],
            data=[[
                self.nome,
                self.cognome,
                self.t_p.ordine_di_appartenenza,
                self.t_p.n_matricola
            ]]
        )
        new_lav_sani.to_sql('Sanitari', connection, if_exists='append', index=False)
        connection.commit()

class Cliente(Persona):
    t_s: TesseraSanitaria #t_s abbreviazione tessera sanitaria

    def __init__(self)->None:
        super().__init__()
        self.t_s = TesseraSanitaria()

    def iscriversi(self) -> bool:

        ck_data: bool

        self.t_s.data_nascita = check_nascita(self.t_s.data_nascita)
        ck_data= check_scadenza(self.t_s.data_scadenza)


        if ck_data and self.t_s.data_nascita != date.today()  :

            #sezione di codice per verificare che il codice inserito non appartenga a un'altra tessera sanitaria

            query:str = f"SELECT * FROM Clienti WHERE codice_fiscale = '{self.t_s.codice_fiscale}'"
            cliente:DataFrame = pd.read_sql(query, connection)
            if not cliente.empty: # è un dataframe
                print("Il codice fiscale inserito appartiene a un utente già registrato")
                print("Digitare 1 se si vuole accedere al servizio ")
                print("Digitare 2 se si vuole ritentare il processo di iscrizione")
                print("Digitare exit se si vuole terminare l'operazione")
                scelta: str= input()

                if scelta == "1":
                    return True
                elif scelta == "2":
                    self.t_s.codice_fiscale = input("Inserire il codice fiscale corretto : ")
                    return self.iscriversi()
                else:
                    return False

            else:
                self.aggiungi_persona_a_db()
                self.crea_profilo()
                return True
        else:
            print("La tessera risulta scaduta o la data di nascita non è valida, non è possibile effettuare l'iscrizione al servizio")
            return False

    def crea_profilo(self) ->None:

        print("CREAZIONE PROFILO UTENTE")
        nome:str = check_se_vuoto(" Inserire un nome utente : ")
        password:str = check_se_vuoto(" Inserire una password : ")

        profilo = ProfiloCliente(nome, password, self.t_s.codice_fiscale, 'cliente')
        ck_profilo:bool = profilo.controllo_nome_utente()

        while not ck_profilo:
            nuovo_nome:str = check_se_vuoto("Inserisci un altro nome utente: ")
            profilo.nome_utente = nuovo_nome
            ck_profilo = profilo.controllo_nome_utente()

        profilo.aggiunta_profilo_utente_a_db()

        print("registrazione effettuata con successo.")
        print(f"        Benvenuto {profilo.nome_utente} !")

    def aggiungi_persona_a_db(self)->None:

        self.t_s.aggiungi_tessera_a_db()

        new_cliente = pd.DataFrame(
            columns=[
                'nome',
                'cognome',
                'codice_fiscale'
            ],
            data=[[
                self.nome,
                self.cognome,
                self.t_s.codice_fiscale
            ]]
        )
        new_cliente.to_sql('Clienti', connection, if_exists='append', index=False)
        connection.commit()
