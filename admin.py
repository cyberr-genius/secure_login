import tkinter as tk
from tkinter import ttk, messagebox
import json
import socket
import ssl
import os
import csv
from client import AuthApp, BG_COLOR, BTN_COLOR, TEXT_COLOR, SERVER_IP, SERVER_PORT

class AdminDashboard(AuthApp):
    def __init__(self, root):
        super().__init__(root)
        self.root.title("ONG SECURE - ADMINISTRATION")
        # Masquer le bouton d'inscription pour l'interface admin
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "S'inscrire":
                widget.pack_forget()

    def envoyer(self, action):
        try:
            login = self.entry_login.get()
            password = self.entry_password.get()
            captcha_user = self.entry_captcha.get()
        except AttributeError:
            messagebox.showerror("Erreur", "Champs d'entrée introuvables.")
            return

        if not captcha_user or captcha_user.upper() != self.captcha_code:
            messagebox.showerror("Erreur", "Captcha incorrect !")
            self.refresh_captcha()
            return

        if not login or not password:
            messagebox.showwarning("Attention", "Champs vides")
            return

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("certs/server.crt")
        context.check_hostname = False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = context.wrap_socket(sock, server_hostname="localhost")
            conn.connect((SERVER_IP, SERVER_PORT))

            donnees = {
                "action": action,
                "login": login,
                "password": password
            }
            conn.send(json.dumps(donnees).encode('utf-8'))

            rep_brute = conn.recv(1024).decode('utf-8')
            reponse = json.loads(rep_brute)

            if reponse["status"] == "success":
                if reponse.get("is_admin") is True:
                    self.open_success_page(login, reponse.get("token"))
                else:
                    messagebox.showerror("Accès Refusé", "Vous n'avez pas les droits administrateur.")
                    self.refresh_captcha()
            else:
                messagebox.showerror("Erreur", reponse["message"])
                self.refresh_captcha()

            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", f"Connexion impossible : {e}")

    def open_success_page(self, login, token):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.root.geometry("950x650")
        tk.Label(self.main_frame, text="dashboard admin", 
                 font=("Arial", 20, "bold"), fg="#5F9EA0", bg=BG_COLOR).pack(pady=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black", rowheight=25)
        style.configure("Treeview.Heading", background="#5F9EA0", foreground="white", font=('Arial', 10, 'bold'))

        table_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        table_frame.pack(fill="both", expand=True, padx=20)

        cols = ('Date', 'Utilisateur', 'Action', 'Statut', 'Détails')
        self.tree = ttk.Treeview(table_frame, columns=cols, show='headings', height=15)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        btn_frame.pack(fill="x", pady=20, padx=20)

        tk.Button(btn_frame, text="🔄 Actualiser", command=self.charger_logs_interface,
                  bg="#5F9EA0", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side="left", padx=10)

        tk.Button(btn_frame, text=" Débloquer", command=self.debloquer_selection,
                  bg="#5F9EA0", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Quitter", command=self.root.quit,
                  bg="#d9534f", fg="white", font=("Arial", 10, "bold"), padx=15).pack(side="right", padx=10)

        self.charger_logs_interface()

    def charger_logs_interface(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if os.path.exists("data/journal.csv"):
            try:
                with open("data/journal.csv", "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    lignes = list(reader)
                    for row in reversed(lignes[-50:]):
                        self.tree.insert("", "end", values=row)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def debloquer_selection(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une ligne dans le tableau")
            return
        
        target = self.tree.item(selected)['values'][1]
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("certs/server.crt")
        context.check_hostname = False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = context.wrap_socket(sock, server_hostname="localhost")
            conn.connect((SERVER_IP, SERVER_PORT))
            conn.send(json.dumps({"action": "unblock", "target": target}).encode('utf-8'))
            rep = json.loads(conn.recv(1024).decode('utf-8'))
            
            if rep["status"] in ["success", "info"]:
                messagebox.showinfo("Succès", rep["message"])
                self.charger_logs_interface()
            else:
                messagebox.showerror("Erreur", rep["message"])
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", f"Action impossible : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()
