import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, obtener_paleta
from frontend.core.ui import campo_texto, boton_primario, boton_secundario, tarjeta_contenedor, fondo_pantalla, en_progreso, aplicar_resize
from frontend.components.alertas import mostrar_notificacion
from backend.dao_pasajeros import dao_pasajeros

PREGUNTAS_SEGURIDAD = [
    "¿Cuál es el nombre de tu primera mascota?",
    "¿Cuál es tu comida favorita?",
    "¿En qué distrito naciste?",
]


async def registrar_pasajero(**kwargs) -> dict:
    return dao_pasajeros.registrar_pasajero(**kwargs)


def vista_register(pagina: ft.Page, modo_oscuro: bool, al_registro_exitoso=None, al_volver_login=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    estilo_radio = ft.TextStyle(color=paleta["texto_principal"])

    campo_nombre = campo_texto(paleta, "Nombre completo", ft.Icons.PERSON_OUTLINE)
    campo_dni = campo_texto(paleta, "DNI", ft.Icons.BADGE_OUTLINED, max_length=8, keyboard_type=ft.KeyboardType.NUMBER)
    campo_email = campo_texto(paleta, "Correo electrónico", ft.Icons.EMAIL_OUTLINED)
    campo_clave = campo_texto(paleta, "Contraseña", ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True)

    grupo_tipo = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="General", label="General", label_style=estilo_radio),
            ft.Radio(value="Medio", label="Medio Pasaje", label_style=estilo_radio),
        ]),
        value="General",
    )

    aviso_medio_pasaje = ft.Text(
        "Se te pedirá un código institucional para verificar tu medio pasaje. Hasta que se apruebe, pagarás tarifa General.",
        size=11, color=paleta["texto_secundario"], visible=False,
    )

    def cambio_tipo(e):
        aviso_medio_pasaje.visible = grupo_tipo.value == "Medio"
        pagina.update()

    grupo_tipo.on_change = cambio_tipo

    dropdown_pregunta = ft.Dropdown(
        label="Pregunta de seguridad",
        options=[ft.dropdown.Option(p) for p in PREGUNTAS_SEGURIDAD],
        bgcolor=paleta["campo"], color=paleta["texto_principal"], border_color="transparent",
        focused_border_color=COLOR_PRIMARIO, filled=True, border_radius=12,
    )
    campo_respuesta = campo_texto(paleta, "Respuesta secreta", ft.Icons.QUESTION_ANSWER_OUTLINED)

    texto_boton = ft.Text("Crear cuenta", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_registro = boton_primario("Crear cuenta")
    boton_registro.content = texto_boton

    async def manejar_registro(e):
        if not dropdown_pregunta.value or not (campo_respuesta.value or "").strip():
            mostrar_notificacion(pagina, "Completa la pregunta de seguridad", tipo="error")
            return

        en_progreso(boton_registro)
        pagina.update()

        resultado = await registrar_pasajero(
            nombre=campo_nombre.value or "", dni=campo_dni.value or "",
            email=campo_email.value or "", clave=campo_clave.value or "",
            tipo_pasajero=grupo_tipo.value or "General",
            pregunta_seguridad=dropdown_pregunta.value, respuesta_seguridad=campo_respuesta.value,
        )

        boton_registro.content = texto_boton

        if resultado["status"]:
            mensaje = "Cuenta creada exitosamente"
            if resultado.get("requiere_verificacion"):
                mensaje += ". Verifica tu medio pasaje desde tu perfil."
            mostrar_notificacion(pagina, mensaje, tipo="exito")
            if al_volver_login:
                al_volver_login()
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "Error al registrar"), tipo="error")
        pagina.update()

    boton_registro.on_click = manejar_registro

    tarjeta = tarjeta_contenedor(paleta, [
        ft.Text("Nueva Cuenta", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"]),
        ft.Text("Únete a LimaPay", size=13, color=paleta["texto_secundario"]),
        ft.Container(
            content=ft.Column(
                [
                    campo_nombre, campo_dni, campo_email, campo_clave,
                    ft.Text("Tipo de pasajero", size=13, color=paleta["texto_secundario"]),
                    grupo_tipo, aviso_medio_pasaje,
                    dropdown_pregunta, campo_respuesta,
                    boton_registro,
                    ft.Container(content=boton_secundario("¿Ya tienes cuenta? Inicia sesión", paleta,
                                                            lambda e: al_volver_login() if al_volver_login else None),
                                 alignment=ft.Alignment.CENTER),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            height=500,
        )
    ])

    aplicar_resize(pagina, tarjeta)

    return fondo_pantalla(paleta, ft.Column(
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[tarjeta],
    ))
