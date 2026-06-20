import flet as ft
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ERROR, obtener_paleta
from backend.dao_transacciones import dao_transacciones

async def procesar_pago_mock(billetera_id: int, bus_id: int) -> dict:
    return dao_transacciones.procesar_pago(billetera_id, bus_id)

def vista_scanner(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")

    texto_estado = ft.Text("Simulador de Escáner", size=18, color=paleta["texto_principal"], weight=ft.FontWeight.BOLD)
    
    campo_bus = ft.TextField(
        label="ID del Bus (Simulado)",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200,
        bgcolor=paleta["campo"],
        color=paleta["texto_principal"]
    )

    async def simular_escaneo(e):
        texto_estado.value = "Procesando pago con la Base de Datos..."
        texto_estado.color = paleta["texto_principal"]
        pagina.update()

        try:
            bus_id = int(campo_bus.value)
            
            resultado = await procesar_pago_mock(billetera_id, bus_id) 

            if resultado["status"]:
                texto_estado.value = f"¡Pago Exitoso!\n{resultado['mensaje']}\nSaldo: S/ {resultado['nuevo_saldo']:.2f}"
                texto_estado.color = COLOR_EXITO
            else:
                texto_estado.value = resultado.get("mensaje", "Saldo insuficiente o error.")
                texto_estado.color = COLOR_ERROR
                
        except Exception as ex:
            texto_estado.value = "Error: Ingresa un ID de bus válido."
            texto_estado.color = COLOR_ERROR
        
        pagina.update()

    boton_simular = ft.Button(
        content=ft.Text("Simular Lectura de QR", color="#0A0E1A", weight=ft.FontWeight.BOLD),
        bgcolor=COLOR_PRIMARIO,
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
            controls=[texto_estado, campo_bus, boton_simular, boton_volver]
        )
    )