# DeggioChat — CLI Minecraft-Style Application

Una chat client-server minimale basata su terminale, con sintassi dei comandi ispirata a Minecraft ed esperienza utente ottimizzata per la console.

## 🚀 Funzionalità Principali

*   **Comandi Stile Minecraft:** Autenticazione, gestione relazioni e messaggistica tramite comandi come `/register`, `/login`, `/chatrequest` e `/chat`.
*   **Sessione Persistente (Auto-Login):** Il client genera e memorizza un token di sessione univoco in un file locale (`.session_token`). Al riavvio, l'accesso avviene istantaneamente in background.
*   **Modalità Chat Focus:** Digitando `/chat <username>`, la console entra in una modalità di conversazione diretta. Non serve digitare comandi prima di ogni messaggio: l'input standard invia direttamente il testo all'utente selezionato. Digitando `/exit` si torna alla gestione globale.
*   **Gestione degli Stati Real-time:** Il server traccia gli utenti online, le richieste pendenti (`accept`/`deny`) e le relazioni approvate.
*   **Architettura Multi-Thread:** Ascolto asincrono dei messaggi in background per evitare il blocco del terminale durante l'input dell'utente.

## 🛠️ Requisiti ed Installazione

L'applicazione utilizza esclusivamente moduli nativi della Standard Library di Python 3. Non è richiesta l'installazione di pacchetti di terze parti.

1. Crea i file sul tuo computer o sul tuo repository GitHub.
2. Assicurati di non caricare le sessioni locali aggiungendo `.session_token` al tuo file `.gitignore`.

## 📖 Manuale dei Comandi

### Autenticazione
*   `/register <email> <username> <password>` - Crea un nuovo account ed effettua il login automatico.
*   `/login <username> <password>` - Accedi al tuo account esistente (genera il token locale).

### Relazioni e Richieste
*   `/chatrequest <username>` - Invia una richiesta di chat a un utente.
*   `/chatrequest accept <username>` - Accetta una richiesta di chat in arrivo.
*   `/chatrequest deny <username>` - Rifiuta una richiesta di chat in arrivo.

### Messaggistica e Navigazione
*   `/chat list` - Mostra la lista di tutti gli utenti con cui hai una chat abilitata.
*   `/chat <username>` - Entra in modalità conversazione diretta con l'utente.
*   `/chat <username> delete` - Revoca i permessi di chat con l'utente e chiude la conversazione.
*   `/exit` - Se sei all'interno di una chat focalizzata, esce e torna alla CLI globale.
*   `/quit` - Disconnette il client e chiude l'applicazione.
