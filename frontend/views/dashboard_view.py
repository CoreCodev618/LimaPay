import asyncio
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, obtener_paleta
from backend.dao_transacciones import dao_transacciones

async def obtener_top_rutas() -> list:
    return dao_transacciones.obtener_rutas_populares()

def vista_dashboard(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)

    titulo = ft.Text("Rutas más transitadas", size=24, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    subtitulo = ft.Text("Top 5 por estación de origen", size=14, color=paleta["texto_secundario"])

    lista_rutas = ft.Column(spacing=10, expand=True)
    progreso = ft.ProgressRing(color=COLOR_PRIMARIO)

    def crear_fila_ruta(item):
        return ft.Container(
            padding=14,
            border_radius=14,
            bgcolor=paleta["tarjeta"],
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Icon(ft.Icons.TRENDING_UP, color=COLOR_PRIMARIO, size=20),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(item["codigo_ruta"], size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
                                    ft.Text(item["estacion"], size=11, color=paleta["texto_secundario"]),
                                ],
                            ),
                        ]
                    ),
                    ft.Container(
                        padding=8,
                        border_radius=10,
                        bgcolor=COLOR_PRIMARIO + "20", # Transparencia al 20%
                        content=ft.Text(f"{item['total_viajes']} viajes", size=12, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO)
                    )
                ],
            ),
        )

    async def cargar_datos():
        rutas = await obtener_top_rutas()
        progreso.visible = False
        if not rutas:
            lista_rutas.controls = [ft.Text("Aún no hay datos de viajes.", color=paleta["texto_secundario"], italic=True)]
        else:
            lista_rutas.controls = [crear_fila_ruta(r) for r in rutas]
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
                titulo, subtitulo, progreso, lista_rutas, ft.Container(content=boton_volver, alignment=ft.Alignment.CENTER)
            ]
        )
    )