import asyncio
import base64
import os
import tempfile
import flet as ft
import flet_camera as fc
from frontend.tema.temas import COLOR_PRIMARIO, COLOR_EXITO, COLOR_ERROR, obtener_paleta
from frontend.core.ui import boton_primario, boton_volver, en_progreso, campo_texto
from frontend.components.alertas import mostrar_notificacion
from backend.dao_transacciones import dao_transacciones
from backend.qr_seguridad import validar_codigo_qr, generar_codigo_qr


def _leer_qr_desde_archivo(ruta: str) -> str | None:
    import cv2
    imagen = cv2.imread(ruta)
    if imagen is None:
        print(f"[QR] cv2.imread no pudo leer: {ruta}")
        return None
    detector = cv2.QRCodeDetector()
    texto, _, _ = detector.detectAndDecode(imagen)
    if texto:
        return texto
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    texto, _, _ = detector.detectAndDecode(gris)
    return texto or None


def _leer_qr_desde_bytes(foto_data) -> str | None:
    import cv2
    import numpy as np
    if isinstance(foto_data, str):
        if "," in foto_data:
            foto_data = foto_data.split(",", 1)[1]
        try:
            foto_data = base64.b64decode(foto_data)
        except Exception as e:
            print(f"[QR] Error decodificando base64: {e}")
            return None
    arreglo = np.frombuffer(foto_data, dtype=np.uint8)
    imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    if imagen is None:
        return None
    detector = cv2.QRCodeDetector()
    texto, _, _ = detector.detectAndDecode(imagen)
    if texto:
        return texto
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    texto, _, _ = detector.detectAndDecode(gris)
    return texto or None


