import json
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

from requests import Response

from controller import UCS_Client


class ScreenParticipants:
    def __init__(self, client: UCS_Client, codigo_disciplina: str):

        self.participantes = client.get_participantes("graduacao", codigo_disciplina)
        self.client = client
        self.nome_disciplina = 'a'
        self.semestre = 'b'
        self.professor = 'c'

        self.root = tk.Tk()
        self.root.title(f"{self.nome_disciplina} - {self.semestre}")
        self.root.geometry("700x600")
        self.root.minsize(600, 400)

        # ===== Cabeçalho =====
        frame_topo = ttk.Frame(self.root, padding=10)
        frame_topo.pack(fill="x")

        ttk.Label(frame_topo, text=f"Disciplina: {self.nome_disciplina}", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(frame_topo, text=f"Semestre: {self.semestre}", font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Label(frame_topo, text=f"Professor: {self.professor}", font=("Segoe UI", 11)).pack(anchor="w")

        ttk.Separator(self.root).pack(fill="x", pady=5)

        # ===== Área com scroll =====
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.frame_lista = ttk.Frame(canvas)

        self.frame_lista.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ===== Cabeçalho da tabela =====
        header = ttk.Frame(self.frame_lista)
        header.pack(fill="x", pady=(0, 5))

        ttk.Label(header, text="Avatar", width=6, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        ttk.Label(header, text="Nome", width=45, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        ttk.Label(header, text="E-mail", width=20, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        ttk.Separator(self.frame_lista).pack(fill="x", pady=3)

        # ===== Processar participantes =====
        print(self.participantes)
        participantes_array = []
        for grupo in self.participantes:
            for p in grupo["participantes"]:
                participantes_array.append(p)

        # Ordenar alfabeticamente pelo nome
        participantes_array.sort(key=lambda x: x["nome_pessoa"].lower())

        # Guardar referências das imagens (importante!)
        self.fotos = []

        # Criar as linhas
        for p in participantes_array:
            self._criar_linha(p)

        # ===== Botão Fechar =====
        frame_botao = ttk.Frame(self.root, padding=10)
        frame_botao.pack(fill="x")

        ttk.Button(frame_botao, text="Fechar", command=self.root.destroy, width=15).pack()

        self.root.mainloop()

    def _criar_linha(self, participante: dict):
        linha = ttk.Frame(self.frame_lista)
        linha.pack(fill="x", pady=2)

        # Foto 32x32
        foto_label = ttk.Label(linha, width=6)
        foto_label.pack(side="left", padx=5)

        # Carrega a foto em thread separada para não travar a interface
        threading.Thread(
            target=self._carregar_foto,
            args=(participante["foto"], foto_label),
            daemon=True
        ).start()

        # Nome
        ttk.Label(linha, text=participante["nome_pessoa"], width=45, anchor="w").pack(side="left", padx=5)

        # Username
        ttk.Label(linha, text=f"{participante["username"]}@ucs.br", width=20, anchor="w").pack(side="left", padx=5)

    def _carregar_foto(self, url: str, label: ttk.Label):
        try:
            print(url)
            response = self.client.request_photo(url, timeout=8)
            print(response)
            print(response.text)
            print(response.content)
            img = Image.open(BytesIO(response.content))
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(img)

            # Precisa manter a referência
            self.fotos.append(foto)
            label.configure(image=foto)
        except Exception as err:
            print(err)
            # Se falhar, deixa em branco ou coloca um placeholder
            label.configure(text="—")
