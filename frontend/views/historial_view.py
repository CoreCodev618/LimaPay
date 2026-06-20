import asyncio
import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_ERROR, obtener_paleta

# --- Mock del backend ---
async def obtener_historial_completo(billetera_id: int) -> list:
    await asyncio.sleep(0.5) # Simula tiempo de carga
    return [
        {"fecha_hora": "10/06/2026 14:30", "origen": "Estación Central", "ruta": "Expreso 4", "monto": -3.50},
        {"fecha_hora": "09/06/2026 08:15", "origen": "Tomas Valle", "ruta": "Alimentador", "monto": -1.50},
        {"fecha_hora": "08/06/2026 18:40", "origen": "Recarga Virtual", "ruta": "Yape", "monto": 20.00},
        {"fecha_hora": "07/06/2026 09:10", "origen": "Naranjal", "ruta": "Expreso 2", "monto": -3.50},
        {"fecha_hora": "05/06/2026 12:00", "origen": "Recarga Efectivo", "ruta": "Taquilla", "monto": 10.00},
        {"fecha_hora": "04/06/2026 07:30", "origen": "Angamos", "ruta": "Expreso 1", "monto": -3.50},
    ]

def vista_historial(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    titulo = ft.Text("Historial de Movimientos", size=24, weight=ft.FontWeight.BOLD, color=paleta["texto_principal"])
    
    # Contenedor con scroll para la lista infinita
    lista_movimientos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    progreso = ft.ProgressRing(color=COLOR_PRIMARIO)

    def crear_fila_historial(item: dict) -> ft.Container:
        es_ingreso = item["monto"] > 0
        color_monto = "#22E0A6" if es_ingreso else COLOR_ERROR
        signo = "+" if es_ingreso else ""

        return ft.Container(
            padding=14,
            border_radius=14,
            bgcolor=paleta["tarjeta"],
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(item["ruta"], size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
                            ft.Text(f'{item["origen"]} · {item["fecha_hora"]}', size=11, color=paleta["texto_secundario"]),
                        ],
                    ),
                    ft.Text(f'{signo}S/ {abs(item["monto"]):.2f}', size=14, weight=ft.FontWeight.BOLD, color=color_monto),
                ],
            ),
        )

    # Cargar datos al abrir la vista
    async def cargar_datos():
        movimientos = await obtener_historial_completo(billetera_id)
        lista_movimientos.controls = [crear_fila_historial(m) for m in movimientos]
        progreso.visible = False
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