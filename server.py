import socket
import ssl
import threading
import json
from logic import verifier_connexion, inscrire_utilisateur, debloquer_utilisateur_logique

HOST = '0.0.0.0'
PORT = 8086

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")

def handle_client(conn_standard, client_ip):
    client_socket = None
    try:
        client_socket = context.wrap_socket(conn_standard, server_side=True)
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            return

        requete = json.loads(data)
        action = requete.get("action")
        login = requete.get("login")
        password = requete.get("password")

        if action == "login":
            reponse = verifier_connexion(login, password, client_ip)
        elif action == "register":
            reponse = inscrire_utilisateur(login, password, client_ip)
        elif action == "unblock":
            target = requete.get("target")
            reponse = debloquer_utilisateur_logique(target, client_ip)
        else:
            reponse = {"status": "error", "message": "Action inconnue"}

        client_socket.send(json.dumps(reponse).encode('utf-8'))

    except Exception as e:
        print(f"[ERREUR CLIENT] : {e}")
    finally:
        if client_socket:
            client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server.bind((HOST, PORT))
    server.listen(5)
    
    print(f"[*] Serveur actif sur {HOST}:{PORT}")
    print("[*] En attente de connexions...")

    while True:
        conn, addr = server.accept()
        client_ip = addr[0]  
        thread = threading.Thread(target=handle_client, args=(conn, client_ip))
        thread.start()

if __name__ == "__main__":
    main()
