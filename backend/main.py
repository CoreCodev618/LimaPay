import os
from dotenv import load_dotenv
load_dotenv()

from backend import db,dao_pasajeros,dao_transacciones
import flet as ft
from frontend.views.login_view import LoginView

def main(page:ft.Page)->None:
    page.title="LimaPay - Billetera de Movilidad"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.bgcolor="#F5F5F5"
    page.window_width=400
    page.window_height=750
    
    LoginView(page).mostrar()

if __name__=="__main__":
    ft.app(target=main)
