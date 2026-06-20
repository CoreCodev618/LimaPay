import asyncio
import flet as ft

from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO, COLOR_ERROR, obtener_paleta
from frontend.components.tarjeta_movimiento import crear_fila_historial
from backend.dao_transacciones import dao_transacciones

async def obtener_saldo(billetera_id: int) -> float:
    return dao_transacciones.obtener_saldo(billetera_id)

async def obtener_historial(billetera_id: int, limite: int = 5) -> list:
    return dao_transacciones.obtener_historial(billetera_id, limite)

def calcular_ancho_contenido(ancho_pagina: float | None) -> int:
    if not ancho_pagina:
        return 420
    return int(max(300, min(ancho_pagina - 40, 420)))

def vista_home(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_cerrar_sesion=None, al_ir_scanner=None, al_ir_recarga=None, al_ir_historial=None, al_ir_dashboard=None  ) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")
    nombre = datos_pasajero.get("nombre", "")

# ---------- Encabezado ----------
    avatar = ft.CircleAvatar(
        content=ft.Text(nombre[0].upper() if nombre else "U", weight=ft.FontWeight.BOLD, color="#0A0E1A"),
        bgcolor=COLOR_PRIMARIO,
        radius=18,
    )
    texto_saludo = ft.Text(f"Hola, {nombre}", size=18, weight=ft.FontWeight.W_600, color=paleta["texto_principal"])

    boton_cerrar_sesion = ft.IconButton(
        icon=ft.Icons.LOGOUT,
        icon_color=paleta["texto_secundario"],
        tooltip="Cerrar sesión",
        on_click=lambda e: al_cerrar_sesion() if al_cerrar_sesion else None,
    )

    encabezado = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row([avatar, texto_saludo], spacing=12), 
            boton_cerrar_sesion
        ],
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
            crear_acceso_rapido(ft.Icons.QR_CODE_SCANNER, "Escanear", on_click=lambda e: al_ir_scanner() if al_ir_scanner else None),
            crear_acceso_rapido(ft.Icons.ADD_CARD, "Recargar", on_click=lambda e: al_ir_recarga() if al_ir_recarga else None),
            crear_acceso_rapido(ft.Icons.HISTORY, "Historial", on_click=lambda e: al_ir_historial() if al_ir_historial else None),
            crear_acceso_rapido(ft.Icons.BAR_CHART, "Top Rutas", on_click=lambda e: al_ir_dashboard() if al_ir_dashboard else None),
        ],
    )

    # ---------- Historial de transacciones ----------
    lista_historial = ft.Column(spacing=10)

    async def cargar_historial():
        movimientos = await obtener_historial(billetera_id, limite=5)
        lista_historial.controls = [crear_fila_historial(item, modo_oscuro) for item in movimientos]
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