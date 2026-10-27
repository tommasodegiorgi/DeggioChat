import socket
import threading
import json
import secrets
import hashlib
import sqlite3

# Server Configuration
HOST = '0.0.0.0'
PORT = 55555
DB_FILE = 'deggiochat.db'

# Runtime memory structures for active connections
online_clients = {}      # { username: socket_connection }
lock = threading.Lock()

# Multi-language dictionary for server-side responses (11 Languages)
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
        "req_accepted": "Solicitud de chat activa con {}.",
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
        "req_sent": "Solicitação di chat enviada para {}.",
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
"chat_removed": "Relation de chat avec {} supprimée avec succès.",
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
},
"de": {
"unknown_cmd": "Unbekannter Befehl.",
"welcome_back": "Willkommen zurück bei DeggioChat, {}! Automatische Anmeldung erfolgreich.",
"expired_token": "Ungültiges oder abgelaufenes Sitzungstoken.",
"usage_register": "Verwendung: /register   ",
"username_taken": "Dieser Benutzername ist bereits registriert.",
"reg_complete": "Registrierung abgeschlossen. Willkommen bei DeggioChat, {}!",
"usage_login": "Verwendung: /login  ",
"login_success": "Anmeldung erfolgreich. Willkommen bei DeggioChat, {}!",
"invalid_creds": "Ungültige Anmeldedaten.",
"auth_required": "Sie müssen sich zuerst mit /login oder /register authentifizieren.",
"self_request": "Sie können keine Chat-Anfrage an sich selbst senden.",
"user_not_found": "Benutzer '{}' existiert nicht.",
"already_friends": "Sie haben bereits einen aktiven Chat mit {}.",
"req_sent": "Chat-Anfrage an {} gesendet.",
"incoming_req": "📩 Sie haben eine Chat-Anfrage von {} erhalten. Geben Sie '/chatrequest accept {}' ein, um anzunehmen.",
"already_pending": "Sie haben bereits eine ausstehende Anfrage an {} gesendet.",
"req_accepted": "Chat-Anfrage angenommen. Sie können jetzt mit {} chatten.",
"req_accepted_notify": "✅ {} hat Ihre Chat-Anfrage angenommen! Geben Sie '/chat {}' ein, um das Gespräch zu beginnen.",
"no_req_found": "Sie haben keine ausstehenden Anfragen von {}.",
"req_denied": "Chat-Anfrage von {} abgelehnt.",
"req_denied_notify": "❌ {} hat Ihre Chat-Anfrage abgelehnt.",
"syntax_request": "Syntaxfehler. Verwenden Sie /chatrequest <accept/deny> ",
"usage_request": "Verwendung: /chatrequest  ODER /chatrequest <accept/deny> ",
"active_chats": "Ihre aktiven Chats: {}",
"no_active_chats": "Keine. Senden Sie Anfragen mit /chatrequest",
"enter_chat": "Fokus-Chat mit {} betreten. Geben Sie Ihre Nachrichten direkt ein. Geben Sie /exit zum Verlassen ein.",
"not_allowed_chat": "Sie dürfen nicht mit {} chatten. Senden Sie zuerst eine Anfrage.",
"chat_removed": "Chat-Beziehung mit {} erfolgreich entfernt.",
"chat_removed_notify": "🗑️ {} hat den gemeinsamen Chatraum mit Ihnen entfernt.",
"usage_chat": "Verwendung: /chat , /chat list, ODER /chat  delete",
"user_offline": "{} ist derzeit offline.",
"no_permission_msg": "Sie haben keine Berechtigung, diesem Benutzer eine Nachricht zu senden."
},
"hr": {
"unknown_cmd": "Nepoznata naredba.",
"welcome_back": "Dobrodošli natrag na DeggioChat, {}! Automatska prijava uspješna.",
"expired_token": "Nevažeći ili istekli token seje.",
"usage_register": "Upotreba: /register  <korisničko_ime> ",
"username_taken": "Ovo korisničko ime je već registrirano.",
"reg_complete": "Registracija završena. Dobrodošli na DeggioChat, {}!",
"usage_login": "Upotreba: /login <korisničko_ime> ",
"login_success": "Prijava uspješna. Dobrodošli na DeggioChat, {}!",
"invalid_creds": "Nevažeći vjerodostojni podaci.",
"auth_required": "Morate se prvo autentificirati koristeći /login ili /register.",
"self_request": "Ne možete poslati zahtjev za chat sami sebi.",
"user_not_found": "Korisnik '{}' ne postoji.",
"already_friends": "Već imate aktivan chat s {}.",
"req_sent": "Zahtjev za chat poslan korisniku {}.",
"incoming_req": "📩 Primili ste zahtjev za chat od {}. Upišite '/chatrequest accept {}' za prihvaćanje.",
"already_pending": "Već imate zahtjev na čekanju poslan korisniku {}.",
"req_accepted": "Zahtjev za chat prihvaćen. Sada možete chatati s {}.",
"req_accepted_notify": "✅ {} je prihvatio vaš zahtjev za chat! Upišite '/chat {}' za početak razgovora.",
"no_req_found": "Nemate zahtjeva na čekanju od korisnika {}.",
"req_denied": "Zahtjev za chat od korisnika {} odbijen.",
"req_denied_notify": "❌ {} je odbio vaš zahtjev za chat.",
"syntax_request": "Sintaktička pogreška. Koristite /chatrequest <accept/deny> <korisničko_ime>",
"usage_request": "Upotreba: /chatrequest <korisničko_ime> ILI /chatrequest <accept/deny> <korisničko_ime>",
"active_chats": "Vaši aktivni chatovi: {}",
"no_active_chats": "Nema ih. Pošaljite zahtjev koristeći /chatrequest",
"enter_chat": "Ušli ste u fokusirani chat s korisnikom {}. Poruke upisujte izravno. Upišite /exit za izlaz.",
"not_allowed_chat": "Nemate dopuštenje za chat s korisnikom {}. Prvo pošaljite zahtjev.",
"chat_removed": "Veza za chat s korisnikom {} uspješno uklonjena.",
"chat_removed_notify": "🗑️ {} je uklonio zajedničku chat sobu s vama.",
"usage_chat": "Upotreba: /chat <korisničko_ime>, /chat list, ILI /chat <korisničko_ime> delete",
"user_offline": "Korisnik {} je trenutno izvan mreže.",
"no_permission_msg": "Nemate dopuštenje za slanje poruka ovom korisniku."
},
"sv": {
"unknown_cmd": "Okänt kommando.",
"welcome_back": "Välkommen tillbaka till DeggioChat, {}! Automatisk inloggning lyckades.",
"expired_token": "Ogiltig eller utgången sessionstoken.",
"usage_register": "Användning: /register  <användarnamn> <lösenord>",
"username_taken": "Detta användarnamn är redan registrerat.",
"reg_complete": "Registreringen klar. Välkommen till DeggioChat, {}!",
"usage_login": "Användning: /login <användarnamn> <lösenord>",
"login_success": "Inloggning lyckades. Välkommen till DeggioChat, {}!",
"invalid_creds": "Felaktiga inloggningsuppgifter.",
"auth_required": "Du måste autentisera dig först med /login eller /register.",
"self_request": "Du kan inte skicka en chatta-förfrågan till dig själv.",
"user_not_found": "Användaren '{}' finns inte.",
"already_friends": "Du har redan en aktiv chatt med {}.",
"req_sent": "Chatta-förfrågan skickad till {}.",
"incoming_req": "📩 Du har fått en chatta-förfrågan från {}. Skriv '/chatrequest accept {}' för att godkänna.",
"already_pending": "Du har redan en väntande förfrågan skickad till {}.",
"req_accepted": "Chatta-förfrågan godkänd. Du kan nu chatta med {}.",
"req_accepted_notify": "✅ {} godkände din chatta-förfrågan! Skriv '/chat {}' för att börja prata.",
"no_req_found": "Du har inga väntande förfrågningar från {}.",
"req_denied": "Chatta-förfrågan från {} avvisad.",
"req_denied_notify": "❌ {} avvisade din chatta-förfrågan.",
"syntax_request": "Syntaxfel. Använd /chatrequest <accept/deny> <användarnamn>",
"usage_request": "Användning: /chatrequest <användarnamn> ELLER /chatrequest <accept/deny> <användarnamn>",
"active_chats": "Dina aktiva chattar: {}",
"no_active_chats": "Inga. Skicka förfrågningar med /chatrequest",
"enter_chat": "Gick in i fokus-chatt med {}. Skriv dina meddelanden direkt. Skriv /exit för att lämna.",
"not_allowed_chat": "Du har inte tillåtelse at chatta med {}. Skicka en förfrågan först.",
"chat_removed": "Chattrelationen med {} har tagits bort.",
"chat_removed_notify": "🗑️ {} tog bort det gemensamma chattrummet med dig.",
"usage_chat": "Användning: /chat <användarnamn>, /chat list, ELLER /chat <användarnamn> delete",
"user_offline": "{} är för närvarande offline.",
"no_permission_msg": "Du har inte behörighet att skicka meddelanden till denna användare."
},
"zh": {
"unknown_cmd": "未知命令。",
"welcome_back": "欢迎回到 DeggioChat，{}！自动登录成功。",
"expired_token": "无效或过期的会话令牌。",
"usage_register": "用法: /register <电子邮件> <用户名> <密码>",
"username_taken": "该用户名已被注册。",
"reg_complete": "注册完成。欢迎来到 DeggioChat，{}！",
"usage_login": "用法: /login <用户名> <密码>",
"login_success": "登录成功。欢迎来到 DeggioChat，{}！",
"invalid_creds": "凭据无效。",
"auth_required": "您必须先使用 /login 或 /register 进行身份验证。",
"self_request": "您 cannot 向自己发送聊天请求。",
"user_not_found": "用户 '{}' 不存在。",
"already_friends": "您已与 {} 建立了活跃聊天。",
"req_sent": "聊天请求已发送至 {}。",
"incoming_req": "📩 您收到了来自 {} 的聊天请求。输入 '/chatrequest accept {}' 以接受。",
"already_pending": "您已向 {} 发送了正在等待处理的请求。",
"req_accepted": "聊天请求已接受。您现在可以与 {} 聊天了。",
"req_accepted_notify": "✅ {} 接受了您的聊天请求！输入 '/chat {}' 开始交谈。",
"no_req_found": "您没有来自 {} 的待处理请求。",
"req_denied": "来自 {} 的聊天请求已被拒绝。",
"req_denied_notify": "❌ {} 拒绝了您的聊天请求。",
"syntax_request": "语法错误。使用 /chatrequest <accept/deny> <用户名>",
"usage_request": "用法: /chatrequest <用户名> 或 /chatrequest <accept/deny> <用户名>",
"active_chats": "您的活跃聊天: {}",
"no_active_chats": "无。使用 /chatrequest 发送请求",
"enter_chat": "已进入与 {} 的专注聊天。直接输入您的消息。输入 /exit 退出。",
"not_allowed_chat": "您未被允许与 {} 聊天。请先发送请求。",
"chat_removed": "与 {} 的聊天关系已成功删除。",
"chat_removed_notify": "🗑️ {} 删掉了与您的共享聊天室。",
"usage_chat": "用法: /chat <用户名>, /chat list, 或 /chat <用户名> delete",
"user_offline": "{} 当前处于离线状态。",
"no_permission_msg": "您没有给该用户发送消息的权限。"
}
}
def get_msg(lang, key, *args):
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
lang = payload.get("lang", "en").lower()
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
