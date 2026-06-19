import asyncio
import flet as ft

from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO, COLOR_ERROR, obtener_paleta

# --- Mock temporal del backend (reemplazar por: from backend.dao_pasajeros import registrar_pasajero) ---
async def registrar_pasajero(nombre: str, dni: str, email: str, clave: str) -> dict:
    await asyncio.sleep(1) # Simula tiempo de red
    if len(dni) != 8 or not dni.isdigit():
        return {"status": False, "mensaje": "El DNI debe tener 8 dígitos"}
    if not nombre or not email or not clave:
        return {"status": False, "mensaje": "Todos los campos son obligatorios"}
    return {"status": True, "mensaje": "Usuario creado exitosamente"}

def calcular_ancho_tarjeta(ancho_pagina: float | None) -> int:
    if not ancho_pagina:
        return 380
    return int(max(280, min(ancho_pagina - 48, 380)))

def vista_register(pagina: ft.Page, modo_oscuro: bool, al_registro_exitoso=None, al_volver_login=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)

    # ---------- Campos de entrada ----------
    estilo_campo = {
        "filled": True,
        "border_radius": 12,
        "border_color": "transparent",
        "focused_border_color": COLOR_PRIMARIO,
        "bgcolor": paleta["campo"],
        "color": paleta["texto_principal"],
    }

    campo_nombre = ft.TextField(label="Nombre completo", prefix_icon=ft.Icons.PERSON_OUTLINE, **estilo_campo)
    campo_dni = ft.TextField(label="DNI", max_length=8, keyboard_type=ft.KeyboardType.NUMBER, prefix_icon=ft.Icons.BADGE_OUTLINED, **estilo_campo)
    campo_email = ft.TextField(label="Correo electrónico", prefix_icon=ft.Icons.EMAIL_OUTLINED, **estilo_campo)
    campo_clave = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINE, **estilo_campo)

    texto_error = ft.Text(color=COLOR_ERROR, size=13, visible=False)

    # ---------- Botones ----------
    texto_boton_registro = ft.Text("Crear cuenta", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_registro = ft.Container(
        content=texto_boton_registro,
        gradient=ft.LinearGradient(colors=[COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO]),
        border_radius=12,
        padding=15,
        alignment=ft.Alignment.CENTER,
        ink=True,
    )

    boton_volver = ft.TextButton(
        "¿Ya tienes cuenta? Inicia sesión", 
        style=ft.ButtonStyle(color=paleta["texto_secundario"]),
        on_click=lambda e: al_volver_login() if al_volver_login else None
    )

    async def manejar_registro(e):
        texto_error.visible = False
        boton_registro.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)
        pagina.update()

        resultado = await registrar_pasajero(
            nombre=campo_nombre.value or "",
            dni=campo_dni.value or "",
            email=campo_email.value or "",
            clave=campo_clave.value or ""
        )

        boton_registro.content = texto_boton_registro

        if resultado["status"]:
            # Si el registro es exitoso, redirigimos al login
            if al_volver_login:
                al_volver_login()
        else:
            texto_error.value = resultado.get("mensaje", "Error al registrar")
            texto_error.visible = True
        pagina.update()

    boton_registro.on_click = manejar_registro

    # ---------- Tarjeta y UI ----------
    texto_titulo = ft.Text("Nueva Cuenta", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    
    tarjeta = ft.Container(
        width=calcular_ancho_tarjeta(pagina.width),
        padding=28,
        border_radius=24,
        bgcolor=paleta["tarjeta"],
        content=ft.Column(
            spacing=16,
            controls=[
                texto_titulo,
                ft.Text("Únete a LimaPay", size=13, color=paleta["texto_secundario"]),
                campo_nombre,
                campo_dni,
                campo_email,
                campo_clave,
                texto_error,
                boton_registro,
                ft.Container(content=boton_volver, alignment=ft.Alignment.CENTER)
            ],
        ),
    )

    def al_redimensionar(e):
        tarjeta.width = calcular_ancho_tarjeta(pagina.width)
        pagina.update()

    pagina.on_resized = al_redimensionar

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
            controls=[tarjeta],
        ),
    )