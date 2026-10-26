import socket
import threading
import json
import os
import sys

TOKEN_FILE = ".session_token"
HOST = "127.0.0.1"
PORT = 55555

class ChatClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.focus_chat = None  
        self.running = True

    def connect(self):
        try:
            self.socket.connect((HOST, PORT))
        except Exception as e:
            print(f"❌ Impossibile connettersi al server ({e}).")
            sys.exit(1)
        
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.try_auto_login()

    def try_auto_login(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
            if token:
                payload = {"command": "token_login", "args": [token]}
                self.send_payload(payload)

    def send_payload(self, payload):
        try:
            self.socket.sendall((json.dumps(payload) + "\n").encode('utf-8'))
        except Exception:
            print("\n❌ Connessione con il server interrotta.")
            self.running = False

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("\n❌ Il server ha chiuso la connessione.")
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
                            print(f"\n💬 [Sussurro] <{sender}> {msg}")
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
        """Disegna il prompt interattivo in base alla modalità corrente."""
        if not self.username:
            prompt = "DeggioChat> "
        elif self.focus_chat:
            prompt = f"[{self.username} -> {self.focus_chat}]> "
        else:
            prompt = f"[{self.username}]> "
        print(prompt, end="", flush=True)

    def run_cli(self):
        print("====================================================")
        print("   🎮   BENVENUTO SU DEGGIOCHAT (CLI STYLE)  🎮      ")
        print("====================================================")
        print("Usa /register o /login per iniziare. I comandi iniziano con '/'")
        print("Esempi: /chatrequest Alpha, /chat Alpha, /exit, /quit\n")
        
        threading.Event().wait(0.2)  # Piccolo buffer per l'output di auto-login
        self.print_prompt()

        while self.running:
            try:
                user_input = sys.stdin.readline().strip()
            except KeyboardInterrupt:
                break

            if not user_input:
                self.print_prompt()
                continue
            
            # Modalità FOCUS CHAT attiva: l'input pulito invia messaggi diretti senza '/'
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
                    print(f"Uscito dalla chat con {self.focus_chat}.")
                    self.focus_chat = None
                else:
                    print("Non ti trovi in nessuna chat focalizzata.")
                self.print_prompt()
                continue
            elif cmd == "/register":
                if len(parts) < 4:
                    print("❌ Uso: /register <email> <username> <password>")
                    self.print_prompt()
                else:
                    self.send_payload({"command": "register", "args": [parts[1], parts[2], parts[3]]})
            elif cmd == "/login":
                if len(parts) < 3:
                    print("❌ Uso: /login <username> <password>")
                    self.print_prompt()
                else:
                    self.send_payload({"command": "login", "args": [parts[1], parts[2]]})
            elif cmd == "/chatrequest":
                if len(parts) == 2:
                    self.send_payload({"command": "chatrequest", "args": [parts[1]]})
                elif len(parts) == 3 and parts[1].lower() in ["accept", "deny"]:
                    self.send_payload({"command": "chatrequest", "args": [parts[1], parts[2]]})
                else:
                    print("❌ Uso: /chatrequest <username> oppure /chatrequest <accept/deny> <username>")
                    self.print_prompt()
            elif cmd == "/chat":
                if len(parts) == 2:
                    self.send_payload({"command": "chat", "args": [parts[1]]})
                elif len(parts) == 3 and parts[2].lower() == "delete":
                    self.send_payload({"command": "chat", "args": [parts[1], parts[2]]})
                else:
                    print("❌ Uso: /chat <username>, /chat list, o /chat <username> delete")
                    self.print_prompt()
            else:
                print("❌ Comando sconosciuto. Usa /register, /login, /chatrequest, /chat, /exit o /quit.")
                self.print_prompt()

        self.socket.close()
        print("\nConnessione terminata.")

if __name__ == "__main__":
    client = ChatClient()
    client.connect()
    client.run_cli()
