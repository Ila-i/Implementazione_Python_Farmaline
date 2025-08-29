# funzioni applicabile a tutte le classi
from datetime import datetime
from datetime import date

#per il controllo di lunghezza stringa
#retituisce il parametro corretto
def controlla(messaggio: str, lunghezza: int) -> str :

   parametro = input(messaggio)

   while len(parametro) != lunghezza :
        parametro = input(f" il parametro non è valido, riprovare : ")
   return parametro

#per il controllo delle date di nascita, verifica che siano già passate
#restituisce la data corretta , o la data del giorno corrente se si terminano i tentativi per inserire quella corretta
def check_nascita(data:datetime.date)-> datetime.date:

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

#per il controllo delle date di scadenza, verifica che non siano già passate
# restituisce true quando può continuare , e false quando deve cessare le operazioni
def check_scadenza(data: datetime.date) -> bool:

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

#controlla che il parametro inserito non sia vuoto
#retituisce il parametro corretto
def check_se_vuoto(messaggio: str) -> str :

   parametro = input(messaggio)

   while len(parametro) == 0 :
        parametro = input(f" il parametro non può essere vuoto, riprovare : ")
   return parametro
