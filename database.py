import psycopg2
from datetime import datetime
import csv
import os

DB_CONFIG = {
    "dbname": "mydatabase",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def ajouter_utilisateur(login, hashed_password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (login, password_hash, failed_attempts, is_admin) VALUES (%s, %s, 0, FALSE)",
            (login, hashed_password)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur insertion: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def recuperer_utilisateur(login):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, login, password_hash, failed_attempts, lock_until, created_at, is_admin 
        FROM users 
        WHERE login = %s
    """, (login,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_account(login, nb_echecs, lock_until=None, reset_lock=False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if reset_lock:
            cur.execute(
                "UPDATE users SET failed_attempts = 0, lock_until = NULL WHERE login = %s",
                (login,)
            )
        else:
            cur.execute(
                "UPDATE users SET failed_attempts = %s, lock_until = %s WHERE login = %s",
                (nb_echecs, lock_until, login)
            )
        conn.commit()
    except Exception as e:
        print(f"Erreur update echecs: {e}")
    finally:
        cur.close()
        conn.close()

def logger_evenement(login, action, client_ip, statut, detail=""):
    fichier_log = "data/journal.csv"
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    en_tete = ["horodatage", "login", "action", "statut", "detail"]
    nouveau_fichier = not os.path.exists(fichier_log)
    
    try:
        with open(fichier_log, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if nouveau_fichier:
                writer.writerow(en_tete)
            
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([horodatage, login, action, statut, f"IP:{client_ip} | {detail}"])
    except Exception as e:
        print(f"Erreur lors de l'écriture du log : {e}")
