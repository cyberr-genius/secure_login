import subprocess
import time
import sys
import os

def lancer_projet():

    try:
        serveur_process = subprocess.Popen([sys.executable, "server.py"])
    except FileNotFoundError:
        print("Erreur : Le fichier server.py est introuvable.")
        return

    time.sleep(2)

    print("[2/2] Ouverture de l'interface client...")
    try:
        subprocess.run([sys.executable, "client.py"])
    except FileNotFoundError:
        print("Erreur : Le fichier client.py est introuvable.")
    finally:
        print("\n[*] Fermeture du système...")
        serveur_process.terminate()
        print("[*] Serveur arrêté")

if __name__ == "__main__":
    if not os.path.exists("certs"):
        print(" Le dossier 'certs' est manquant !")
    
    lancer_projet()
