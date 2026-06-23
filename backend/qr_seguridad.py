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

LARGO_CHECKSUM = 6  # caracteres hexadecimales del checksum visible en el QR


def _clave_secreta() -> bytes:
    clave = os.getenv("QR_SECRET_KEY", "limapay-clave-demo-2026")
    return clave.encode("utf-8")


def generar_codigo_qr(placa: str) -> str:
    """Genera el texto exacto que debe codificarse en el QR físico de un bus."""
    placa = placa.strip().upper()
    checksum = hmac.new(_clave_secreta(), placa.encode("utf-8"), hashlib.sha256).hexdigest()[:LARGO_CHECKSUM]
    return f"{placa}|{checksum}"


def validar_codigo_qr(contenido: str) -> dict:
    """Valida el texto leído desde el QR escaneado. Devuelve {valido, placa, mensaje}."""
    if not contenido or "|" not in contenido:
        return {"valido": False, "placa": None, "mensaje": "Código QR no reconocido"}

    placa, _, checksum_recibido = contenido.strip().partition("|")
    placa = placa.strip().upper()
    checksum_recibido = checksum_recibido.strip().lower()
    checksum_esperado = hmac.new(_clave_secreta(), placa.encode("utf-8"), hashlib.sha256).hexdigest()[:LARGO_CHECKSUM]

    if not hmac.compare_digest(checksum_recibido, checksum_esperado):
        return {"valido": False, "placa": placa, "mensaje": "QR inválido o manipulado"}

    return {"valido": True, "placa": placa, "mensaje": "QR verificado"}
