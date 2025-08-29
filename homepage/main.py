from classi.persone.classe_persona import ProfiloUtente, ProfiloCliente, ProfiloFarmacista, ProfiloMedico, Persona
from db import connection

ck_op: bool = False
ck_f : bool = False
ck_m : bool = False
operazione : str
verifica : bool
opzioni : str = "1"
controllo : bool
profilo : ProfiloUtente


# modifica accesso con il controllo password e i due return exit e continua
#prova

print("HOME PAGE")
print("Se si è in possesso di un profilo utente digitare 1 per accedere al servizio.")
print("Se non si possiede un profilo utente digitare 2 per registrarsi al servizio.")
operazione= input()

# Operazioni con scelta di accesso al servizio
while operazione == "1":
    operazione= ProfiloUtente.accesso_utente()  # restituisce il profilo con cui si fa l'accesso se l'operazione si è conclusa correttamente ,
                                   # 2 se ci si vuole registare ,
                                   # exit per terminare le operazioni
    if operazione == "2" :
        if Persona.registrazione_utente() : # se è vero la registarzione è avvenuta correttamente , altrimenti vengono terminate le operazioni
            operazione = "1" #per poi procedere all'acesso
        else :
            operazione = "exit"

# Operazioni con scelta di registrazione al servizio
while operazione == "2":
    verifica = Persona.registrazione_utente()# se è vero la registarzione è avvenuta correttamente , altrimenti vengono terminate le operazioni

    if verifica:
        operazione = ProfiloUtente.accesso_utente()  # restituisce il profilo con cui si fa l'accesso se l'operazione si è conclusa correttamente ,
                                       # 2 se ci si vuole registare ,
                                       # exit per terminare le operazioni
    else:
        operazione = "exit"


if isinstance( operazione , ProfiloUtente) : # dentro il servizio della farmacia

    profilo = operazione

    # sezione dedicata al cliente
    if  isinstance(profilo , ProfiloCliente):

        while opzioni == "1":
            profilo.search_bar()
            print("Se si desidera continuare a ricercare medicinali da acquistare digitare 1")
            print("Se si desidera terminare la ricerca e procedere all'acquisto digitare 2")
            opzioni = input()

        if opzioni == "2":
            print("PROCEDURA DI ACQUISTO")
            profilo.scelta_indirizzi()

        else:
            print("operazione non disponibile")

    # sezione dedicata al farmacista
    elif isinstance(profilo , ProfiloFarmacista) :

        while not ck_f :
            print("Se si desidera aggiornare il magazzino digitare 1")
            print("Per verificare l'esistenza dell'ordine e confermare l'avvenuta consegna digitare 2")
            print("Per terminare le operazioni digitare exit.")
            opzioni = input()

            if opzioni == "1":
                profilo.aggiorna_magazzino()
                print("Se si desidera aggiungere nuovi farmaci al magazzino digitare 1")
                print("Per terminare le operazioni digitare exit.")
                opzioni = input()

                if opzioni == "2":
                    ck_op = True

            while opzioni == "1":
                print("PROCEDURA DI AGGIUNTA FARMACI")
                profilo.aggiunta_farmaci()
                print("Se si desidera continuare a aggiungere nuovi farmaci al magazzino digitare 1")
                print("Per verificare l'esistenza dell'ordine e confermare l'avvenuta consegna digitare 2")
                print("Per terminare le operazioni digitare exit.")
                opzioni = input()

            while opzioni == "2" and not ck_op:
                print("PROCEDURA DI VERIFICA")
                profilo.verifica_ordine()
                print("Se si desidera aggiungere nuovi farmaci al magazzino digitare 1")
                print("Per verificare l'esistenza di un altro ordine e confermare l'avvenuta consegna digitare 2")
                print("Per terminare le operazioni digitare exit.")
                opzioni = input()

            if opzioni == "exit" :
                ck_f = True
            else:
                print("operazione inesistente")
                ck_op = False

    #sezione dedicata al medico
    elif isinstance(profilo , ProfiloMedico):

        while not ck_m :
            print("Se si desidera prescivere una ricetta medica digitare 1")
            print("Se si desidera terminare le operazioni digitare exit")
            opzioni = input()

            while opzioni == "1" :
                print("PROCEDURA DI PRESCRIZIONE RICETTA MEDICA")
                profilo.crea_ricetta()
                print("Se si desidera prescivere un'altra ricetta medica digitare 1")
                print("Se si desidera terminare le operazioni digitare exit")
                opzioni = input()

            if opzioni == "exit" :
                ck_m = True
            else :
                print("operazione inesistente")

    else:
        print("Operazione non valida")
else :
    print("Operazione terminata")

#TODO controllo quantità dei farmaci corrisponda al numero di ricette( e aggiornare i documenti)