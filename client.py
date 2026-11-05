import socket
import threading
import json
import os
import sys

TOKEN_FILE = ".session_token"
LANG_FILE = ".lang_config"
HOST = "127.0.0.1"
PORT = 55555

# Comprehensive i18n Dictionary supporting 11 languages (Default: English)
LANGUAGES = {
    "en": {
        "welcome_title": "   ðŸŽ®   WELCOME TO DEGGIOCHAT (CLI STYLE)    ðŸŽ®      ",
        "welcome_subtitle": "Use /register or /login to start. Commands start with '/'",
        "welcome_examples": "Examples: /chatrequest Alpha, /chat Alpha, /lang it, /exit, /quit\n",
        "err_conn": "âŒ Unable to connect to the server",
        "err_server_lost": "\nâŒ Connection to the server lost.",
        "err_server_closed": "\nâŒ The server closed the connection.",
        "whisper": "ðŸ’¬ [Whisper]",
        "motd_online": "Online players",
        "exit_chat": "Left focus chat with",
        "not_in_chat": "You are not in any focused chat.",
        "usage_register": "âŒ Usage: /register <email> <username> <password>",
        "usage_login": "âŒ Usage: /login <username> <password>",
        "usage_request": "âŒ Usage: /chatrequest <username> OR /chatrequest <accept/deny> <username>",
        "usage_chat": "âŒ Usage: /chat <username>, /chat list, OR /chat <username> delete",
        "usage_lang": "âŒ Usage: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Unknown command. Use /register, /login, /chatrequest, /chat, /lang, /exit or /quit.",
        "conn_ended": "\nConnection terminated.",
        "lang_changed": "ðŸŒ Language changed to English!"
    },
    "it": {
        "welcome_title": "   ðŸŽ®   BENVENUTO SU DEGGIOCHAT (CLI STYLE)  ðŸŽ®      ",
        "welcome_subtitle": "Usa /register o /login per iniziare. I comandi iniziano con '/'",
        "welcome_examples": "Esempi: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ Impossibile connettersi al server",
        "err_server_lost": "\nâŒ Connessione con il server interrotta.",
        "err_server_closed": "\nâŒ Il server ha chiuso la connessione.",
        "whisper": "ðŸ’¬ [Sussurro]",
        "motd_online": "Giocatori online",
        "exit_chat": "Uscito dalla chat con",
        "not_in_chat": "Non ti trovi in nessuna chat focalizzata.",
        "usage_register": "âŒ Uso: /register <email> <username> <password>",
        "usage_login": "âŒ Uso: /login <username> <password>",
        "usage_request": "âŒ Uso: /chatrequest <username> oppure /chatrequest <accept/deny> <username>",
        "usage_chat": "âŒ Uso: /chat <username>, /chat list, o /chat <username> delete",
        "usage_lang": "âŒ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Comando sconosciuto. Usa /register, /login, /chatrequest, /chat, /lang, /exit o /quit.",
        "conn_ended": "\nConnessione terminata.",
        "lang_changed": "ðŸŒ Lingua cambiata in Italiano!"
    },
    "es": {
        "welcome_title": "   ðŸŽ®   BIENVENIDO A DEGGIOCHAT (ESTILO CLI) ðŸŽ®      ",
        "welcome_subtitle": "Usa /register o /login para comenzar. Los comandos empiezan con '/'",
        "welcome_examples": "Ejemplos: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ No se pudo conectar al servidor",
        "err_server_lost": "\nâŒ Se perdiÃ³ la conexiÃ³n con el servidor.",
        "err_server_closed": "\nâŒ El servidor cerrÃ³ la conexiÃ³n.",
        "whisper": "ðŸ’¬ [Susurro]",
        "motd_online": "Jugadores en lÃ­nea",
        "exit_chat": "Saliste del chat enfocado con",
        "not_in_chat": "No estÃ¡s en ningÃºn chat enfocado.",
        "usage_register": "âŒ Uso: /register <email> <username> <password>",
        "usage_login": "âŒ Uso: /login <username> <password>",
        "usage_request": "âŒ Uso: /chatrequest <username> O /chatrequest <accept/deny> <username>",
        "usage_chat": "âŒ Uso: /chat <username>, /chat list, O /chat <username> delete",
        "usage_lang": "âŒ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Comando desconocido. Usa /register, /login, /chatrequest, /chat, /lang, /exit o /quit.",
        "conn_ended": "\nConexiÃ³n terminada.",
        "lang_changed": "ðŸŒ Â¡Idioma cambiado a EspaÃ±ol!"
    },
    "pt": {
        "welcome_title": "   ðŸŽ®   BEM-VINDO AO DEGGIOCHAT (ESTILO CLI) ðŸŽ®      ",
        "welcome_subtitle": "Use /register ou /login para iniciar. Comandos comeÃ§am com '/'",
        "welcome_examples": "Exemplos: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ NÃ£o foi possÃ­vel conectar ao servidor",
        "err_server_lost": "\nâŒ ConexÃ£o com o servidor perdida.",
        "err_server_closed": "\nâŒ O servidor fechou a conexÃ£o.",
        "whisper": "ðŸ’¬ [Sussurro]",
        "motd_online": "Jogadores online",
        "exit_chat": "Saiu do chat focado com",
        "not_in_chat": "VocÃª nÃ£o estÃ¡ em nenhum chat focado.",
        "usage_register": "âŒ Uso: /register <email> <username> <password>",
        "usage_login": "âŒ Uso: /login <username> <password>",
        "usage_request": "âŒ Uso: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "usage_chat": "âŒ Uso: /chat <username>, /chat list, OU /chat <username> delete",
        "usage_lang": "âŒ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Comando desconhecido. Use /register, /login, /chatrequest, /chat, /lang, /exit ou /quit.",
        "conn_ended": "\nConexÃ£o terminada.",
        "lang_changed": "ðŸŒ Idioma alterado para PortuguÃªs!"
    },
    "ja": {
        "welcome_title": "   ðŸŽ®   DEGGIOCHAT ã¸ã‚ˆã†ã“ã (CLIã‚¹ã‚¿ã‚¤ãƒ«)   ðŸŽ®      ",
        "welcome_subtitle": "é–‹å§‹ã™ã‚‹ã«ã¯ /register ã¾ãŸã¯ /login ã‚’ä½¿ç”¨ã—ã¦ãã ã•ã„ã€‚ã‚³ãƒžãƒ³ãƒ‰ã¯ '/' ã§å§‹ã¾ã‚Šã¾ã™",
        "welcome_examples": "ä¾‹: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ ã‚µãƒ¼ãƒãƒ¼ã«æŽ¥ç¶šã§ãã¾ã›ã‚“",
        "err_server_lost": "\nâŒ ã‚µãƒ¼ãƒãƒ¼ã¨ã®æŽ¥ç¶šãŒåˆ‡æ–­ã•ã‚Œã¾ã—ãŸã€‚",
        "err_server_closed": "\nâŒ ã‚µãƒ¼ãƒãƒ¼ãŒæŽ¥ç¶šã‚’é–‰ã˜ã¾ã—ãŸã€‚",
        "whisper": "ðŸ’¬ [å¯†è«‡]",
        "motd_online": "ã‚ªãƒ³ãƒ©ã‚¤ãƒ³ã®ãƒ—ãƒ¬ã‚¤ãƒ¤ãƒ¼",
        "exit_chat": "é›†ä¸­ãƒãƒ£ãƒƒãƒˆã‚’çµ‚äº†ã—ã¾ã—ãŸ: ",
        "not_in_chat": "ã©ã®é›†ä¸­ãƒãƒ£ãƒƒãƒˆã«ã‚‚å…¥ã£ã¦ã„ã¾ã›ã‚“ã€‚",
        "usage_register": "âŒ ä½¿ç”¨æ³•: /register <ãƒ¡ãƒ¼ãƒ«> <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> <ãƒ‘ã‚¹ãƒ¯ãƒ¼ãƒ‰>",
        "usage_login": "âŒ ä½¿ç”¨æ³•: /login <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> <ãƒ‘ã‚¹ãƒ¯ãƒ¼ãƒ‰>",
        "usage_request": "âŒ ä½¿ç”¨æ³•: /chatrequest <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> ã¾ãŸã¯ /chatrequest <accept/deny> <ãƒ¦ãƒ¼ã‚¶ãƒ¼å>",
        "usage_chat": "âŒ ä½¿ç”¨æ³•: /chat <ãƒ¦ãƒ¼ã‚¶ãƒ¼å>, /chat list, ã¾ãŸã¯ /chat <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> delete",
        "usage_lang": "âŒ ä½¿ç”¨æ³•: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ ä¸æ˜Žãªã‚³ãƒžãƒ³ãƒ‰ã§ã™ã€‚/register, /login, /chatrequest, /chat, /lang, /exit, /quit ã‚’ä½¿ç”¨ã—ã¦ãã ã•ã„ã€‚",
        "conn_ended": "\næŽ¥ç¶šãŒçµ‚äº†ã—ã¾ã—ãŸã€‚",
        "lang_changed": "ðŸŒ è¨€èªžãŒæ—¥æœ¬èªžã«å¤‰æ›´ã•ã‚Œã¾ã—ãŸï¼"
    },
    "fr": {
        "welcome_title": "   ðŸŽ®   BIENVENUE SUR DEGGIOCHAT (STYLE CLI) ðŸŽ®      ",
        "welcome_subtitle": "Utilisez /register ou /login pour commencer. Les commandes commencent par '/'",
        "welcome_examples": "Exemples: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ Impossible de se connecter au serveur",
        "err_server_lost": "\nâŒ Connexion au serveur perdue.",
        "err_server_closed": "\nâŒ Le serveur a fermÃ© la connexion.",
        "whisper": "ðŸ’¬ [Chuchotement]",
        "motd_online": "Joueurs en ligne",
        "exit_chat": "QuittÃ© le chat ciblÃ© avec",
        "not_in_chat": "Vous n'Ãªtes dans aucun chat ciblÃ©.",
        "usage_register": "âŒ Usage: /register <email> <username> <password>",
        "usage_login": "âŒ Usage: /login <username> <password>",
        "usage_request": "âŒ Usage: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "usage_chat": "âŒ Usage: /chat <username>, /chat list, OU /chat <username> delete",
        "usage_lang": "âŒ Usage: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Commande inconnue. Utilisez /register, /login, /chatrequest, /chat, /lang, /exit ou /quit.",
        "conn_ended": "\nConnexion terminÃ©e.",
        "lang_changed": "ðŸŒ Langue changÃ©e en FranÃ§ais !"
    },
    "sl": {
        "welcome_title": "   ðŸŽ®   DOBRODOÅ LI NA DEGGIOCHAT (CLI STIL)  ðŸŽ®      ",
        "welcome_subtitle": "Uporabite /register ali /login za zaÄetek. Ukazi se zaÄnejo z '/'",
        "welcome_examples": "Primeri: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ Ni se mogoÄe povezati s streÅ¾nikom",
        "err_server_lost": "\nâŒ Povezava s streÅ¾nikom prekinjena.",
        "err_server_closed": "\nâŒ StreÅ¾nik je zaprl povezavo.",
        "whisper": "ðŸ’¬ [Å epet]",
        "motd_online": "Spletni igralci",
        "exit_chat": "Zapustili ste klepet z uporabnikom",
        "not_in_chat": "Niste v nobenem osredotoÄenem klepetu.",
        "usage_register": "âŒ Uporaba: /register <e-poÅ¡ta> <uporabniÅ¡ko_ime> <geslo>",
        "usage_login": "âŒ Uporaba: /login <uporabniÅ¡ko_ime> <geslo>",
        "usage_request": "âŒ Uporaba: /chatrequest <uporabniÅ¡ko_ime> ALI /chatrequest <accept/deny> <uporabniÅ¡ko_ime>",
        "usage_chat": "âŒ Uporaba: /chat <uporabniÅ¡ko_ime>, /chat list, ALI /chat <uporabniÅ¡ko_ime> delete",
        "usage_lang": "âŒ Uporaba: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "âŒ Neznan ukaz. Uporabite /register, /login, /chatrequest, /chat, /lang, /exit ali /quit.",
        "conn_ended": "\nPovezava prekinjena.",
        "lang_changed": "ðŸŒ Jezik spremenjen v SlovenÅ¡Äino!"
    },
    "de": {
        "welcome_title": "   ðŸŽ®   WILLKOMMEN BEI DEGGIOCHAT (CLI-STIL)  ðŸŽ®      ",
        "welcome_subtitle": "Nutze /register oder /login zum Starten. Befehle beginnen mit '/'",
        "welcome_examples": "Beispiele: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "âŒ Verbindung zum Server fehlgeschlagen",
        "err_server_lost": "\nâŒ Verbindung zum Server verloren.",
        "err_server_closed": "\nâŒ Der Server hat die Verbindung geschlossen.",
        "whisper": "ðŸ’¬ [FlÃ¼stern]",
        "motd_online": "Online-Spieler",
        "exit_chat": "Fokus-Chat verlassen mit",
"not_in_chat": "Du befindest dich in keinem Fokus-Chat.",
"usage_register": "âŒ Verwendung: /register   ",
"usage_login": "âŒ Verwendung: /login  ",
"usage_request": "âŒ Verwendung: /chatrequest  ODER /chatrequest <accept/deny> ",
"usage_chat": "âŒ Verwendung: /chat , /chat list, ODER /chat  delete",
"usage_lang": "âŒ Verwendung: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "âŒ Unbekannter Befehl. Nutze /register, /login, /chatrequest, /chat, /lang, /exit oder /quit.",
"conn_ended": "\nVerbindung beendet.",
"lang_changed": "ðŸŒ Sprache auf Deutsch geÃ¤ndert!"
},
"hr": {
"welcome_title": "   ðŸŽ®   DOBRODOÅ LI NA DEGGIOCHAT (CLI STIL)  ðŸŽ®      ",
"welcome_subtitle": "Koristite /register ili /login za poÄetak. Naredbe poÄinju s '/'",
"welcome_examples": "Primjeri: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "âŒ Nije se moguÄ‡e povezati na posluÅ¾itelj",
"err_server_lost": "\nâŒ Veza s posluÅ¾iteljem je prekinuta.",
"err_server_closed": "\nâŒ PosluÅ¾itelj je zatvorio vezu.",
"whisper": "ðŸ’¬ [Å apat]",
"motd_online": "MreÅ¾ni igraÄi",
"exit_chat": "Napustili ste fokusirani chat s",
"not_in_chat": "Niste ni u jednom fokusiranom chatu.",
"usage_register": "âŒ Upotreba: /register  <korisniÄko_ime> ",
"usage_login": "âŒ Upotreba: /login <korisniÄko_ime> ",
"usage_request": "âŒ Upotreba: /chatrequest <korisniÄko_ime> ILI /chatrequest <accept/deny> <korisniÄko_ime>",
"usage_chat": "âŒ Upotreba: /chat <korisniÄko_ime>, /chat list, ILI /chat <korisniÄko_ime> delete",
"usage_lang": "âŒ Upotreba: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "âŒ Nepoznata naredba. Koristite /register, /login, /chatrequest, /chat, /lang, /exit ili /quit.",
"conn_ended": "\nVeza prekinuta.",
"lang_changed": "ðŸŒ Jezik promijenjen na Hrvatski!"
},
"sv": {
"welcome_title": "   ðŸŽ®   VÃ„LKOMMEN TILL DEGGIOCHAT (CLI-STIL)  ðŸŽ®      ",
"welcome_subtitle": "AnvÃ¤nd /register eller /login fÃ¶r att starta. Kommandot bÃ¶rjar med '/'",
"welcome_examples": "Exempel: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "âŒ Kunde inte ansluta till servern",
"err_server_lost": "\nâŒ Anslutningen till servern brÃ¶ts.",
"err_server_closed": "\nâŒ Servern stÃ¤ngde anslutningen.",
"whisper": "ðŸ’¬ [Viskning]",
"motd_online": "Online-spelare",
"exit_chat": "LÃ¤mnade fokus-chatten med",
"not_in_chat": "Du Ã¤r inte i nÃ¥gon fokus-chatt.",
"usage_register": "âŒ AnvÃ¤ndning: /register  <anvÃ¤ndarnamn> <lÃ¶senord>",
"usage_login": "âŒ AnvÃ¤ndning: /login <anvÃ¤ndarnamn> <lÃ¶senord>",
"usage_request": "âŒ AnvÃ¤ndning: /chatrequest <anvÃ¤ndarnamn> ELLER /chatrequest <accept/deny> <anvÃ¤ndarnamn>",
"usage_chat": "âŒ AnvÃ¤ndning: /chat <anvÃ¤ndarnamn>, /chat list, ELLER /chat <anvÃ¤ndarnamn> delete",
"usage_lang": "âŒ AnvÃ¤ndning: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "âŒ OkÃ¤nt kommando. AnvÃ¤nd /register, /login, /chatrequest, /chat, /lang, /exit eller /quit.",
"conn_ended": "\nAnslutningen avslutad.",
"lang_changed": "ðŸŒ SprÃ¥k Ã¤ndrat till Svenska!"
},
"zh": {
"welcome_title": "   ðŸŽ®   æ¬¢è¿Žæ¥åˆ° DEGGIOCHAT (CLI æ ·å¼)      ðŸŽ®      ",
"welcome_subtitle": "ä½¿ç”¨ /register æˆ– /login å¼€å§‹ã€‚å‘½ä»¤ä»¥ '/' å¼€å¤´",
"welcome_examples": "ç¤ºä¾‹: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "âŒ æ— æ³•è¿žæŽ¥åˆ°æœåŠ¡å™¨",
"err_server_lost": "\nâŒ ä¸ŽæœåŠ¡å™¨çš„è¿žæŽ¥å·²æ–­å¼€ã€‚",
"err_server_closed": "\nâŒ æœåŠ¡å™¨å·²å…³é—­è¿žæŽ¥ã€‚",
"whisper": "ðŸ’¬ [ç§èŠ]",
"motd_online": "åœ¨çº¿çŽ©å®¶",
"exit_chat": "å·²é€€å‡ºä¸Žè¯¥ç”¨æˆ·çš„ä¸“æ³¨èŠå¤©: ",
"not_in_chat": "æ‚¨å½“å‰ä¸åœ¨ä»»ä½•ä¸“æ³¨èŠå¤©ä¸­ã€‚",
"usage_register": "âŒ ç”¨æ³•: /register <ç”µå­é‚®ä»¶> <ç”¨æˆ·å> <å¯†ç >",
"usage_login": "âŒ ç”¨æ³•: /login <ç”¨æˆ·å> <å¯†ç >",
"usage_request": "âŒ ç”¨æ³•: /chatrequest <ç”¨æˆ·å> æˆ– /chatrequest <accept/deny> <ç”¨æˆ·å>",
"usage_chat": "âŒ ç”¨æ³•: /chat <ç”¨æˆ·å>, /chat list, æˆ– /chat <ç”¨æˆ·å> delete",
"usage_lang": "âŒ ç”¨æ³•: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "âŒ æœªçŸ¥å‘½ä»¤ã€‚ä½¿ç”¨ /registerã€/loginã€/chatrequestã€/chatã€/langã€/exit æˆ– /quitã€‚",
"conn_ended": "\nè¿žæŽ¥å·²ç»“æŸã€‚",
"lang_changed": "ðŸŒ è¯­è¨€å·²æ›´æ”¹ä¸ºä¸­æ–‡ï¼"
}
}

class ChatClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.focus_chat = None
        self.running = True
        self.lang = self.load_lang_preference()

    def load_lang_preference(self):
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                lang = f.read().strip().lower()
            return lang if lang in LANGUAGES else "en"
        except OSError:
            return "en"

    def save_lang_preference(self, lang):
        self.lang = lang
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            f.write(lang)

    def t(self, key):
        return LANGUAGES[self.lang].get(key, LANGUAGES["en"].get(key, key))

    def connect(self):
        try:
            self.socket.connect((HOST, PORT))
        except OSError as exc:
            print(f"{self.t('err_conn')} ({exc}).")
            self.socket.close()
            return False
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.try_auto_login()
        return True

    def try_auto_login(self):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
        except OSError:
            return
        if token:
            self.send_payload({"command": "token_login", "args": [token]})

    def send_payload(self, payload):
        payload["lang"] = self.lang
        try:
            self.socket.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        except OSError:
            print(self.t("err_server_lost"))
            self.running = False

    def print_motd(self, online_count):
        print("\n" + "=" * 52)
        print(f"{self.t('motd_online')}: {online_count}")
        print("=" * 52 + "\n")

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode("utf-8")
                if not data:
                    if self.running:
                        print(self.t("err_server_closed"))
                    self.running = False
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        response = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    response_type = response.get("type")
                    status = response.get("status")
                    if response_type in ("notification", "msg"):
                        if response_type == "msg":
                            sender = response.get("from", "?")
                            prefix = "" if self.focus_chat == sender else self.t("whisper") + " "
                            print(f"\n{prefix}<{sender}> {response.get('message', '')}")
                        else:
                            print(f"\n{response.get('message', '')}")
                        self.print_prompt()
                        continue
                    if status == "success" and response.get("action") in ("auth", "login"):
                        self.username = response.get("username")
                        token = response.get("token")
                        if token:
                            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                                f.write(token)
                        if response.get("message"):
                            print(f"\n{response['message']}")
                        if response.get("show_motd"):
                            self.print_motd(response.get("online_count", 1))
                    elif status == "enter_chat":
                        self.focus_chat = response.get("target")
                    if response.get("message") and not (status == "success" and response.get("action") in ("auth", "login")):
                        print(f"\n{response['message']}")
                    self.print_prompt()
            except (OSError, UnicodeDecodeError):
                self.running = False
                break

    def print_prompt(self):
        if not self.username:
            prompt = "DeggioChat> "
        elif self.focus_chat:
            prompt = f"[{self.username} -> {self.focus_chat}]> "
        else:
            prompt = f"[{self.username}]> "
        print(prompt, end="", flush=True)

    def run_cli(self):
        print("=" * 52)
        print(self.t("welcome_title"))
        print("=" * 52)
        print(self.t("welcome_subtitle"))
        print(self.t("welcome_examples"))
        self.print_prompt()
        while self.running:
            try:
                raw = sys.stdin.readline()
            except KeyboardInterrupt:
                break
            if not raw:
                break
            user_input = raw.strip()
            if not user_input:
                self.print_prompt()
                continue
            if self.focus_chat and not user_input.startswith("/"):
                self.send_payload({"command": "msg", "args": [self.focus_chat, user_input]})
                continue
            parts = user_input.split()
            cmd = parts[0].lower()
            if cmd == "/quit":
                break
            if cmd == "/exit":
                if self.focus_chat:
                    print(f"{self.t('exit_chat')} {self.focus_chat}.")
                    self.focus_chat = None
                else:
                    print(self.t("not_in_chat"))
                self.print_prompt()
            elif cmd == "/lang":
                if len(parts) < 2 or parts[1].lower() not in LANGUAGES:
                    print(self.t("usage_lang"))
                else:
                    self.save_lang_preference(parts[1].lower())
                    print(self.t("lang_changed"))
                self.print_prompt()
            elif cmd == "/register":
                if len(parts) != 4:
                    print(self.t("usage_register"))
                    self.print_prompt()
                else:
                    self.send_payload({"command": "register", "args": parts[1:4]})
            elif cmd == "/login":
                if len(parts) != 3:
                    print(self.t("usage_login"))
                    self.print_prompt()
                else:
                    self.send_payload({"command": "login", "args": parts[1:3]})
            elif cmd == "/chatrequest":
                if len(parts) == 2 or (len(parts) == 3 and parts[1].lower() in ("accept", "deny")):
                    self.send_payload({"command": "chatrequest", "args": parts[1:]})
                else:
                    print(self.t("usage_request"))
                    self.print_prompt()
            elif cmd == "/chat":
                if len(parts) == 2 or (len(parts) == 3 and parts[2].lower() == "delete"):
                    self.send_payload({"command": "chat", "args": parts[1:]})
                else:
                    print(self.t("usage_chat"))
                    self.print_prompt()
            else:
                print(self.t("unknown_cmd"))
                self.print_prompt()
        self.running = False
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.socket.close()
        print(self.t("conn_ended"))


if __name__ == "__main__":
    client = ChatClient()
    if client.connect():
        client.run_cli()
