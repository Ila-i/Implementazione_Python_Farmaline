from classi.persone.classe_persone import ProfiloUtente, ProfiloCliente, ProfiloFarmacista, ProfiloMedico, Persona
from classi.documenti.classe_tessera_sanitaria import TesseraSanitaria
from typing import Optional

profilo : Optional[ProfiloUtente] = None #può appartenere alla classe ProfiloUtente o assumere valore None
operazione : str # per registare la scelta dell'utente tra accedere e registrarsi

print("HOME PAGE")
print("Digitare 1 per accedere al servizio se si è in possesso di un profilo utente.")
print("Digitare 2 per registrarsi al servizio se non si possiede un profilo utente .")
operazione= input()

# Operazioni con scelta di accesso al servizio
while operazione == "1":

    operazione = ProfiloUtente.accesso_utente()

    if operazione == "2" :
        if Persona.registrazione_utente() :
            operazione = "1"
        else :
            operazione = "exit"
    elif operazione == "exit" :
        break
    else :
        profilo = ProfiloUtente.get_profilo(operazione)

# Operazioni con scelta di registrazione al servizio
while operazione == "2":
    verifica: bool
    verifica = Persona.registrazione_utente()

    if verifica:
        operazione = ProfiloUtente.accesso_utente()

        if operazione == "2":
            if Persona.registrazione_utente():
                operazione = "1"
            else:
                operazione = "exit"
        elif operazione == "exit":
            break
        else:
            profilo = ProfiloUtente.get_profilo(operazione)
    else:
        operazione = "exit"


if isinstance( profilo , ProfiloUtente) :
    #sezione eseguibile solo dopo aver effettuato l'accesso al servizio

    # sezione dedicata al cliente
    if  isinstance(profilo , ProfiloCliente):

        opzioni_c: str = "1"# opzioni cliente

        check_tessera = TesseraSanitaria.check_se_ancora_valida(profilo.id_utente)

        # sezione per ricerca e acquisto farmaci
        if check_tessera :
            while opzioni_c == "1":
                profilo.search_bar()
                print("Digitare 1 se si desidera continuare a ricercare medicinali da acquistare ")
                print("Digitare 2 se si desidera terminare la ricerca e procedere all'acquisto ")
                opzioni_c = input()

            if opzioni_c == "2":
                print("PROCEDURA DI ACQUISTO")
                profilo.scelta_indirizzi()

    # sezione dedicata al farmacista
    elif isinstance(profilo , ProfiloFarmacista) :

        opzioni_f: str = "1"# opzioni farmacista
        ck_f: bool = False # abbreviazione per check_farmacista

        while not ck_f :

            ck_op: bool = False  # abbreviazione per check_opzioni

            print("Digitare 1 se si desidera aggiornare la quantità di scorte in magazzino")
            print("Digitare 2 se si desidera aggiungere nuovi farmaci al magazzino")
            print("Digitare 3 per verificare l'esistenza dell'ordine e confermare l'avvenuta consegna")
            print("Digitare exit per terminare le operazioni")
            opzioni_f = input()

            # sezione per aggiornare la quantità di farmaci in magazzino
            if opzioni_f == "1":
                profilo.aggiorna_magazzino()

            # sezione per aggiungere nuovi farmaci in magazzino
            elif opzioni_f == "2":
                print("PROCEDURA DI AGGIUNTA FARMACI")
                profilo.aggiunta_farmaci()

            #sezione per confermare l'avvenuta consegna degli ordini arrivati alla farmacia
            elif opzioni_f == "3" and not ck_op:
                print("PROCEDURA DI VERIFICA")
                profilo.verifica_ordine()

            elif opzioni_f == "exit" :
                ck_f = True
            else:
                print("Operazione inesistente")
                ck_op = False

    #sezione dedicata al medico
    elif isinstance(profilo , ProfiloMedico):

        opzioni_m: str = "1"#opzioni medico
        ck_m: bool = False #ck abbreviazione per check_medico

        while not ck_m :
            print("Digitare 1 se si desidera prescivere una ricetta medica")
            print("Digitare exit se si desidera terminare le operazioni")
            opzioni_m = input()

            # sezione dedicata alla prescrizione di ricette
            while opzioni_m == "1" :
                print("PROCEDURA DI PRESCRIZIONE RICETTA MEDICA")
                ck_m =profilo.crea_ricetta(profilo.id_utente)
                if ck_m:
                    print("Digitare 1 se si desidera prescivere un'altra ricetta medica")
                    print("Digitare exit se si desidera terminare le operazioni")
                    opzioni_m = input()
                else :
                    opzioni_m = "exit"

            if opzioni_m == "exit" :
                ck_m = True
            else :
                print("Operazione inesistente")

    else:
        print("Operazione non valida")
else :
    print("Operazione terminata")

