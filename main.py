import flet as ft

from frontend.tema.temas import obtener_paleta, COLOR_PRIMARIO
from frontend.views.login_view import vista_login
from frontend.views.register_view import vista_register
from frontend.views.recuperar_clave_view import vista_recuperar_clave
from frontend.views.home_view import vista_home
from frontend.views.scanner_view import vista_scanner
from frontend.views.recarga_view import vista_recarga
from frontend.views.historial_view import vista_historial
from frontend.views.dashboard_view import vista_dashboard
from frontend.views.perfil_view import vista_perfil


def main(pagina: ft.Page):
    pagina.title = "LimaPay"
    pagina.padding = 0
    pagina.window.width = 420
    pagina.window.height = 800
    pagina.window.min_width = 360

    estado = {"oscuro": True, "ruta": "login", "datos_pasajero": None}

    boton_tema = ft.IconButton(icon=ft.Icons.LIGHT_MODE_OUTLINED, icon_color=COLOR_PRIMARIO,
                                tooltip="Cambiar tema", on_click=lambda e: alternar_tema())
    titulo_barra = ft.Text("LimaPay", weight=ft.FontWeight.BOLD)
    pagina.appbar = ft.AppBar(title=titulo_barra, center_title=False, actions=[boton_tema])

    # ---------- Navegación ----------
    def navegar(ruta: str, **datos):
        estado["ruta"] = ruta
        estado.update(datos)
        repintar()

    def ir_a_login(e=None):
        navegar("login", datos_pasajero=None)

    def ir_a_home(datos_pasajero: dict):
        navegar("home", datos_pasajero=datos_pasajero)

    # ---------- Tema ----------
    def alternar_tema():
        estado["oscuro"] = not estado["oscuro"]
        repintar()

    # ---------- Mapa de rutas: ruta -> función constructora de vista ----------
    def construir_vista():
        dp = estado["datos_pasajero"]
        oscuro = estado["oscuro"]
        rutas = {
            "login": lambda: vista_login(pagina, oscuro, al_iniciar_sesion=ir_a_home,
                                          al_ir_registro=lambda: navegar("registro"),
                                          al_ir_recuperar=lambda: navegar("recuperar")),
            "registro": lambda: vista_register(pagina, oscuro, al_registro_exitoso=ir_a_login, al_volver_login=ir_a_login),
            "recuperar": lambda: vista_recuperar_clave(pagina, oscuro, al_volver_login=ir_a_login),
            "home": lambda: vista_home(
                pagina, oscuro, dp, al_cerrar_sesion=ir_a_login,
                al_ir_scanner=lambda: navegar("scanner"), al_ir_recarga=lambda: navegar("recarga"),
                al_ir_historial=lambda: navegar("historial"), al_ir_dashboard=lambda: navegar("dashboard"),
                al_ir_perfil=lambda: navegar("perfil"),
            ),
            "scanner": lambda: vista_scanner(pagina, oscuro, dp, al_volver_home=ir_a_home),
            "recarga": lambda: vista_recarga(pagina, oscuro, dp, al_volver_home=ir_a_home),
            "historial": lambda: vista_historial(pagina, oscuro, dp, al_volver_home=ir_a_home),
            "dashboard": lambda: vista_dashboard(pagina, oscuro, dp, al_volver_home=ir_a_home),
            "perfil": lambda: vista_perfil(pagina, oscuro, dp, al_volver_home=ir_a_home),
        }
        return rutas[estado["ruta"]]()

    # ---------- Motor de redibujado ----------
    def repintar():
        paleta = obtener_paleta(estado["oscuro"])
        pagina.bgcolor = paleta["fondo_inicio"]
        pagina.appbar.bgcolor = paleta["tarjeta"]
        titulo_barra.color = paleta["texto_principal"]
        boton_tema.icon = ft.Icons.LIGHT_MODE_OUTLINED if estado["oscuro"] else ft.Icons.DARK_MODE_OUTLINED

        pagina.controls.clear()
        pagina.add(construir_vista())
        pagina.update()

    repintar()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
