"""
Generación y validación del contenido de los QR físicos pegados en cada bus.

Cada QR contiene: PLACA|CHECKSUM
El checksum es un HMAC-SHA256 truncado de la placa, firmado con una clave secreta
del sistema (QR_SECRET_KEY en .env). Esto evita que cualquiera pueda fabricar un QR
válido escribiendo la placa a mano en un generador online: necesitaría conocer la clave.

No es un sistema criptográfico de producción, pero impide la falsificación trivial.
"""
import hashlib
import hmac
import os

LARGO_CHECKSUM = 6

def _clave_secreta() -> bytes:
    clave = os.getenv("QR_SECRET_KEY", "limapay-clave-demo-2026")
    return clave.encode("utf-8")

def generar_codigo_qr(placa: str, ruta_id: int, estacion_id: int) -> str:
    placa = placa.strip().upper()
    # Ahora agrupamos Placa, Ruta y Estación
    datos = f"{placa}|{ruta_id}|{estacion_id}"
    checksum = hmac.new(_clave_secreta(), datos.encode("utf-8"), hashlib.sha256).hexdigest()[:LARGO_CHECKSUM]
    return f"{datos}|{checksum}"

def validar_codigo_qr(contenido: str) -> dict:
    if not contenido or contenido.count("|") != 3:
        return {"valido": False, "placa": None, "mensaje": "Formato QR inválido. Usa los nuevos QRs."}

    # Desempaquetamos los 4 valores del código escaneado
    placa, ruta_id, estacion_id, checksum_recibido = contenido.strip().split("|")
    placa = placa.strip().upper()
    checksum_recibido = checksum_recibido.strip().lower()
    
    datos = f"{placa}|{ruta_id}|{estacion_id}"
    checksum_esperado = hmac.new(_clave_secreta(), datos.encode("utf-8"), hashlib.sha256).hexdigest()[:LARGO_CHECKSUM]

    if not hmac.compare_digest(checksum_recibido, checksum_esperado):
        return {"valido": False, "placa": placa, "mensaje": "QR inválido o manipulado"}

    return {
        "valido": True, 
        "placa": placa, 
        "ruta_id": int(ruta_id), 
        "estacion_id": int(estacion_id), 
        "mensaje": "QR verificado"
    }