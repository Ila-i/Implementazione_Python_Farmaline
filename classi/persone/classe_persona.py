from funzioni_generali.controlli_function import check_date, check_se_vuoto, controlla, check_nascita
from classi.documenti.classe_tesserino_professionale import TesserinoProfessionale
from classi.documenti.classe_tessera_sanitaria import TesseraSanitaria
from funzioni_generali.random_function import create_random_string
from classi.oggetti.classe_ricetta import Ricetta
from classi.oggetti.classe_ordine import Ordine
from abc import ABC, abstractmethod
from datetime import datetime, date
from sqlalchemy import text
from db import connection
import pandas as pd
import string


class Persona (ABC) :
    nome: str
    cognome: str

    def __init__(self):
        self.nome = check_se_vuoto("Inserire il proprio nome : ")
        self.cognome = check_se_vuoto("Inserire il proprio cognome : ")

    @abstractmethod
    def iscriversi(self) -> bool:
        ...

    @abstractmethod
    def crea_profilo(self) ->bool:
        ...

    @classmethod
    def registrazione_utente(cls) -> bool:
        print("Creazione profilo utente, seguire le istruzioni mostrate di seguito :")

        verifica: bool = False
        pearson: Persona

        while not verifica:

            print("Se si desidera iscriversi come cliente digitare 1")
            print("Se si desidera iscriversi come farmacista digitare 2 ")
            print("Se si desidera iscriversi come medico digitare 3 ")
            controllo = input()

            if controllo == '1':
                pearson = Cliente()
                break

            elif controllo == '2':
                pearson = LavoratoreSanitario("farmacista")
                break

            elif controllo == '3':
                pearson = LavoratoreSanitario("medico")
                break

            else:
                print("opzione non valida riprovare")

        return pearson.iscriversi()

