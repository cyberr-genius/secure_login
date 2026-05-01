import bcrypt
import uuid
from datetime import datetime, timedelta
from database import ajouter_utilisateur, recuperer_utilisateur, update_account, logger_evenement

sessions_actives = {}

def debloquer_utilisateur_logique(target_login, client_ip):
    user = recuperer_utilisateur(target_login)
    
    if not user:
        return {"status": "error", "message": "Utilisateur introuvable"}

    if user[4] is None and user[3] == 0:
        return {"status": "info", "message": "L'utilisateur est déjà débloqué"}

    update_account(target_login, 0, reset_lock=True)
    logger_evenement("ADMIN", "UNBLOCK", client_ip, "SUCCES", f"Cible: {target_login}")
    
    return {"status": "success", "message": f"L'utilisateur {target_login} a été débloqué !"}

def inscrire_utilisateur(login, password, client_ip):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    succes = ajouter_utilisateur(login, hashed)
    
    if succes:
        logger_evenement(login, "INSCRIPTION", client_ip, "SUCCES")
        return {"status": "success", "message": "Inscription réussie !"}
    else:
        logger_evenement(login, "INSCRIPTION", client_ip, "ECHEC", "Login déjà utilisé ou erreur")
        return {"status": "error", "message": "Ce login est déjà utilisé"}

def verifier_connexion(login, password_clair, client_ip):
    user = recuperer_utilisateur(login)
    if not user:
        logger_evenement(login, "CONNEXION", client_ip, "ECHEC", "Utilisateur inconnu")
        return {"status": "error", "message": "Identifiants invalides"}

    try:
        db_id, db_login, db_hash, failed_attempts, lock_until, created_at, is_admin = user
    except ValueError:
        return {"status": "error", "message": "Erreur de structure de données serveur"}

    if lock_until and datetime.now() < lock_until:
        attente = (lock_until - datetime.now()).seconds
        return {"status": "error", "message": f"Compte bloqué. Réessayez dans {attente // 60}m {attente % 60}s."}

    if bcrypt.checkpw(password_clair.encode('utf-8'), db_hash.encode('utf-8')):
        update_account(login, 0, reset_lock=True)
        token = str(uuid.uuid4())
        sessions_actives[token] = {"login": login, "expiry": datetime.now() + timedelta(minutes=30)}
        logger_evenement(login, "CONNEXION", client_ip, "SUCCES", f"Token: {token[:8]}")
        
        return {
            "status": "success", 
            "message": f"Bienvenue {login}",
            "token": token,
            "is_admin": is_admin
        }
    else:
        nouveaux_echecs = failed_attempts + 1
        lock_time = None
        if nouveaux_echecs >= 3:
            lock_time = datetime.now() + timedelta(minutes=5)
            message = "Compte verrouillé pour 5 minutes."
        else:
            message = f"Mot de passe incorrect ({nouveaux_echecs}/3)"
            
        update_account(login, nouveaux_echecs, lock_until=lock_time)
        logger_evenement(login, "CONNEXION", client_ip, "ECHEC", f"Tentative {nouveaux_echecs}/3")
        return {"status": "error", "message": message}
