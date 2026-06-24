import flet as ft
import flet_charts as fc
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
            ft.Container(
                content=ft.IconButton(icon=ft.Icons.QR_CODE_SCANNER, icon_color=paleta["texto_principal"], tooltip="Escanear QR", on_click=lambda e: al_ir_scanner() if al_ir_scanner else None),
                bgcolor=paleta["tarjeta"], border_radius=20,
            ),
            ft.Container(
                content=ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=paleta["texto_principal"], tooltip="Cerrar sesión", on_click=lambda e: al_cerrar_sesion() if al_cerrar_sesion else None),
                bgcolor=paleta["tarjeta"], border_radius=20,
            ),
        ], spacing=10),
    ])

    # ---------- Tarjeta de saldo con Gráfico de fondo ----------
    texto_saldo = ft.Text("S/ --.--", size=46, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    
    grafico_lineas = fc.LineChart(
        data_series=[
            fc.LineChartData(
                points=[], 
                stroke_width=3, 
                color=COLOR_PRIMARIO, 
                curved=False, 
                below_line_bgcolor=COLOR_PRIMARIO + "33",
            )
        ],
        border=ft.Border(bottom=ft.BorderSide(0, "transparent")),
        left_axis=fc.ChartAxis(label_size=0), bottom_axis=fc.ChartAxis(label_size=0),
        horizontal_grid_lines=fc.ChartGridLines(width=0), 
        vertical_grid_lines=fc.ChartGridLines(width=0),
        min_y=0, 
        expand=True,
        interactive=True,
    )

    # Botón tipo píldora para recargar
    boton_recargar = ft.Container(
        content=ft.Row(spacing=6, controls=[
            ft.Icon(ft.Icons.ADD_CARD, color="#0A0E1A", size=18),
            ft.Text("Recargar", color="#0A0E1A", weight=ft.FontWeight.BOLD, size=13)
        ]),
        bgcolor=COLOR_PRIMARIO,
        padding=ft.Padding(14, 8, 14, 8),
        border_radius=20,
        ink=True,
        on_click=lambda e: al_ir_recarga() if al_ir_recarga else None
    )

    tarjeta_saldo = ft.Container(
        height=200, border_radius=24,
        gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT, colors=["#0D1321", "#1E2A44"]),
        content=ft.Stack([
            # Gráfico de lado a lado en la mitad inferior de la tarjeta
            ft.Container(content=grafico_lineas, alignment=ft.Alignment.BOTTOM_CENTER, padding=ft.Padding(0, 90, 0, 0), expand=True),
            
            ft.Container(
                padding=24, 
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(spacing=4, controls=[ft.Text("Saldo actual", size=14, color="#8A93A6"), texto_saldo]),
                        boton_recargar,
                    ]
                )
            ),
        ], expand=True),
    )

    # ---------- Historial reciente ----------
    lista_historial = ft.Column(spacing=10)

    async def cargar_datos_home():
        info = dao_transacciones.obtener_saldo(billetera_id)
        texto_saldo.value = f"S/ {info['saldo']:.2f}"
        if info["saldo_bajo"]:
            mostrar_notificacion(pagina, "Tu saldo está bajo. ¡Recarga!", tipo="advertencia")
        
        movimientos = dao_transacciones.obtener_historial(billetera_id, limite=10)
        lista_historial.controls = [crear_fila_historial(item, modo_oscuro) for item in movimientos[:5]]
        
        # Filtramos recargas para el gráfico
        recargas = [m for m in movimientos if m["monto"] > 0]
        recargas.reverse()
        
        # Asignamos x e y explícitamente para evitar problemas de parámetros posicionales
        puntos = [fc.LineChartDataPoint(x=i, y=r["monto"]) for i, r in enumerate(recargas)]
            
        if len(puntos) < 2:
            puntos = [fc.LineChartDataPoint(x=0, y=10), fc.LineChartDataPoint(x=1, y=15), fc.LineChartDataPoint(x=2, y=8), fc.LineChartDataPoint(x=3, y=info['saldo'] if info['saldo'] > 0 else 20)]
            
        grafico_lineas.data_series[0].points = puntos # CORRECCIÓN: Atributo es 'points'
        pagina.update()

    pagina.run_task(cargar_datos_home)

    contenido = ft.Container(
        width=ancho_responsive(pagina.width, maximo=420, margen=40, minimo=300),
        content=ft.Column(spacing=24, scroll=ft.ScrollMode.AUTO, controls=[
            encabezado, 
            tarjeta_saldo,
            ft.Text("Últimos movimientos", size=16, weight=ft.FontWeight.W_600, color=paleta["texto_principal"]),
            lista_historial,
        ]),
    )

    def al_redimensionar(e):
        contenido.width = ancho_responsive(pagina.width, maximo=420, margen=40, minimo=300)
        pagina.update()

    pagina.on_resized = al_redimensionar

    return ft.Container(
        expand=True, alignment=ft.Alignment.TOP_CENTER, padding=20,
        bgcolor="transparent",
        content=contenido,
    )