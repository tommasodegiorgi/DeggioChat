import socket
import threading
import json
import secrets
import hashlib
import sqlite3

# Configurazione Server
HOST = '127.0.0.1'
PORT = 55555
DB_FILE = 'deggiochat.db'

# Strutture dati temporanee in memoria RAM (solo per le connessioni attive del momento)
online_clients = {}      # { username: socket_connection }
lock = threading.Lock()

def init_db():
    """Inizializza il database SQLite creando le tabelle se non esistono."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabella Utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Tabella Sessioni (Token)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    # Tabella Richieste di Chat Pendenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_requests (
            mittente TEXT,
            destinatario TEXT,
            PRIMARY KEY (mittente, destinatario),
            FOREIGN KEY(mittente) REFERENCES users(username),
            FOREIGN KEY(destinatario) REFERENCES users(username)
        )
    ''')
    
    # Tabella Chat Approvate (Relazioni)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approved_chats (
            utente1 TEXT,
            utente2 TEXT,
            PRIMARY KEY (utente1, utente2),
            FOREIGN KEY(utente1) REFERENCES users(username),
            FOREIGN KEY(utente2) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Genera un hash sicuro SHA-256 usando un salt casuale."""
    if not salt:
        salt = secrets.token_hex(8)
    hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
    return hash_obj.hexdigest(), salt

def broadcast_to_user(username, data_dict):
    """Invia un pacchetto JSON a uno specifico utente se online."""
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
    
    # Apriamo una connessione SQLite dedicata a questo thread/client
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
                response = {"status": "error", "message": "Comando sconosciuto."}
                
                # 1. TOKEN LOGIN (Persistente su DB)
                if command == "token_login":
                    token = args if len(args) > 0 else ""
                    cursor.execute("SELECT username FROM sessions WHERE token = ?", (token,))
                    row = cursor.fetchone()
                    
                    if row:
                        username = row
                        current_user = username
                        with lock:
                            online_clients[username] = client_socket
                        
                        with lock:
                            count_online = len(online_clients)
                            
                        response = {
                            "status": "success", "action": "login", "username": username,
                            "message": f"Bentornato su DeggioChat, {username}! Accesso automatico eseguito.",
                            "show_motd": True, "online_count": count_online
                        }
                    else:
                        response = {"status": "fail", "message": "Token non valido o scaduto."}
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue
                
                # 2. REGISTER (Inserimento su DB)
                if command == "register":
                    if len(args) < 3:
                        response = {"status": "error", "message": "Uso: /register <email> <username> <password>"}
                    else:
                        email, username, password = args, args, args
                        
                        # Controlla se l'utente esiste già
                        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                        if cursor.fetchone():
                            response = {"status": "error", "message": "Questo username è già registrato."}
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
                                "message": f"Registrazione completata. Benvenuto su DeggioChat, {username}!",
                                "show_motd": True, "online_count": count_online
                            }
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue

                # 3. LOGIN (Verifica da DB)
                if command == "login":
                    if len(args) < 2:
                        response = {"status": "error", "message": "Uso: /login <username> <password>"}
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
                                    "message": f"Accesso eseguito. Benvenuto su DeggioChat, {username}!",
                                    "show_motd": True, "online_count": count_online
                                }
                            else:
                                response = {"status": "error", "message": "Credenziali errate."}
                        else:
                            response = {"status": "error", "message": "Credenziali errate."}
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue

                # SICUREZZA: DA QUI IN POI È RICHIESTA L'AUTENTICAZIONE
                if not current_user:
                    response = {"status": "error", "message": "Devi prima autenticarti con /login o /register."}
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue

                # 4. CHATREQUEST (Gestione su tabelle DB)
                if command == "chatrequest":
                    if len(args) == 1:
                        target = args
                        
                        cursor.execute("SELECT username FROM users WHERE username = ?", (target,))
                        target_exists = cursor.fetchone()
                        
                        cursor.execute("SELECT 1 FROM approved_chats WHERE (utente1=? AND utente2=?) OR (utente1=? AND utente2=?)", 
                                       (current_user, target, target, current_user))
                        already_friends = cursor.fetchone()
                        
                        if target == current_user:
                            response = {"status": "error", "message": "Non puoi inviare una richiesta a te stesso."}
                        elif not target_exists:
                            response = {"status": "error", "message": f"L'utente '{target}' non esiste."}
                        elif already_friends:
