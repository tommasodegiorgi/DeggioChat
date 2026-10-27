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
        "usage_lang": "❌ Usage: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ Uso: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ 使用法: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ Usage: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
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
        "usage_lang": "❌ Uporaba: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
        "unknown_cmd": "❌ Neznan ukaz. Uporabite /register, /login, /chatrequest, /chat, /lang, /exit ali /quit.",
        "conn_ended": "\nPovezava prekinjena.",
        "lang_changed": "🌐 Jezik spremenjen v Slovenščino!"
    },
    "de": {
        "welcome_title": "   🎮   WILLKOMMEN BEI DEGGIOCHAT (CLI-STIL)  🎮      ",
        "welcome_subtitle": "Nutze /register oder /login zum Starten. Befehle beginnen mit '/'",
        "welcome_examples": "Beispiele: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
        "err_conn": "❌ Verbindung zum Server fehlgeschlagen",
        "err_server_lost": "\n❌ Verbindung zum Server verloren.",
        "err_server_closed": "\n❌ Der Server hat die Verbindung geschlossen.",
        "whisper": "💬 [Flüstern]",
        "motd_online": "Online-Spieler",
        "exit_chat": "Fokus-Chat verlassen mit",
"not_in_chat": "Du befindest dich in keinem Fokus-Chat.",
"usage_register": "❌ Verwendung: /register   ",
"usage_login": "❌ Verwendung: /login  ",
"usage_request": "❌ Verwendung: /chatrequest  ODER /chatrequest <accept/deny> ",
"usage_chat": "❌ Verwendung: /chat , /chat list, ODER /chat  delete",
"usage_lang": "❌ Verwendung: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "❌ Unbekannter Befehl. Nutze /register, /login, /chatrequest, /chat, /lang, /exit oder /quit.",
"conn_ended": "\nVerbindung beendet.",
"lang_changed": "🌐 Sprache auf Deutsch geändert!"
},
"hr": {
"welcome_title": "   🎮   DOBRODOŠLI NA DEGGIOCHAT (CLI STIL)  🎮      ",
"welcome_subtitle": "Koristite /register ili /login za početak. Naredbe počinju s '/'",
"welcome_examples": "Primjeri: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "❌ Nije se moguće povezati na poslužitelj",
"err_server_lost": "\n❌ Veza s poslužiteljem je prekinuta.",
"err_server_closed": "\n❌ Poslužitelj je zatvorio vezu.",
"whisper": "💬 [Šapat]",
"motd_online": "Mrežni igrači",
"exit_chat": "Napustili ste fokusirani chat s",
"not_in_chat": "Niste ni u jednom fokusiranom chatu.",
"usage_register": "❌ Upotreba: /register  <korisničko_ime> ",
"usage_login": "❌ Upotreba: /login <korisničko_ime> ",
"usage_request": "❌ Upotreba: /chatrequest <korisničko_ime> ILI /chatrequest <accept/deny> <korisničko_ime>",
"usage_chat": "❌ Upotreba: /chat <korisničko_ime>, /chat list, ILI /chat <korisničko_ime> delete",
"usage_lang": "❌ Upotreba: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "❌ Nepoznata naredba. Koristite /register, /login, /chatrequest, /chat, /lang, /exit ili /quit.",
"conn_ended": "\nVeza prekinuta.",
"lang_changed": "🌐 Jezik promijenjen na Hrvatski!"
},
"sv": {
"welcome_title": "   🎮   VÄLKOMMEN TILL DEGGIOCHAT (CLI-STIL)  🎮      ",
"welcome_subtitle": "Använd /register eller /login för att starta. Kommandot börjar med '/'",
"welcome_examples": "Exempel: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "❌ Kunde inte ansluta till servern",
"err_server_lost": "\n❌ Anslutningen till servern bröts.",
"err_server_closed": "\n❌ Servern stängde anslutningen.",
"whisper": "💬 [Viskning]",
"motd_online": "Online-spelare",
"exit_chat": "Lämnade fokus-chatten med",
"not_in_chat": "Du är inte i någon fokus-chatt.",
"usage_register": "❌ Användning: /register  <användarnamn> <lösenord>",
"usage_login": "❌ Användning: /login <användarnamn> <lösenord>",
"usage_request": "❌ Användning: /chatrequest <användarnamn> ELLER /chatrequest <accept/deny> <användarnamn>",
"usage_chat": "❌ Användning: /chat <användarnamn>, /chat list, ELLER /chat <användarnamn> delete",
"usage_lang": "❌ Användning: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "❌ Okänt kommando. Använd /register, /login, /chatrequest, /chat, /lang, /exit eller /quit.",
"conn_ended": "\nAnslutningen avslutad.",
"lang_changed": "🌐 Språk ändrat till Svenska!"
},
"zh": {
"welcome_title": "   🎮   欢迎来到 DEGGIOCHAT (CLI 样式)      🎮      ",
"welcome_subtitle": "使用 /register 或 /login 开始。命令以 '/' 开头",
"welcome_examples": "示例: /chatrequest Alpha, /chat Alpha, /lang en, /exit, /quit\n",
"err_conn": "❌ 无法连接到服务器",
"err_server_lost": "\n❌ 与服务器的连接已断开。",
"err_server_closed": "\n❌ 服务器已关闭连接。",
"whisper": "💬 [私聊]",
"motd_online": "在线玩家",
"exit_chat": "已退出与该用户的专注聊天: ",
"not_in_chat": "您当前不在任何专注聊天中。",
"usage_register": "❌ 用法: /register <电子邮件> <用户名> <密码>",
"usage_login": "❌ 用法: /login <用户名> <密码>",
"usage_request": "❌ 用法: /chatrequest <用户名> 或 /chatrequest <accept/deny> <用户名>",
"usage_chat": "❌ 用法: /chat <用户名>, /chat list, 或 /chat <用户名> delete",
"usage_lang": "❌ 用法: /lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>",
"unknown_cmd": "❌ 未知命令。使用 /register、/login、/chatrequest、/chat、/lang、/exit 或 /quit。",
"conn_ended": "\n连接已结束。",
"lang_changed": "🌐 语言已更改为中文！"
}
}
class ChatClient:
def init(self):
self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.username = None
self.focus_chat = None
self.running = True
self.lang = self.load_lang_preference()
def load_lang_preference(self):
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
payload["lang"] = self.lang
try:
self.socket.sendall((json.dumps(payload) + "\n").encode('utf-8'))
except Exception:
print(self.t('err_server_lost'))
self.running = False
def print_motd(self, online_count):
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
cmd = parts[0].lower()
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
if len(parts) < 2 or parts[1].lower() not in LANGUAGES:
print(self.t('usage_lang'))
else:
self.save_lang_preference(parts[1].lower())
print(self.t('lang_changed'))
self.print_prompt()
continue
elif cmd == "/register":
if len(parts) < 4:
print(self.t('usage_register'))
self.print_prompt()
else:
self.send_payload({"command": "register", "args": [parts[1], parts[2], parts[3]]})
elif cmd == "/login":
if len(parts) < 3:
print(self.t('usage_login'))
self.print_prompt()
else:
self.send_payload({"command": "login", "args": [parts[1], parts[2]]})
elif cmd == "/chatrequest":
if len(parts) == 2:
self.send_payload({"command": "chatrequest", "args": [parts[1]]})
elif len(parts) == 3 and parts[1].lower() in ["accept", "deny"]:
self.send_payload({"command": "chatrequest", "args": [parts[1], parts[2]]})
else:
print(self.t('usage_request'))
self.print_prompt()
elif cmd == "/chat":
if len(parts) == 2:
self.send_payload({"command": "chat", "args": [parts[1]]})
elif len(parts) == 3 and parts[2].lower() == "delete":
self.send_payload({"command": "chat", "args": [parts[1], parts[2]]})
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
