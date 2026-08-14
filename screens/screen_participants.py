import queue
import threading
from io import BytesIO

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from controller import UCS_Client


class ScreenParticipants:
    def __init__(self, client: UCS_Client, codigo_disciplina: str,
                 nome_disciplina: str = "", semestre: str = "", professor: str = ""):

        self.client = client
        self.participantes = client.get_participantes("graduacao", codigo_disciplina)

        self.nome_disciplina = nome_disciplina
        self.semestre = semestre
        self.professor = professor

        self.root = tk.Tk()
        self.root.title(f"{self.nome_disciplina} - {self.semestre}")
        self.root.geometry("700x600")
        self.root.minsize(600, 400)

        # informações no topo da janela
        frame_topo = ttk.Frame(self.root, padding=10)
        frame_topo.pack(fill="x")

        ttk.Label(frame_topo, text=f"Disciplina: {self.nome_disciplina}", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(frame_topo, text=f"Semestre: {self.semestre}", font=("Segoe UI", 11)).pack(anchor="w")
        ttk.Label(frame_topo, text=f"Professor: {self.professor}", font=("Segoe UI", 11)).pack(anchor="w")

        ttk.Separator(self.root).pack(fill="x", pady=5)

        # parte que tme scroll
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

        # roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # cabeçalhos da tabela
        header = ttk.Frame(self.frame_lista)
        header.pack(fill="x", pady=(0, 5))

        ttk.Label(header, text="Avatar", width=6, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        ttk.Label(header, text="Nome", width=45, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        ttk.Label(header, text="E-mail", width=20, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

        ttk.Separator(self.frame_lista).pack(fill="x", pady=3)

        # para cada um dos alunos
        if self.client.debug:
            print(self.participantes)

        participantes_array = []
        for grupo in self.participantes:
            for p in grupo["participantes"]:
                participantes_array.append(p)

        # ordenar pelo nome
        participantes_array.sort(key=lambda x: x["nome_pessoa"].lower())

        self.fotos = []

        # criar fila para baixar as fotos
        self.fila_fotos = queue.Queue()
        self._worker_fotos_thread = threading.Thread(target=self._worker_fotos, daemon=True)
        self._worker_fotos_thread.start()

        # criar as linhas
        for p in participantes_array:
            self._criar_linha(p)

        # botão fechar
        frame_botao = ttk.Frame(self.root, padding=10)
        frame_botao.pack(fill="x")

        ttk.Button(frame_botao, text="Fechar", command=self.root.destroy, width=15).pack()

        self.root.mainloop()

    def _criar_linha(self, participante: dict):
        linha = ttk.Frame(self.frame_lista)
        linha.pack(fill="x", pady=2)

        # foto 32x32
        foto_label = ttk.Label(linha, width=6, text="…")
        foto_label.pack(side="left", padx=5)

        # fila para baixar as fotos
        self.fila_fotos.put((participante["foto"], foto_label))

        # nome + e-mail
        ttk.Label(linha, text=participante["nome_pessoa"], width=45, anchor="w").pack(side="left", padx=5)
        ttk.Label(linha, text=f"{participante['username']}@ucs.br", width=20, anchor="w").pack(side="left", padx=5)

    def _worker_fotos(self):
        # uma foto de cada vez para evitar spam
        while True:
            url, label = self.fila_fotos.get()
            try:
                self._baixar_foto(url, label)
            finally:
                self.fila_fotos.task_done()

    def _baixar_foto(self, url: str, label: ttk.Label):
        try:
            response = self.client.request_photo(url, timeout=8)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image"):
                raise ValueError(f"resposta não é imagem (Content-Type={content_type!r})")

            img = Image.open(BytesIO(response.content))
            img = img.resize((32, 32), Image.Resampling.LANCZOS)

            self.root.after(0, self._aplicar_foto, img, label)
        except Exception as err:
            if self.client.debug:
                print(f"[fotos] falha ao carregar {url}: {err}")
            self.root.after(0, lambda: label.configure(text="—"))

    def _aplicar_foto(self, img: Image.Image, label: ttk.Label):
        # roda na main thread já que é seguro para atualizar o widget.
        foto = ImageTk.PhotoImage(img, master=self.root)
        self.fotos.append(foto)
        label.configure(image=foto, text="")
