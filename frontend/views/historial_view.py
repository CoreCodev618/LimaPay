import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, obtener_paleta
from frontend.core.ui import pantalla_simple
from frontend.components.tarjeta_movimiento import crear_fila_historial
from backend.dao_transacciones import dao_transacciones


def vista_historial(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    lista_movimientos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    progreso = ft.ProgressRing(color=COLOR_PRIMARIO)

    async def cargar_datos():
        movimientos = dao_transacciones.obtener_historial(billetera_id, limite=15)
        progreso.visible = False
        if not movimientos:
            lista_movimientos.controls = [ft.Container(
                padding=40, alignment=ft.Alignment.CENTER,
                content=ft.Text("Aún no tienes movimientos", color=paleta["texto_secundario"], italic=True),
            )]
        else:
            lista_movimientos.controls = [crear_fila_historial(item, modo_oscuro) for item in movimientos]
        pagina.update()

    pagina.run_task(cargar_datos)

    return pantalla_simple(paleta, "Historial de Movimientos", [progreso, lista_movimientos], datos_pasajero, al_volver_home)
