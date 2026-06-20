import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ERROR, obtener_paleta
from backend.dao_transacciones import dao_transacciones

async def procesar_pago_mock(billetera_id: int, placa_bus: str, tipo_pasajero: str = "General") -> dict:
    return dao_transacciones.procesar_pago(billetera_id, placa_bus, tipo_pasajero)

def vista_scanner(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")
    tipo_pasajero = datos_pasajero.get("tipo_pasajero", "General")

    texto_estado = ft.Text("Simulador de Escáner QR", size=18, color=paleta["texto_principal"], weight=ft.FontWeight.BOLD)
    
    campo_bus = ft.TextField(
        label="Placa del Bus (Ej: A1T-001, B2R-201)",
        value="A1T-001",
        width=300,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"],
        border_color="transparent",
        focused_border_color=COLOR_PRIMARIO,
        filled=True,
        border_radius=12
    )

    async def simular_escaneo(e):
        texto_estado.value = f"Procesando pago ({tipo_pasajero})..."
        texto_estado.color = paleta["texto_principal"]
        boton_simular.content = ft.ProgressRing(width=18, height=18, color="#0A0E1A", stroke_width=2)
        pagina.update()

        placa_bus = campo_bus.value.strip()
        resultado = await procesar_pago_mock(billetera_id, placa_bus, tipo_pasajero)

        boton_simular.content = ft.Text("Simular Lectura de QR", color="#0A0E1A", weight=ft.FontWeight.BOLD)

        if resultado["status"]:
            texto_estado.value = f"¡Pago Exitoso!\n{resultado['mensaje']}\nSaldo Restante: S/ {resultado['nuevo_saldo']:.2f}"
            texto_estado.color = COLOR_EXITO
        else:
            texto_estado.value = resultado.get("mensaje", "Saldo insuficiente o error.")
            texto_estado.color = COLOR_ERROR
        
        pagina.update()

    boton_simular = ft.Container(
        content=ft.Text("Simular Lectura de QR", color="#0A0E1A", weight=ft.FontWeight.BOLD),
        bgcolor=COLOR_PRIMARIO,
        border_radius=12,
        padding=15,
        alignment=ft.Alignment.CENTER,
        ink=True,
        on_click=simular_escaneo
    )

    boton_volver = ft.Button(
        content=ft.Text("Volver al inicio", color=paleta["texto_secundario"]),
        on_click=lambda e: al_volver_home(datos_pasajero) if al_volver_home else None
    )

    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        bgcolor=paleta["fondo_inicio"],
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.QR_CODE_SCANNER, size=80, color=COLOR_PRIMARIO),
                texto_estado, 
                campo_bus, 
                boton_simular, 
                boton_volver
            ]
        )
    )