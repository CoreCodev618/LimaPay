import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ADVERTENCIA, obtener_paleta
from frontend.core.ui import campo_texto, boton_primario, boton_volver, en_progreso
from frontend.components.alertas import mostrar_notificacion
from backend.dao_pasajeros import dao_pasajeros

ESTADO_COLOR = {"Pendiente": COLOR_ADVERTENCIA, "Aprobado": COLOR_EXITO, "Rechazado": "#FF5C5C", "Sin solicitud": None}


def vista_perfil(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    pasajero_id = datos_pasajero.get("pasajero_id")
    billetera_id = datos_pasajero.get("billetera_id")

    # ---------- Tarjeta de datos básicos ----------
    columna_datos = ft.Column(spacing=4)
    progreso_perfil = ft.ProgressRing(color=COLOR_PRIMARIO, width=20, height=20)
    seccion_medio_pasaje = ft.Column(spacing=8, visible=False)

    badge_estado = ft.Container(padding=8, border_radius=10, content=ft.Text("", size=12, weight=ft.FontWeight.BOLD))
    campo_codigo_institucional = campo_texto(paleta, "Código institucional", ft.Icons.SCHOOL_OUTLINED)
    texto_boton_verificar = ft.Text("Solicitar verificación", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_verificar = boton_primario("Solicitar verificación")
    boton_verificar.content = texto_boton_verificar

    async def refrescar_estado_verificacion(ya_verificado: bool):
        if ya_verificado:
            badge_estado.bgcolor = COLOR_EXITO + "20"
            badge_estado.content.value = "Medio pasaje verificado ✓"
            badge_estado.content.color = COLOR_EXITO
            campo_codigo_institucional.visible = False
            boton_verificar.visible = False
        else:
            estado = dao_pasajeros.estado_verificacion(pasajero_id).get("estado", "Sin solicitud")
            color = ESTADO_COLOR.get(estado, COLOR_ADVERTENCIA)
            badge_estado.bgcolor = (color + "20") if color else paleta["campo"]
            badge_estado.content.value = f"Estado de verificación: {estado}"
            badge_estado.content.color = color or paleta["texto_secundario"]
            campo_codigo_institucional.visible = estado != "Pendiente"
            boton_verificar.visible = estado != "Pendiente"

    async def cargar_perfil():
        perfil = dao_pasajeros.obtener_perfil(pasajero_id)
        progreso_perfil.visible = False
        if not perfil["status"]:
            columna_datos.controls = [ft.Text("No se pudo cargar el perfil", color=paleta["texto_secundario"])]
            pagina.update()
            return

        columna_datos.controls = [
            ft.Text(perfil["nombre"], size=20, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"]),
            ft.Text(f"DNI: {perfil['dni']}", size=13, color=paleta["texto_secundario"]),
            ft.Text(f"Correo: {perfil['email']}", size=13, color=paleta["texto_secundario"]),
            ft.Text(f"Tipo de pasajero: {perfil['tipo_pasajero']}", size=13, color=paleta["texto_secundario"]),
        ]

        if perfil["tipo_pasajero"] == "Medio":
            seccion_medio_pasaje.visible = True
            await refrescar_estado_verificacion(perfil["medio_pasaje_verificado"])

        campo_umbral.value = str(perfil["umbral_alerta"])
        pagina.update()

    async def manejar_verificacion(e):
        en_progreso(boton_verificar)
        pagina.update()
        resultado = dao_pasajeros.solicitar_verificacion_medio_pasaje(pasajero_id, campo_codigo_institucional.value or "")
        boton_verificar.content = texto_boton_verificar
        if resultado["status"]:
            mostrar_notificacion(pagina, resultado["mensaje"], tipo="exito")
            await refrescar_estado_verificacion(False)
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "No se pudo enviar la solicitud"), tipo="error")
        pagina.update()

    boton_verificar.on_click = manejar_verificacion
    seccion_medio_pasaje.controls = [
        ft.Text("Verificación de medio pasaje", size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
        badge_estado, campo_codigo_institucional, boton_verificar,
    ]

    # ---------- Umbral de alerta de saldo bajo ----------
    campo_umbral = campo_texto(paleta, "Avisarme cuando el saldo sea menor a (S/)", ft.Icons.NOTIFICATIONS_OUTLINED,
                                keyboard_type=ft.KeyboardType.NUMBER)
    texto_boton_umbral = ft.Text("Guardar preferencia", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_umbral = boton_primario("Guardar preferencia", degradado=False)
    boton_umbral.content = texto_boton_umbral

    async def guardar_umbral(e):
        try:
            nuevo_umbral = float(campo_umbral.value)
        except (ValueError, TypeError):
            mostrar_notificacion(pagina, "Ingresa un monto válido", tipo="error")
            return
        en_progreso(boton_umbral)
        pagina.update()
        resultado = dao_pasajeros.actualizar_umbral_alerta(billetera_id, nuevo_umbral)
        boton_umbral.content = texto_boton_umbral
        mostrar_notificacion(pagina, resultado["mensaje"], tipo="exito" if resultado["status"] else "error")
        pagina.update()

    boton_umbral.on_click = guardar_umbral

    # ---------- Cambiar contraseña ----------
    campo_clave_actual = campo_texto(paleta, "Contraseña actual", ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True)
    campo_clave_nueva = campo_texto(paleta, "Nueva contraseña", ft.Icons.LOCK_OUTLINE, password=True, can_reveal_password=True)
    texto_boton_clave = ft.Text("Cambiar contraseña", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_cambiar_clave = boton_primario("Cambiar contraseña", degradado=False)
    boton_cambiar_clave.content = texto_boton_clave

    async def manejar_cambio_clave(e):
        en_progreso(boton_cambiar_clave)
        pagina.update()
        resultado = dao_pasajeros.cambiar_clave(pasajero_id, campo_clave_actual.value or "", campo_clave_nueva.value or "")
        boton_cambiar_clave.content = texto_boton_clave
        if resultado["status"]:
            campo_clave_actual.value = ""
            campo_clave_nueva.value = ""
        mostrar_notificacion(pagina, resultado["mensaje"], tipo="exito" if resultado["status"] else "error")
        pagina.update()

    boton_cambiar_clave.on_click = manejar_cambio_clave

    pagina.run_task(cargar_perfil)

    def seccion(titulo: str, controles: list) -> ft.Container:
        return ft.Container(
            padding=18, border_radius=16, bgcolor=paleta["tarjeta"],
            content=ft.Column(spacing=10, controls=([ft.Text(titulo, size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"])] if titulo else []) + controles),
        )

    contenido = [
        ft.Text("Mi Perfil", size=24, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"]),
        ft.Container(padding=18, border_radius=16, bgcolor=paleta["tarjeta"],
                     content=ft.Column(spacing=6, controls=[progreso_perfil, columna_datos])),
        seccion("", [seccion_medio_pasaje]),
        seccion("Alertas de saldo", [campo_umbral, boton_umbral]),
        seccion("Seguridad", [campo_clave_actual, campo_clave_nueva, boton_cambiar_clave]),
        ft.Container(content=boton_volver(paleta, datos_pasajero, al_volver_home), alignment=ft.Alignment.CENTER),
    ]

    return ft.Container(
        expand=True, padding=20, bgcolor="transparent",
        content=ft.Column(spacing=16, scroll=ft.ScrollMode.AUTO, controls=contenido),
    )
