import asyncio
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_ERROR, obtener_paleta
from frontend.components.tarjeta_movimiento import crear_fila_historial
from backend.dao_transacciones import dao_transacciones

async def obtener_historial_completo(billetera_id: int) -> list:
    return dao_transacciones.obtener_historial(billetera_id, limite=15)

def vista_historial(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    titulo = ft.Text("Historial de Movimientos", size=24, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    
    # Contenedor con scroll para la lista infinita
    lista_movimientos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    progreso = ft.ProgressRing(color=COLOR_PRIMARIO)

    # Cargar datos al abrir la vista
    async def cargar_datos():
        movimientos = await obtener_historial_completo(billetera_id)
        progreso.visible = False
        
        if not movimientos:
            lista_movimientos.controls = [
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("Aún no tienes movimientos", color=paleta["texto_secundario"], italic=True)
                )
            ]
        else:
            lista_movimientos.controls = [crear_fila_historial(item, modo_oscuro) for item in movimientos]
            
        pagina.update()

    pagina.run_task(cargar_datos)

    boton_volver = ft.Button(
        content=ft.Text("Volver al inicio", color=paleta["texto_secundario"]),
        on_click=lambda e: al_volver_home(datos_pasajero) if al_volver_home else None
    )

    return ft.Container(
        expand=True,
        padding=20,
        bgcolor=paleta["fondo_inicio"],
        content=ft.Column(
            controls=[
                titulo, 
                progreso, 
                lista_movimientos, 
                ft.Container(content=boton_volver, alignment=ft.Alignment.CENTER)
            ]
        )
    )