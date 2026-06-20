import asyncio
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ERROR, obtener_paleta
from frontend.components.alertas import mostrar_notificacion
from backend.dao_transacciones import dao_transacciones

async def recargar_saldo(billetera_id: int, monto: float, metodo_pago_id: int) -> dict:
    return dao_transacciones.recargar_saldo(billetera_id, monto, metodo_pago_id)

def vista_recarga(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    # ---------- Elementos de UI ----------
    titulo = ft.Text("Recargar Saldo", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    subtitulo = ft.Text("Selecciona tu método y monto:", size=14, color=paleta["texto_secundario"])
    
    campo_monto = ft.TextField(
        label="Monto (S/)",
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.Icons.ATTACH_MONEY,
        filled=True,
        border_radius=12,
        border_color="transparent",
        focused_border_color=COLOR_PRIMARIO,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"],
    )

    # Imagen que cambia
    logo_pago = ft.Image(src="logo-yape.webp", width=70, height=70, fit="contain")

    def cambiar_seleccion(e):
        logos = {
            "1": "logo-yape.webp",
            "2": "logo-plin.webp",
            "3": "logo-visa.png",
            "4": "logo-efectivo.webp"
        }
        logo_pago.src = logos.get(e.control.value, "logo-yape.webp")
        pagina.update()

    # Grupo de radios (Checks)
    estilo_etiqueta_radio = ft.TextStyle(color=paleta["texto_principal"])
    grupo_metodos = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="1", label="Yape", label_style=estilo_etiqueta_radio),
            ft.Radio(value="2", label="Plin", label_style=estilo_etiqueta_radio),
            ft.Radio(value="3", label="Tarjeta Visa/Mastercard", label_style=estilo_etiqueta_radio),
            ft.Radio(value="4", label="Agente Físico", label_style=estilo_etiqueta_radio),
        ]),
        value="1",
        on_change=cambiar_seleccion
    )

    # ---------- Lógica de validación ----------
    async def manejar_recarga(e):
        try:
            monto = float(campo_monto.value)
            if monto < 5:
                mostrar_notificacion(pagina, "El monto mínimo es S/ 5.", es_error=True)
                return
        except ValueError:
            mostrar_notificacion(pagina, "Ingresa un número válido.", es_error=True)
            return

        boton_recargar.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)
        pagina.update()

        metodo_id = int(grupo_metodos.value)
        resultado = await recargar_saldo(billetera_id, monto, metodo_id)

        boton_recargar.content = ft.Text("Confirmar Recarga", color="#0A0E1A", weight=ft.FontWeight.BOLD)

        if resultado["status"]:
            mostrar_notificacion(pagina, resultado["mensaje"], es_error=False)
            campo_monto.value = "" 
        else:
            mostrar_notificacion(pagina, resultado.get("mensaje", "Error en la recarga."), es_error=True)
        
        pagina.update()

    # ---------- Botones ----------
    boton_recargar = ft.Container(
        content=ft.Text("Confirmar Recarga", color="#0A0E1A", weight=ft.FontWeight.BOLD),
        bgcolor=COLOR_PRIMARIO,
        border_radius=12,
        padding=15,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=manejar_recarga
    )

    boton_volver = ft.Button(
        content=ft.Text("Volver al inicio", color=paleta["texto_secundario"]),
        on_click=lambda e: al_volver_home(datos_pasajero) if al_volver_home else None
    )

    # ---------- Renderizado Final ----------
    tarjeta = ft.Container(
        width=380,
        padding=28,
        border_radius=24,
        bgcolor=paleta["tarjeta"],
        content=ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                titulo, 
                subtitulo, 
                campo_monto, 
                ft.Row([logo_pago, grupo_metodos], alignment=ft.MainAxisAlignment.START),
                boton_recargar, 
                boton_volver
            ],
        ),
    )

    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=20,
        bgcolor=paleta["fondo_inicio"],
        content=tarjeta,
    )