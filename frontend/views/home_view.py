import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO, obtener_paleta
from frontend.core.ui import ancho_responsive
from frontend.components.tarjeta_movimiento import crear_fila_historial
from frontend.components.alertas import mostrar_notificacion
from backend.dao_transacciones import dao_transacciones


def vista_home(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_cerrar_sesion=None, al_ir_scanner=None,
               al_ir_recarga=None, al_ir_historial=None, al_ir_dashboard=None, al_ir_perfil=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")
    nombre = datos_pasajero.get("nombre", "")

    # ---------- Encabezado ----------
    avatar = ft.CircleAvatar(
        content=ft.Text(nombre[0].upper() if nombre else "U", weight=ft.FontWeight.BOLD, color="#0A0E1A"),
        bgcolor=COLOR_PRIMARIO, radius=18,
    )
    encabezado = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
        ft.Row([avatar, ft.Text(f"Hola, {nombre}", size=18, weight=ft.FontWeight.W_600, color=paleta["texto_principal"])], spacing=12),
        ft.Row([
            ft.IconButton(icon=ft.Icons.PERSON_OUTLINE, icon_color=paleta["texto_secundario"], tooltip="Mi perfil",
                          on_click=lambda e: al_ir_perfil() if al_ir_perfil else None),
            ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=paleta["texto_secundario"], tooltip="Cerrar sesión",
                          on_click=lambda e: al_cerrar_sesion() if al_cerrar_sesion else None),
        ], spacing=0),
    ])

    # ---------- Tarjeta de saldo ----------
    texto_saldo = ft.Text("S/ --.--", size=34, weight=ft.FontWeight.BOLD, color="#0A0E1A")
    tarjeta_saldo = ft.Container(
        padding=24, border_radius=20,
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
                                     colors=[COLOR_PRIMARIO, COLOR_PRIMARIO_OSCURO]),
        content=ft.Column(spacing=2, controls=[ft.Text("Saldo disponible", size=13, color="#0A0E1A"), texto_saldo]),
    )

    async def cargar_saldo():
        info = dao_transacciones.obtener_saldo(billetera_id)
        texto_saldo.value = f"S/ {info['saldo']:.2f}"
        pagina.update()
        if info["saldo_bajo"]:
            mostrar_notificacion(pagina, "Tu saldo está bajo. ¡Recarga para evitar quedarte sin viajes!", tipo="advertencia")

    pagina.run_task(cargar_saldo)

    # ---------- Accesos rápidos ----------
    def acceso_rapido(icono: str, etiqueta: str, on_click=None) -> ft.Container:
        return ft.Container(
            width=104, padding=14, border_radius=16, bgcolor=paleta["tarjeta"], ink=True, on_click=on_click,
            content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[
                ft.Icon(icono, color=COLOR_PRIMARIO, size=24),
                ft.Text(etiqueta, size=12, color=paleta["texto_principal"], text_align=ft.TextAlign.CENTER),
            ]),
        )

    fila_accesos = ft.Row(wrap=True, spacing=12, run_spacing=12, alignment=ft.MainAxisAlignment.CENTER, controls=[
        acceso_rapido(ft.Icons.QR_CODE_SCANNER, "Escanear", lambda e: al_ir_scanner() if al_ir_scanner else None),
        acceso_rapido(ft.Icons.ADD_CARD, "Recargar", lambda e: al_ir_recarga() if al_ir_recarga else None),
        acceso_rapido(ft.Icons.HISTORY, "Historial", lambda e: al_ir_historial() if al_ir_historial else None),
        acceso_rapido(ft.Icons.BAR_CHART, "Top Rutas", lambda e: al_ir_dashboard() if al_ir_dashboard else None),
    ])

    # ---------- Historial reciente ----------
    lista_historial = ft.Column(spacing=10)

    async def cargar_historial():
        movimientos = dao_transacciones.obtener_historial(billetera_id, limite=5)
        lista_historial.controls = [crear_fila_historial(item, modo_oscuro) for item in movimientos]
        pagina.update()

    pagina.run_task(cargar_historial)

    contenido = ft.Container(
        width=ancho_responsive(pagina.width, maximo=420, margen=40, minimo=300),
        content=ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, controls=[
            encabezado, tarjeta_saldo, fila_accesos,
            ft.Text("Últimos movimientos", size=14, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
            lista_historial,
        ]),
    )

    def al_redimensionar(e):
        contenido.width = ancho_responsive(pagina.width, maximo=420, margen=40, minimo=300)
        pagina.update()

    pagina.on_resized = al_redimensionar

    return ft.Container(
        expand=True, alignment=ft.Alignment.TOP_CENTER, padding=20,
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                                     colors=[paleta["fondo_inicio"], paleta["fondo_fin"]]),
        content=contenido,
    )
