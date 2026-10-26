# DeggioChat — CLI Minecraft-Style Multilingual Chat Application

A minimal client-server chat application based entirely on the terminal, featuring a command syntax inspired by Minecraft and a text user experience optimized for the console. It natively supports SQLite persistence, secure authentication, real-time i18n localization, and automated GitHub Action executable builds.

---

## 🚀 Key Features

*   **Multilingual System (i18n):** English by default. Switch dynamically at runtime between English, Italian, Spanish, Portuguese, Japanese, French, and Slovenian using the `/lang` command.
*   **Minecraft-Style Commands:** Core workflow handled via `/register`, `/login`, `/chatrequest`, and `/chat`.
*   **Persistent SQLite DB:** Users data, hashed passwords, relationships, and active sessions are fully preserved on server restart.
*   **Persistent Session (Auto-Login):** Unique background tokens allow automated logins upon app restart.
*   **Focus Chat Mode:** Typing `/chat <username>` switches input to direct communication mode. Type `/exit` to go back.
*   **Secure Authentication:** Passwords are fully hashed using SHA-256 algorithms combined with unique runtime user salts.

---

## 📖 Command Manual

### 🔑 Authentication
*   `/register <email> <username> <password>` - Create a brand new account and trigger an automatic login.
*   `/login <username> <password>` - Access an existing account (generates the local token).

### 📩 Relationships & Requests
*   `/chatrequest <username>` - Send a chat request permission to a specific user.
*   `/chatrequest accept <username>` - Accept an incoming chat request.
*   `/chatrequest deny <username>` - Refuse an incoming chat request.

### 💬 Messaging & Navigation
*   `/chat list` - List all users you are currently allowed to chat with.
*   `/chat <username>` - Enter focus chat mode with that user.
*   `/chat <username> delete` - Revoke chat permissions with that user and close the link.
*   🌐 `/lang <en/it/es/pt/ja/fr/sl>` - Switch software language instantly (Default: English).
*   `/exit` - Leave focused chat room and return to global CLI prompt.
*   `/quit` - Disconnects the client and safely closes the application.
