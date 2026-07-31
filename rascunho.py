import os

from dotenv import load_dotenv
from controller import UCS_Client

load_dotenv()
client = UCS_Client()
client.set_login_details(os.getenv("USERNAME"), os.getenv("PASSWORD"))
client.login()
print(client.get_login_profile())
segmentos = client.get_segmentos()
print(segmentos)
ambientes = client.get_ambientes("graduacao")
print(ambientes)

for semestre in ambientes:
    print(semestre["agrupador"])
    for turma in semestre["itens"]:
        print(" -", turma["nome"])
        print(turma)

participantes = client.get_participantes(
    "graduacao",
    "20264FBX4039A",
)
print(participantes)
for grupo in participantes:
    print(grupo["grupo"]["descricao"])

    for pessoa in grupo["participantes"]:
        print("  ", pessoa["nome_pessoa"])
        print("  ", pessoa["username"], "@ucs.br")
        print("  ", pessoa["foto"])
        print("  ", pessoa["codigo_pessoa"])
