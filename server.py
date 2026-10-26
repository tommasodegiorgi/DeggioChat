import socket
import threading
import json
import secrets
import hashlib
import sqlite3

# Server Configuration
HOST = '127.0.0.1'
PORT = 55555
DB_FILE = 'deggiochat.db'

# Global memory runtime structures
online_clients = {}      # { username: socket_connection }
lock = threading.Lock()

# Multi-language dictionary for server-side responses
LOCALIZATION = {
    "en": {
        "unknown_cmd": "Unknown command.",
        "welcome_back": "Welcome back to DeggioChat, {}! Auto-login successful.",
        "expired_token": "Invalid or expired session token.",
        "usage_register": "Usage: /register <email> <username> <password>",
        "username_taken": "This username is already registered.",
        "reg_complete": "Registration complete. Welcome to DeggioChat, {}!",
        "usage_login": "Usage: /login <username> <password>",
        "login_success": "Login successful. Welcome to DeggioChat, {}!",
        "invalid_creds": "Invalid credentials.",
        "auth_required": "You must authenticate first using /login or /register.",
        "self_request": "You cannot send a chat request to yourself.",
        "user_not_found": "User '{}' does not exist.",
        "already_friends": "You already have an active chat with {}.",
        "req_sent": "Chat request sent to {}.",
        "incoming_req": "📩 You received a chat request from {}. Type '/chatrequest accept {}' to accept.",
        "already_pending": "You already have a pending request sent to {}.",
        "req_accepted": "Chat request accepted. You can now chat with {}.",
        "req_accepted_notify": "✅ {} accepted your chat request! Type '/chat {}' to start talking.",
        "no_req_found": "You have no pending requests from {}.",
        "req_denied": "Chat request from {} denied.",
        "req_denied_notify": "❌ {} denied your chat request.",
        "syntax_request": "Syntax error. Use /chatrequest <accept/deny> <username>",
        "usage_request": "Usage: /chatrequest <username> OR /chatrequest <accept/deny> <username>",
        "active_chats": "Your active chats: {}",
        "no_active_chats": "None. Send requests using /chatrequest",
        "enter_chat": "Entered focus chat with {}. Type your messages directly. Type /exit to leave.",
        "not_allowed_chat": "You are not allowed to chat with {}. Send a request first.",
        "chat_removed": "Chat relationship with {} successfully removed.",
        "chat_removed_notify": "🗑️ {} removed their shared chat room with you.",
        "usage_chat": "Usage: /chat <username>, /chat list, OR /chat <username> delete",
        "user_offline": "{} is currently offline.",
        "no_permission_msg": "You do not have permission to message this user."
    },
    "it": {
        "unknown_cmd": "Comando sconosciuto.",
        "welcome_back": "Bentornato su DeggioChat, {}! Accesso automatico eseguito.",
        "expired_token": "Token di sessione non valido o scaduto.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Questo username è già registrato.",
        "reg_complete": "Registrazione completata. Benvenuto su DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Accesso eseguito. Benvenuto su DeggioChat, {}!",
        "invalid_creds": "Credenziali errate.",
        "auth_required": "Devi prima autenticarti con /login o /register.",
        "self_request": "Non puoi inviare una richiesta a te stesso.",
        "user_not_found": "L'utente '{}' non esiste.",
        "already_friends": "Hai già una chat attiva con {}.",
        "req_sent": "Richiesta di chat inviata a {}.",
        "incoming_req": "📩 Hai ricevuto una richiesta di chat da {}. Usa '/chatrequest accept {}' per accettare.",
        "already_pending": "Hai già una richiesta pendente verso {}.",
        "req_accepted": "Richiesta di chat accettata. Ora puoi chattare con {}.",
        "req_accepted_notify": "✅ {} ha accettato la tua richiesta di chat! Usa '/chat {}' per parlare.",
        "no_req_found": "Non hai nessuna richiesta pendente da parte di {}.",
        "req_denied": "Richiesta di chat da {} rifiutata.",
        "req_denied_notify": "❌ {} ha rifiutato la tua richiesta di chat.",
        "syntax_request": "Sintassi errata. Usa /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> oppure /chatrequest <accept/deny> <username>",
        "active_chats": "Le tue chat attive: {}",
        "no_active_chats": "Nessuna. Invia richieste con /chatrequest",
        "enter_chat": "Entrato nella chat con {}. Digita i messaggi direttamente. Usa /exit per uscire.",
        "not_allowed_chat": "Non sei abilitato a chattare con {}. Devi prima inviare una richiesta.",
        "chat_removed": "Relazione di chat con {} rimossa con successo.",
        "chat_removed_notify": "🗑️ {} ha rimosso la chat condivisa con te.",
        "usage_chat": "Uso: /chat <username>, /chat list, oppure /chat <username> delete",
        "user_offline": "{} è offline al momento.",
        "no_permission_msg": "Non hai i permessi per inviare messaggi a questo utente."
    },
    "es": {
        "unknown_cmd": "Comando desconocido.",
        "welcome_back": "¡Bienvenido de nuevo a DeggioChat, {}! Inicio de sesión automático exitoso.",
        "expired_token": "Token de sesión inválido o expirado.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Este nombre de usuario ya está registrado.",
        "reg_complete": "Registro completado. ¡Bienvenido a DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Inicio de sesión exitoso. ¡Bienvenido a DeggioChat, {}!",
        "invalid_creds": "Credenciales incorrectas.",
        "auth_required": "Primero debes autenticarte usando /login o /register.",
        "self_request": "No puedes enviarte una solicitud de chat a ti mismo.",
        "user_not_found": "El usuario '{}' no existe.",
        "already_friends": "Ya tienes un chat activo con {}.",
        "req_sent": "Solicitud de chat enviada a {}.",
        "incoming_req": "📩 Has recibido una solicitud de chat de {}. Escribe '/chatrequest accept {}' para aceptar.",
        "already_pending": "Ya tienes una solicitud pendiente enviada a {}.",
        "req_accepted": "Solicitud de chat aceptada. Ahora puedes chatear con {}.",
        "req_accepted_notify": "✅ ¡{} aceptó tu solicitud de chat! Escribe '/chat {}' para empezar a hablar.",
        "no_req_found": "No tienes solicitudes pendientes de {}.",
        "req_denied": "Solicitud de chat de {} rechazada.",
        "req_denied_notify": "❌ {} rechazó tu solicitud de chat.",
        "syntax_request": "Error de sintaxis. Usa /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> O /chatrequest <accept/deny> <username>",
        "active_chats": "Tus chats activos: {}",
        "no_active_chats": "Ninguno. Envía solicitudes usando /chatrequest",
        "enter_chat": "Entraste al chat enfocado con {}. Escribe tus mensajes directamente. Escribe /exit para salir.",
        "not_allowed_chat": "No tienes permitido chatear con {}. Envía una solicitud primero.",
        "chat_removed": "Relación de chat con {} eliminada con éxito.",
        "chat_removed_notify": "🗑️ {} eliminó la sala de chat compartida contigo.",
        "usage_chat": "Uso: /chat <username>, /chat list, O /chat <username> delete",
        "user_offline": "{} está actualmente desconectado.",
        "no_permission_msg": "No tienes permiso para enviar mensajes a este usuario."
    },
    "pt": {
        "unknown_cmd": "Comando desconhecido.",
        "welcome_back": "Bem-vindo de volta ao DeggioChat, {}! Login automático bem-sucedido.",
        "expired_token": "Token de sessão inválido ou expirado.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Este nome de usuário já está registrado.",
        "reg_complete": "Registro concluído. Bem-vindo ao DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Login bem-sucedido. Bem-vindo ao DeggioChat, {}!",
        "invalid_creds": "Credenciais inválidas.",
        "auth_required": "Você deve se autenticar primeiro usando /login ou /register.",
        "self_request": "Você não pode enviar uma solicitação de chat para si mesmo.",
        "user_not_found": "O usuário '{}' não existe.",
        "already_friends": "Você já tem um chat ativo com {}.",
        "req_sent": "Solicitação de chat enviada para {}.",
        "incoming_req": "📩 Você recebeu uma solicitação de chat de {}. Digite '/chatrequest accept {}' para aceitar.",
        "already_pending": "Você já tem uma solicitação pendente enviada para {}.",
        "req_accepted": "Solicitação de chat aceita. Agora você pode conversar com {}.",
        "req_accepted_notify": "✅ {} aceitou sua solicitação de chat! Digite '/chat {}' para começar a falar.",
        "no_req_found": "Você não tem solicitações pendentes de {}.",
        "req_denied": "Solicitação de chat de {} recusada.",
        "req_denied_notify": "❌ {} recusou sua solicitação de chat.",
        "syntax_request": "Erro de sintaxe. Use /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "active_chats": "Seus chats ativos: {}",
        "no_active_chats": "Nenhum. Envie solicitações usando /chatrequest",
        "enter_chat": "Entrou no chat focado com {}. Digite suas mensagens diretamente. Digite /exit para sair.",
        "not_allowed_chat": "Você não tem permissão para conversar com {}. Envie uma solicitação primeiro.",
        "chat_removed": "Relação de chat com {} removida com sucesso.",
        "chat_removed_notify": "🗑️ {} removeu a sala de chat compartilhada com você.",
"usage_chat": "Uso: /chat , /chat list, OU /chat  delete",
"user_offline": "{} está atualmente offline.",
"no_permission_msg": "Você não tem permissão para enviar mensagens a este usuário."
},
"ja": {
"unknown_cmd": "不明なコマンドです。",
"welcome_back": "DeggioChatへおかえりなさい、{}！自動ログインに成功しました。",
"expired_token": "セッショントークンが無効か、または期限切れです。",
"usage_register": "使用法: /register <メール> <ユーザー名> <パスワード>",
"username_taken": "このユーザー名は既に登録されています。",
"reg_complete": "登録が完了しました。DeggioChatへようこそ、{}！",
"usage_login": "使用法: /login <ユーザー名> <パスワード>",
"login_success": "ログインに成功しました。DeggioChatへようこそ、{}！",
"invalid_creds": "認証情報が正しくありません。",
"auth_required": "最初に /login または /register を使用して認証してください。",
"self_request": "自分自身にチャットリクエストを送信することはできません。",
"user_not_found": "ユーザー '{}' は存在しません。",
"already_friends": "既に {} との有効なチャットがあります。",
"req_sent": "{} にチャットリクエストを送信しました。",
"incoming_req": "📩 {} からチャットリクエストを受信しました。承認するには '/chatrequest accept {}' と入力してください。",
"already_pending": "すでに {} に送信された保留中のリクエストがあります。",
"req_accepted": "チャットリクエストが承認されました。{} とチャットできるようになりました。",
"req_accepted_notify": "✅ {} がチャットリクエストを承認しました！ '/chat {}' と入力して会話を始めましょう。",
"no_req_found": "{} からの保留中のリクエストはありません。",
"req_denied": "{} からのチャットリクエストを拒否しました。",
"req_denied_notify": "❌ {} はあなたのチャットリクエストを拒否しました。",
"syntax_request": "構文エラー。/chatrequest <accept/deny> <ユーザー名> を使用してください。",
"usage_request": "使用法: /chatrequest <ユーザー名> または /chatrequest <accept/deny> <ユーザー名>",
"active_chats": "アクティブなチャット: {}",
"no_active_chats": "なし。/chatrequest を使用してリクエストを送信してください。",
"enter_chat": "{} との集中チャットに入りました。メッセージを直接入力してください。終了するには /exit と入力します。",
"not_allowed_chat": "{} とのチャットは許可されていません。最初にリクエストを送信してください。",
"chat_removed": "{} とのチャット関係が正常に削除されました。",
"chat_removed_notify": "🗑️ {} があなたとの共有チャットルームを削除しました。",
"usage_chat": "使用法: /chat <ユーザー名>, /chat list, または /chat <ユーザー名> delete",
"user_offline": "{} は現在オフラインです。",
"no_permission_msg": "このユーザーにメッセージを送信する権限がありません。"
},
"fr": {
"unknown_cmd": "Commande inconnue.",
"welcome_back": "Bon retour sur DeggioChat, {} ! Connexion automatique réussie.",
"expired_token": "Jeton de session invalide ou expiré.",
"usage_register": "Usage: /register   ",
"username_taken": "Ce nom d'utilisateur est déjà enregistré.",
"reg_complete": "Inscription terminée. Bienvenue sur DeggioChat, {} !",
"usage_login": "Usage: /login  ",
"login_success": "Connexion réussie. Bienvenue sur DeggioChat, {} !",
"invalid_creds": "Identifiants invalides.",
"auth_required": "Vous devez d'abord vous authentifier avec /login ou /register.",
"self_request": "Vous ne pouvez pas vous envoyer une demande de chat à vous-même.",
"user_not_found": "L'utilisateur '{}' n'existe pas.",
"already_friends": "Vous avez déjà un chat actif avec {}.",
"req_sent": "Demande de chat envoyée à {}.",
"incoming_req": "📩 Vous avez reçu une demande de chat de {}. Tapez '/chatrequest accept {}' pour accepter.",
"already_pending": "Vous avez déjà une demande en attente envoyée à {}.",
"req_accepted": "Demande de chat acceptée. Vous pouvez maintenant chatter avec {}.",
"req_accepted_notify": "✅ {} a accepté votre demande de chat ! Tapez '/chat {}' pour commencer à parler.",
"no_req_found": "Vous n'avez aucune demande en attente de la part de {}.",
"req_denied": "Demande de chat de {} refusée.",
"req_denied_notify": "❌ {} a refusé votre demande de chat.",
"syntax_request": "Erreur de syntaxe. Utilisez /chatrequest <accept/deny> ",
"usage_request": "Usage: /chatrequest  OU /chatrequest <accept/deny> ",
"active_chats": "Vos chats actifs : {}",
"no_active_chats": "Aucun. Envoyez des demandes via /chatrequest",
"enter_chat": "Entré dans le chat ciblé avec {}. Tapez vos messages directement. Tapez /exit pour quitter.",
"not_allowed_chat": "Vous n'êtes pas autorisé à chatter avec {}. Envoyez d'abord une demande.",
"chat_removed": "Relation de chat con {} supprimée avec succès.",
"chat_removed_notify": "🗑️ {} a supprimé le salon de chat partagé avec vous.",
"usage_chat": "Usage: /chat , /chat list, OU /chat  delete",
"user_offline": "{} est actuellement hors ligne.",
"no_permission_msg": "Vous n'avez pas la permission d'envoyer un message à cet utilisateur."
},
"sl": {
"unknown_cmd": "Neznan ukaz.",
"welcome_back": "Dobrodošli nazaj na DeggioChat, {}! Samodejna prijava uspešna.",
"expired_token": "Neveljaven ali potekel žeton seje.",
"usage_register": "Uporaba: /register <e-pošta> <uporabniško_ime> ",
"username_taken": "To uporabniško ime je že registrirano.",
"reg_complete": "Registracija zaključena. Dobrodošli na DeggioChat, {}!",
"usage_login": "Uporaba: /login <uporabniško_ime> ",
"login_success": "Prijava uspešna. Dobrodošli na DeggioChat, {}!",
"invalid_creds": "Napačni podatki za prijavo.",
"auth_required": "Najprej se morate avtenticirati z ukazom /login ali /register.",
"self_request": "Sami sebi ne morete poslati prošnje za klepet.",
"user_not_found": "Uporabnik '{}' ne obstaja.",
"already_friends": "S tem uporabnikom ({}) že imate aktiven klepet.",
"req_sent": "Prošnja za klepet poslana uporabniku {}.",
"incoming_req": "📩 Prejeli ste prošnjo za klepet od {}. Vtipkajte '/chatrequest accept {}' za sprejem.",
"already_pending": "Uporabniku {} ste že poslali prošnjo, ki je v čakanju.",
"req_accepted": "Prošnja za klepet sprejeta. Sedaj lahko klepetate z uporabnikom {}.",
"req_accepted_notify": "✅ {} je sprejel vašo prošnjo za klepet! Vtipkajte '/chat {}' za začetek pogovora.",
"no_req_found": "Nimate nobenih prošenj na čakanju od uporabnika {}.",
"req_denied": "Prošnja za klepet od {} je bila zavrnjena.",
"req_denied_notify": "❌ {} je zavrnil vašo prošnjo za klepet.",
"syntax_request": "Sintaktična napaka. Uporabite /chatrequest <accept/deny> <uporabniško_ime>",
"usage_request": "Uporaba: /chatrequest <uporabniško_ime> ALI /chatrequest <accept/deny> <uporabniško_ime>",
"active_chats": "Vaši aktivni klepeti: {}",
"no_active_chats": "Nobenega. Pošljite prošnjo z ukazom /chatrequest",
"enter_chat": "Vstopili ste v osredotočen klepet z {}. Sporočila vpisujte neposredno. Vtipkajte /exit za izhod.",
"not_allowed_chat": "Nimate dovoljenja za klepet z uporabnikom {}. Najprej pošljite prošnjo.",
"chat_removed": "Klepet z uporabnikom {} je bil uspešno odstranjen.",
"chat_removed_notify": "🗑️ Uporabnik {} je odstranil skupno klepetalnico z vami.",
"usage_chat": "Uporaba: /chat <uporabniško_ime>, /chat list, ALI /chat <uporabniško_ime> delete",
"user_offline": "Uporabnik {} je trenutno nedosegljiv.",
"no_permission_msg": "Nimate dovoljenja za pošiljanje sporočil temu uporabniku."
}
}
def get_msg(lang, key, *args):
"""Safely retrieves a localized string based on the active client language."""
if lang not in LOCALIZATION:
lang = "en"
template = LOCALIZATION[lang].get(key, LOCALIZATION["en"].get(key, key))
return template.format(*args)
def init_db():
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT NOT NULL, salt TEXT NOT NULL, password_hash TEXT NOT NULL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, username TEXT NOT NULL, FOREIGN KEY(username) REFERENCES users(username))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_requests (sender TEXT, receiver TEXT, PRIMARY KEY (sender, receiver))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS approved_chats (user1 TEXT, user2 TEXT, PRIMARY KEY (user1, user2))''')
conn.commit()
conn.close()
def hash_password(password, salt=None):
if not salt:
salt = secrets.token_hex(8)
hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
return hash_obj.hexdigest(), salt
def broadcast_to_user(username, data_dict):
with lock:
client_socket = online_clients.get(username)
if client_socket:
try:
client_socket.sendall((json.dumps(data_dict) + "\n").encode('utf-8'))
return True
except Exception:
return False
return False
def handle_client(client_socket):
current_user = None
buffer = ""
db = sqlite3.connect(DB_FILE)
cursor = db.cursor()
try:
while True:
data = client_socket.recv(4096).decode('utf-8')
if not data:
break
buffer += data
while "\n" in buffer:
line, buffer = buffer.split("\n", 1)
if not line.strip():
continue
try:
payload = json.loads(line)
except json.JSONDecodeError:
continue
command = payload.get("command")
args = payload.get("args", [])
lang = payload.get("lang", "en").lower()  # Receives language context from client (Default: en)
# 1. TOKEN LOGIN
if command == "token_login":
token = args if len(args) > 0 else ""
cursor.execute("SELECT username FROM sessions WHERE token = ?", (token,))
row = cursor.fetchone()
if row:
username = row
current_user = username
with lock:
online_clients[username] = client_socket
count_online = len(online_clients)
response = {
"status": "success", "action": "login", "username": username,
"message": get_msg(lang, "welcome_back", username),
"show_motd": True, "online_count": count_online
}
else:
response = {"status": "fail", "message": get_msg(lang, "expired_token")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
continue
# 2. REGISTER
if command == "register":
if len(args) < 3:
response = {"status": "error", "message": get_msg(lang, "usage_register")}
else:
email, username, password = args, args, args
cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
if cursor.fetchone():
response = {"status": "error", "message": get_msg(lang, "username_taken")}
else:
p_hash, p_salt = hash_password(password)
cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, email, p_salt, p_hash))
token = secrets.token_hex(16)
cursor.execute("INSERT INTO sessions VALUES (?, ?)", (token, username))
db.commit()
current_user = username
with lock:
online_clients[username] = client_socket
count_online = len(online_clients)
response = {
"status": "success", "action": "auth", "token": token, "username": username,
"message": get_msg(lang, "reg_complete", username),
"show_motd": True, "online_count": count_online
}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
continue
# 3. LOGIN
if command == "login":
if len(args) < 2:
response = {"status": "error", "message": get_msg(lang, "usage_login")}
else:
username, password = args, args
cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
row = cursor.fetchone()
if row:
saved_hash, saved_salt = row, row
check_hash, _ = hash_password(password, saved_salt)
if check_hash == saved_hash:
token = secrets.token_hex(16)
cursor.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (token, username))
db.commit()
current_user = username
with lock:
online_clients[username] = client_socket
count_online = len(online_clients)
response = {
"status": "success", "action": "auth", "token": token, "username": username,
"message": get_msg(lang, "login_success", username),
"show_motd": True, "online_count": count_online
}
else:
response = {"status": "error", "message": get_msg(lang, "invalid_creds")}
else:
response = {"status": "error", "message": get_msg(lang, "invalid_creds")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
continue
# REQUIRE LOGIN FOR OTHER COMMANDS
if not current_user:
response = {"status": "error", "message": get_msg(lang, "auth_required")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
continue
# 4. CHATREQUEST
if command == "chatrequest":
if len(args) == 1:
target = args
cursor.execute("SELECT username FROM users WHERE username = ?", (target,))
target_exists = cursor.fetchone()
cursor.execute("SELECT 1 FROM approved_chats WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)", (current_user, target, target, current_user))
already_friends = cursor.fetchone()
if target == current_user:
response = {"status": "error", "message": get_msg(lang, "self_request")}
elif not target_exists:
response = {"status": "error", "message": get_msg(lang, "user_not_found", target)}
elif already_friends:
response = {"status": "error", "message": get_msg(lang, "already_friends", target)}
else:
try:
cursor.execute("INSERT INTO chat_requests VALUES (?, ?)", (current_user, target))
db.commit()
response = {"status": "info", "message": get_msg(lang, "req_sent", target)}
broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "incoming_req", current_user, current_user)})
except sqlite3.IntegrityError:
response = {"status": "error", "message": get_msg(lang, "already_pending", target)}
elif len(args) == 2:
sub_cmd, target = args.lower(), args
cursor.execute("SELECT 1 FROM chat_requests WHERE sender = ? AND receiver = ?", (target, current_user))
has_request = cursor.fetchone()
if sub_cmd == "accept":
if has_request:
cursor.execute("DELETE FROM chat_requests WHERE sender = ? AND receiver = ?", (target, current_user))
u1, u2 = sorted([current_user, target])
cursor.execute("INSERT OR IGNORE INTO approved_chats VALUES (?, ?)", (u1, u2))
db.commit()
response = {"status": "success", "message": get_msg(lang, "req_accepted", target)}
broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "req_accepted_notify", current_user, current_user)})
else:
response = {"status": "error", "message": get_msg(lang, "no_req_found", target)}
elif sub_cmd == "deny":
if has_request:
cursor.execute("DELETE FROM chat_requests WHERE sender = ? AND receiver = ?", (target, current_user))
db.commit()
response = {"status": "info", "message": get_msg(lang, "req_denied", target)}
broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "req_denied_notify", current_user)})
else:
response = {"status": "error", "message": get_msg(lang, "no_req_found", target)}
else:
response = {"status": "error", "message": get_msg(lang, "syntax_request")}
else:
response = {"status": "error", "message": get_msg(lang, "usage_request")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
# 5. CHAT
elif command == "chat":
if len(args) == 1:
target = args
if target == "list":
cursor.execute("SELECT user2 FROM approved_chats WHERE user1 = ?", (current_user,))
chats = [r for r in cursor.fetchall()]
cursor.execute("SELECT user1 FROM approved_chats WHERE user2 = ?", (current_user,))
chats.extend([r for r in cursor.fetchall()])
chats_str = ", ".join(chats) if chats else get_msg(lang, "no_active_chats")
response = {"status": "info", "message": get_msg(lang, "active_chats", chats_str)}
else:
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE user1 = ? AND user2 = ?", (u1, u2))
if cursor.fetchone():
response = {"status": "enter_chat", "target": target, "message": get_msg(lang, "enter_chat", target)}
else:
response = {"status": "error", "message": get_msg(lang, "not_allowed_chat", target)}
elif len(args) == 2 and args.lower() == "delete":
target = args
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE user1 = ? AND user2 = ?", (u1, u2))
if cursor.fetchone():
cursor.execute("DELETE FROM approved_chats WHERE user1 = ? AND user2 = ?", (u1, u2))
db.commit()
response = {"status": "success", "message": get_msg(lang, "chat_removed", target)}
broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "chat_removed_notify", current_user)})
else:
response = {"status": "error", "message": get_msg(lang, "no_req_found", target)}
else:
response = {"status": "error", "message": get_msg(lang, "usage_chat")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
# 6. DIRECT MESSAGING (msg)
elif command == "msg":
if len(args) < 2:
continue
target, msg_text = args, args
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE user1 = ? AND user2 = ?", (u1, u2))
if cursor.fetchone():
delivered = broadcast_to_user(target, {"type": "msg", "from": current_user, "message": msg_text})
if delivered:
response = {"status": "msg_sent"}
else:
response = {"status": "error", "message": get_msg(lang, "user_offline", target)}
else:
response = {"status": "error", "message": get_msg(lang, "no_permission_msg")}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
except Exception:
pass
finally:
db.close()
with lock:
if current_user and online_clients.get(current_user) == client_socket:
del online_clients[current_user]
client_socket.close()
def start_server():
init_db()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"[] DeggioChat Server (SQLite Persistent Mode) listening on {HOST}:{PORT}...")
try:
while True:
client_sock, _ = server.accept()
threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
except KeyboardInterrupt:
print("\n[] Shutting down server.")
finally:
server.close()
if name == "main":
start_server()
