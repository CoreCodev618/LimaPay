import hashlib
import logging
import psycopg2
from backend.config_db import db

logger = logging.getLogger("limapay.pasajeros")
logger.setLevel(logging.DEBUG)


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _validar_dni(dni: str) -> bool:
    return isinstance(dni, str) and len(dni) == 8 and dni.isdigit()


class DAOPasajeros:

    def iniciar_sesion(self, dni: str, clave: str) -> dict:
        if not _validar_dni(dni):
            return {"status": False, "mensaje": "DNI inválido (debe tener 8 dígitos)"}
        sql = """
            SELECT p.id AS pasajero_id, p.nombre, p.tipo_pasajero, p.medio_pasaje_verificado,
                   b.id AS billetera_id, b.umbral_alerta
            FROM Pasajeros p JOIN Billeteras b ON b.pasajero_id = p.id
            WHERE p.dni = %s AND p.clave = %s AND b.estado_activa = TRUE LIMIT 1;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (dni, _hash(clave)))
                fila = cur.fetchone()
                if not fila:
                    return {"status": False, "mensaje": "Credenciales incorrectas"}
                logger.info(f"Login exitoso DNI={dni}")
                return {
                    "status": True,
                    "pasajero_id": int(fila["pasajero_id"]),
                    "billetera_id": int(fila["billetera_id"]),
                    "nombre": fila["nombre"],
                    "tipo_pasajero": fila["tipo_pasajero"],
                    "medio_pasaje_verificado": bool(fila["medio_pasaje_verificado"]),
                    "umbral_alerta": float(fila["umbral_alerta"]),
                }
        except Exception as e:
            logger.error(f"iniciar_sesion DNI={dni}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error de BD: {type(e).__name__}"}

    def registrar_pasajero(self, dni: str, nombre: str, email: str, clave: str, tipo_pasajero: str = "General",
                            pregunta_seguridad: str = None, respuesta_seguridad: str = None) -> dict:
        if not _validar_dni(dni):
            return {"status": False, "mensaje": "DNI inválido (debe tener 8 dígitos numéricos)"}
        if not nombre or not nombre.strip():
            return {"status": False, "mensaje": "Nombre inválido"}
        if not email or "@" not in email:
            return {"status": False, "mensaje": "Email inválido"}
        if not clave or len(clave) < 4:
            return {"status": False, "mensaje": "La contraseña debe tener al menos 4 caracteres"}
        if not pregunta_seguridad or not respuesta_seguridad:
            return {"status": False, "mensaje": "Debes registrar una pregunta de seguridad"}

        tipo_pasajero = tipo_pasajero if tipo_pasajero in ("General", "Medio") else "General"
        verificado = tipo_pasajero == "General"  # "Medio" requiere verificación posterior

        sql_p = """
            INSERT INTO Pasajeros (dni, nombre, email, clave, tipo_pasajero, medio_pasaje_verificado,
                                    pregunta_seguridad, respuesta_seguridad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        sql_b = "INSERT INTO Billeteras (pasajero_id, saldo_actual, estado_activa) VALUES (%s, 0.00, TRUE) RETURNING id;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_p, (dni, nombre.strip(), email.strip().lower(), _hash(clave), tipo_pasajero,
                                     verificado, pregunta_seguridad, _hash(respuesta_seguridad.strip().lower())))
                pasajero_id = cur.fetchone()["id"]
                cur.execute(sql_b, (pasajero_id,))
                billetera_id = cur.fetchone()["id"]
                logger.info(f"Pasajero registrado id={pasajero_id} tipo={tipo_pasajero}")
                return {"status": True, "pasajero_id": pasajero_id, "billetera_id": billetera_id,
                        "requiere_verificacion": tipo_pasajero == "Medio"}
        except psycopg2.errors.UniqueViolation:
            return {"status": False, "mensaje": "DNI o email ya registrado"}
        except Exception as e:
            logger.error(f"registrar_pasajero DNI={dni}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error interno: {type(e).__name__}"}

    def obtener_perfil(self, pasajero_id: int) -> dict:
        sql = """
            SELECT p.dni, p.nombre, p.email, p.tipo_pasajero, p.medio_pasaje_verificado,
                   b.saldo_actual, b.umbral_alerta
            FROM Pasajeros p JOIN Billeteras b ON b.pasajero_id = p.id
            WHERE p.id = %s LIMIT 1;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (pasajero_id,))
                fila = cur.fetchone()
                if not fila:
                    return {"status": False, "mensaje": "Pasajero no encontrado"}
                return {"status": True, **fila, "saldo_actual": float(fila["saldo_actual"]),
                         "umbral_alerta": float(fila["umbral_alerta"])}
        except Exception as e:
            logger.error(f"obtener_perfil id={pasajero_id}: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": f"Error de BD: {type(e).__name__}"}

    def actualizar_umbral_alerta(self, billetera_id: int, nuevo_umbral: float) -> dict:
        if nuevo_umbral < 0:
            return {"status": False, "mensaje": "El umbral no puede ser negativo"}
        try:
            with db.obtener_cursor() as cur:
                cur.execute("UPDATE Billeteras SET umbral_alerta = %s WHERE id = %s;", (nuevo_umbral, billetera_id))
                return {"status": True, "mensaje": "Umbral de alerta actualizado"}
        except Exception as e:
            logger.error(f"actualizar_umbral_alerta: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    # ---------- Recuperación de contraseña (vía pregunta de seguridad) ----------

    def obtener_pregunta_seguridad(self, dni: str) -> dict:
        if not _validar_dni(dni):
            return {"status": False, "mensaje": "DNI inválido"}
        try:
            with db.obtener_cursor() as cur:
                cur.execute("SELECT pregunta_seguridad FROM Pasajeros WHERE dni = %s LIMIT 1;", (dni,))
                fila = cur.fetchone()
                if not fila or not fila["pregunta_seguridad"]:
                    return {"status": False, "mensaje": "No existe una cuenta con ese DNI"}
                return {"status": True, "pregunta_seguridad": fila["pregunta_seguridad"]}
        except Exception as e:
            logger.error(f"obtener_pregunta_seguridad: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    def restablecer_clave(self, dni: str, respuesta_seguridad: str, nueva_clave: str) -> dict:
        if not nueva_clave or len(nueva_clave) < 4:
            return {"status": False, "mensaje": "La nueva contraseña debe tener al menos 4 caracteres"}
        sql = """
            UPDATE Pasajeros SET clave = %s
            WHERE dni = %s AND respuesta_seguridad = %s RETURNING id;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (_hash(nueva_clave), dni, _hash(respuesta_seguridad.strip().lower())))
                if not cur.fetchone():
                    return {"status": False, "mensaje": "Respuesta de seguridad incorrecta"}
                logger.info(f"Clave restablecida para DNI={dni}")
                return {"status": True, "mensaje": "Contraseña actualizada correctamente"}
        except Exception as e:
            logger.error(f"restablecer_clave: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    def cambiar_clave(self, pasajero_id: int, clave_actual: str, nueva_clave: str) -> dict:
        if not nueva_clave or len(nueva_clave) < 4:
            return {"status": False, "mensaje": "La nueva contraseña debe tener al menos 4 caracteres"}
        sql = "UPDATE Pasajeros SET clave = %s WHERE id = %s AND clave = %s RETURNING id;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (_hash(nueva_clave), pasajero_id, _hash(clave_actual)))
                if not cur.fetchone():
                    return {"status": False, "mensaje": "Contraseña actual incorrecta"}
                return {"status": True, "mensaje": "Contraseña actualizada correctamente"}
        except Exception as e:
            logger.error(f"cambiar_clave: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    # ---------- Verificación de medio pasaje ----------

    def solicitar_verificacion_medio_pasaje(self, pasajero_id: int, codigo_institucional: str) -> dict:
        if not codigo_institucional or len(codigo_institucional.strip()) < 4:
            return {"status": False, "mensaje": "Ingresa un código institucional válido"}
        try:
            with db.obtener_cursor() as cur:
                cur.execute("SELECT 1 FROM Solicitudes_Medio_Pasaje WHERE pasajero_id = %s AND estado = 'Pendiente';", (pasajero_id,))
                if cur.fetchone():
                    return {"status": False, "mensaje": "Ya tienes una solicitud pendiente de revisión"}
                cur.execute(
                    "INSERT INTO Solicitudes_Medio_Pasaje (pasajero_id, codigo_institucional) VALUES (%s, %s);",
                    (pasajero_id, codigo_institucional.strip()),
                )
                logger.info(f"Solicitud de medio pasaje creada para pasajero_id={pasajero_id}")
                return {"status": True, "mensaje": "Solicitud enviada. Será revisada en 24-48 horas."}
        except Exception as e:
            logger.error(f"solicitar_verificacion_medio_pasaje: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    def resolver_verificacion_simulada(self, pasajero_id: int) -> dict:
        """Simula la aprobación automática de una solicitud pendiente (uso en demo/QA)."""
        sql_sol = """
            UPDATE Solicitudes_Medio_Pasaje SET estado = 'Aprobado', fecha_resolucion = CURRENT_TIMESTAMP
            WHERE pasajero_id = %s AND estado = 'Pendiente' RETURNING id;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_sol, (pasajero_id,))
                if not cur.fetchone():
                    return {"status": False, "mensaje": "No hay solicitud pendiente"}
                cur.execute("UPDATE Pasajeros SET medio_pasaje_verificado = TRUE WHERE id = %s;", (pasajero_id,))
                return {"status": True, "mensaje": "Medio pasaje verificado correctamente"}
        except Exception as e:
            logger.error(f"resolver_verificacion_simulada: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}

    def estado_verificacion(self, pasajero_id: int) -> dict:
        sql = """
            SELECT estado FROM Solicitudes_Medio_Pasaje WHERE pasajero_id = %s
            ORDER BY fecha_solicitud DESC LIMIT 1;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (pasajero_id,))
                fila = cur.fetchone()
                return {"status": True, "estado": fila["estado"] if fila else "Sin solicitud"}
        except Exception as e:
            logger.error(f"estado_verificacion: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD"}


dao_pasajeros = DAOPasajeros()