class ProfiloUtente(ABC):

    nome_utente: str
    password: str
    tipo_profilo: str
    id_utente :str

    def __init__(self, nome : str, password :str, id_u : str , tipo_p : str):
        self.nome_utente = nome
        self.password = password
        self.id_utente = id_u
        self.tipo_profilo = tipo_p

    @abstractmethod
    def associazione_profilo_utente(self) -> None:
        ...

    def controllo_nome_utente(self) -> bool:
        query = f"SELECT * FROM ProfiloUtente WHERE nome_utente = '{self.nome_utente}'"
        profilo_esistente = pd.read_sql(query, connection)
        if not profilo_esistente.empty:  # pd.read_sql(...) restituisce sempre un DataFrame di pandas.
            print(f"Il nome utente '{self.nome_utente}' è già in uso. Scegliere un altro nome.")
            return False
        else:
            return True

    @classmethod
    def get_profilo(cls, username) -> "ProfiloUtente":#"ProfiloUtente" usato per indicare che la funzione può essere chiamta dalla classe senza che venga istanziata

        query = f"SELECT password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
        profile = pd.read_sql_query(query, connection)

        pw = str(profile.iloc[0, 0])
        tipo_prof = str(profile.iloc[0, 1])

        if tipo_prof == "cliente":
            query = f"SELECT id_cliente FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_c = pd.read_sql_query(query, connection)
            id_c = str(id_c.iloc[0, 0])

            profilo = ProfiloCliente(username, pw, id_c, tipo_prof)

        elif tipo_prof == "farmacista":
            query = f"SELECT id_sanitari FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_f = pd.read_sql_query(query, connection)
            id_f = str(id_f.iloc[0, 0])
            profilo = ProfiloFarmacista(username, pw, id_f, tipo_prof)

        elif tipo_prof == "medico":
            query = f"SELECT id_sanitari FROM ProfiloUtente WHERE nome_utente = '{username}'"
            id_m = pd.read_sql_query(query, connection)
            id_m = str(id_m.iloc[0, 0])
            profilo = ProfiloMedico(username, pw, id_m, tipo_prof)
        else:
            print("Operazione fallita")

        return profilo

    @staticmethod
    def accesso_utente() -> "ProfiloUtente | str" :

        username: str
        prof: ProfiloUtente
        verifica: str
        pw: str  # pw abbrevviazione per password
        count: int = 3
        controllo: int= 3

        print("INSERIMENTO DATI PER ACCESSO")

        # sezione dedicata al controllo del nome utente, si verifica se è presente nel database
        username = check_se_vuoto("Inserire il proprio nome utente : ")
        query = f"SELECT nome_utente, password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
        profile_check = pd.read_sql(query, connection)

        while profile_check.empty:
            username = check_se_vuoto(
                f" Il nome utente inserito non appartiente a un utente registarto, riprovare (tentativi rimasti {count}): ")
            query = f"SELECT nome_utente, password, tipo_profilo FROM ProfiloUtente WHERE nome_utente = '{username}'"
            profile_check = pd.read_sql(query, connection)
            count -= 1

            if count == 0:
                print("se non si è in possesso di un profilo utente già registrato selezionare 2 per iscriversi al servizio")
                print("digitare exit se si vuole terminare le operazioni")
                verify = input()
                pass  # si riconduce al main dove fa la nuova iscrizione

        if count > 0:

            # sezione dedicata al controllo password
            pw = check_se_vuoto("Inserire la propria password : ")
            pw_check = str(profile_check.iloc[0, 1])

            while pw != pw_check:
                controllo -= 1
                if controllo > 0:
                    pw = check_se_vuoto(f" La password inserita  per questo username è incorretta, riprovare (tentetivi rimasti {controllo}): ")

                elif controllo == 0:
                    print(f"La password inserita  per questo username è incorretta, tentativi rimasti {controllo}")
                    print(f"Operazione fallita")
                    return "exit"

            if pw_check == pw:

                prof = ProfiloUtente.get_profilo(username)

                #sezione che nel caso di profilo cliente controlla che la tessera sanitaria sia in regola
                if isinstance(prof, ProfiloCliente):

                    query = f"SELECT data_scadenza FROM TesseraSanitaria WHERE codice_Fiscale= '{prof.id_utente}'"
                    data = pd.read_sql_query(query, connection)
                    data_ck = data.iloc[0, 0]
                    data_ck = datetime.strptime(data_ck, "%Y-%m-%d").date()
                    data_ck = check_date(data_ck)
                    if not data_ck:
                        print(
                            "La tessera sanitaria risulta scaduta. Vuoi aggiornare la data di scadenza ? Digitare si o no")
                        verifica = input()
                        if verifica == "si":
                            ck = False
                            while not ck:
                                data_input = controlla("NUOVA DATA DI SCADENZA (gg/mm/aaaa) : ", 10)
                                try:
                                    new_date = datetime.strptime(data_input, "%d/%m/%Y").date()
                                    ck = True
                                except ValueError:
                                    print("Data non valida!")
                                    ck = False

                            query = f"UPDATE TesseraSanitaria SET data_scadenza= '{new_date}' WHERE codice_Fiscale= '{prof.id_utente}'"
                            connection.executed(text(query))
                            connection.commit()
                        elif verifica == "no":
                            print("Il profilo verrà eliminato")
                            query = f"DELETE FROM TesseraSanitaria WHERE codice_Fiscale='{prof.id_utente}'"
                            connection.execute(text(query))
                            connection.commit()
                            return "exit"
                        else:
                            print("operazione non valida")
                            return "exit"
        return prof


class ProfilolavoratoreSanitario(ProfiloUtente) :

    def associazione_profilo_utente(self) -> None:

        new_profile = pd.DataFrame(  # prf fa riferimento al profilo utente da associare alla relativa tebella
            columns=['nome_utente', 'password', 'tipo_profilo', 'id_sanitari'],
            data=[
                [self.nome_utente, self.password, self.tipo_profilo, self.id_utente]
            ]
        )
        new_profile.to_sql('ProfiloUtente', connection, if_exists='append', index=False)
        connection.commit()

        print("Profilo utente aggiunto con successo.")
        return None

