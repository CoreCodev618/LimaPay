import asyncio
import flet as ft

from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO, COLOR_ERROR, obtener_paleta
from frontend.components.alertas import mostrar_notificacion
from backend.dao_pasajeros import dao_pasajeros

async def iniciar_sesion(dni: str, clave: str) -> dict:
    return dao_pasajeros.iniciar_sesion(dni,clave)


def calcular_ancho_tarjeta(ancho_pagina: float | None) -> int:
    if not ancho_pagina:
        return 380
    return int(max(280, min(ancho_pagina - 48, 380)))


def vista_login(pagina: ft.Page, modo_oscuro: bool, al_iniciar_sesion=None, al_ir_registro = None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)

    # ---------- Campos de entrada ----------
    campo_dni = ft.TextField(
        label="DNI",
        max_length=8,
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.BADGE_OUTLINED,
        filled=True,
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLOR_PRIMARIO,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"],
    )

    campo_clave = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        filled=True,
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLOR_PRIMARIO,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"],
    )   

    # ---------- Botón de ingreso ----------
    texto_boton_login = ft.Text("Iniciar sesión", color="#0A0E1A", weight=ft.FontWeight.BOLD)

    boton_login = ft.Container(
        content=texto_boton_login,
        gradient=ft.LinearGradient(colors=[COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO]),
        border_radius=12,
        padding=15,
        alignment=ft.Alignment.CENTER,
        ink=True,
    )
    
    boton_ir_registro = ft.TextButton(
        "¿No tienes cuenta? Regístrate", 
        style=ft.ButtonStyle(color=paleta["texto_secundario"]),
        on_click=lambda e: al_ir_registro() if al_ir_registro else None
    )
    
    async def manejar_login(e):
        dni = campo_dni.value or ""
        if len(dni) != 8 or not dni.isdigit():
            mostrar_notificacion(pagina, "El DNI debe tener 8 dígitos numéricos", es_error=True)
            return

        boton_login.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)
        pagina.update()

        resultado = await iniciar_sesion(dni, campo_clave.value or "")

        boton_login.content = texto_boton_login

        if resultado["status"] and al_iniciar_sesion:
            al_iniciar_sesion(resultado)
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "No se pudo iniciar sesión"), es_error=True)
        pagina.update()

    boton_login.on_click = manejar_login

    # ---------- Tarjeta ----------
    tarjeta = ft.Container(
        width=calcular_ancho_tarjeta(pagina.width),
        padding=28,
        border_radius=24,
        bgcolor=paleta["tarjeta"],
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Bienvenido de vuelta", size=20, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
                ft.Text("Inicia sesión para continuar", size=13, color=paleta["texto_secundario"]),
                campo_dni,
                campo_clave,
                boton_login,
                boton_ir_registro,
            ],
        ),
    )
    
    # ---------- Logo + nombre de la app ----------
    archivo_logo = "logo_dark.png" if modo_oscuro else "logo_light.png"

    logo = ft.Image(
        src=archivo_logo,
        width=90,
        height=90,
        fit="contain",
    )
    
    texto_nombre_app = ft.Text("LimaPay", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])

    # ---------- Responsive: la tarjeta se ajusta al ancho de la ventana ----------
    def al_redimensionar(e):
        tarjeta.width = calcular_ancho_tarjeta(pagina.width)
        pagina.update()

    pagina.on_resized = al_redimensionar

    # ---------- Fondo ----------
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[paleta["fondo_inicio"], paleta["fondo_fin"]],
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=24,
            controls=[logo, texto_nombre_app, tarjeta],
        ),
    )