def vista_scanner(pagina: ft.Page, modo_oscuro: bool, datos_pasajero: dict, al_volver_home=None) -> ft.Container:
    paleta = obtener_paleta(modo_oscuro)
    billetera_id = datos_pasajero.get("billetera_id")
    tipo_pasajero = datos_pasajero.get("tipo_pasajero", "General")
    medio_verificado = datos_pasajero.get("medio_pasaje_verificado", True)

    texto_estado = ft.Text(
        "Iniciando camara...",
        size=15,
        color=paleta["texto_secundario"],
        text_align=ft.TextAlign.CENTER,
    )

    camara = fc.Camera(width=320, height=280, preview_enabled=True)

    texto_boton = ft.Text("Capturar QR", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_capturar = boton_primario("Capturar QR", degradado=False)
    boton_capturar.content = texto_boton
    boton_capturar.disabled = True

    campo_qr_manual = campo_texto(
        paleta, "O escribe el codigo QR del bus", ft.Icons.EDIT_OUTLINED,
    )
    texto_boton_manual = ft.Text("Pagar con codigo", color="#0A0E1A", weight=ft.FontWeight.BOLD)
    boton_manual = boton_primario("Pagar con codigo", degradado=False)
    boton_manual.content = texto_boton_manual

    async def pagar_con_placa(placa: str, ruta_id: int, estacion_id: int):
        texto_estado.value = f"Procesando pago ({tipo_pasajero})..."
        texto_estado.color = paleta["texto_principal"]
        pagina.update()

        resultado = dao_transacciones.procesar_pago(billetera_id, placa, tipo_pasajero, medio_verificado, ruta_id, estacion_id)
        boton_capturar.content = texto_boton
        boton_capturar.disabled = False
        boton_manual.content = texto_boton_manual

        if resultado["status"]:
            texto_estado.value = (
                f"Pago Exitoso. {resultado['mensaje']}\n"
                f"Saldo Restante: S/ {resultado['nuevo_saldo']:.2f}"
            )
            texto_estado.color = COLOR_EXITO
            campo_qr_manual.value = ""
            if resultado.get("aviso_tarifa"):
                mostrar_notificacion(pagina, resultado["aviso_tarifa"], tipo="advertencia")
            elif resultado.get("saldo_bajo"):
                mostrar_notificacion(pagina, "Tu saldo quedó bajo. Considera recargar.", tipo="advertencia")
        else:
            texto_estado.value = resultado.get("mensaje", "Error al procesar el pago.")
            texto_estado.color = COLOR_ERROR
        pagina.update()

    def procesar_contenido_qr(contenido_qr: str):
        validacion = validar_codigo_qr(contenido_qr)
        print(f"[QR] Validacion: {validacion}")
        if not validacion["valido"]:
            texto_estado.value = validacion["mensaje"]
            texto_estado.color = COLOR_ERROR
            boton_capturar.disabled = False
            boton_capturar.content = texto_boton
            boton_manual.content = texto_boton_manual
            pagina.update()
            return
        pagina.run_task(pagar_con_placa, validacion["placa"], validacion["ruta_id"], validacion["estacion_id"])
        
    async def capturar_y_escanear(e):
        texto_estado.value = "Capturando foto..."
        texto_estado.color = paleta["texto_principal"]
        en_progreso(boton_capturar)
        boton_capturar.disabled = True
        pagina.update()

        contenido_qr = None
        ruta_tmp = os.path.join(tempfile.gettempdir(), "limapay_qr_scan.jpg")

        if hasattr(camara, "take_picture"):
            try:
                resultado_pic = await camara.take_picture()
                print(f"[QR] take_picture resultado tipo={type(resultado_pic)!r} valor={str(resultado_pic)[:120]!r}")
                if isinstance(resultado_pic, str) and os.path.exists(resultado_pic):
                    # Devolvió una ruta de archivo
                    contenido_qr = _leer_qr_desde_archivo(resultado_pic)
                    try:
                        os.remove(resultado_pic)
                    except Exception:
                        pass
                elif isinstance(resultado_pic, (bytes, str)):
                    # Devolvió bytes o base64
                    contenido_qr = _leer_qr_desde_bytes(resultado_pic)
                else:
                    print(f"[QR] take_picture tipo inesperado: {type(resultado_pic)}")
            except Exception as ex:
                print(f"[QR] take_picture error: {type(ex).__name__}: {ex}")

        elif hasattr(camara, "take_photo"):
            try:
                foto_data = await camara.take_photo()
                contenido_qr = _leer_qr_desde_bytes(foto_data)
            except Exception as ex:
                print(f"[QR] take_photo error: {type(ex).__name__}: {ex}")

        else:
            todos = [m for m in dir(camara) if not m.startswith("_")]
            captura = [m for m in todos if any(k in m.lower() for k in ("take", "captur", "photo", "pic", "snap"))]
            print(f"[QR] METODOS DE CAPTURA DISPONIBLES: {captura}")
            print(f"[QR] TODOS LOS METODOS: {todos}")
            boton_capturar.content = texto_boton
            boton_capturar.disabled = False
            texto_estado.value = "Captura no soportada. Usa el ingreso manual."
            texto_estado.color = COLOR_ERROR
            pagina.update()
            return

        boton_capturar.content = texto_boton
        boton_capturar.disabled = False

        if not contenido_qr:
            texto_estado.value = "No se detecto QR. Intenta mas cerca o usa el ingreso manual."
            texto_estado.color = COLOR_ERROR
            pagina.update()
            return

        print(f"[QR] Contenido detectado: {contenido_qr!r}")
        procesar_contenido_qr(contenido_qr)

    async def pagar_manual(e):
        contenido = (campo_qr_manual.value or "").strip()
        if not contenido:
            mostrar_notificacion(pagina, "Ingresa el código QR del bus", tipo="error")
            return
            
        # UX Fix: Si el usuario escribe solo la placa (ej. "A1T-001"), autogeneramos el código completo 
        # asumiendo Ruta 1 y Estación 1 por defecto, para que no tenga que adivinar el checksum a mano.
        if len(contenido) in (7, 8) and "|" not in contenido:
            contenido = generar_codigo_qr(contenido, 1, 1)

        en_progreso(boton_manual)
        pagina.update()
        procesar_contenido_qr(contenido)

    boton_capturar.on_click = capturar_y_escanear
    boton_manual.on_click = pagar_manual

    async def al_montar():
        await asyncio.sleep(0.5)
        try:
            camaras = await camara.get_available_cameras()
            print(f"[QR] Camaras: {camaras}")
            if camaras:
                trasera = next(
                    (c for c in camaras if "back" in str(c).lower() or "rear" in str(c).lower()),
                    camaras[0],
                )
                await camara.initialize(description=trasera, resolution_preset=fc.ResolutionPreset.HIGH)
            else:
                await camara.initialize(resolution_preset=fc.ResolutionPreset.HIGH)

            boton_capturar.disabled = False
            texto_estado.value = "Camara lista. Apunta al QR del bus y captura."
            texto_estado.color = paleta["texto_secundario"]
            pagina.update()
        except Exception as ex:
            print(f"[QR] Init error: {type(ex).__name__}: {ex}")
            texto_estado.value = "Camara no disponible. Usa el ingreso manual."
            texto_estado.color = COLOR_ERROR
            pagina.update()

    pagina.run_task(al_montar)

    return ft.Container(
        expand=True,
        bgcolor="transparent",
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Icon(ft.Icons.QR_CODE_SCANNER, size=40, color=COLOR_PRIMARIO),
                camara,
                texto_estado,
                boton_capturar,
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(expand=True, content=ft.Divider(color=paleta["texto_secundario"], thickness=0.5)),
                        ft.Text("  o  ", color=paleta["texto_secundario"], size=12),
                        ft.Container(expand=True, content=ft.Divider(color=paleta["texto_secundario"], thickness=0.5)),
                    ],
                ),
                ft.Container(
                    width=340,
                    content=ft.Column(spacing=10, controls=[campo_qr_manual, boton_manual]),
                ),
                ft.Container(height=4),
                boton_volver(paleta, datos_pasajero, al_volver_home),
            ],
        ),
    )