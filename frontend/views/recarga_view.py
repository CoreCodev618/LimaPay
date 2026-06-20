import asyncio
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ERROR, obtener_paleta
from backend.dao_transacciones import dao_transacciones

async def recargar_saldo(billetera_id: int, monto: float) -> dict:
    return dao_transacciones.recargar_saldo(billetera_id, monto, 1)

def vista_recarga(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    # ---------- Elementos de UI ----------
    titulo = ft.Text("Recargar Saldo", size=28, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    subtitulo = ft.Text("Ingresa el monto a recargar (Min. S/ 5)", size=14, color=paleta["texto_secundario"])

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

    texto_estado = ft.Text("", size=14, visible=False)

    # ---------- Lógica de validación ----------
    async def manejar_recarga(e):
        texto_estado.visible = False
        pagina.update()

        try:
            monto = float(campo_monto.value)
            if monto < 5:
                texto_estado.value = "El monto mínimo es S/ 5."
                texto_estado.color = COLOR_ERROR
                texto_estado.visible = True
                pagina.update()
                return
        except ValueError:
            texto_estado.value = "Ingresa un número válido."
            texto_estado.color = COLOR_ERROR
            texto_estado.visible = True
            pagina.update()
            return

        # Animación de carga
        boton_recargar.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)
        pagina.update()

        resultado = await recargar_saldo(billetera_id, monto)

        # Restaurar botón
        boton_recargar.content = ft.Text("Confirmar Recarga", color="#0A0E1A", weight=ft.FontWeight.BOLD)

        if resultado["status"]:
            texto_estado.value = resultado["mensaje"]
            texto_estado.color = COLOR_EXITO
            campo_monto.value = "" # Limpia el campo tras el éxito
        else:
            texto_estado.value = resultado.get("mensaje", "Error en la recarga.")
            texto_estado.color = COLOR_ERROR
        
        texto_estado.visible = True
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
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[titulo, subtitulo, campo_monto, texto_estado, boton_recargar, boton_volver],
        ),
    )

    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=20,
        bgcolor=paleta["fondo_inicio"],
        content=tarjeta,
    )