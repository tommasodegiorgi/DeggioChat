import socket
import threading
import json
import secrets
import hashlib

# Configurazione Server
HOST = '127.0.0.1'
PORT = 55555

# Strutture dati globali (Stato in memoria)
# db_users memorizzerà ora: { username: { "email": email, "salt": salt_hex, "password_hash": hash_hex } }
db_users = {}            
active_sessions = {}     # { token: username }
online_clients = {}      # { username: socket_connection }
pending_requests = {}    # { destinatario: set(mittenti) }
approved_chats = {}      # { utente: set(amici_abilitati) }

lock = threading.Lock()

def hash_password(password, salt=None):
    """Genera un hash sicuro SHA-256 usando un salt casuale."""
    if not salt:
        salt = secrets.token_hex(8)
    # Unisce la password al salt per evitare attacchi a dizionario
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
                
                # 1. TOKEN LOGIN (Pre-autenticazione automatica)
                if command == "token_login":
                    token = args[0] if len(args) > 0 else ""
                    with lock:
                        username = active_sessions.get(token)
                        if username:
                            current_user = username
                            online_clients[username] = client_socket
                            
                            # Calcola quanti utenti sono online per il MOTD dinamico
                            count_online = len(online_clients)
                            response = {
                                "status": "success", 
                                "action": "login", 
                                "username": username, 
                                "message": f"Bentornato su DeggioChat, {username}! Accesso automatico eseguito.",
                                "show_motd": True,
                                "online_count": count_online
                            }
                        else:
                            response = {"status": "fail", "message": "Token non valido o scaduto."}
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue
                
                # 2. REGISTER
                if command == "register":
                    if len(args) < 3:
                        response = {"status": "error", "message": "Uso: /register <email> <username> <password>"}
                    else:
                        email, username, password = args[0], args[1], args[2]
                        with lock:
                            if username in db_users:
                                response = {"status": "error", "message": "Questo username è già registrato."}
                            else:
                                # Sicurezza avanzata: Hashing della password con Salt
                                p_hash, p_salt = hash_password(password)
                                db_users[username] = {
                                    "email": email, 
                                    "salt": p_salt, 
                                    "password_hash": p_hash
                                }
                                
                                token = secrets.token_hex(16)
                                active_sessions[token] = username
                                current_user = username
                                online_clients[username] = client_socket
                                approved_chats[username] = set()
                                pending_requests[username] = set()
                                
                                count_online = len(online_clients)
                                response = {
                                    "status": "success", 
                                    "action": "auth", 
                                    "token": token, 
                                    "username": username, 
                                    "message": f"Registrazione completata. Benvenuto su DeggioChat, {username}!",
                                    "show_motd": True,
                                    "online_count": count_online
                                }
                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                    continue

                # 3. LOGIN
                if command == "login":
                    if len(args) < 2:
                        response = {"status": "error", "message": "Uso: /login <username> <password>"}
                    else:
                        username, password = args[0], args[1]
                        with lock:
                            user_data = db_users.get(username)
                            if user_data:
                                # Verifica l'hash rigenerandolo con lo stesso salt salvato
                                saved_hash = user_data["password_hash"]
                                saved_salt = user_data["salt"]
                                check_hash, _ = hash_password(password, saved_salt)
                                
                                if check_hash == saved_hash:
                                    token = secrets.token_hex(16)
                                    active_sessions[token] = username
                                    current_user = username
                                    online_clients[username] = client_socket
                                    if username not in approved_chats: approved_chats[username] = set()
                                    if username not in pending_requests: pending_requests[username] = set()
                                    
                                    count_online = len(online_clients)
                                    response = {
                                        "status": "success", 
                                        "action": "auth", 
                                        "token": token, 
                                        "username": username, 
                                        "message": f"Accesso eseguito. Benvenuto su DeggioChat, {username}!",
                                        "show_motd": True,
                                        "online_count": count_online
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

                # 4. CHATREQUEST
                if command == "chatrequest":
                    if len(args) == 1:
                        target = args[0]
                        if target == current_user:
                            response = {"status": "error", "message": "Non puoi inviare una richiesta a te stesso."}
                        elif target not in db_users:
                            response = {"status": "error", "message": f"L'utente '{target}' non esiste."}
                        else:
                            with lock:
                                if target in approved_chats.get(current_user, set()):
                                    response = {"status": "error", "message": f"Hai già una chat attiva con {target}."}
                                else:
                                    if target not in pending_requests:
                                        pending_requests[target] = set()
                                    pending_requests[target].add(current_user)
                                    response = {"status": "info", "message": f"Richiesta di chat inviata a {target}."}
                                    broadcast_to_user(target, {"type": "notification", "message": f"📩 Hai ricevuto una richiesta di chat da {current_user}. Usa '/chatrequest accept {current_user}' per accettare."})
                    
                    elif len(args) == 2:
                        sub_cmd, target = args[0].lower(), args[1]
                        if sub_cmd == "accept":
                            with lock:
                                if current_user in pending_requests and target in pending_requests[current_user]:
pending_requests[current_user].remove(target)
approved_chats[current_user].add(target)
if target not in approved_chats: approved_chats[target] = set()
approved_chats[target].add(current_user)
response = {"status": "success", "message": f"Richiesta di chat accettata. Ora puoi chattare con {target}."}
broadcast_to_user(target, {"type": "notification", "message": f"✅ {current_user} ha accettato la tua richiesta di chat! Usa '/chat {current_user}' per parlare."})
else:
response = {"status": "error", "message": f"Non hai nessuna richiesta pendente da parte di {target}."}
elif sub_cmd == "deny":
with lock:
if current_user in pending_requests and target in pending_requests[current_user]:
pending_requests[current_user].remove(target)
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
target = args[0]
if target == "list":
with lock:
chats = list(approved_chats.get(current_user, []))
response = {"status": "info", "message": f"Le tue chat attive: {', '.join(chats) if chats else 'Nessuna chat attiva. Invia richieste con /chatrequest'}"}
else:
with lock:
is_approved = target in approved_chats.get(current_user, set())
if is_approved:
response = {"status": "enter_chat", "target": target, "message": f"Entrato nella chat con {target}. Digita i messaggi direttamente. Usa /exit per uscire."}
else:
response = {"status": "error", "message": f"Non sei abilitato a chattare con {target}. Devi prima inviare una richiesta e attendere."}
elif len(args) == 2 and args[1].lower() == "delete":
target = args[0]
with lock:
if target in approved_chats.get(current_user, set()):
approved_chats[current_user].remove(target)
if current_user in approved_chats.get(target, set()):
approved_chats[target].remove(current_user)
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
target, msg_text = args[0], args[1]
with lock:
is_approved = target in approved_chats.get(current_user, set())
if is_approved:
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
with lock:
if current_user and online_clients.get(current_user) == client_socket:
del online_clients[current_user]
client_socket.close()
def start_server():
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"[*] DeggioChat Server (Secure Mode) in ascolto su {HOST}:{PORT}...")
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