response = {"status": "error", "message": f"Hai già una chat attiva con {target}."}
else:
try:
cursor.execute("INSERT INTO chat_requests VALUES (?, ?)", (current_user, target))
db.commit()
response = {"status": "info", "message": f"Richiesta di chat inviata a {target}."}
broadcast_to_user(target, {"type": "notification", "message": f"📩 Hai ricevuto una richiesta di chat da {current_user}. Usa '/chatrequest accept {current_user}' per accettare."})
except sqlite3.IntegrityError:
response = {"status": "error", "message": f"Hai già una richiesta pendente verso {target}."}
elif len(args) == 2:
sub_cmd, target = args.lower(), args
cursor.execute("SELECT 1 FROM chat_requests WHERE mittente = ? AND destinatario = ?", (target, current_user))
has_request = cursor.fetchone()
if sub_cmd == "accept":
if has_request:
cursor.execute("DELETE FROM chat_requests WHERE mittente = ? AND destinatario = ?", (target, current_user))
# Per evitare duplicati incrociati inseriamo sempre l'alfabeticamente minore per primo
u1, u2 = sorted([current_user, target])
cursor.execute("INSERT OR IGNORE INTO approved_chats VALUES (?, ?)", (u1, u2))
db.commit()
response = {"status": "success", "message": f"Richiesta di chat accettata. Ora puoi chattare con {target}."}
broadcast_to_user(target, {"type": "notification", "message": f"✅ {current_user} ha accettato la tua richiesta di chat! Usa '/chat {current_user}' per parlare."})
else:
response = {"status": "error", "message": f"Non hai nessuna richiesta pendente da parte di {target}."}
elif sub_cmd == "deny":
if has_request:
cursor.execute("DELETE FROM chat_requests WHERE mittente = ? AND destinatario = ?", (target, current_user))
db.commit()
response = {"status": "info", "message": f"Richiesta di chat da {target} rifiutata."}
broadcast_to_user(target, {"type": "notification", "message": f"❌ {current_user} ha rifiutato la tua richiesta di chat."})
else:
response = {"status": "error", "message": f"Non hai nessuna richiesta pendente da parte di {target}."}
else:
response = {"status": "error", "message": "Sintassi errata. Usa /chatrequest <accept/deny> "}
else:
response = {"status": "error", "message": "Uso: /chatrequest  oppure /chatrequest <accept/deny> "}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
# 5. GESTIONE CHAT
elif command == "chat":
if len(args) == 1:
target = args
if target == "list":
# Cerca tutte le chat in cui l'utente è coinvolto (come utente1 o utente2)
cursor.execute("SELECT utente2 FROM approved_chats WHERE utente1 = ?", (current_user,))
chats = [r for r in cursor.fetchall()]
cursor.execute("SELECT utente1 FROM approved_chats WHERE utente2 = ?", (current_user,))
chats.extend([r for r in cursor.fetchall()])
response = {"status": "info", "message": f"Le tue chat attive: {', '.join(chats) if chats else 'Nessuna chat attiva. Invia richieste con /chatrequest'}"}
else:
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE utente1 = ? AND utente2 = ?", (u1, u2))
if cursor.fetchone():
response = {"status": "enter_chat", "target": target, "message": f"Entrato nella chat con {target}. Digita i messaggi direttamente. Usa /exit per uscire."}
else:
response = {"status": "error", "message": f"Non sei abilitato a chattare con {target}. Devi prima inviare una richiesta e attendere."}
elif len(args) == 2 and args.lower() == "delete":
target = args
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE utente1 = ? AND utente2 = ?", (u1, u2))
if cursor.fetchone():
cursor.execute("DELETE FROM approved_chats WHERE utente1 = ? AND utente2 = ?", (u1, u2))
db.commit()
response = {"status": "success", "message": f"Relazione di chat con {target} rimossa con successo."}
broadcast_to_user(target, {"type": "notification", "message": f"🗑️ {current_user} ha rimosso la chat condivisa con te."})
else:
response = {"status": "error", "message": f"Non hai nessuna chat attiva con {target}."}
else:
response = {"status": "error", "message": "Uso: /chat , /chat list, oppure /chat  delete"}
client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
# 6. INVIO MESSAGGIO DIRETTO
elif command == "msg":
if len(args) < 2:
continue
target, msg_text = args, args
u1, u2 = sorted([current_user, target])
cursor.execute("SELECT 1 FROM approved_chats WHERE utente1 = ? AND utente2 = ?", (u1, u2))
if cursor.fetchone():
delivered = broadcast_to_user(target, {"type": "msg", "from": current_user, "message": msg_text})
if delivered:
response = {"status": "msg_sent"}
else:
response = {"status": "error", "message": f"{target} è offline al momento."}
else:
response = {"status": "error", "message": "Non hai i permessi per inviare messaggi a questo utente."}
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
init_db()  # Crea database e tabelle se non esistono
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"[*] DeggioChat Server (SQLite Persistent Mode) in ascolto su {HOST}:{PORT}...")
try:
while True:
client_sock, _ = server.accept()
threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
except KeyboardInterrupt:
print("\n[*] Spegnimento del server.")
finally:
server.close()
if name == "main":
start_server()
