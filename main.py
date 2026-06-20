import os
from dotenv import load_dotenv
load_dotenv()
from backend import db
import flet as ft
from frontend.views.login_view import vista_login
from frontend.views.register_view import vista_register
from frontend.views.home_view import vista_home

def main(pagina:ft.Page)->None:
    pagina.title="LimaPay - Billetera de Movilidad"
    pagina.padding=0
    pagina.window.width=420
    pagina.window.height=860
    pagina.window.min_width=360
    estado={"oscuro":True,"ruta":"login","datos_pasajero":None}

    def repintar():
        pagina.controls.clear()
        if estado["ruta"]=="login":
            vista=vista_login(pagina,estado["oscuro"],al_iniciar_sesion=ir_a_home,al_ir_registro=ir_a_registro)
        elif estado["ruta"]=="registro":
            vista=vista_register(pagina,estado["oscuro"],al_registro_exitoso=ir_a_login,al_volver_login=ir_a_login)
        elif estado["ruta"]=="home":
            vista=vista_home(pagina,estado["oscuro"],estado["datos_pasajero"],al_cerrar_sesion=ir_a_login)
        pagina.add(vista)
        pagina.update()

    def ir_a_login(e=None):
        estado["ruta"]="login"
        estado["datos_pasajero"]=None
        repintar()

    def ir_a_registro(e=None):
        estado["ruta"]="registro"
        repintar()

    def ir_a_home(datos_pasajero:dict):
        estado["ruta"]="home"
        estado["datos_pasajero"]=datos_pasajero
        repintar()

    repintar()

if __name__=="__main__":
    ft.app(target=main)