from controller import UCS_Client
from screens.screen_login import ScreenLogin
from screens.screen_classrooms import ScreenClassrooms

client = UCS_Client()
janela_login = ScreenLogin(client)
token = janela_login.executar()

if token:
    janela_turmas = ScreenClassrooms(client)
    janela_turmas.executar()