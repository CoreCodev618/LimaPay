import flet as ft

from frontend.tema.temas import obtener_paleta, COLOR_PRIMARIO
from frontend.views.login_view import vista_login
#from frontend.views.home_view import vista_home


def main(pagina: ft.Page):
    pagina.title = "LimaPay"
    pagina.padding = 0
    pagina.window.width = 420
    pagina.window.height = 860
    pagina.window.min_width = 360

    estado = {"oscuro": True, "datos_pasajero": None}

    # ---------- Botón de tema, vive en la barra superior (toda la app) ----------
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
    def ir_a_home(datos_pasajero: dict):
        estado["datos_pasajero"] = datos_pasajero
        repintar()

    def ir_a_login():
        estado["datos_pasajero"] = None
        repintar()

    def construir_vista_actual() -> ft.Container:
        if estado["datos_pasajero"] is None:
            return vista_login(pagina, estado["oscuro"], al_iniciar_sesion=ir_a_home)
        return vista_home(pagina, estado["oscuro"], estado["datos_pasajero"], al_cerrar_sesion=ir_a_login)

    # ---------- Tema ----------
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
        pagina.controls.append(construir_vista_actual())
        pagina.update()

    repintar()


if __name__ == "__main__":
    ft.run(main, assets_dir="frontend/assets")