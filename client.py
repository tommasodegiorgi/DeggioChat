import socket
import threading
import json
import os
import sys

TOKEN_FILE = ".session_token"
LANG_FILE = ".lang_config"
HOST = "127.0.0.1"
PORT = 55555

# Comprehensive i18n Dictionary supporting 7 languages (Default: English)
LANGUAGES = {
    "en": {
        "welcome_title": "   🎮   WELCOME TO DEGGIOCHAT (CLI STYLE)    🎮      ",
        "welcome_subtitle": "Use /register or /login to start. Commands start with '/'",
        "welcome_examples": "Examples: /chatrequest Alpha, /chat Alpha, /lang it, /exit, /quit\n",
        "err_conn": "❌ Unable to connect to the server",
        "err_server_lost": "\n❌ Connection to the server lost.",
        "err_server_closed": "\n❌ The server closed the connection.",
        "whisper": "💬 [Whisper]",
        "motd_online": "Online players",
        "exit_chat": "Left focus chat with",
        "not_in_chat": "You are not in any focused chat.",
        "usage_register": "❌ Usage: /register <email> <username> <password>",
        "usage_login": "❌ Usage: /login <username> <password>",
        "usage_request": "❌ Usage: /chatrequest <username> OR /chatrequest <accept/deny> <username>",
        "usage_chat": "❌ Usage: /chat <username>, /chat list, OR /chat <username> delete",
        "usage_lang": "❌ Usage: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Unknown command. Use /register, /login, /chatrequest, /chat, /lang, /exit or /quit.",
        "conn_ended": "\nConnection terminated.",
        "lang_changed": "🌐 Language changed to English!"
    },
    "it": {
        "welcome_title": "   🎮   BENVENUTO SU DEGGIOCHAT (CLI STYLE)  🎮      ",
        "welcome_subtitle": "Usa /register o /login per iniziare. I comandi iniziano con '/'",
        "welcome_examples": "Esempi: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ Impossibile connettersi al server",
        "err_server_lost": "\n❌ Connessione con il server interrotta.",
        "err_server_closed": "\n❌ Il server ha chiuso la connessione.",
        "whisper": "💬 [Sussurro]",
        "motd_online": "Giocatori online",
        "exit_chat": "Uscito dalla chat con",
        "not_in_chat": "Non ti trovi in nessuna chat focalizzata.",
        "usage_register": "❌ Uso: /register <email> <username> <password>",
        "usage_login": "❌ Uso: /login <username> <password>",
        "usage_request": "❌ Uso: /chatrequest <username> oppure /chatrequest <accept/deny> <username>",
        "usage_chat": "❌ Uso: /chat <username>, /chat list, o /chat <username> delete",
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Comando sconosciuto. Usa /register, /login, /chatrequest, /chat, /lang, /exit o /quit.",
        "conn_ended": "\nConnessione terminata.",
        "lang_changed": "🌐 Lingua cambiata in Italiano!"
    },
    "es": {
        "welcome_title": "   🎮   BIENVENIDO A DEGGIOCHAT (ESTILO CLI) 🎮      ",
        "welcome_subtitle": "Usa /register o /login para comenzar. Los comandos empiezan con '/'",
        "welcome_examples": "Ejemplos: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ No se pudo conectar al servidor",
        "err_server_lost": "\n❌ Se perdió la conexión con el servidor.",
        "err_server_closed": "\n❌ El servidor cerró la conexión.",
        "whisper": "💬 [Susurro]",
        "motd_online": "Jugadores en línea",
        "exit_chat": "Saliste del chat enfocado con",
        "not_in_chat": "No estás en ningún chat enfocado.",
        "usage_register": "❌ Uso: /register <email> <username> <password>",
        "usage_login": "❌ Uso: /login <username> <password>",
        "usage_request": "❌ Uso: /chatrequest <username> O /chatrequest <accept/deny> <username>",
        "usage_chat": "❌ Uso: /chat <username>, /chat list, O /chat <username> delete",
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Comando desconocido. Usa /register, /login, /chatrequest, /chat, /lang, /exit o /quit.",
        "conn_ended": "\nConexión terminada.",
        "lang_changed": "🌐 ¡Idioma cambiado a Español!"
    },
    "pt": {
        "welcome_title": "   🎮   BEM-VINDO AO DEGGIOCHAT (ESTILO CLI) 🎮      ",
        "welcome_subtitle": "Use /register ou /login para iniciar. Comandos começam com '/'",
        "welcome_examples": "Exemplos: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ Não foi possível conectar ao servidor",
        "err_server_lost": "\n❌ Conexão com o servidor perdida.",
        "err_server_closed": "\n❌ O servidor fechou a conexão.",
        "whisper": "💬 [Sussurro]",
        "motd_online": "Jogadores online",
        "exit_chat": "Saiu do chat focado com",
        "not_in_chat": "Você não está em nenhum chat focado.",
        "usage_register": "❌ Uso: /register <email> <username> <password>",
        "usage_login": "❌ Uso: /login <username> <password>",
        "usage_request": "❌ Uso: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "usage_chat": "❌ Uso: /chat <username>, /chat list, OU /chat <username> delete",
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Comando desconhecido. Use /register, /login, /chatrequest, /chat, /lang, /exit ou /quit.",
        "conn_ended": "\nConexão terminada.",
        "lang_changed": "🌐 Idioma alterado para Português!"
    },
    "ja": {
        "welcome_title": "   🎮   DEGGIOCHAT へようこそ (CLIスタイル)   🎮      ",
        "welcome_subtitle": "開始するには /register または /login を使用してください。コマンドは '/' で始まります",
        "welcome_examples": "例: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ サーバーに接続できません",
        "err_server_lost": "\n❌ サーバーとの接続が切断されました。",
        "err_server_closed": "\n❌ サーバーが接続を閉じました。",
        "whisper": "💬 [密談]",
        "motd_online": "オンラインのプレイヤー",
        "exit_chat": "集中チャットを終了しました: ",
        "not_in_chat": "どの集中チャットにも入っていません。",
        "usage_register": "❌ 使用法: /register <メール> <ユーザー名> <パスワード>",
        "usage_login": "❌ 使用法: /login <ユーザー名> <パスワード>",
        "usage_request": "❌ 使用法: /chatrequest <ユーザー名> または /chatrequest <accept/deny> <ユーザー名>",
        "usage_chat": "❌ 使用法: /chat <ユーザー名>, /chat list, または /chat <ユーザー名> delete",
        "usage_lang": "❌ 使用法: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ 不明なコマンドです。/register, /login, /chatrequest, /chat, /lang, /exit, /quit を使用してください。",
        "conn_ended": "\n接続が終了しました。",
        "lang_changed": "🌐 言語が日本語に変更されました！"
    },
    "fr": {
        "welcome_title": "   🎮   BIENVENUE SUR DEGGIOCHAT (STYLE CLI) 🎮      ",
        "welcome_subtitle": "Utilisez /register ou /login pour commencer. Les commandes commencent par '/'",
        "welcome_examples": "Exemples: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ Impossible de se connecter au serveur",
        "err_server_lost": "\n❌ Connexion au serveur perdue.",
        "err_server_closed": "\n❌ Le serveur a fermé la connexion.",
        "whisper": "💬 [Chuchotement]",
        "motd_online": "Joueurs en ligne",
        "exit_chat": "Quitté le chat ciblé avec",
        "not_in_chat": "Vous n'êtes dans aucun chat ciblé.",
        "usage_register": "❌ Usage: /register <email> <username> <password>",
        "usage_login": "❌ Usage: /login <username> <password>",
        "usage_request": "❌ Usage: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "usage_chat": "❌ Usage: /chat <username>, /chat list, OU /chat <username> delete",
        "usage_lang": "❌ Usage: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Commande inconnue. Utilisez /register, /login, /chatrequest, /chat, /lang, /exit ou /quit.",
        "conn_ended": "\nConnexion terminée.",
        "lang_changed": "🌐 Langue changée en Français !"
    },
    "sl": {
        "welcome_title": "   🎮   DOBRODOŠLI NA DEGGIOCHAT (CLI STIL)  🎮      ",
        "welcome_subtitle": "Uporabite /register ali /login za začetek. Ukazi se začnejo z '/'",
        "welcome_examples": "Primeri: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ Ni se mogoče povezati s strežnikom",
        "err_server_lost": "\n❌ Povezava s strežnikom prekinjena.",
        "err_server_closed": "\n❌ Strežnik je zaprl povezavo.",
        "whisper": "💬 [Šepet]",
        "motd_online": "Spletni igralci",
        "exit_chat": "Zapustili ste klepet z uporabnikom",
        "not_in_chat": "Niste v nobenem osredotočenem klepetu.",
        "usage_register": "❌ Uporaba: /register <e-pošta> <uporabniško_ime> <geslo>",
        "usage_login": "❌ Uporaba: /login <uporabniško_ime> <geslo>",
        "usage_request": "❌ Uporaba: /chatrequest <uporabniško_ime> ALI /chatrequest <accept/deny> <uporabniško_ime>",
        "usage_chat": "❌ Uporaba: /chat <uporabniško_ime>, /chat list, ALI /chat <uporabniško_ime> delete",
        "usage_lang": "❌ Uporaba: /lang <en/it/es/pt/ja/fr/sl>",
        "unknown_cmd": "❌ Neznan ukaz. Uporabite /register, /login, /chatrequest, /chat, /lang, /exit ali /quit.",
        "conn_ended": "\nPovezava prekinjena.",
        "lang_changed": "🌐 Jezik spremenjen v Slovenščino!"
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
        """Loads local language setting. Defaults to English ('en')."""
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, "r") as f:
                lang = f.read().strip().lower()
                if lang in LANGUAGES:
                    return lang
        return "en"

    def save_lang_preference(self, lang):
        self.lang = lang
        with open(LANG_FILE, "w") as f:
            f.write(lang)

    def t(self, key):
"""Localization translator helper."""
return LANGUAGES[self.lang].get(key, key)
def connect(self):
try:
self.socket.connect((HOST, PORT))
except Exception as e:
print(f"{self.t('err_conn')} ({e}).")
sys.exit(1)
threading.Thread(target=self.receive_messages, daemon=True).start()
self.try_auto_login()
def try_auto_login(self):
if os.path.exists(TOKEN_FILE):
with open(TOKEN_FILE, "r") as f:
token = f.read().strip()
if token:
payload = {"command": "token_login", "args": [token], "lang": self.lang}
self.send_payload(payload)
def send_payload(self, payload):
# Attach dynamic language property to every server packet
payload["lang"] = self.lang
try:
self.socket.sendall((json.dumps(payload) + "\n").encode('utf-8'))
except Exception:
print(self.t('err_server_lost'))
self.running = False
def print_motd(self, online_count):
"""Renders the graphical multi-language ASCII Minecraft-Style MOTD."""
print("\n" + "="*52)
print(r"  _____                      _        _____ _           _   ")
print(r" |  __ \                    ()      / | |         | |  ")
print(r" | |  | | ___  __ _  __ _ _  ___    | |    | |   __ | | ")
print(r" | |  | |/ _ /  |/ _ | |/ _ \   | |    | ' \ / ` | |")
print(r" | || |  __/ (| | (| | | () |  | || | | | (| | | ")
print(r" |___/ _|_, |_, ||__/    _|| ||_,|_|")
print(r"               / | / |                                  ")
print(r"              |/ |/                                   ")
print("\n" + " "*12 + f"🎮 {self.t('motd_online')}: {online_count} 🎮")
print("="*52 + "\n")
def receive_messages(self):
buffer = ""
while self.running:
try:
data = self.socket.recv(4096).decode('utf-8')
if not data:
print(self.t('err_server_closed'))
self.running = False
break
buffer += data
while "\n" in buffer:
line, buffer = buffer.split("\n", 1)
if not line.strip():
continue
response = json.loads(line)
status = response.get("status")
resp_type = response.get("type")
if resp_type == "notification":
print(f"\n{response.get('message')}")
self.print_prompt()
elif resp_type == "msg":
sender = response.get("from")
msg = response.get("message")
if self.focus_chat == sender:
print(f"\n<{sender}> {msg}")
else:
print(f"\n{self.t('whisper')} <{sender}> {msg}")
self.print_prompt()
else:
if status == "success":
action = response.get("action")
if action == "auth":
self.username = response.get("username")
token = response.get("token")
with open(TOKEN_FILE, "w") as f:
f.write(token)
elif action == "login":
self.username = response.get("username")
print(f"\n{response.get('message')}")
if response.get("show_motd"):
self.print_motd(response.get("online_count", 1))
self.print_prompt()
elif status == "enter_chat":
self.focus_chat = response.get("target")
print(f"\n{response.get('message')}")
self.print_prompt()
elif status == "error" or status == "fail" or status == "info":
print(f"\n{response.get('message')}")
self.print_prompt()
except Exception:
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
print("====================================================")
print(self.t("welcome_title"))
print("====================================================")
print(self.t("welcome_subtitle"))
print(self.t("welcome_examples"))
threading.Event().wait(0.2)
self.print_prompt()
while self.running:
try:
user_input = sys.stdin.readline().strip()
except KeyboardInterrupt:
break
if not user_input:
self.print_prompt()
continue
if self.focus_chat and not user_input.startswith("/"):
payload = {"command": "msg", "args": [self.focus_chat, user_input]}
self.send_payload(payload)
continue
parts = user_input.split(" ")
cmd = parts.lower()
if cmd == "/quit":
self.running = False
break
elif cmd == "/exit":
if self.focus_chat:
print(f"{self.t('exit_chat')} {self.focus_chat}.")
self.focus_chat = None
else:
print(self.t('not_in_chat'))
self.print_prompt()
continue
elif cmd == "/lang":
if len(parts) < 2 or parts.lower() not in LANGUAGES:
print(self.t('usage_lang'))
else:
self.save_lang_preference(parts.lower())
print(self.t('lang_changed'))
self.print_prompt()
continue
elif cmd == "/register":
if len(parts) < 4:
print(self.t('usage_register'))
self.print_prompt()
else:
self.send_payload({"command": "register", "args": [parts, parts, parts]})
elif cmd == "/login":
if len(parts) < 3:
print(self.t('usage_login'))
self.print_prompt()
else:
self.send_payload({"command": "login", "args": [parts, parts]})
elif cmd == "/chatrequest":
if len(parts) == 2:
self.send_payload({"command": "chatrequest", "args": [parts]})
elif len(parts) == 3 and parts.lower() in ["accept", "deny"]:
self.send_payload({"command": "chatrequest", "args": [parts, parts]})
else:
print(self.t('usage_request'))
self.print_prompt()
elif cmd == "/chat":
if len(parts) == 2:
self.send_payload({"command": "chat", "args": [parts]})
elif len(parts) == 3 and parts.lower() == "delete":
self.send_payload({"command": "chat", "args": [parts, parts]})
else:
print(self.t('usage_chat'))
self.print_prompt()
else:
print(self.t('unknown_cmd'))
self.print_prompt()
self.socket.close()
print(self.t('conn_ended'))
if name == "main":
client = ChatClient()
client.connect()
client.run_cli()