class ProfiloCliente(ProfiloUtente) :

    ordine : Ordine
    ricetta: Ricetta

    def __init__(self, nome: str, password: str, id_u: str, tipo_p: str):
        super().__init__(nome,password,id_u,tipo_p)
        self.ordine=Ordine()
        self.ricetta= Ricetta(self.id_utente)

    def associazione_profilo_utente(self) -> None:

        new_profile = pd.DataFrame(  # prf fa riferimento al profilo utente da associare alla relativa tebella
            columns=['nome_utente', 'password', 'tipo_profilo', 'id_cliente'],
            data=[
                [self.nome_utente, self.password, self.tipo_profilo, self.id_utente]
            ]
        )
        new_profile.to_sql('ProfiloUtente', connection, if_exists='append', index=False)
        connection.commit()

        print("Profilo utente aggiunto con successo.")
        return None

    def search_bar(self) -> None:
        #richiama self.aggiunta_carrello
        medicinale: str
        filtri: str
        aggiungi_carrello: str

        print("BARRA DI RICERCA")
        filtri = input("Vuoi applicare dei filtri alla tua ricerca? (digitare si o no) : ")

        if filtri == "si":
            print("Indica almeno uno dei seguenti filtri, quando non si vuole mettere un filtro premere semplicemente invio")
            indicazioni_terapeutiche = input("Inserire le indicazioni terapeutiche : ")
            composizione = input("Inserire la composizione: ")
            posologia = input("Inserire la posologia : ")

            filters = []  # lista
            if indicazioni_terapeutiche:
                filters.append(f"LOWER(s.indicazioni_terapeutiche) LIKE LOWER ('%{indicazioni_terapeutiche}%')")

            if composizione:
                filters.append(f"LOWER (s.composizione) LIKE LOWER ('%{composizione}%')")

            if posologia:
                filters.append(f"LOWER (s.posologia) LIKE LOWER ('%{posologia}%')")

            query = """
                    SELECT 

                        f.codice AS codice_farmaco,      -- alias univoco
                        f.nome,
                        f.ricetta,
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
                      ON f.codice = s.codice 
                    """
            if filters:
                query += " WHERE " + " AND ".join(filters)
                results = pd.read_sql(query, connection)

            else:
                print("Nessun filtro inserito. Ricerca annullata.")
                results = pd.DataFrame()  # equivalente a lista vuota

        elif filtri == "no":
            medicinale = input("Digitare il nome del farmaco che si sta cercando(premendo invio si visualizza tutto l'elenco): ")

            query = f"""
                    SELECT
                        f.codice AS codice_farmaco,      -- alias univoco
                        f.nome,
                        f.ricetta,
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
                      ON f.codice = s.codice
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

            self.ordine.aggiunta_carrello(results)

        if results.empty:
            print("Nessun farmaco trovato.")
            return  # torna al menu precedente

    def scelta_indirizzi(self) -> None:

        indirizzo_domicilio: str
        scelta_ind: str = "exit"
        controllo_ricetta: int

        controllo_ricetta = self.ricetta.verifica_dati_ricetta(self.ordine.carrello, self.ordine.quanto_compro)

        if len(self.ordine.carrello) > 0 :
            if controllo_ricetta == 0:
                print("per ricevere l'ordine a domicilio digitare 1")
                print("per ritirare l'ordine nella farmacia fisica 2")
                scelta_ind = input()
            elif controllo_ricetta > 0:
                scelta_ind= "2"

            if scelta_ind == "1":
                indirizzo_domicilio = input("Inserire l'indirizzo di domicilio a cui si vuole ricevere l'ordine : ")
                print(f"Operazione andata a buon fine, l'ordine sarà spedito presso {indirizzo_domicilio}")
                self.pagare(indirizzo_domicilio)


            elif scelta_ind== "2":
                print("L'ordine potrà essere ritirato entro 10 giorni presso la nostra sede fisica in Via Univeristà di Santa Marta, 26")
                print("Operazione andata a buon fine")

                self.pagare("Via Univeristà di Santa Marta, 26")

            else:
                print("operazione non valida ")
        else :
            print("il carrello è vuoto , l'operazione di acquisto verrà terminata")

    def pagare(self, indirizzo: str) -> None:

        ck_data: bool = False
        metodo: str
        prezzo_tot: float = 0

        self.ordine.stampa_carrello()

        for prodotto in self.ordine.carrello:
            prezzo_tot = prezzo_tot + float(prodotto["prezzo"]) * self.ordine.quanto_compro[prodotto["codice_farmaco"]]

        print(f"Prezzo totale dell'ordine : {prezzo_tot} €")

        print("se si desidera procedere all'acquisto digitare 1")
        print("se si desidera annullare l'operazione digitare exit")
        scelta = input()

        if scelta == "1":
            print("Scegliere metodo di pagamento")
            print("digitare 1 per pagare con carta di credito o debito (American Express, Euro/Mastercard, Visa, Maestro)")
            print("digitare 2 per pagare con portafoglio digitale (paypal , Google pay, Apple pay)")
            metodo = input()

            if metodo == "1":

                print("INSERIMENTO DATI CARTA")
                nome = check_se_vuoto("Inserire il nome dell'intestatario : ")
                cognome = check_se_vuoto("Inserire il cognome dell'intestatario : ")
                numero_carta = controlla("Inserire numero della carta : ", 16)

                while not ck_data :
                    data_input = controlla("Inserire  data di scadenza della carta(gg/mm/aaaa): ", 10)

                    try:
                        data_scadenza = datetime.strptime(data_input, "%d/%m/%Y").date()
                        ck_data = True
                    except ValueError:
                        print("Data non valida!")
                        ck_data = False

                cvc = controlla("Inserire il CVC : ", 3)

                print("DATI DELLA CARTA")
                print(f"NOME : {nome}")
                print(f"COGNOME : {cognome}")
                print(f"NUMERO CARTA : {numero_carta}")
                print(f"DATA SCADENZA : {data_scadenza}")
                print(f"CVC : {cvc}")

                ck_data = check_date(data_scadenza)

                if not ck_data:
                    print("operazione fallita")#carta scaduta
                else:
                    print("operazione andata a buon fine")
                    self.ordine.associa_numero_ordine(indirizzo, self.id_utente)
                    self.ordine.update_database(self.id_utente)

            elif metodo == "2":
                print("operazione andata a buon fine")
                self.ordine.associa_numero_ordine(indirizzo, self.id_utente)
                self.ordine.update_database(self.id_utente)

            else :
                print("Opzione non valida")

            return None

        elif scelta == "exit":
            return None
        else:
            print("Opzione non valida")

class ProfiloFarmacista(ProfilolavoratoreSanitario) :

    @staticmethod
    def verifica_ordine() -> None:

        cod_fisc: str
        n_ordine: str
        count: int = 3

        print("RICERCA ORDINE NEL DATABASE")

        cod_fisc = check_se_vuoto("Inserire il codice fiscale del cliente : ")
        n_ordine = check_se_vuoto("Inserire il numero dell'ordine : ")

        query = f"SELECT * FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo = 'Via Univeristà di Santa Marta, 26' "
        trovato = pd.read_sql(query, connection)

        while trovato.empty:

            print(f"Ordine non trovato, riprovare (tentativi rimasti {count}")
            cod_fisc = check_se_vuoto("Inserire il codice fiscale del cliente : ")
            n_ordine = check_se_vuoto("Inserire il numero dell'ordine : ")

            query = f"SELECT * FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo = 'Via Univeristà di Santa Marta, 26' "
            trovato = pd.read_sql(query, connection)
            count -= 1

            if count == 0:
                print("Operazione fallita")
                return None

        if count > 0:
            print("Ordine trovato")
            print(str(trovato.iloc[0]))
            query = f"DELETE FROM Ordine WHERE numero_ordine = '{n_ordine}' AND codice_fiscale = '{cod_fisc}' AND indirizzo = 'Via Univeristà di Santa Marta, 26' "
            connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
            connection.commit()
            print("Ordine rimosso dal database")
        else:
            print("Errore")

    @staticmethod
    def aggiorna_magazzino() -> None:

        scelta_op: str
        controllo_scelta: bool = False
        continua: str = "1"
        new_quantity: int

        query = "SELECT codice, nome, quantità FROM FarmaciMagazzino WHERE quantità <= 2 "
        riordinare = pd.read_sql(query, connection)

        if not riordinare.empty:
            print("ATTENZIONE!! I seguenti farmaci stanno per terminare o sono già terminati ")
            for farmaco in riordinare.to_dict(orient="records"):
                print(farmaco)
        else:
            return None

        while not controllo_scelta:
            print("Se si vuole aggiornare le quantità dei farmaci sopra elencati digitare 1")
            print("Per procedere con altre operazioni digitare 2")
            scelta_op = input()

            if scelta_op == "1":

                controllo_scelta = True

                while continua == "1":
                    new_quantity = 0
                    cod = input("Inserire il codice del farmaco che si vuole aggiornare : ")

                    query = f"SELECT codice FROM FarmaciMagazzino WHERE codice = '{cod}' AND quantità <= 2 "
                    ricerca = pd.read_sql(query, connection)

                    if not ricerca.empty:
                        while new_quantity <= 0:
                            try:
                                new_quantity = int(input("Inserire la quantità aggiornata : "))
                            except ValueError:
                                print("Il valore inserito non è compatibile, riprovare ")

                            if new_quantity <= 0:
                                print("Il parametro non può assumere valore negativo o nullo")

                        query = f"UPDATE FarmaciMagazzino SET quantità = '{new_quantity}' WHERE codice = '{cod}'"
                        connection.execute(text(query))  # serve per eseguire query che non devono restituire valori
                        connection.commit()

                        query = "SELECT codice, nome, quantità FROM FarmaciMagazzino WHERE quantità <= 2 "
                        new_elenco = pd.read_sql(query, connection)

                        if not new_elenco.empty:
                            print("ELENCO AGGIORNATO")
                            for farmaco in new_elenco.to_dict(orient="records"):
                                print(farmaco)
                        else:
                            return None

                        print("Se si desidera continuare ad aggiornare le quantità digitare 1 ")
                        print("Per procedere con altre operazioni digitare 2 ")
                        continua = input()

                        if continua!= '2':
                            print("operazione non valida, riprovare")
                            continua = "1"


                    else:
                        print("Il codice inserito non è presente nella lista fornita , riprovare ")
                        continua = "1"

            elif scelta_op == "2":
                return None

            else:
                print("Operazione non valida")
                controllo_scelta = False

    @staticmethod
    def aggiunta_farmaci() -> None:

        ck: bool = False
        nome: str
        ricetta: str
        preparato_galenico: str
        quanto: int = 0
        prezzo: float = 0.0

        print("Per aggiungere una nuova tipologia di medicinale in magazzino, seguire le istruzioni di seguito riportate ")

        query = "SELECT MAX(codice) FROM FarmaciMagazzino"
        cod = pd.read_sql(query, connection)
        cod = str(cod.iloc[0, 0])

        if cod == "None":#caso di databse vuoto
            cod = "1"
        else :
            cod = str(int(cod) + 1)

        nome = check_se_vuoto("Inserire il nome del farmaco : ")
        ricetta = check_se_vuoto("Il farmaco necessita di ricetta ? (digitare si o no) : ")
        preparato_galenico = check_se_vuoto("È un preparato galenico ? (digitare si o no) : ")

        while quanto <= 0:
            try:
                quanto = int(input("Inserire la quantità di farmaco che si vuole aggiungere in magazzino : "))
            except ValueError:
                print("Il valore inserito non è compatibile, riprovare")
            if quanto <= 0:
                print("Il parametro non può assumere valore negativo o nullo")

        while not ck:
            try:
                prezzo = float(input("Inserire il prezzo del prodotto in euro ( 0.00 ): "))
                ck = True
            except ValueError:
                print("Il valore inserito non è compatibile, riprovare")

        indicazioni_terapeutiche = check_se_vuoto(" Inserire le idicazioni terapeutiche : ")
        composizione = check_se_vuoto("Inserire i componenti del farmaco : ")
        eccipienti = check_se_vuoto("Inserire gli eccipienti del farmaco : ")
        controindicazioni = check_se_vuoto("Inserire le controindicazioni : ")
        posologia = check_se_vuoto("Inserire la posologia : ")
        avvertenze = check_se_vuoto("Inserire le avvertenze : ")
        effetti_indesiderati = check_se_vuoto("Inserire gli effetti indesiderati : ")


        # sezione per aggiornare la tabella di SchedaTecnica sul database
        new_scheda = pd.DataFrame(
            [[
                cod,
                indicazioni_terapeutiche,
                composizione,
                eccipienti,
                controindicazioni,
                posologia,
                avvertenze,
                effetti_indesiderati
            ]],
            columns=[
                'codice',  # <-- niente spazio finale
                'indicazioni_terapeutiche',
                'composizione',
                'eccipienti',
                'controindicazioni',
                'posologia',
                'avvertenze',
                'effetti_indesiderati'
            ]
        )
        new_scheda.to_sql('SchedaTecnica', connection, if_exists='append', index=False)

        # sezione per aggiornare la tabella di FarmaciMagazzino sul database
        new_farmaco = pd.DataFrame(
            [[
                nome,
                ricetta,
                preparato_galenico,
                prezzo,
                quanto,
                cod
            ]],
            columns=[
                'nome',  # <-- niente spazio finale
                'ricetta',
                'preparato_galenico',
                'prezzo',
                'quantità',
                'codice'
            ]
        )
        new_farmaco.to_sql('FarmaciMagazzino', connection, if_exists='append', index=False)

        connection.commit()

class ProfiloMedico(ProfilolavoratoreSanitario) :

    @staticmethod
    def crea_ricetta() -> None: #funzione medico

        ck_cod: bool= False
        cod: str
        i: int

        print("Digitare il codice del farmaco che si vuole prescrivere, selezionando dal segunete elenco ")

        query = "SELECT codice , nome FROM FarmaciMagazzino WHERE ricetta = 'si' "
        elenco = pd.read_sql(query, connection)

        if not elenco.empty:
            for farmaco in elenco.to_dict(orient="records"):
                print(farmaco)

            while not ck_cod:

                cod_farmaco = input()
                query = f"SELECT nome FROM FarmaciMagazzino WHERE codice='{cod_farmaco}' AND ricetta = 'si'"
                farma = pd.read_sql(query, connection)

                if not farma.empty:
                    cod_fisc = controlla("Inserire il codice fiscale del paziente a cui si sta prescrivendo il farmaco : ", 16)

                    cod_ricetta = ((create_random_string(4, string.digits)
                                   + create_random_string(1, string.ascii_uppercase))
                                   + ' '
                                   + create_random_string(10, string.digits))

                    new_ricetta = pd.DataFrame(
                        [[
                            cod_ricetta,
                            cod_fisc,
                            cod_farmaco
                        ]],
                        columns=[
                            'codice_ricetta',  # <-- niente spazio finale
                            'codice_fiscale',
                            'codice_farmaco',
                        ]
                    )
                    new_ricetta.to_sql('Ricetta', connection, if_exists='append', index=False)
                    connection.commit()

                    print(f"Fornire il seguente codice al paziente , CODICE RICETTA : {cod_ricetta}")
                    ck_cod=True

                else:
                    print("Il codice inserito non appartiente a nessun farmaco nell'elenco , riprovare: ")
                    ck_cod=False

        else:
            print("Non ci sono farmaci con ricetta da poter prescrivere in magazzino")


class LavoratoreSanitario (Persona) :#classe base

    t_p: TesserinoProfessionale  # t_p abbreviazione tesserino professionale

    def __init__(self, tipo_p :str ):
        super().__init__()
        self.t_p = TesserinoProfessionale(tipo_p)

    def iscriversi(self) -> bool:

        ck_scelta: bool = False
        query = f"SELECT * FROM Sanitari WHERE matricola = '{self.t_p.n_matricola}'"
        lav_sani = pd.read_sql(query, connection)

        # si definisce la ricerca da database per controllare se la persona è già registrata
        if not lav_sani.empty:  # è un dataframe
            print("La matricola inserita appartiene a un utente già registrato")

            while not ck_scelta:
                print("Se si vuole accedere al servizio digitare 1")
                print("Se si vuole ritentare il processo di iscrizione digitare 2")
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
            self.t_p.associazione_tessera_a_db()
            new_lav_sani = pd.DataFrame(
                columns=['nome', 'cognome', 'professione', 'matricola'],
                data=[
                    [self.nome, self.cognome, self.t_p.ordine_di_appartenenza, self.t_p.n_matricola]
                ]
            )
            new_lav_sani.to_sql('Sanitari', connection, if_exists='append', index=False)
            connection.commit()

            # sezione per associazione profilo utente
            return self.crea_profilo()

    def crea_profilo(self) ->bool:

        print("CREAZIONE PROFILO UTENTE")
        nome = check_se_vuoto(" inserire un nome utente : ")  # inserire controllo per corrispondenza profilo utente
        password = check_se_vuoto(" inserire una password : ")

        profilo = ProfilolavoratoreSanitario(nome, password, self.t_p.n_matricola, self.t_p.ordine_di_appartenenza)

        ck = profilo.controllo_nome_utente()

        while not ck:  # questo nuovo
            nuovo_nome = check_se_vuoto("Inserisci un altro nome utente: ")
            profilo.nome_utente = nuovo_nome
            ck = profilo.controllo_nome_utente()

        profilo.associazione_profilo_utente()

        print("registrazione effettuata con successo.")
        print(f"        Benvenuto {profilo.nome_utente} !")
        return True

class Cliente(Persona):
    t_s: TesseraSanitaria #t_s abbreviazione tessera sanitaria

    def __init__(self):
        super().__init__()
        self.t_s = TesseraSanitaria()

    def iscriversi(self) -> bool:

        ck_data: bool

        self.t_s.data_nascita = check_nascita(self.t_s.data_nascita)# per verificare che la data di nascita non indichi una data futura
        ck_data= check_date(self.t_s.data_scadenza)# per verificare che la tessera registrata non sia scaduta


        if ck_data and self.t_s.data_nascita != date.today()  :
            #per verificare che il codice inserito non appartenga a un'altra tessera sanitaria
            query = f"SELECT * FROM Clienti WHERE codice_fiscale = '{self.t_s.codice_fiscale}'"
            cliente = pd.read_sql(query, connection)
            if not cliente.empty: # è un dataframe
                print("Il codice fiscale inserito appartiene a un utente già registrato")
                print("Se si vuole accedere al servizio digitare 1")
                print("Se si vuole ritentare il processo di iscrizione digitare 2")
                print("Digitare exit se si vuole terminare l'operazione")
                scelta = input()

                if scelta == "1":
                    return True
                elif scelta == "2":
                    self.t_s.codice_fiscale = input("Inserire il codice fiscale corretto : ")
                    return self.iscriversi()
                else:
                    return False

            else:
                self.t_s.associazione_tessera_a_db()
                new_cliente = pd.DataFrame(
                    columns=['nome','cognome','codice_fiscale'],
                    data=[
                    [self.nome, self.cognome, self.t_s.codice_fiscale ]
                    ]
                )
                new_cliente.to_sql('Clienti', connection, if_exists='append', index=False)
                connection.commit()
                #sezione per associazione profilo utente
                return self.crea_profilo()
        else:
            print("La tessera risulta scaduta o la data di nascita non è valida, non è possibile effettuare l'iscrizione al servizio")
            return False

    def crea_profilo(self) ->bool:

        print("CREAZIONE PROFILO UTENTE")
        nome = check_se_vuoto(" inserire un nome utente : ")  # inserire controllo per corrispondenza profilo utente
        password = check_se_vuoto(" inserire una password : ")
        profilo = ProfiloCliente(nome, password, self.t_s.codice_fiscale, 'cliente')
        ck = profilo.controllo_nome_utente()

        while not ck:  # questo nuovo
            nuovo_nome = check_se_vuoto("Inserisci un altro nome utente: ")
            profilo.nome_utente = nuovo_nome
            ck = profilo.controllo_nome_utente()

        profilo.associazione_profilo_utente()

        print("registrazione effettuata con successo.")
        print(f"        Benvenuto {profilo.nome_utente} !")
        return True

