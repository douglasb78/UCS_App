import random
import time

import requests

class UCS_Client():
    def __init__(self):
        self.debug = False
        self.api_url = "https://sou.ucs.br/api"
        self.nephalem_url = "https://auth.ucs.br"
        self.versao_app = "3.3.0"
        self.ga_id = "UA-77518593-1"
        self.selfgcm_sender_id = "956362207129"
        self.nome_do_app = "UCS Ensino"
        self.nome_push = "APP_UCSDISCIPLINAS"
        self.token = ""
        self.username = ""
        self.password = ""
        self.session = requests.Session()
    def __delay(self):
        delay = random.uniform(0.5, 1.0)
        delay = 0
        time.sleep(delay)
    def get(self, url, **kwargs):
        self.__delay()
        return self.session.get(url, **kwargs)
    def post(self, url, **kwargs):
        self.__delay()
        return self.session.post(url, **kwargs)
    def login(self):
        url = f"{self.nephalem_url}/auth-token/api-token-auth/"
        payload = {
            "username": self.username,
            "password": self.password
        }
        r = self.post(url, json=payload)
        r.raise_for_status()
        self.token = r.json()["token"]
        self.session.headers.update({
            "Authorization": f"Token {self.token}"
        })
        return self.token
    def set_login_details(self, username: str, password: str):
        self.username = username
        self.password = password
        return
    def get_login_profile(self):
        url = f"{self.api_url}/v1/auth/get-dados-usuario-logado/"
        return self.get(url).json()
        # {"username":"dbiazus1","foto":"https://ucsvirtual.ucs.br/pagina_pessoal/dbiazus1/foto/mostrar/foto.jpg","first_name":"Douglas","last_name":"Biazus","email":"dbiazus1@ucs.br"}
    def get_segmentos(self):
        url = f"{self.api_url}/v1/ambientes/segmentos/"
        return self.get(url).json()
        #[{"url":"graduacao","ferramentas_comuns":[],"nome":"Graduação"}]
    def get_segmentos_detalhe(self, segmento):
        url = f"{self.api_url}/v1/ambientes/segmentos/{segmento}/"
        return self.get(url).json()
        # parece ter sido implementado de forma redundante
        #{"url":"graduacao","ferramentas_comuns":[],"nome":"Graduação"}
    def get_destaques(self):
        url = f"{self.api_url}/v1/ambientes/segmentos/retornar-destaques/"
        return self.post(url, json={}).json()
        # não é usado no aplicativo
        #[]
    def get_ambientes(self, segmento):
        url = (
            f"{self.api_url}/v1/ambientes/segmentos/"
            f"{segmento}/ambientes/?com_cache=false"
        )
        return self.get(url).json()
    def get_docentes_nome(self, ambiente):
        lista_participantes = self.get_participantes("graduacao", ambiente["url"])
        nome = ""
        for professor in lista_participantes[0]["participantes"]:
            if nome:
                nome += ", "
            nome += professor["nome_pessoa"]
        return nome
    def get_numero_alunos_ambiente(self, ambiente):
        lista_participantes = self.get_participantes("graduacao", ambiente["url"])
        return len(lista_participantes[1]["participantes"])
    def get_participantes(self, segmento, ambiente):
        url = (
            f"{self.api_url}/v1/ambientes/segmentos/"
            f"{segmento}/ambientes/{ambiente}/"
            "ferramentas/listagem-participantes/"
        )
        return self.get(url).json()

