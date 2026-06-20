import asyncio
import flet as ft

from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO, COLOR_ERROR, obtener_paleta


# --- Mocks temporales del backend (reemplazar por: from backend.dao_transacciones import ...) ---
async def obtener_saldo(billetera_id: int) -> float:
    await asyncio.sleep(0.6)
    return 25.50


async def obtener_historial(billetera_id: int, limite: int = 5) -> list:
    await asyncio.sleep(0.6)
    return [
        {"fecha_hora": "10/06/2026 14:30", "origen": "Estación Central", "ruta": "Expreso 4", "monto": -3.50},
        {"fecha_hora": "09/06/2026 08:15", "origen": "Tomas Valle", "ruta": "Alimentador", "monto": -1.50},
        {"fecha_hora": "08/06/2026 18:40", "origen": "Recarga Virtual", "ruta": "Yape", "monto": 20.00},
    ][:limite]


def calcular_ancho_contenido(ancho_pagina: float | None) -> int:
    """Contenido de 420px en pantallas grandes, se achica en pantallas angostas (mínimo 300px)."""
    if not ancho_pagina:
        return 420
    return int(max(300, min(ancho_pagina - 40, 420)))


def vista_home(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_cerrar_sesion=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")
    nombre = datos_pasajero.get("nombre", "")

    # ---------- Encabezado ----------
    texto_saludo = ft.Text(f"Hola, {nombre} 👋", size=18, weight=ft.FontWeight.W_600, color=paleta["texto_principal"])

    boton_cerrar_sesion = ft.IconButton(
        icon=ft.Icons.LOGOUT,
        icon_color=paleta["texto_secundario"],
        tooltip="Cerrar sesión",
        on_click=lambda e: al_cerrar_sesion() if al_cerrar_sesion else None,
    )

    encabezado = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[texto_saludo, boton_cerrar_sesion],
    )

    # ---------- Tarjeta de saldo ----------
    texto_saldo = ft.Text("S/ --.--", size=34, weight=ft.FontWeight.BOLD, color="#0A0E1A")

    tarjeta_saldo = ft.Container(
        padding=24,
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO],
        ),
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text("Saldo disponible", size=13, color="#0A0E1A"),
                texto_saldo,
            ],
        ),
    )

    async def cargar_saldo():
        saldo = await obtener_saldo(billetera_id)
        texto_saldo.value = f"S/ {saldo:.2f}"
        pagina.update()

    pagina.run_task(cargar_saldo)

    # ---------- Accesos rápidos ----------
    def crear_acceso_rapido(icono: str, etiqueta: str, on_click=None) -> ft.Container:
        return ft.Container(
            width=104,
            padding=14,
            border_radius=16,
            bgcolor=paleta["tarjeta"],
            ink=True,
            on_click=on_click,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(icono, color=COLOR_PRIMARIO, size=24),
                    ft.Text(etiqueta, size=12, color=paleta["texto_principal"], text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

    fila_accesos_rapidos = ft.Row(
        wrap=True,
        spacing=12,
        run_spacing=12,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            crear_acceso_rapido(ft.Icons.QR_CODE_SCANNER, "Escanear"),
            crear_acceso_rapido(ft.Icons.ADD_CARD, "Recargar"),
            crear_acceso_rapido(ft.Icons.HISTORY, "Historial"),
        ],
    )

    # ---------- Historial de transacciones ----------
    lista_historial = ft.Column(spacing=10)

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

    async def cargar_historial():
        movimientos = await obtener_historial(billetera_id, limite=5)
        lista_historial.controls = [crear_fila_historial(item) for item in movimientos]
        pagina.update()

    pagina.run_task(cargar_historial)

    # ---------- Composición de la pantalla ----------
    contenido = ft.Container(
        width=calcular_ancho_contenido(pagina.width),
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                encabezado,
                tarjeta_saldo,
                fila_accesos_rapidos,
                ft.Text("Últimos movimientos", size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
                lista_historial,
            ],
        ),
    )

    def al_redimensionar(e):
        contenido.width = calcular_ancho_contenido(pagina.width)
        pagina.update()

    pagina.on_resized = al_redimensionar

    return ft.Container(
        expand=True,
        alignment=ft.Alignment.TOP_CENTER,
        padding=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[paleta["fondo_inicio"], paleta["fondo_fin"]],
        ),
        content=contenido,
    )

