import flet as ft
from frontend.tema.temas import obtener_paleta
from frontend.core.ui import campo_texto, boton_primario, boton_secundario, tarjeta_contenedor, fondo_pantalla, en_progreso, aplicar_resize
from frontend.components.alertas import mostrar_notificacion
from backend.dao_pasajeros import dao_pasajeros


def vista_recuperar_clave(pagina: ft.Page, modo_oscuro: bool, al_volver_login=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)

    campo_dni = campo_texto(paleta, "DNI", ft.Icons.BADGE_OUTLINED, max_length=8, keyboard_type=ft.KeyboardType.NUMBER)
    texto_pregunta = ft.Text("", size=13, color=paleta["texto_principal"], visible=False)
    campo_respuesta = campo_texto(paleta, "Tu respuesta", ft.Icons.QUESTION_ANSWER_OUTLINED, visible=False)
    campo_nueva_clave = campo_texto(paleta, "Nueva contraseña", ft.Icons.LOCK_OUTLINE, password=True,
                                     can_reveal_password=True, visible=False)

    texto_buscar = ft.Text("Buscar cuenta", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_buscar = boton_primario("Buscar cuenta")
    boton_buscar.content = texto_buscar

    texto_confirmar = ft.Text("Restablecer contraseña", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_confirmar = boton_primario("Restablecer contraseña")
    boton_confirmar.content = texto_confirmar
    boton_confirmar.visible = False

    async def buscar_cuenta(e):
        dni = campo_dni.value or ""
        if len(dni) != 8 or not dni.isdigit():
            mostrar_notificacion(pagina, "El DNI debe tener 8 dígitos numéricos", tipo="error")
            return
        en_progreso(boton_buscar)
        pagina.update()

        resultado = dao_pasajeros.obtener_pregunta_seguridad(dni)
        boton_buscar.content = texto_buscar

        if resultado["status"]:
            texto_pregunta.value = resultado["pregunta_seguridad"]
            texto_pregunta.visible = True
            campo_respuesta.visible = True
            campo_nueva_clave.visible = True
            boton_confirmar.visible = True
            campo_dni.disabled = True
            boton_buscar.visible = False
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "No se encontró la cuenta"), tipo="error")
        pagina.update()

    async def confirmar_restablecimiento(e):
        en_progreso(boton_confirmar)
        pagina.update()

        resultado = dao_pasajeros.restablecer_clave(campo_dni.value, campo_respuesta.value or "", campo_nueva_clave.value or "")
        boton_confirmar.content = texto_confirmar

        if resultado["status"]:
            mostrar_notificacion(pagina, resultado["mensaje"], tipo="exito")
            if al_volver_login:
                al_volver_login()
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "No se pudo restablecer"), tipo="error")
        pagina.update()

    boton_buscar.on_click = buscar_cuenta
    boton_confirmar.on_click = confirmar_restablecimiento

    tarjeta = tarjeta_contenedor(paleta, [
        ft.Text("Recuperar contraseña", size=22, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
        ft.Text("Ingresa tu DNI para continuar", size=13, color=paleta["texto_secundario"]),
        campo_dni,
        boton_buscar,
        texto_pregunta,
        campo_respuesta,
        campo_nueva_clave,
        boton_confirmar,
        ft.Container(content=boton_secundario("Volver a iniciar sesión", paleta,
                                                lambda e: al_volver_login() if al_volver_login else None),
                     alignment=ft.Alignment.CENTER),
    ])

    aplicar_resize(pagina, tarjeta)

    return fondo_pantalla(paleta, ft.Column(
        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[tarjeta],
    ))
