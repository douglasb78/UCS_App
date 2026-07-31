from controller import UCS_Client
from screens.screen_login import ScreenLogin

client = UCS_Client()
janela_login = ScreenLogin(client)
janela_login.executar()