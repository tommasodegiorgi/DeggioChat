import socket
import threading
import json
import secrets
import hashlib
import sqlite3
import os  # Assicurati che os sia importato

# Configurazione Server per Render Free
HOST = '0.0.0.0'  # Accetta connessioni da tutto il mondo
PORT = int(os.environ.get("PORT", 55555))  # Prende la porta assegnata da Render
DB_FILE = 'deggiochat.db'  # Salva localmente nella cartella del server


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
        "incoming_req": "ðŸ“© You received a chat request from {}. Type '/chatrequest accept {}' to accept.",
        "already_pending": "You already have a pending request sent to {}.",
        "req_accepted": "Chat request accepted. You can now chat with {}.",
        "req_accepted_notify": "âœ… {} accepted your chat request! Type '/chat {}' to start talking.",
        "no_req_found": "You have no pending requests from {}.",
        "req_denied": "Chat request from {} denied.",
        "req_denied_notify": "âŒ {} denied your chat request.",
        "syntax_request": "Syntax error. Use /chatrequest <accept/deny> <username>",
        "usage_request": "Usage: /chatrequest <username> OR /chatrequest <accept/deny> <username>",
        "active_chats": "Your active chats: {}",
        "no_active_chats": "None. Send requests using /chatrequest",
        "enter_chat": "Entered focus chat with {}. Type your messages directly. Type /exit to leave.",
        "not_allowed_chat": "You are not allowed to chat with {}. Send a request first.",
        "chat_removed": "Chat relationship with {} successfully removed.",
        "chat_removed_notify": "ðŸ—‘ï¸ {} removed their shared chat room with you.",
        "usage_chat": "Usage: /chat <username>, /chat list, OR /chat <username> delete",
        "user_offline": "{} is currently offline.",
        "no_permission_msg": "You do not have permission to message this user."
    },
    "it": {
        "unknown_cmd": "Comando sconosciuto.",
        "welcome_back": "Bentornato su DeggioChat, {}! Accesso automatico eseguito.",
        "expired_token": "Token di sessione non valido o scaduto.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Questo username Ã¨ giÃ  registrato.",
        "reg_complete": "Registrazione completata. Benvenuto su DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Accesso eseguito. Benvenuto su DeggioChat, {}!",
        "invalid_creds": "Credenziali errate.",
        "auth_required": "Devi prima autenticarti con /login o /register.",
        "self_request": "Non puoi inviare una richiesta a te stesso.",
        "user_not_found": "L'utente '{}' non esiste.",
        "already_friends": "Hai giÃ  una chat attiva con {}.",
        "req_sent": "Richiesta di chat inviata a {}.",
        "incoming_req": "ðŸ“© Hai ricevuto una richiesta di chat da {}. Usa '/chatrequest accept {}' per accettare.",
        "already_pending": "Hai giÃ  una richiesta pendente verso {}.",
        "req_accepted": "Richiesta di chat accettata. Ora puoi chattare con {}.",
        "req_accepted_notify": "âœ… {} ha accettato la tua richiesta di chat! Usa '/chat {}' per parlare.",
        "no_req_found": "Non hai nessuna richiesta pendente da parte di {}.",
        "req_denied": "Richiesta di chat da {} rifiutata.",
        "req_denied_notify": "âŒ {} ha rifiutato la tua richiesta di chat.",
        "syntax_request": "Sintassi errata. Usa /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> oppure /chatrequest <accept/deny> <username>",
        "active_chats": "Le tue chat attive: {}",
        "no_active_chats": "Nessuna. Invia richieste con /chatrequest",
        "enter_chat": "Entrato nella chat con {}. Digita i messaggi direttamente. Usa /exit per uscire.",
        "not_allowed_chat": "Non sei abilitato a chattare con {}. Devi prima inviare una richiesta.",
        "chat_removed": "Relazione di chat con {} rimossa con successo.",
        "chat_removed_notify": "ðŸ—‘ï¸ {} ha rimosso la chat condivisa con te.",
        "usage_chat": "Uso: /chat <username>, /chat list, oppure /chat <username> delete",
        "user_offline": "{} Ã¨ offline al momento.",
        "no_permission_msg": "Non hai i permessi per inviare messaggi a questo utente."
    },
    "es": {
        "unknown_cmd": "Comando desconocido.",
        "welcome_back": "Â¡Bienvenido de nuevo a DeggioChat, {}! Inicio de sesiÃ³n automÃ¡tico exitoso.",
        "expired_token": "Token de sesiÃ³n invÃ¡lido o expirado.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Este nombre de usuario ya estÃ¡ registrado.",
        "reg_complete": "Registro completado. Â¡Bienvenido a DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Inicio de sesiÃ³n exitoso. Â¡Bienvenido a DeggioChat, {}!",
        "invalid_creds": "Credenciales incorrectas.",
        "auth_required": "Primero debes autenticarte usando /login o /register.",
        "self_request": "No puedes enviarte una solicitud de chat a ti mismo.",
        "user_not_found": "El usuario '{}' no existe.",
        "already_friends": "Ya tienes un chat activo con {}.",
        "req_sent": "Solicitud de chat enviada a {}.",
        "incoming_req": "ðŸ“© Has recibido una solicitud de chat de {}. Escribe '/chatrequest accept {}' para aceptar.",
        "already_pending": "Ya tienes una solicitud pendiente enviada a {}.",
        "req_accepted": "Solicitud de chat activa con {}.",
        "req_accepted_notify": "âœ… Â¡{} aceptÃ³ tu solicitud de chat! Escribe '/chat {}' para empezar a hablar.",
        "no_req_found": "No tienes solicitudes pendientes de {}.",
        "req_denied": "Solicitud de chat de {} rechazada.",
        "req_denied_notify": "âŒ {} rechazÃ³ tu solicitud de chat.",
        "syntax_request": "Error de sintaxis. Usa /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> O /chatrequest <accept/deny> <username>",
        "active_chats": "Tus chats activos: {}",
        "no_active_chats": "Ninguno. EnvÃ­a solicitudes usando /chatrequest",
        "enter_chat": "Entraste al chat enfocado con {}. Escribe tus mensajes directamente. Escribe /exit para salir.",
        "not_allowed_chat": "No tienes permitido chatear con {}. EnvÃ­a una solicitud primero.",
        "chat_removed": "RelaciÃ³n de chat con {} eliminada con Ã©xito.",
        "chat_removed_notify": "ðŸ—‘ï¸ {} eliminÃ³ la sala de chat compartida contigo.",
        "usage_chat": "Uso: /chat <username>, /chat list, O /chat <username> delete",
        "user_offline": "{} estÃ¡ actualmente desconectado.",
        "no_permission_msg": "No tienes permiso para enviar mensajes a este usuario."
    },
    "pt": {
        "unknown_cmd": "Comando desconhecido.",
        "welcome_back": "Bem-vindo de volta ao DeggioChat, {}! Login automÃ¡tico bem-sucedido.",
        "expired_token": "Token de sessÃ£o invÃ¡lido ou expirado.",
        "usage_register": "Uso: /register <email> <username> <password>",
        "username_taken": "Este nome de usuÃ¡rio jÃ¡ estÃ¡ registrado.",
        "reg_complete": "Registro concluÃ­do. Bem-vindo ao DeggioChat, {}!",
        "usage_login": "Uso: /login <username> <password>",
        "login_success": "Login bem-sucedido. Bem-vindo ao DeggioChat, {}!",
        "invalid_creds": "Credenciais invÃ¡lidas.",
        "auth_required": "VocÃª deve se autenticar primeiro usando /login ou /register.",
        "self_request": "VocÃª nÃ£o pode enviar uma solicitaÃ§Ã£o de chat para si mesmo.",
        "user_not_found": "O usuÃ¡rio '{}' nÃ£o existe.",
        "already_friends": "VocÃª jÃ¡ tem um chat ativo com {}.",
        "req_sent": "SolicitaÃ§Ã£o di chat enviada para {}.",
        "incoming_req": "ðŸ“© VocÃª recebeu uma solicitaÃ§Ã£o de chat de {}. Digite '/chatrequest accept {}' para aceitar.",
        "already_pending": "VocÃª jÃ¡ tem uma solicitaÃ§Ã£o pendente enviada para {}.",
        "req_accepted": "SolicitaÃ§Ã£o de chat aceita. Agora vocÃª pode conversar com {}.",
        "req_accepted_notify": "âœ… {} aceitou sua solicitaÃ§Ã£o de chat! Digite '/chat {}' para comeÃ§ar a falar.",
        "no_req_found": "VocÃª nÃ£o tem solicitaÃ§Ãµes pendentes de {}.",
        "req_denied": "SolicitaÃ§Ã£o de chat de {} recusada.",
        "req_denied_notify": "âŒ {} recusou sua solicitaÃ§Ã£o de chat.",
        "syntax_request": "Erro de sintaxe. Use /chatrequest <accept/deny> <username>",
        "usage_request": "Uso: /chatrequest <username> OU /chatrequest <accept/deny> <username>",
        "active_chats": "Seus chats ativos: {}",
        "no_active_chats": "Nenhum. Envie solicitaÃ§Ãµes usando /chatrequest",
        "enter_chat": "Entrou no chat focado com {}. Digite suas mensagens diretamente. Digite /exit para sair.",
        "not_allowed_chat": "VocÃª nÃ£o tem permissÃ£o para conversar com {}. Envie uma solicitaÃ§Ã£o primeiro.",
        "chat_removed": "RelaÃ§Ã£o de chat com {} removida com sucesso.",
"chat_removed_notify": "ðŸ—‘ï¸ {} removeu a sala de chat compartilhada com vocÃª.",
"usage_chat": "Uso: /chat , /chat list, OU /chat  delete",
"user_offline": "{} estÃ¡ atualmente offline.",
"no_permission_msg": "VocÃª nÃ£o tem permissÃ£o para enviar mensagens a este usuÃ¡rio."
},
"ja": {
"unknown_cmd": "ä¸æ˜Žãªã‚³ãƒžãƒ³ãƒ‰ã§ã™ã€‚",
"welcome_back": "DeggioChatã¸ãŠã‹ãˆã‚Šãªã•ã„ã€{}ï¼è‡ªå‹•ãƒ­ã‚°ã‚¤ãƒ³ã«æˆåŠŸã—ã¾ã—ãŸã€‚",
"expired_token": "ã‚»ãƒƒã‚·ãƒ§ãƒ³ãƒˆãƒ¼ã‚¯ãƒ³ãŒç„¡åŠ¹ã‹ã€ã¾ãŸã¯æœŸé™åˆ‡ã‚Œã§ã™ã€‚",
"usage_register": "ä½¿ç”¨æ³•: /register <ãƒ¡ãƒ¼ãƒ«> <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> <ãƒ‘ã‚¹ãƒ¯ãƒ¼ãƒ‰>",
"username_taken": "ã“ã®ãƒ¦ãƒ¼ã‚¶ãƒ¼åã¯æ—¢ã«ç™»éŒ²ã•ã‚Œã¦ã„ã¾ã™ã€‚",
"reg_complete": "ç™»éŒ²ãŒå®Œäº†ã—ã¾ã—ãŸã€‚DeggioChatã¸ã‚ˆã†ã“ãã€{}ï¼",
"usage_login": "ä½¿ç”¨æ³•: /login <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> <ãƒ‘ã‚¹ãƒ¯ãƒ¼ãƒ‰>",
"login_success": "ãƒ­ã‚°ã‚¤ãƒ³ã«æˆåŠŸã—ã¾ã—ãŸã€‚DeggioChatã¸ã‚ˆã†ã“ãã€{}ï¼",
"invalid_creds": "èªè¨¼æƒ…å ±ãŒæ­£ã—ãã‚ã‚Šã¾ã›ã‚“ã€‚",
"auth_required": "æœ€åˆã« /login ã¾ãŸã¯ /register ã‚’ä½¿ç”¨ã—ã¦èªè¨¼ã—ã¦ãã ã•ã„ã€‚",
"self_request": "è‡ªåˆ†è‡ªèº«ã«ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’é€ä¿¡ã™ã‚‹ã“ã¨ã¯ã§ãã¾ã›ã‚“ã€‚",
"user_not_found": "ãƒ¦ãƒ¼ã‚¶ãƒ¼ '{}' ã¯å­˜åœ¨ã—ã¾ã›ã‚“ã€‚",
"already_friends": "æ—¢ã« {} ã¨ã®æœ‰åŠ¹ãªãƒãƒ£ãƒƒãƒˆãŒã‚ã‚Šã¾ã™ã€‚",
"req_sent": "{} ã«ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’é€ä¿¡ã—ã¾ã—ãŸã€‚",
"incoming_req": "ðŸ“© {} ã‹ã‚‰ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’å—ä¿¡ã—ã¾ã—ãŸã€‚æ‰¿èªã™ã‚‹ã«ã¯ '/chatrequest accept {}' ã¨å…¥åŠ›ã—ã¦ãã ã•ã„ã€‚",
"already_pending": "ã™ã§ã« {} ã«é€ä¿¡ã•ã‚ŒãŸä¿ç•™ä¸­ã®ãƒªã‚¯ã‚¨ã‚¹ãƒˆãŒã‚ã‚Šã¾ã™ã€‚",
"req_accepted": "ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆãŒæ‰¿èªã•ã‚Œã¾ã—ãŸã€‚{} ã¨ãƒãƒ£ãƒƒãƒˆã§ãã‚‹ã‚ˆã†ã«ãªã‚Šã¾ã—ãŸã€‚",
"req_accepted_notify": "âœ… {} ãŒãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’æ‰¿èªã—ã¾ã—ãŸï¼ '/chat {}' ã¨å…¥åŠ›ã—ã¦ä¼šè©±ã‚’å§‹ã‚ã¾ã—ã‚‡ã†ã€‚",
"no_req_found": "{} ã‹ã‚‰ã®ä¿ç•™ä¸­ã®ãƒªã‚¯ã‚¨ã‚¹ãƒˆã¯ã‚ã‚Šã¾ã›ã‚“ã€‚",
"req_denied": "{} ã‹ã‚‰ã®ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’æ‹’å¦ã—ã¾ã—ãŸã€‚",
"req_denied_notify": "âŒ {} ã¯ã‚ãªãŸã®ãƒãƒ£ãƒƒãƒˆãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’æ‹’å¦ã—ã¾ã—ãŸã€‚",
"syntax_request": "æ§‹æ–‡ã‚¨ãƒ©ãƒ¼ã€‚/chatrequest <accept/deny> <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> ã‚’ä½¿ç”¨ã—ã¦ãã ã•ã„ã€‚",
"usage_request": "ä½¿ç”¨æ³•: /chatrequest <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> ã¾ãŸã¯ /chatrequest <accept/deny> <ãƒ¦ãƒ¼ã‚¶ãƒ¼å>",
"active_chats": "ã‚¢ã‚¯ãƒ†ã‚£ãƒ–ãªãƒãƒ£ãƒƒãƒˆ: {}",
"no_active_chats": "ãªã—ã€‚/chatrequest ã‚’ä½¿ç”¨ã—ã¦ãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’é€ä¿¡ã—ã¦ãã ã•ã„ã€‚",
"enter_chat": "{} ã¨ã®é›†ä¸­ãƒãƒ£ãƒƒãƒˆã«å…¥ã‚Šã¾ã—ãŸã€‚ãƒ¡ãƒƒã‚»ãƒ¼ã‚¸ã‚’ç›´æŽ¥å…¥åŠ›ã—ã¦ãã ã•ã„ã€‚çµ‚äº†ã™ã‚‹ã«ã¯ /exit ã¨å…¥åŠ›ã—ã¾ã™ã€‚",
"not_allowed_chat": "{} ã¨ã®ãƒãƒ£ãƒƒãƒˆã¯è¨±å¯ã•ã‚Œã¦ã„ã¾ã›ã‚“ã€‚æœ€åˆã«ãƒªã‚¯ã‚¨ã‚¹ãƒˆã‚’é€ä¿¡ã—ã¦ãã ã•ã„ã€‚",
"chat_removed": "{} ã¨ã®ãƒãƒ£ãƒƒãƒˆé–¢ä¿‚ãŒæ­£å¸¸ã«å‰Šé™¤ã•ã‚Œã¾ã—ãŸã€‚",
"chat_removed_notify": "ðŸ—‘ï¸ {} ãŒã‚ãªãŸã¨ã®å…±æœ‰ãƒãƒ£ãƒƒãƒˆãƒ«ãƒ¼ãƒ ã‚’å‰Šé™¤ã—ã¾ã—ãŸã€‚",
"usage_chat": "ä½¿ç”¨æ³•: /chat <ãƒ¦ãƒ¼ã‚¶ãƒ¼å>, /chat list, ã¾ãŸã¯ /chat <ãƒ¦ãƒ¼ã‚¶ãƒ¼å> delete",
"user_offline": "{} ã¯ç¾åœ¨ã‚ªãƒ•ãƒ©ã‚¤ãƒ³ã§ã™ã€‚",
"no_permission_msg": "ã“ã®ãƒ¦ãƒ¼ã‚¶ãƒ¼ã«ãƒ¡ãƒƒã‚»ãƒ¼ã‚¸ã‚’é€ä¿¡ã™ã‚‹æ¨©é™ãŒã‚ã‚Šã¾ã›ã‚“ã€‚"
},
"fr": {
"unknown_cmd": "Commande inconnue.",
"welcome_back": "Bon retour sur DeggioChat, {} ! Connexion automatique rÃ©ussie.",
"expired_token": "Jeton de session invalide ou expirÃ©.",
"usage_register": "Usage: /register   ",
"username_taken": "Ce nom d'utilisateur est dÃ©jÃ  enregistrÃ©.",
"reg_complete": "Inscription terminÃ©e. Bienvenue sur DeggioChat, {} !",
"usage_login": "Usage: /login  ",
"login_success": "Connexion rÃ©ussie. Bienvenue sur DeggioChat, {} !",
"invalid_creds": "Identifiants invalides.",
"auth_required": "Vous devez d'abord vous authentifier avec /login ou /register.",
"self_request": "Vous ne pouvez pas vous envoyer une demande de chat Ã  vous-mÃªme.",
"user_not_found": "L'utilisateur '{}' n'existe pas.",
"already_friends": "Vous avez dÃ©jÃ  un chat actif avec {}.",
"req_sent": "Demande de chat envoyÃ©e Ã  {}.",
"incoming_req": "ðŸ“© Vous avez reÃ§u une demande de chat de {}. Tapez '/chatrequest accept {}' pour accepter.",
"already_pending": "Vous avez dÃ©jÃ  une demande en attente envoyÃ©e Ã  {}.",
"req_accepted": "Demande de chat acceptÃ©e. Vous pouvez maintenant chatter avec {}.",
"req_accepted_notify": "âœ… {} a acceptÃ© votre demande de chat ! Tapez '/chat {}' pour commencer Ã  parler.",
"no_req_found": "Vous n'avez aucune demande en attente de la part de {}.",
"req_denied": "Demande de chat de {} refusÃ©e.",
"req_denied_notify": "âŒ {} a refusÃ© votre demande de chat.",
"syntax_request": "Erreur de syntaxe. Utilisez /chatrequest <accept/deny> ",
"usage_request": "Usage: /chatrequest  OU /chatrequest <accept/deny> ",
"active_chats": "Vos chats actifs : {}",
"no_active_chats": "Aucun. Envoyez des demandes via /chatrequest",
"enter_chat": "EntrÃ© dans le chat ciblÃ© avec {}. Tapez vos messages directement. Tapez /exit pour quitter.",
"not_allowed_chat": "Vous n'Ãªtes pas autorisÃ© Ã  chatter avec {}. Envoyez d'abord une demande.",
"chat_removed": "Relation de chat avec {} supprimÃ©e avec succÃ¨s.",
"chat_removed_notify": "ðŸ—‘ï¸ {} a supprimÃ© le salon de chat partagÃ© avec vous.",
"usage_chat": "Usage: /chat , /chat list, OU /chat  delete",
"user_offline": "{} est actuellement hors ligne.",
"no_permission_msg": "Vous n'avez pas la permission d'envoyer un message Ã  cet utilisateur."
},
"sl": {
"unknown_cmd": "Neznan ukaz.",
"welcome_back": "DobrodoÅ¡li nazaj na DeggioChat, {}! Samodejna prijava uspeÅ¡na.",
"expired_token": "Neveljaven ali potekel Å¾eton seje.",
"usage_register": "Uporaba: /register <e-poÅ¡ta> <uporabniÅ¡ko_ime> ",
"username_taken": "To uporabniÅ¡ko ime je Å¾e registrirano.",
"reg_complete": "Registracija zakljuÄena. DobrodoÅ¡li na DeggioChat, {}!",
"usage_login": "Uporaba: /login <uporabniÅ¡ko_ime> ",
"login_success": "Prijava uspeÅ¡na. DobrodoÅ¡li na DeggioChat, {}!",
"invalid_creds": "NapaÄni podatki za prijavo.",
"auth_required": "Najprej se morate avtenticirati z ukazom /login ali /register.",
"self_request": "Sami sebi ne morete poslati proÅ¡nje za klepet.",
"user_not_found": "Uporabnik '{}' ne obstaja.",
"already_friends": "S tem uporabnikom ({}) Å¾e imate aktiven klepet.",
"req_sent": "ProÅ¡nja za klepet poslana uporabniku {}.",
"incoming_req": "ðŸ“© Prejeli ste proÅ¡njo za klepet od {}. Vtipkajte '/chatrequest accept {}' za sprejem.",
"already_pending": "Uporabniku {} ste Å¾e poslali proÅ¡njo, ki je v Äakanju.",
"req_accepted": "ProÅ¡nja za klepet sprejeta. Sedaj lahko klepetate z uporabnikom {}.",
"req_accepted_notify": "âœ… {} je sprejel vaÅ¡o proÅ¡njo za klepet! Vtipkajte '/chat {}' za zaÄetek pogovora.",
"no_req_found": "Nimate nobenih proÅ¡enj na Äakanju od uporabnika {}.",
"req_denied": "ProÅ¡nja za klepet od {} je bila zavrnjena.",
"req_denied_notify": "âŒ {} je zavrnil vaÅ¡o proÅ¡njo za klepet.",
"syntax_request": "SintaktiÄna napaka. Uporabite /chatrequest <accept/deny> <uporabniÅ¡ko_ime>",
"usage_request": "Uporaba: /chatrequest <uporabniÅ¡ko_ime> ALI /chatrequest <accept/deny> <uporabniÅ¡ko_ime>",
"active_chats": "VaÅ¡i aktivni klepeti: {}",
"no_active_chats": "Nobenega. PoÅ¡ljite proÅ¡njo z ukazom /chatrequest",
"enter_chat": "Vstopili ste v osredotoÄen klepet z {}. SporoÄila vpisujte neposredno. Vtipkajte /exit za izhod.",
"not_allowed_chat": "Nimate dovoljenja za klepet z uporabnikom {}. Najprej poÅ¡ljite proÅ¡njo.",
"chat_removed": "Klepet z uporabnikom {} je bil uspeÅ¡no odstranjen.",
"chat_removed_notify": "ðŸ—‘ï¸ Uporabnik {} je odstranil skupno klepetalnico z vami.",
"usage_chat": "Uporaba: /chat <uporabniÅ¡ko_ime>, /chat list, ALI /chat <uporabniÅ¡ko_ime> delete",
"user_offline": "Uporabnik {} je trenutno nedosegljiv.",
"no_permission_msg": "Nimate dovoljenja za poÅ¡iljanje sporoÄil temu uporabniku."
},
"de": {
"unknown_cmd": "Unbekannter Befehl.",
"welcome_back": "Willkommen zurÃ¼ck bei DeggioChat, {}! Automatische Anmeldung erfolgreich.",
"expired_token": "UngÃ¼ltiges oder abgelaufenes Sitzungstoken.",
"usage_register": "Verwendung: /register   ",
"username_taken": "Dieser Benutzername ist bereits registriert.",
"reg_complete": "Registrierung abgeschlossen. Willkommen bei DeggioChat, {}!",
"usage_login": "Verwendung: /login  ",
"login_success": "Anmeldung erfolgreich. Willkommen bei DeggioChat, {}!",
"invalid_creds": "UngÃ¼ltige Anmeldedaten.",
"auth_required": "Sie mÃ¼ssen sich zuerst mit /login oder /register authentifizieren.",
"self_request": "Sie kÃ¶nnen keine Chat-Anfrage an sich selbst senden.",
"user_not_found": "Benutzer '{}' existiert nicht.",
"already_friends": "Sie haben bereits einen aktiven Chat mit {}.",
"req_sent": "Chat-Anfrage an {} gesendet.",
"incoming_req": "ðŸ“© Sie haben eine Chat-Anfrage von {} erhalten. Geben Sie '/chatrequest accept {}' ein, um anzunehmen.",
"already_pending": "Sie haben bereits eine ausstehende Anfrage an {} gesendet.",
"req_accepted": "Chat-Anfrage angenommen. Sie kÃ¶nnen jetzt mit {} chatten.",
"req_accepted_notify": "âœ… {} hat Ihre Chat-Anfrage angenommen! Geben Sie '/chat {}' ein, um das GesprÃ¤ch zu beginnen.",
"no_req_found": "Sie haben keine ausstehenden Anfragen von {}.",
"req_denied": "Chat-Anfrage von {} abgelehnt.",
"req_denied_notify": "âŒ {} hat Ihre Chat-Anfrage abgelehnt.",
"syntax_request": "Syntaxfehler. Verwenden Sie /chatrequest <accept/deny> ",
"usage_request": "Verwendung: /chatrequest  ODER /chatrequest <accept/deny> ",
"active_chats": "Ihre aktiven Chats: {}",
"no_active_chats": "Keine. Senden Sie Anfragen mit /chatrequest",
"enter_chat": "Fokus-Chat mit {} betreten. Geben Sie Ihre Nachrichten direkt ein. Geben Sie /exit zum Verlassen ein.",
"not_allowed_chat": "Sie dÃ¼rfen nicht mit {} chatten. Senden Sie zuerst eine Anfrage.",
"chat_removed": "Chat-Beziehung mit {} erfolgreich entfernt.",
"chat_removed_notify": "ðŸ—‘ï¸ {} hat den gemeinsamen Chatraum mit Ihnen entfernt.",
"usage_chat": "Verwendung: /chat , /chat list, ODER /chat  delete",
"user_offline": "{} ist derzeit offline.",
"no_permission_msg": "Sie haben keine Berechtigung, diesem Benutzer eine Nachricht zu senden."
},
"hr": {
"unknown_cmd": "Nepoznata naredba.",
"welcome_back": "DobrodoÅ¡li natrag na DeggioChat, {}! Automatska prijava uspjeÅ¡na.",
"expired_token": "NevaÅ¾eÄ‡i ili istekli token seje.",
"usage_register": "Upotreba: /register  <korisniÄko_ime> ",
"username_taken": "Ovo korisniÄko ime je veÄ‡ registrirano.",
"reg_complete": "Registracija zavrÅ¡ena. DobrodoÅ¡li na DeggioChat, {}!",
"usage_login": "Upotreba: /login <korisniÄko_ime> ",
"login_success": "Prijava uspjeÅ¡na. DobrodoÅ¡li na DeggioChat, {}!",
"invalid_creds": "NevaÅ¾eÄ‡i vjerodostojni podaci.",
"auth_required": "Morate se prvo autentificirati koristeÄ‡i /login ili /register.",
"self_request": "Ne moÅ¾ete poslati zahtjev za chat sami sebi.",
"user_not_found": "Korisnik '{}' ne postoji.",
"already_friends": "VeÄ‡ imate aktivan chat s {}.",
"req_sent": "Zahtjev za chat poslan korisniku {}.",
"incoming_req": "ðŸ“© Primili ste zahtjev za chat od {}. UpiÅ¡ite '/chatrequest accept {}' za prihvaÄ‡anje.",
"already_pending": "VeÄ‡ imate zahtjev na Äekanju poslan korisniku {}.",
"req_accepted": "Zahtjev za chat prihvaÄ‡en. Sada moÅ¾ete chatati s {}.",
"req_accepted_notify": "âœ… {} je prihvatio vaÅ¡ zahtjev za chat! UpiÅ¡ite '/chat {}' za poÄetak razgovora.",
"no_req_found": "Nemate zahtjeva na Äekanju od korisnika {}.",
"req_denied": "Zahtjev za chat od korisnika {} odbijen.",
"req_denied_notify": "âŒ {} je odbio vaÅ¡ zahtjev za chat.",
"syntax_request": "SintaktiÄka pogreÅ¡ka. Koristite /chatrequest <accept/deny> <korisniÄko_ime>",
"usage_request": "Upotreba: /chatrequest <korisniÄko_ime> ILI /chatrequest <accept/deny> <korisniÄko_ime>",
"active_chats": "VaÅ¡i aktivni chatovi: {}",
"no_active_chats": "Nema ih. PoÅ¡aljite zahtjev koristeÄ‡i /chatrequest",
"enter_chat": "UÅ¡li ste u fokusirani chat s korisnikom {}. Poruke upisujte izravno. UpiÅ¡ite /exit za izlaz.",
"not_allowed_chat": "Nemate dopuÅ¡tenje za chat s korisnikom {}. Prvo poÅ¡aljite zahtjev.",
"chat_removed": "Veza za chat s korisnikom {} uspjeÅ¡no uklonjena.",
"chat_removed_notify": "ðŸ—‘ï¸ {} je uklonio zajedniÄku chat sobu s vama.",
"usage_chat": "Upotreba: /chat <korisniÄko_ime>, /chat list, ILI /chat <korisniÄko_ime> delete",
"user_offline": "Korisnik {} je trenutno izvan mreÅ¾e.",
"no_permission_msg": "Nemate dopuÅ¡tenje za slanje poruka ovom korisniku."
},
"sv": {
"unknown_cmd": "OkÃ¤nt kommando.",
"welcome_back": "VÃ¤lkommen tillbaka till DeggioChat, {}! Automatisk inloggning lyckades.",
"expired_token": "Ogiltig eller utgÃ¥ngen sessionstoken.",
"usage_register": "AnvÃ¤ndning: /register  <anvÃ¤ndarnamn> <lÃ¶senord>",
"username_taken": "Detta anvÃ¤ndarnamn Ã¤r redan registrerat.",
"reg_complete": "Registreringen klar. VÃ¤lkommen till DeggioChat, {}!",
"usage_login": "AnvÃ¤ndning: /login <anvÃ¤ndarnamn> <lÃ¶senord>",
"login_success": "Inloggning lyckades. VÃ¤lkommen till DeggioChat, {}!",
"invalid_creds": "Felaktiga inloggningsuppgifter.",
"auth_required": "Du mÃ¥ste autentisera dig fÃ¶rst med /login eller /register.",
"self_request": "Du kan inte skicka en chatta-fÃ¶rfrÃ¥gan till dig sjÃ¤lv.",
"user_not_found": "AnvÃ¤ndaren '{}' finns inte.",
"already_friends": "Du har redan en aktiv chatt med {}.",
"req_sent": "Chatta-fÃ¶rfrÃ¥gan skickad till {}.",
"incoming_req": "ðŸ“© Du har fÃ¥tt en chatta-fÃ¶rfrÃ¥gan frÃ¥n {}. Skriv '/chatrequest accept {}' fÃ¶r att godkÃ¤nna.",
"already_pending": "Du har redan en vÃ¤ntande fÃ¶rfrÃ¥gan skickad till {}.",
"req_accepted": "Chatta-fÃ¶rfrÃ¥gan godkÃ¤nd. Du kan nu chatta med {}.",
"req_accepted_notify": "âœ… {} godkÃ¤nde din chatta-fÃ¶rfrÃ¥gan! Skriv '/chat {}' fÃ¶r att bÃ¶rja prata.",
"no_req_found": "Du har inga vÃ¤ntande fÃ¶rfrÃ¥gningar frÃ¥n {}.",
"req_denied": "Chatta-fÃ¶rfrÃ¥gan frÃ¥n {} avvisad.",
"req_denied_notify": "âŒ {} avvisade din chatta-fÃ¶rfrÃ¥gan.",
"syntax_request": "Syntaxfel. AnvÃ¤nd /chatrequest <accept/deny> <anvÃ¤ndarnamn>",
"usage_request": "AnvÃ¤ndning: /chatrequest <anvÃ¤ndarnamn> ELLER /chatrequest <accept/deny> <anvÃ¤ndarnamn>",
"active_chats": "Dina aktiva chattar: {}",
"no_active_chats": "Inga. Skicka fÃ¶rfrÃ¥gningar med /chatrequest",
"enter_chat": "Gick in i fokus-chatt med {}. Skriv dina meddelanden direkt. Skriv /exit fÃ¶r att lÃ¤mna.",
"not_allowed_chat": "Du har inte tillÃ¥telse at chatta med {}. Skicka en fÃ¶rfrÃ¥gan fÃ¶rst.",
"chat_removed": "Chattrelationen med {} har tagits bort.",
"chat_removed_notify": "ðŸ—‘ï¸ {} tog bort det gemensamma chattrummet med dig.",
"usage_chat": "AnvÃ¤ndning: /chat <anvÃ¤ndarnamn>, /chat list, ELLER /chat <anvÃ¤ndarnamn> delete",
"user_offline": "{} Ã¤r fÃ¶r nÃ¤rvarande offline.",
"no_permission_msg": "Du har inte behÃ¶righet att skicka meddelanden till denna anvÃ¤ndare."
},
"zh": {
"unknown_cmd": "æœªçŸ¥å‘½ä»¤ã€‚",
"welcome_back": "æ¬¢è¿Žå›žåˆ° DeggioChatï¼Œ{}ï¼è‡ªåŠ¨ç™»å½•æˆåŠŸã€‚",
"expired_token": "æ— æ•ˆæˆ–è¿‡æœŸçš„ä¼šè¯ä»¤ç‰Œã€‚",
"usage_register": "ç”¨æ³•: /register <ç”µå­é‚®ä»¶> <ç”¨æˆ·å> <å¯†ç >",
"username_taken": "è¯¥ç”¨æˆ·åå·²è¢«æ³¨å†Œã€‚",
"reg_complete": "æ³¨å†Œå®Œæˆã€‚æ¬¢è¿Žæ¥åˆ° DeggioChatï¼Œ{}ï¼",
"usage_login": "ç”¨æ³•: /login <ç”¨æˆ·å> <å¯†ç >",
"login_success": "ç™»å½•æˆåŠŸã€‚æ¬¢è¿Žæ¥åˆ° DeggioChatï¼Œ{}ï¼",
"invalid_creds": "å‡­æ®æ— æ•ˆã€‚",
"auth_required": "æ‚¨å¿…é¡»å…ˆä½¿ç”¨ /login æˆ– /register è¿›è¡Œèº«ä»½éªŒè¯ã€‚",
"self_request": "æ‚¨ cannot å‘è‡ªå·±å‘é€èŠå¤©è¯·æ±‚ã€‚",
"user_not_found": "ç”¨æˆ· '{}' ä¸å­˜åœ¨ã€‚",
"already_friends": "æ‚¨å·²ä¸Ž {} å»ºç«‹äº†æ´»è·ƒèŠå¤©ã€‚",
"req_sent": "èŠå¤©è¯·æ±‚å·²å‘é€è‡³ {}ã€‚",
"incoming_req": "ðŸ“© æ‚¨æ”¶åˆ°äº†æ¥è‡ª {} çš„èŠå¤©è¯·æ±‚ã€‚è¾“å…¥ '/chatrequest accept {}' ä»¥æŽ¥å—ã€‚",
"already_pending": "æ‚¨å·²å‘ {} å‘é€äº†æ­£åœ¨ç­‰å¾…å¤„ç†çš„è¯·æ±‚ã€‚",
"req_accepted": "èŠå¤©è¯·æ±‚å·²æŽ¥å—ã€‚æ‚¨çŽ°åœ¨å¯ä»¥ä¸Ž {} èŠå¤©äº†ã€‚",
"req_accepted_notify": "âœ… {} æŽ¥å—äº†æ‚¨çš„èŠå¤©è¯·æ±‚ï¼è¾“å…¥ '/chat {}' å¼€å§‹äº¤è°ˆã€‚",
"no_req_found": "æ‚¨æ²¡æœ‰æ¥è‡ª {} çš„å¾…å¤„ç†è¯·æ±‚ã€‚",
"req_denied": "æ¥è‡ª {} çš„èŠå¤©è¯·æ±‚å·²è¢«æ‹’ç»ã€‚",
"req_denied_notify": "âŒ {} æ‹’ç»äº†æ‚¨çš„èŠå¤©è¯·æ±‚ã€‚",
"syntax_request": "è¯­æ³•é”™è¯¯ã€‚ä½¿ç”¨ /chatrequest <accept/deny> <ç”¨æˆ·å>",
"usage_request": "ç”¨æ³•: /chatrequest <ç”¨æˆ·å> æˆ– /chatrequest <accept/deny> <ç”¨æˆ·å>",
"active_chats": "æ‚¨çš„æ´»è·ƒèŠå¤©: {}",
"no_active_chats": "æ— ã€‚ä½¿ç”¨ /chatrequest å‘é€è¯·æ±‚",
"enter_chat": "å·²è¿›å…¥ä¸Ž {} çš„ä¸“æ³¨èŠå¤©ã€‚ç›´æŽ¥è¾“å…¥æ‚¨çš„æ¶ˆæ¯ã€‚è¾“å…¥ /exit é€€å‡ºã€‚",
"not_allowed_chat": "æ‚¨æœªè¢«å…è®¸ä¸Ž {} èŠå¤©ã€‚è¯·å…ˆå‘é€è¯·æ±‚ã€‚",
"chat_removed": "ä¸Ž {} çš„èŠå¤©å…³ç³»å·²æˆåŠŸåˆ é™¤ã€‚",
"chat_removed_notify": "ðŸ—‘ï¸ {} åˆ æŽ‰äº†ä¸Žæ‚¨çš„å…±äº«èŠå¤©å®¤ã€‚",
"usage_chat": "ç”¨æ³•: /chat <ç”¨æˆ·å>, /chat list, æˆ– /chat <ç”¨æˆ·å> delete",
"user_offline": "{} å½“å‰å¤„äºŽç¦»çº¿çŠ¶æ€ã€‚",
"no_permission_msg": "æ‚¨æ²¡æœ‰ç»™è¯¥ç”¨æˆ·å‘é€æ¶ˆæ¯çš„æƒé™ã€‚"
}
}

