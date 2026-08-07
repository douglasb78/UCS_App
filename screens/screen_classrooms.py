import os
import tkinter as tk
from tkinter import ttk

from controller import UCS_Client
from dotenv import load_dotenv

from screens.screen_participants import ScreenParticipants


class ScreenClassrooms:
    def __init__(self, client: UCS_Client):
        self.janela = tk.Tk()
        self.janela.title("Portal")
        self.janela.geometry("1100x800")

        self.client = client
        self.self_profile = client.get_login_profile()

        frame_usuario = ttk.Frame(self.janela, padding=10)
        frame_usuario.pack(fill="x")

        # Nome aluno:
        ttk.Label(
            frame_usuario,
            text=f"{self.self_profile["first_name"]} {self.self_profile["last_name"]}",
            font=("Arial", 16, "bold")
        ).pack(anchor="w")

        semestres = client.get_ambientes("graduacao")
        #[{'itens': [{'url': '20264FBX4039A', 'horarios': '28-29', 'codigo': 'FBX4039A', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Arquitetura de Computadores'}, {'url': '20264CIC4003A', 'horarios': '68-69', 'codigo': 'CIC4003A', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Complexidade de Algoritmos'}, {'url': '20264FBI4020A', 'horarios': '58-59', 'codigo': 'FBI4020A', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Fundamentos de Redes de Computadores'}], 'agrupador': '2026/4'}, {'itens': [{'url': '20262CIC4006A', 'horarios': '38-39', 'codigo': 'CIC4006A', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Computação Aplicada II'}, {'url': '20262ADS3006A', 'horarios': '58-59', 'codigo': 'ADS3006A', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Programação de Aplicações Web II'}, {'url': '20262FBI4015AA', 'horarios': '68-69', 'codigo': 'FBI4015AA', 'ferramentas_comuns': [{'url': 'cronograma', 'nome': 'Cronograma'}, {'url': 'informacoes-turma', 'nome': 'Informações da Turma'}, {'url': 'listagem-participantes', 'nome': 'Listagem de Participantes'}, {'url': 'mural', 'nome': 'Mural'}, {'url': 'nivel-satisfacao', 'nome': 'Nível de Satisfação'}, {'url': 'notas', 'nome': 'Notas'}, {'url': 'registro-frequencia', 'nome': 'Registro de Frequência'}], 'nome': 'Programação para Dispositivos Móveis'}], 'agrupador': '2026/2'}]

        # Frame com scrollbar
        container = ttk.Frame(self.janela)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cria uma tabela para cada semestre
        for semestre in semestres:

            ttk.Label(
                scroll_frame,
                text=semestre["agrupador"],
                font=("Arial", 14, "bold")
            ).pack(anchor="w", pady=(15, 5))

            tree = self.criar_tabela(scroll_frame)

            for turma in semestre["itens"]:
                tree.insert("", tk.END, values=(
                    turma["codigo"],
                    turma["url"],
                    turma["nome"],
                    turma["horarios"],
                    self.client.get_docentes_nome(turma),
                    self.client.get_numero_alunos_ambiente(turma)
                ))

            tree.bind("<Double-1>", self.abrir_turma)

        ttk.Button(
            self.janela,
            text="Desconectar",
            command=self.desconectar
        ).pack(pady=20)

    def criar_tabela(self, parent):
        colunas = (
            "codigo",
            "url",
            "nome",
            "horarios",
            "professor",
            "numero_alunos"
        )

        tree = ttk.Treeview(
            parent,
            columns=colunas,
            show="headings",
            height=min(6, len(colunas))
        )

        tree.heading("codigo", text="Código")
        tree.heading("url", text="ID")
        tree.heading("nome", text="Nome da Disciplina")
        tree.heading("horarios", text="Horário")
        tree.heading("professor", text="Professor")
        tree.heading("numero_alunos", text="Número de Colegas")

        tree.column("codigo", width=120, anchor="center")
        tree.column("url", width=120, anchor="center")
        tree.column("nome", width=350)
        tree.column("horarios", width=90, anchor="center")
        tree.column("professor", width=220)
        tree.column("numero_alunos", width=150, anchor="center")

        tree.pack(fill="x", padx=10)

        return tree

    def abrir_turma(self, event):
        tree = event.widget
        item = tree.focus()

        if not item:
            return

        dados = tree.item(item)["values"]
        print(dados)
        codigo = dados[1]

        print(f"Abrir turma: {codigo}")
        janela_participantes = ScreenParticipants(client=self.client,codigo_disciplina=codigo)


    def desconectar(self):
        self.janela.destroy()
    def executar(self):
        self.janela.mainloop()
        self.janela.focus()
