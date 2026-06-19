import flet as ft

# Importaciones de vistas y temas
from frontend.tema.temas import obtener_paleta, COLOR_PRIMARIO
from frontend.views.login_view import vista_login
from frontend.views.register_view import vista_register
from frontend.views.home_view import vista_home

def main(pagina: ft.Page):
    # ---------- Configuración Base ----------
    pagina.title = "LimaPay"
    pagina.padding = 0
    pagina.window.width = 420
    pagina.window.height = 860
    pagina.window.min_width = 360
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

    # ---------- Motor de Redibujado (Tema y Rutas) ----------
    def alternar_tema():
        estado["oscuro"] = not estado["oscuro"]
        repintar()

    def repintar():
        # 1. Obtenemos los colores actuales
        paleta = obtener_paleta(estado["oscuro"])

        # 2. Actualizamos el chasis global (Fondo y AppBar)
        pagina.bgcolor = paleta["fondo_inicio"]
        pagina.appbar.bgcolor = paleta["tarjeta"]
        titulo_barra.color = paleta["texto_principal"]
        boton_tema.icon = ft.Icons.LIGHT_MODE_OUTLINED if estado["oscuro"] else ft.Icons.DARK_MODE_OUTLINED

        # 3. Limpiamos la pantalla
        pagina.controls.clear()

        # 4. Construimos la vista correspondiente según la ruta actual
        if estado["ruta"] == "login":
            vista = vista_login(pagina, estado["oscuro"], al_iniciar_sesion=ir_a_home, al_ir_registro=ir_a_registro)
        elif estado["ruta"] == "registro":
            vista = vista_register(pagina, estado["oscuro"], al_registro_exitoso=ir_a_login, al_volver_login=ir_a_login)
        elif estado["ruta"] == "home":
            vista = vista_home(pagina, estado["oscuro"], estado["datos_pasajero"], al_cerrar_sesion=ir_a_login)

        # 5. Agregamos la vista y forzamos la actualización visual
        pagina.add(vista)
        pagina.update()

    # Arrancamos la aplicación pintando la primera pantalla
    repintar()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="frontend/assets")