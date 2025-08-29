from classi.documenti.classe_tessera_sanitaria import TesseraSanitaria
from classi.persone.classe_persona import ProfiloUtente, ProfiloCliente, ProfiloFarmacista, ProfiloMedico, Persona
from db import connection
from typing import Optional

ck_op: bool = False #ck abbreviazione per check
ck_f : bool = False # controllo usato nella sezione del faramcista
ck_m : bool = False # controllo usato nella sezione del medico


opzioni : str = "1"
controllo : bool
profilo : Optional[ProfiloUtente] #può assumere

operazione : str # per registare la scelta dell'utente tra accedere e registrarsi

print("HOME PAGE")
print("Digitare 1 per accedere al servizio se si è in possesso di un profilo utente.")
print("Digitare 2 per registrarsi al servizio se non si possiede un profilo utente .")
operazione= input()

# Operazioni con scelta di accesso al servizio
while operazione == "1":

    operazione = ProfiloUtente.accesso_utente() # ritorna : il nome utente quando l'operazione va a buon fine,
                                                #           2 se ci si vuole registare
                                                #           exit per terminare le operazioni

    profilo = ProfiloUtente.get_profilo(operazione) # restituisce il profilo con cui si fa l'accesso se l'operazione si è conclusa correttamente

    if operazione == "2" :
        if Persona.registrazione_utente() : # se è vero la registarzione è avvenuta correttamente , altrimenti vengono terminate le operazioni
            operazione = "1" #per poi procedere all'acesso
        else :
            operazione = "exit"

# Operazioni con scelta di registrazione al servizio
while operazione == "2":
    verifica: bool
    verifica = Persona.registrazione_utente()# se è vero la registarzione è avvenuta correttamente , altrimenti vengono terminate le operazioni

    if verifica:
        operazione = ProfiloUtente.accesso_utente() # ritorna : il nome utente quando l'operazione va a buon fine,
                                                    #           2 se ci si vuole registare
                                                    #           exit per terminare le operazioni
        profilo = ProfiloUtente.get_profilo(operazione)  # restituisce il profilo con cui si fa l'accesso se l'operazione si è conclusa correttamente
    else:
        operazione = "exit"


if isinstance( profilo , ProfiloUtente) : # dentro il servizio della farmacia

    # sezione dedicata al cliente
    if  isinstance(profilo , ProfiloCliente):

        check_tessera = TesseraSanitaria.check_se_ancora_valida(profilo.id_utente) #controlla che la tessera sanitaria sia ancora in regola
        if check_tessera is not None :
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