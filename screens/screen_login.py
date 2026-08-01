import tkinter as tk
from tkinter import messagebox

from controller import UCS_Client

class ScreenLogin:
    def __init__(self, cliente: UCS_Client):
        # Cliente
        self.cliente = cliente
        self.resultado = None

        # Janela
        self.janela = tk.Tk()
        self.janela.title("Login")
        self.janela.geometry("300x180")
        self.janela.resizable(False, False)

        # Usuário
        tk.Label(self.janela, text="Login").pack(pady=(15, 5))
        self.entry_usuario = tk.Entry(self.janela, width=30)
        self.entry_usuario.pack()

        # Senha
        tk.Label(self.janela, text="Senha").pack(pady=(10, 5))
        self.entry_senha = tk.Entry(self.janela, show="*", width=30)
        self.entry_senha.pack()

        # Botão
        tk.Button(self.janela, text="Login", command=self.fazer_login, width=15).pack(pady=15)

        # Permite pressionar Enter para logar
        self.janela.bind("<Return>", lambda event: self.fazer_login())
        self.entry_usuario.focus()

    def fazer_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        self.cliente.set_login_details(usuario, senha)
        try:
            self.resultado = self.cliente.login()
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.janela.destroy()  # Fecha a janela
        except Exception as err:
            print(err)
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            self.entry_senha.delete(0, tk.END)
            self.entry_senha.focus()
    def executar(self):
        self.janela.mainloop()
        return self.resultado