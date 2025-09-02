from datetime import datetime
from datetime import date

def controlla_lunghezza(messaggio: str, lunghezza: int) -> str :

   """Controlla che il valore in inmput abbia la stessa lunghezza indicata dal parametro lunghezza

   messaggio contiene il messaggio che si vuole stampare a schermo per dare indicazioni all'utente su cosa inserire
   lunghezza indica quanto deve essere lungo il parametro da inserire in input come indicato dal messeggio

   Ritrona il valore del parametro corretto """

   parametro = input(messaggio)

   while len(parametro) != lunghezza :
        parametro = input(f" il parametro non è valido, riprovare : ")
   return parametro

def check_nascita(data:datetime.date)-> datetime.date:

    """Controlla dche la data di nascita sia già passata

    Ritorna la data corretta , o la data del giorno corrente se si terminano i tentativi per inserire quella corretta """

    ck: bool
    today = date.today() #funzione di Python che restituisce la data odierna

    if data > today :
        for i in reversed (range (3)):
            try:
                data = input("Inserire la data di nascita corretta : ")
                data = datetime.strptime(data, "%d/%m/%Y").date()

                if data > today:
                    print(f"data di nascita non valida, riprovare (rimangono {i} tentativi)")
                else:
                    return data
            except ValueError:
                print("formato della data non valida , riprovare")
    else :
        return  data

    return today

def check_scadenza(data: datetime.date) -> bool:

    """Controlla che le date di scadenza non siano già passate

    Ritorns True quando può continuare
    Ritrona False quando deve cessare le operazioni
    """
    today = date.today()  # funzione di Python che restituisce la data odierna

    if data < today:
        print(" data di scadenza passata ")
        return False
    elif data == today:
        print("La scadenza è oggi, sei sicuro di voler proseguire? Digita si o no")
        verifica = input()
        if verifica == "si":
            return True
        elif verifica == "no":
            return False
    else:
        return True

def check_se_vuoto(messaggio: str) -> str :

   """Controlla che il parametro inserito non sia vuoto

   Ritorna il valore del parametro corretto
   """

   parametro = input(messaggio)

   while len(parametro) == 0 :
        parametro = input(f" il parametro non può essere vuoto, riprovare : ")
   return parametro

def controlla_si_no(messaggio:str)-> str :

    """Verifica che la risposta al messaggio sia un si o un no

    Restituisce la risposta corretta"""

    risposta: str = input(messaggio)

    while risposta != "si" and risposta != "no":
        risposta = input("La risposta fornita non è valida, riprovare")

    return risposta