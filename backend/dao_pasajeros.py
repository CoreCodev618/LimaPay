import hashlib
import logging
import psycopg2
from backend.config_db import db

logger = logging.getLogger("limapay.pasajeros")
logger.setLevel(logging.DEBUG)

def _hashear_clave(clave: str) -> str:
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()

class DAOPasajeros:
    def iniciar_sesion(self, dni: str, clave: str) -> dict:
        if not isinstance(dni, str) or len(dni) != 8 or not dni.isdigit():
            return {"status": False, "mensaje": "DNI inválido (debe tener 8 dígitos)"}
        clave_hash = _hashear_clave(clave)
        logger.debug(f"Intentando login para DNI={dni}")
        sql = """
            SELECT p.id AS pasajero_id, p.nombre, b.id AS billetera_id
            FROM Pasajeros p
            JOIN Billeteras b ON b.pasajero_id = p.id
            WHERE p.dni = %s AND p.clave = %s AND b.estado_activa = TRUE
            LIMIT 1;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (dni, clave_hash))
                fila = cur.fetchone()
                if not fila:
                    logger.warning(f"Credenciales incorrectas para DNI={dni}")
                    return {"status": False, "mensaje": "Credenciales incorrectas"}
                logger.info(f"Login exitoso para DNI={dni}")
                return {
                    "status": True,
                    "pasajero_id": int(fila["pasajero_id"]),
                    "billetera_id": int(fila["billetera_id"]),
                    "nombre": str(fila["nombre"])
                }
        except Exception as e:
            logger.error(f"Error en iniciar_sesion DNI={dni}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error de BD: {type(e).__name__}"}

    def registrar_pasajero(self, dni: str, nombre: str, email: str, clave: str) -> dict:
        if not dni or len(dni) != 8 or not dni.isdigit():
            return {"status": False, "mensaje": "DNI inválido (debe tener 8 dígitos numéricos)"}
        if not nombre or not nombre.strip():
            return {"status": False, "mensaje": "Nombre inválido"}
        if not email or "@" not in email:
            return {"status": False, "mensaje": "Email inválido"}
        if not clave or len(clave) < 4:
            return {"status": False, "mensaje": "La contraseña debe tener al menos 4 caracteres"}
        clave_hash = _hashear_clave(clave)
        logger.debug(f"Registrando pasajero DNI={dni}, email={email}")
        sql_p = "INSERT INTO Pasajeros (dni, nombre, email, clave) VALUES (%s, %s, %s, %s) RETURNING id;"
        sql_b = "INSERT INTO Billeteras (pasajero_id, saldo_actual, estado_activa) VALUES (%s, 0.00, TRUE) RETURNING id;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_p, (dni, nombre.strip(), email.strip().lower(), clave_hash))
                pasajero_id = cur.fetchone()["id"]
                cur.execute(sql_b, (pasajero_id,))
                billetera_id = cur.fetchone()["id"]
                logger.info(f"Pasajero registrado: id={pasajero_id}, billetera_id={billetera_id}")
                return {"status": True, "pasajero_id": pasajero_id, "billetera_id": billetera_id}
        except psycopg2.errors.UniqueViolation as e:
            logger.warning(f"UniqueViolation al registrar DNI={dni}: {e}")
            return {"status": False, "mensaje": "DNI o email ya registrado"}
        except Exception as e:
            logger.error(f"Error en registrar_pasajero DNI={dni}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error interno: {type(e).__name__}"}

    def obtener_perfil(self, pasajero_id: int) -> dict:
        sql = "SELECT dni, nombre, email FROM Pasajeros WHERE id = %s LIMIT 1;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (pasajero_id,))
                fila = cur.fetchone()
                if not fila:
                    return {"status": False, "mensaje": "Pasajero no encontrado"}
                return {"status": True, "dni": fila["dni"], "nombre": fila["nombre"], "email": fila["email"]}
        except Exception as e:
            logger.error(f"Error en obtener_perfil id={pasajero_id}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error de BD: {type(e).__name__}"}

dao_pasajeros = DAOPasajeros()