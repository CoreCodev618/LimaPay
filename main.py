import flet as ft
from frontend.views.login_view import vista_login

def main(page: ft.Page):
    #Configuracion de la pantalla 
    page.window.width=  400
    page.window.height = 800
    page.window.resizable = False
    page.title = 'LimaPay - Login'
    
    #Alineacion de los elementos
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    login = vista_login()
    page.add(login)
    
# Codigo para arrancar la app
if __name__ == "__main__":
    ft.app(target = main)