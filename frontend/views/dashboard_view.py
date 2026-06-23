import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, obtener_paleta
from frontend.core.ui import pantalla_simple
from backend.dao_transacciones import dao_transacciones


def vista_dashboard(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    lista_rutas = ft.Column(spacing=10, expand=True)
    grafico_container = ft.Container(visible=False)
    progreso = ft.ProgressRing(color=COLOR_PRIMARIO)

    def construir_grafico(rutas: list) -> ft.Container:
        if not rutas:
            return ft.Container()

        max_viajes = max(r["total_viajes"] for r in rutas)
        BAR_MAX_WIDTH = 220  # px ancho máximo de barra

        filas = []
        for i, item in enumerate(rutas):
            proporcion = item["total_viajes"] / max_viajes if max_viajes > 0 else 0
            ancho_barra = max(24, int(BAR_MAX_WIDTH * proporcion))
            # Opacidad varía de 55% (menos viajes) a 100% (más viajes)
            alfa = int(140 + 115 * proporcion)
            color_barra = COLOR_PRIMARIO + format(alfa, "02X")

            etiqueta = item["codigo_ruta"]
            if len(etiqueta) > 14:
                etiqueta = etiqueta[:13] + "…"

            filas.append(
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Etiqueta izquierda fija
                        ft.Container(
                            width=80,
                            content=ft.Text(
                                etiqueta, size=10,
                                color=paleta["texto_secundario"],
                                text_align=ft.TextAlign.RIGHT,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ),
                        # Barra
                        ft.Container(
                            width=ancho_barra,
                            height=22,
                            border_radius=ft.BorderRadius(0, 6, 6, 0),
                            bgcolor=color_barra,
                        ),
                        # Valor
                        ft.Text(
                            str(item["total_viajes"]),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_PRIMARIO,
                        ),
                    ],
                )
            )

        return ft.Container(
            padding=ft.Padding(14, 16, 14, 14),
            border_radius=16,
            bgcolor=paleta["tarjeta"],
            content=ft.Column(spacing=12, controls=[
                ft.Text(
                    "Viajes por ruta",
                    size=13, weight=ft.FontWeight.W_600,
                    color=paleta["texto_principal"],
                ),
                *filas,
            ]),
        )

    def fila_ruta(item, puesto: int) -> ft.Container:
        medallas = {1: "🥇", 2: "🥈", 3: "🥉"}
        badge = medallas.get(puesto, f"#{puesto}")
        return ft.Container(
            padding=14, border_radius=14, bgcolor=paleta["tarjeta"],
            content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(spacing=12, controls=[
                    ft.Text(badge, size=18),
                    ft.Column(spacing=2, controls=[
                        ft.Text(item["codigo_ruta"], size=14, weight=ft.FontWeight.W_600,
                                color=paleta["texto_principal"]),
                        ft.Text(item["estacion"], size=11, color=paleta["texto_secundario"]),
                    ]),
                ]),
                ft.Container(
                    padding=ft.Padding(10, 6, 10, 6),
                    border_radius=10,
                    bgcolor=COLOR_PRIMARIO + "20",
                    content=ft.Text(
                        f"{item['total_viajes']} viajes",
                        size=12, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO,
                    ),
                ),
            ]),
        )

    async def cargar_datos():
        rutas = dao_transacciones.obtener_rutas_populares()
        progreso.visible = False

        if not rutas:
            lista_rutas.controls = [
                ft.Text("Aun no hay datos de viajes.", color=paleta["texto_secundario"], italic=True)
            ]
        else:
            grafico_container.content = construir_grafico(rutas)
            grafico_container.visible = True
            lista_rutas.controls = [fila_ruta(r, i + 1) for i, r in enumerate(rutas)]

        pagina.update()

    pagina.run_task(cargar_datos)

    return pantalla_simple(
        paleta,
        "Top Rutas",
        [progreso, grafico_container, ft.Container(height=4), lista_rutas],
        datos_pasajero,
        al_volver_home,
        subtitulo="Top 5 por estacion de origen",
    )