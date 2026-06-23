import flet as ft
from frontend.tema.temas import obtener_paleta
from frontend.core.ui import campo_texto, boton_primario, boton_secundario, tarjeta_contenedor, fondo_pantalla, en_progreso, aplicar_resize
from frontend.components.alertas import mostrar_notificacion
from backend.dao_pasajeros import dao_pasajeros


async def iniciar_sesion(dni: str, clave: str) -> dict:
    return dao_pasajeros.iniciar_sesion(dni, clave)


def vista_login(pagina: ft.Page, modo_oscuro: bool, al_iniciar_sesion=None, al_ir_registro=None, al_ir_recuperar=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)

    campo_dni = campo_texto(paleta, "DNI", ft.Icons.BADGE_OUTLINED, max_length=8, keyboard_type=ft.KeyboardType.NUMBER)
    campo_clave = campo_texto(paleta, "Contraseña", ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True)

    texto_boton = ft.Text("Iniciar sesión", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_login = boton_primario("Iniciar sesión", degradado=True)
    boton_login.content = texto_boton

    async def manejar_login(e):
        dni = campo_dni.value or ""
        if len(dni) != 8 or not dni.isdigit():
            mostrar_notificacion(pagina, "El DNI debe tener 8 dígitos numéricos", tipo="error")
            return
        en_progreso(boton_login)
        pagina.update()

        resultado = await iniciar_sesion(dni, campo_clave.value or "")
        boton_login.content = texto_boton

        if resultado["status"] and al_iniciar_sesion:
            al_iniciar_sesion(resultado)
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "No se pudo iniciar sesión"), tipo="error")
        pagina.update()

    boton_login.on_click = manejar_login

    tarjeta = tarjeta_contenedor(paleta, [
        ft.Text("Bienvenido de vuelta", size=20, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
        ft.Text("Inicia sesión para continuar", size=13, color=paleta["texto_secundario"]),
        campo_dni,
        campo_clave,
        boton_login,
        ft.Row([
            boton_secundario("¿No tienes cuenta? Regístrate", paleta, lambda e: al_ir_registro() if al_ir_registro else None),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            boton_secundario("¿Olvidaste tu contraseña?", paleta, lambda e: al_ir_recuperar() if al_ir_recuperar else None),
        ], alignment=ft.MainAxisAlignment.CENTER),
    ])

    aplicar_resize(pagina, tarjeta)

    archivo_logo = "logo_dark.png" if modo_oscuro else "logo_light.png"
    return fondo_pantalla(paleta, ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=24,
        controls=[
            ft.Image(src=archivo_logo, width=90, height=90, fit="contain", border_radius=17),
            ft.Text("LimaPay", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"]),
            tarjeta,
        ],
    ))
