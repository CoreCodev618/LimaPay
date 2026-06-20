import flet as ft

from frontend.tema.temas import obtener_paleta, COLOR_PRIMARIO
from frontend.views.login_view import vista_login
from frontend.views.register_view import vista_register
from frontend.views.home_view import vista_home
from frontend.views.scanner_view import vista_scanner
from frontend.views.recarga_view import vista_recarga
from frontend.views.historial_view import vista_historial
from frontend.views.dashboard_view import vista_dashboard

def main(pagina: ft.Page):
    # ---------- Configuración Base ----------
    pagina.title = "LimaPay"
    pagina.padding = 0
    pagina.window.width = 420
    pagina.window.height = 800
    pagina.window.min_width = 360

    # Estado global de la aplicación
    estado = {
        "oscuro": True, 
        "ruta": "login", 
        "datos_pasajero": None
    }

    # ---------- AppBar Global ----------
    boton_tema = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_OUTLINED,
        icon_color=COLOR_PRIMARIO,
        tooltip="Cambiar tema",
        on_click=lambda e: alternar_tema(),
    )

    titulo_barra = ft.Text("LimaPay", weight=ft.FontWeight.BOLD)

    pagina.appbar = ft.AppBar(
        title=titulo_barra,
        center_title=False,
        actions=[boton_tema],
    )

    # ---------- Navegación ----------
    def ir_a_login(e=None):
        estado["ruta"] = "login"
        estado["datos_pasajero"] = None
        repintar()

    def ir_a_registro(e=None):
        estado["ruta"] = "registro"
        repintar()

    def ir_a_home(datos_pasajero: dict):
        estado["ruta"] = "home"
        estado["datos_pasajero"] = datos_pasajero
        repintar()

    def ir_a_scanner(e=None):
        estado["ruta"] = "scanner"
        repintar()

    def ir_a_recarga(e=None):
        estado["ruta"] = "recarga"
        repintar()
    
    def ir_a_historial(e=None):
        estado["ruta"] = "historial"
        repintar()
        
    def ir_a_dashboard(e=None):
        estado["ruta"] = "dashboard"
        repintar()
        
    # ---------- Motor de Redibujado ----------
    def alternar_tema():
        estado["oscuro"] = not estado["oscuro"]
        repintar()

    def repintar():
        paleta = obtener_paleta(estado["oscuro"])

        pagina.bgcolor = paleta["fondo_inicio"]
        pagina.appbar.bgcolor = paleta["tarjeta"]
        titulo_barra.color = paleta["texto_principal"]
        boton_tema.icon = ft.Icons.LIGHT_MODE_OUTLINED if estado["oscuro"] else ft.Icons.DARK_MODE_OUTLINED

        pagina.controls.clear()

        if estado["ruta"] == "login":
            vista = vista_login(pagina, estado["oscuro"], al_iniciar_sesion=ir_a_home, al_ir_registro=ir_a_registro)
        elif estado["ruta"] == "registro":
            vista = vista_register(pagina, estado["oscuro"], al_registro_exitoso=ir_a_login, al_volver_login=ir_a_login)
        elif estado["ruta"] == "home":
            vista = vista_home(pagina, estado["oscuro"], estado["datos_pasajero"], al_cerrar_sesion=ir_a_login, al_ir_scanner=ir_a_scanner, al_ir_recarga=ir_a_recarga,al_ir_historial=ir_a_historial, al_ir_dashboard=ir_a_dashboard)
        elif estado["ruta"] == "scanner":
            vista = vista_scanner(pagina, estado["oscuro"], estado["datos_pasajero"], al_volver_home=ir_a_home)
        elif estado["ruta"] == "recarga":
            vista = vista_recarga(pagina, estado["oscuro"], estado["datos_pasajero"],al_volver_home=ir_a_home)
        elif estado["ruta"] == "historial":
            vista = vista_historial(pagina, estado["oscuro"], estado["datos_pasajero"], al_volver_home=ir_a_home)
        elif estado["ruta"] == "dashboard":
            vista = vista_dashboard(pagina, estado["oscuro"], estado["datos_pasajero"], al_volver_home=ir_a_home)
        
        pagina.add(vista)
        pagina.update()

    repintar()

if __name__ == "__main__":
    ft.run(main, assets_dir="frontend/assets")