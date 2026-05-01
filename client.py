import socket
import ssl
import json
import random
import string
import tkinter as tk
from tkinter import messagebox

SERVER_IP = '0.0.0.0'
SERVER_PORT = 8086

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ONG SECURE LOGIN APP")
        self.root.geometry("400x580")
        self.root.configure(bg="#DEB887")

        self.captcha_code = ""
        self.main_frame = tk.Frame(root, bg="#DEB887" )
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.main_frame, text=" Connexion", font=("Arial", 20, "bold"), fg="#F0FFF0", bg="#DEB887").pack(pady=20)

        tk.Label(self.main_frame, text="Nom d'utilisateur", fg="#1a2238", bg="#DEB887").pack(anchor="w")
        self.entry_login = tk.Entry(self.main_frame, bg="white", fg="#1a2238",  borderwidth=0)
        self.entry_login.pack(fill="x", pady=5, ipady=8)

        tk.Label(self.main_frame, text="Mot de passe", fg="#1a2238", bg="#DEB887").pack(anchor="w", pady=(10,0))
        self.entry_password = tk.Entry(self.main_frame, show="*", bg="white", fg="#1a2238",  borderwidth=0)
        self.entry_password.pack(fill="x", pady=5, ipady=8)

        self.lbl_captcha = tk.Label(self.main_frame, text="", font=("Courier", 14, "bold italic"), 
                                    fg="white", bg="#DEB887")
        self.lbl_captcha.pack(pady=10, fill="x")
        self.refresh_captcha()

        tk.Label(self.main_frame, text="Recopiez le captcha ci-dessus", fg=TEXT_COLOR, bg=BG_COLOR).pack(anchor="w")
        self.entry_captcha = tk.Entry(self.main_frame, bg="#B0C4DE", fg="#1a2238", borderwidth=0)
        self.entry_captcha.pack(fill="x", pady=5, ipady=5)

        btn_style = {
            "bg": BTN_COLOR, 
            "fg": "#1a2238", 
            "font": ("Arial", 10, "bold"), 
            "borderwidth": 0, 
            "cursor": "hand2",
            "activebackground": "#f5d5b0"
        }
        
        tk.Button(self.main_frame, text="Se connecter", command=lambda: self.envoyer("login"), **btn_style).pack(fill="x", pady=(20, 10), ipady=10)
        tk.Button(self.main_frame, text="S'inscrire", command=lambda: self.envoyer("register"), **btn_style).pack(fill="x", ipady=10)

    def refresh_captcha(self):
        self.captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.lbl_captcha.config(text=f"  {self.captcha_code}  ")

    def open_success_page(self, login, token):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.main_frame, text=f"Bienvenue sur l'espace sécurisé {login}", 
                 font=("Arial", 16, "bold"), fg="white", bg="#DEB887", wraplength=300).pack(pady=50)
        
        tk.Label(self.main_frame, text=f"Votre token de session est : \n{token}\n\nCe token est valable 30mn si aucune activité n'est détectée.", 
                 font=("Arial", 9), fg="#1a2238", bg="#DEB887", wraplength=350).pack(pady=20)
        
        tk.Button(self.main_frame, text="Déconnexion", command=self.root.quit, 
                  bg="#d9534f", fg="white", borderwidth=0).pack(pady=20, ipady=5, ipadx=10)

    def envoyer(self, action):
        if self.entry_captcha.get().upper() != self.captcha_code:
            messagebox.showerror("Erreur", "Captcha incorrect !")
            self.refresh_captcha()
            return

        login = self.entry_login.get()
        password = self.entry_password.get()

        if not login or not password:
            messagebox.showwarning("Veuillez remplir tous les champs avant de  valider le formulaire")
            return

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("certs/server.crt")
        context.check_hostname = False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = context.wrap_socket(sock, server_hostname="localhost")
            conn.connect((SERVER_IP, SERVER_PORT))

            requete = {"action": action, "login": login, "password": password}
            conn.send(json.dumps(requete).encode('utf-8'))

            rep_brute = conn.recv(1024).decode('utf-8')
            reponse = json.loads(rep_brute)

            if reponse["status"] == "success":
                if action == "login":
                    self.open_success_page(login, reponse.get("token", "N/A"))
                else:
                    messagebox.showinfo("Succès", reponse["message"])
            else:
                messagebox.showerror("Erreur", reponse["message"])
                self.refresh_captcha()

        except Exception as e:
            messagebox.showerror( f"Nous n'arrivons pas a joindre le serveur patientez puis réessayez : {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()
