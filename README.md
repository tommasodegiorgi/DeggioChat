# DeggioChat — CLI Minecraft-Style Multilingual Chat Application

A minimal, low-overhead client-server chat application operating entirely inside the terminal. It features a command syntax inspired by Minecraft multiplayer servers and a text user experience optimized for console navigation. 

DeggioChat natively supports cross-platform execution from source code, 11 dynamic runtime languages, automated local SQLite database persistence, and secure SHA-256 password hashing.

---

## 🚀 Key Features

*   **11-Language Multilingual Core (i18n):** English by default. Switch dynamically at runtime between English, Italian, Spanish, Portuguese, Japanese, French, Slovenian, German, Croatian, Swedish, and Mandarin Chinese using the `/lang` command. Your preference is automatically saved locally.
*   **Minecraft-Style Controls:** Core authentication and messaging workflows are handled via intuitive slash commands: `/register`, `/login`, `/chatrequest`, and `/chat`.
*   **Persistent Local Storage:** Driven by a native SQLite database engine (`deggiochat.db`), all user credentials, hashed passwords, active sessions, and relationships are safely preserved on server restart.
*   **Persistent Session (Auto-Login):** Unique background tokens allow automated logins upon app restart without re-entering credentials.
*   **Graphical MOTD:** Displays a dynamic Minecraft-style "Message of the Day" banner upon successful login, showing the real-time count of online players.
*   **Focus Chat Mode:** Typing `/chat <username>` locks the terminal prompt into a direct conversation lane. Standard user input sends text instantly as a direct message without needing pre-fixed commands. Type `/exit` to return to the global CLI shell.

---

## 📖 Command Manual

### 🔑 Authentication
*   `/register <email> <username> <password>` - Create a brand new secure account and trigger automatic login.
*   `/login <username> <password>` - Access an existing account (restores or generates the local hidden session token).

### 📩 Relationships & Requests
*   `/chatrequest <username>` - Send a secure chat permission request to an active user.
*   `/chatrequest accept <username>` - Accept an incoming pending chat request.
*   `/chatrequest deny <username>` - Refuse an incoming pending chat request.

### 💬 Messaging & Navigation
*   `/chat list` - List all active users you currently share a dynamic chat channel with.
*   `/chat <username>` - Enter target focus chat mode with that user.
*   `/chat <username> delete` - Revoke shared chat permissions with that user and close the link.
*   🌐 `/lang <en/it/es/pt/ja/fr/sl/de/hr/sv/zh>` - Switch the entire interface and server responses instantly (Default: English).
*   `/exit` - Leave a focused chat room and safely return to the global prompt environment.
*   `/quit` - Disconnect from the remote host and close the CLI process.

---

## 🛠️ How to Run DeggioChat (OS-Specific Instructions)

DeggioChat relies strictly on the native Python 3 Standard Library. No external heavy dependencies (`pip`) are required. Ensure you have **Python 3.8 or higher** installed on your machine.

Open your terminal inside the project directory and follow the instructions for your OS:

### 🪟 1. Windows
Open **PowerShell** or **Command Prompt (CMD)**:
```bash
python server.py
# Open a new terminal instance to run the client
python client.py
```

### 🍏 2. macOS & 🐧 3. Linux
Open your system terminal shell:
```bash
python3 server.py
# Open a new terminal instance to run the client
python3 client.py
```

### 📱 4. iPad / iOS
Download **a-Shell** or **iSH Shell** from the App Store. Open the interface, pull the source files, and run the commands using internal tabs or split screen:
```bash
python3 server.py
# Open a new tab or split view for the client
python3 client.py
```

---

## 🔒 Security & Privacy Notice
All user passwords are encrypted using SHA-256 with a unique random cryptographic *salt* generated per user, ensuring maximum database protection against credential attacks. The local files `.session_token`, `.lang_config`, and `deggiochat.db` are strictly ignored by Git (`.gitignore`) to keep your private local data secure and untracked.
