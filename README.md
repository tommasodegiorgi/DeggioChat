# DeggioChat — CLI Minecraft-Style Multilingual Chat Application

A minimal, low-overhead client-server chat application operating entirely inside the terminal. It features a command syntax inspired by Minecraft multiplayer servers and a text user experience optimized for console navigation. 

DeggioChat natively supports cross-platform execution from source code, 7 dynamic runtime languages, automated SQLite database persistence, and secure SHA-256 password hashing.

---

## 🚀 Key Features

*   **Multilingual Core (i18n):** English by default. Switch dynamically at runtime between English, Italian, Spanish, Portuguese, Japanese, French, and Slovenian using the `/lang` command.
*   **Minecraft-Style Controls:** Core authentication and messaging workflows are handled via `/register`, `/login`, `/chatrequest`, and `/chat`.
*   **Cloud & Network Ready:** The server is fully optimized to stay online 24/7 on cloud hosting platforms (e.g., Render, Railway), allowing clients to connect globally.
*   **Focus Chat Mode:** Typing `/chat <username>` locks the terminal prompt into a direct conversation lane. Standard user input sends text instantly without needing pre-fixed commands. Type `/exit` to return to the global CLI shell.

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
*   🌐 `/lang <en/it/es/pt/ja/fr/sl>` - Switch the entire interface and server logs instantly (Default: English).
*   `/exit` - Leave a focused chat room and safely return to the global prompt environment.
*   `/quit` - Disconnect from the remote host and close the CLI process.

---

## 🛠️ How to Run DeggioChat (OS-Specific Instructions)

DeggioChat relies strictly on the native Python 3 Standard Library. No external heavy dependencies (`pip`) are required. Ensure you have **Python 3.8 or higher** installed on your machine.

Clone or download the repository to your environment, then open your terminal inside the project directory and follow the instructions for your OS:

### 🪟 1. Windows
Open **PowerShell** or **Command Prompt (CMD)** and execute the script directly:
```bash
python client.py
```
*(If Python is registered as `py` in your system PATH, use `py client.py` instead).*

### 🍏 2. macOS
Open **Terminal.app**. Mac operating systems might require explicit execution calls depending on environment paths:
```bash
python3 client.py
```

### 🐧 3. Linux (Ubuntu, Debian, Fedora, Arch, etc.)
Open your system terminal shell. Run:
```bash
python3 client.py
```

### 📱 4. iPad / iOS
Since iOS cannot native-compile bin executables or run terminal processes out of the box, you can run the source code natively using free App Store environments:
1.  Download **a-Shell** or **iSH Shell** from the iOS App Store.
2.  Open the application interface.
3.  Clone this repository or use the internal file provider to drop the `client.py` script.
4.  Run the client application inside the sandbox:
    ```bash
    python3 client.py
    ```

---

## 🌐 Server Deployment Notes

If you are hosting the backend instance (`server.py`) yourself:
1.  Run `python server.py` to initiate the listener. A local file named `deggiochat.db` will automatically spawn to manage storage persistent engines.
2.  If deploying to cloud ecosystems (e.g., Render, Railway), the environment variables will auto-map `HOST = '0.0.0.0'` and intercept the assigned routing `PORT`. Make sure to update the `HOST` address string inside `client.py` to match your cloud public domain url before distribution.