def get_msg(lang, key, *args):
    if not isinstance(lang, str) or lang not in LOCALIZATION:
        lang = "en"
    template = LOCALIZATION[lang].get(key, LOCALIZATION["en"].get(key, key))
    return template.format(*args)


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT NOT NULL, salt TEXT NOT NULL, password_hash TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES users(username))")
        conn.execute("CREATE TABLE IF NOT EXISTS chat_requests (sender TEXT NOT NULL, receiver TEXT NOT NULL, PRIMARY KEY (sender, receiver))")
        conn.execute("CREATE TABLE IF NOT EXISTS approved_chats (user1 TEXT NOT NULL, user2 TEXT NOT NULL, PRIMARY KEY (user1, user2))")


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return digest, salt


def send_to_socket(client_socket, data_dict):
    client_socket.sendall((json.dumps(data_dict, ensure_ascii=False) + "\n").encode("utf-8"))


def broadcast_to_user(username, data_dict):
    with lock:
        client_socket = online_clients.get(username)
        if client_socket is None:
            return False
        try:
            send_to_socket(client_socket, data_dict)
            return True
        except OSError:
            if online_clients.get(username) is client_socket:
                del online_clients[username]
            return False


def handle_client(client_socket):
    current_user = None
    buffer = ""
    try:
        with sqlite3.connect(DB_FILE) as db:
            db.execute("PRAGMA foreign_keys = ON")
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                try:
                    buffer += data.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(payload, dict):
                        continue
                    command = payload.get("command")
                    args = payload.get("args", [])
                    if not isinstance(args, list):
                        args = []
                    lang = payload.get("lang", "en")
                    if not isinstance(lang, str):
                        lang = "en"
                    lang = lang.lower()
                    response = None

                    if command == "token_login":
                        token = args[0] if args and isinstance(args[0], str) else ""
                        row = db.execute("SELECT username FROM sessions WHERE token = ?", (token,)).fetchone()
                        if row:
                            current_user = row[0]
                            with lock:
                                online_clients[current_user] = client_socket
                                count_online = len(online_clients)
                            response = {"status": "success", "action": "login", "username": current_user,
                                        "message": get_msg(lang, "welcome_back", current_user),
                                        "show_motd": True, "online_count": count_online}
                        else:
                            response = {"status": "fail", "message": get_msg(lang, "expired_token")}

                    elif command == "register":
                        if len(args) < 3:
                            response = {"status": "error", "message": get_msg(lang, "usage_register")}
                        else:
                            email, username, password = args[:3]
                            if not all(isinstance(v, str) and v for v in (email, username, password)):
                                response = {"status": "error", "message": get_msg(lang, "usage_register")}
                            elif db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
                                response = {"status": "error", "message": get_msg(lang, "username_taken")}
                            else:
                                password_hash, salt = hash_password(password)
                                token = secrets.token_hex(32)
                                db.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, email, salt, password_hash))
                                db.execute("INSERT INTO sessions VALUES (?, ?)", (token, username))
                                current_user = username
                                with lock:
                                    online_clients[username] = client_socket
                                    count_online = len(online_clients)
                                response = {"status": "success", "action": "auth", "token": token,
                                            "username": username, "message": get_msg(lang, "reg_complete", username),
                                            "show_motd": True, "online_count": count_online}

                    elif command == "login":
                        if len(args) < 2:
                            response = {"status": "error", "message": get_msg(lang, "usage_login")}
                        else:
                            username, password = args[:2]
                            row = db.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,)).fetchone()
                            if row and isinstance(password, str):
                                check_hash, _ = hash_password(password, row[1])
                            else:
                                check_hash = None
                            if row and check_hash == row[0]:
                                token = secrets.token_hex(32)
                                db.execute("INSERT INTO sessions VALUES (?, ?)", (token, username))
                                current_user = username
                                with lock:
                                    online_clients[username] = client_socket
                                    count_online = len(online_clients)
                                response = {"status": "success", "action": "auth", "token": token,
                                            "username": username, "message": get_msg(lang, "login_success", username),
                                            "show_motd": True, "online_count": count_online}
                            else:
                                response = {"status": "error", "message": get_msg(lang, "invalid_creds")}

                    elif not current_user:
                        response = {"status": "error", "message": get_msg(lang, "auth_required")}

                    elif command == "chatrequest":
                        if len(args) == 1 and isinstance(args[0], str):
                            target = args[0]
                            exists = db.execute("SELECT 1 FROM users WHERE username = ?", (target,)).fetchone()
                            friends = db.execute("SELECT 1 FROM approved_chats WHERE (user1=? AND user2=?) OR (user1=? AND user2=?)",
                                                 (current_user, target, target, current_user)).fetchone()
                            if target == current_user:
                                response = {"status": "error", "message": get_msg(lang, "self_request")}
                            elif not exists:
                                response = {"status": "error", "message": get_msg(lang, "user_not_found", target)}
                            elif friends:
                                response = {"status": "error", "message": get_msg(lang, "already_friends", target)}
                            else:
                                try:
                                    db.execute("INSERT INTO chat_requests VALUES (?, ?)", (current_user, target))
                                    response = {"status": "info", "message": get_msg(lang, "req_sent", target)}
                                    broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "incoming_req", current_user, current_user)})
                                except sqlite3.IntegrityError:
                                    response = {"status": "error", "message": get_msg(lang, "already_pending", target)}
                        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
                            sub_cmd, target = args[0].lower(), args[1]
                            has_request = db.execute("SELECT 1 FROM chat_requests WHERE sender=? AND receiver=?", (target, current_user)).fetchone()
                            if sub_cmd in ("accept", "deny") and has_request:
                                db.execute("DELETE FROM chat_requests WHERE sender=? AND receiver=?", (target, current_user))
                                if sub_cmd == "accept":
                                    first, second = sorted((current_user, target))
                                    db.execute("INSERT OR IGNORE INTO approved_chats VALUES (?, ?)", (first, second))
                                    response = {"status": "success", "message": get_msg(lang, "req_accepted", target)}
                                    broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "req_accepted_notify", current_user, current_user)})
                                else:
                                    response = {"status": "info", "message": get_msg(lang, "req_denied", target)}
                                    broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "req_denied_notify", current_user)})
                            elif sub_cmd in ("accept", "deny"):
                                response = {"status": "error", "message": get_msg(lang, "no_req_found", target)}
                            else:
                                response = {"status": "error", "message": get_msg(lang, "syntax_request")}
                        else:
                            response = {"status": "error", "message": get_msg(lang, "usage_request")}

                    elif command == "chat":
                        if len(args) == 1 and isinstance(args[0], str):
                            target = args[0]
                            if target.lower() == "list":
                                rows = db.execute("SELECT user2 FROM approved_chats WHERE user1=? UNION SELECT user1 FROM approved_chats WHERE user2=?", (current_user, current_user)).fetchall()
                                chats = ", ".join(row[0] for row in rows) or get_msg(lang, "no_active_chats")
                                response = {"status": "info", "message": get_msg(lang, "active_chats", chats)}
                            else:
                                first, second = sorted((current_user, target))
                                allowed = db.execute("SELECT 1 FROM approved_chats WHERE user1=? AND user2=?", (first, second)).fetchone()
                                response = ({"status": "enter_chat", "target": target, "message": get_msg(lang, "enter_chat", target)}
                                            if allowed else {"status": "error", "message": get_msg(lang, "not_allowed_chat", target)})
                        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str) and args[1].lower() == "delete":
                            target = args[0]
                            first, second = sorted((current_user, target))
                            exists = db.execute("SELECT 1 FROM approved_chats WHERE user1=? AND user2=?", (first, second)).fetchone()
                            if exists:
                                db.execute("DELETE FROM approved_chats WHERE user1=? AND user2=?", (first, second))
                                response = {"status": "success", "message": get_msg(lang, "chat_removed", target)}
                                broadcast_to_user(target, {"type": "notification", "message": get_msg(lang, "chat_removed_notify", current_user)})
                            else:
                                response = {"status": "error", "message": get_msg(lang, "no_req_found", target)}
                        else:
                            response = {"status": "error", "message": get_msg(lang, "usage_chat")}

                    elif command == "msg":
                        if len(args) < 2 or not isinstance(args[0], str):
                            continue
                        target = args[0]
                        message = " ".join(str(part) for part in args[1:])
                        first, second = sorted((current_user, target))
                        allowed = db.execute("SELECT 1 FROM approved_chats WHERE user1=? AND user2=?", (first, second)).fetchone()
                        if allowed and broadcast_to_user(target, {"type": "msg", "from": current_user, "message": message}):
                            response = {"status": "msg_sent"}
                        elif allowed:
                            response = {"status": "error", "message": get_msg(lang, "user_offline", target)}
                        else:
                            response = {"status": "error", "message": get_msg(lang, "no_permission_msg")}
                    else:
                        response = {"status": "error", "message": get_msg(lang, "unknown_cmd")}

                    if response is not None:
                        send_to_socket(client_socket, response)
    except (OSError, sqlite3.Error):
        pass
    finally:
        with lock:
            if current_user and online_clients.get(current_user) is client_socket:
                del online_clients[current_user]
        try:
            client_socket.close()
        except OSError:
            pass


def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"DeggioChat server listening on {HOST}:{PORT}...")
    try:
        while True:
            client_socket, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down server.")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
