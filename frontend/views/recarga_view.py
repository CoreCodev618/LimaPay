import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, obtener_paleta
from frontend.core.ui import campo_texto, boton_primario, boton_volver, en_progreso
from frontend.components.alertas import mostrar_notificacion
from backend.dao_transacciones import dao_transacciones

LOGOS_METODO_PAGO = {"1": "logo-yape.webp", "2": "logo-plin.webp", "3": "logo-visa.png", "4": "logo-efectivo.webp"}
MONTO_MINIMO = 5


def vista_recarga(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    campo_monto = campo_texto(paleta, "Monto (S/)", ft.Icons.ATTACH_MONEY, keyboard_type=ft.KeyboardType.NUMBER)
    logo_pago = ft.Image(src="logo-yape.webp", width=70, height=70, fit="contain")

    estilo_radio = ft.TextStyle(color=paleta["texto_principal"])
    grupo_metodos = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="1", label="Yape", label_style=estilo_radio),
            ft.Radio(value="2", label="Plin", label_style=estilo_radio),
            ft.Radio(value="3", label="Tarjeta Visa/Mastercard", label_style=estilo_radio),
            ft.Radio(value="4", label="Agente Físico", label_style=estilo_radio),
        ]),
        value="1",
        on_change=lambda e: (setattr(logo_pago, "src", LOGOS_METODO_PAGO.get(e.control.value, "logo-yape.webp")), pagina.update()),
    )

    texto_boton = ft.Text("Confirmar Recarga", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_recargar = boton_primario("Confirmar Recarga", degradado=False)
    boton_recargar.content = texto_boton

    async def manejar_recarga(e):
        try:
            monto = float(campo_monto.value)
            if monto < MONTO_MINIMO:
                mostrar_notificacion(pagina, f"El monto mínimo es S/ {MONTO_MINIMO}.", tipo="error")
                return
        except (ValueError, TypeError):
            mostrar_notificacion(pagina, "Ingresa un número válido.", tipo="error")
            return

        en_progreso(boton_recargar)
        pagina.update()

        resultado = dao_transacciones.recargar_saldo(billetera_id, monto, int(grupo_metodos.value))
        boton_recargar.content = texto_boton

        if resultado["status"]:
            mostrar_notificacion(pagina, resultado["mensaje"], tipo="exito")
            campo_monto.value = ""
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "Error en la recarga."), tipo="error")
        pagina.update()

    boton_recargar.on_click = manejar_recarga

    tarjeta = ft.Container(
        width=380, padding=28, border_radius=24, bgcolor=paleta["tarjeta"],
        content=ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            ft.Text("Recargar Saldo", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"]),
            ft.Text("Selecciona tu método y monto:", size=14, color=paleta["texto_secundario"]),
            campo_monto,
            ft.Row([logo_pago, grupo_metodos], alignment=ft.MainAxisAlignment.START),
            boton_recargar,
            boton_volver(paleta, datos_pasajero, al_volver_home),
        ]),
    )

    return ft.Container(expand=True, alignment=ft.Alignment.CENTER, padding=20, bgcolor=paleta["fondo_inicio"], content=tarjeta)
