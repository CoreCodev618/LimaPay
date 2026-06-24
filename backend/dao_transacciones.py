import logging
from backend.config_db import db

logger = logging.getLogger("limapay.transacciones")
logger.setLevel(logging.DEBUG)

TARIFA_POR_OPERADOR = {
    1: {"General": "General - Metropolitano", "Medio": "Medio - Metropolitano"},
    2: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    3: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    4: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    5: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
    6: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
    7: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
}
METODOS_PAGO_VALIDOS = (1, 2, 3, 4)
MONTO_MAXIMO_RECARGA = 500


class DAOTransacciones:

    def obtener_saldo(self, billetera_id: int) -> dict:
        sql = "SELECT saldo_actual, umbral_alerta FROM Billeteras WHERE id = %s AND estado_activa = TRUE LIMIT 1;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (billetera_id,))
                fila = cur.fetchone()
                if not fila:
                    return {"saldo": -1.0, "saldo_bajo": False}
                saldo = float(fila["saldo_actual"])
                return {"saldo": saldo, "saldo_bajo": saldo <= float(fila["umbral_alerta"])}
        except Exception as e:
            logger.error(f"obtener_saldo billetera_id={billetera_id}: {type(e).__name__}: {e}")
            return {"saldo": -1.0, "saldo_bajo": False}

    def procesar_pago(self, billetera_id: int, placa_bus: str, tipo_pasajero: str = "General",
                       medio_verificado: bool = True, ruta_id: int = 1, estacion_id: int = 1) -> dict:
        # Un pasajero "Medio" sin verificación aprobada paga tarifa General (anti-fraude).
        tipo_efectivo = tipo_pasajero if (tipo_pasajero == "General" or medio_verificado) else "General"

        sql_bus = "SELECT id, operador_id FROM Buses WHERE placa = %s LIMIT 1;"
        sql_bloquear = "SELECT saldo_actual, umbral_alerta, estado_activa FROM Billeteras WHERE id = %s FOR UPDATE;"
        sql_tarifa = "SELECT id, monto FROM Tarifas WHERE tipo_pasajero = %s LIMIT 1;"
        sql_desc = "UPDATE Billeteras SET saldo_actual = saldo_actual - %s WHERE id = %s RETURNING saldo_actual;"
        sql_viaje = "INSERT INTO Viajes (billetera_id, bus_id, ruta_id, tarifa_id, estacion_origen_id) VALUES (%s, %s, %s, %s, %s);"

        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_bus, (placa_bus.strip().upper(),))
                fila_bus = cur.fetchone()
                if not fila_bus:
                    return {"status": False, "mensaje": "Placa de bus no registrada en el sistema."}
                bus_id, operador_id = fila_bus["id"], fila_bus["operador_id"]

                cur.execute(sql_bloquear, (billetera_id,))
                fila_billetera = cur.fetchone()
                if not fila_billetera or not fila_billetera["estado_activa"]:
                    return {"status": False, "mensaje": "Billetera inactiva."}
                saldo_actual = float(fila_billetera["saldo_actual"])

                nombres_tarifa = TARIFA_POR_OPERADOR.get(operador_id, TARIFA_POR_OPERADOR[3])
                cur.execute(sql_tarifa, (nombres_tarifa.get(tipo_efectivo, nombres_tarifa["General"]),))
                fila_tarifa = cur.fetchone()
                if not fila_tarifa:
                    return {"status": False, "mensaje": "Tarifa no configurada para este operador."}
                tarifa_id, monto_tarifa = fila_tarifa["id"], float(fila_tarifa["monto"])

                if saldo_actual < monto_tarifa:
                    return {"status": False, "mensaje": f"Saldo insuficiente (S/ {saldo_actual:.2f})"}

                cur.execute(sql_desc, (monto_tarifa, billetera_id))
                nuevo_saldo = float(cur.fetchone()["saldo_actual"])

                cur.execute(sql_viaje, (billetera_id, bus_id, ruta_id, tarifa_id, estacion_id))

                logger.info(f"Viaje autorizado placa={placa_bus} tipo={tipo_efectivo} nuevo_saldo={nuevo_saldo}")
                aviso_tarifa = None
                if tipo_pasajero == "Medio" and tipo_efectivo == "General":
                    aviso_tarifa = "Se cobró tarifa General: tu medio pasaje aún no está verificado."

                return {
                    "status": True,
                    "mensaje": "Viaje Autorizado",
                    "nuevo_saldo": nuevo_saldo,
                    "saldo_bajo": nuevo_saldo <= float(fila_billetera["umbral_alerta"]),
                    "aviso_tarifa": aviso_tarifa,
                }
        except Exception as e:
            logger.error(f"procesar_pago: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de Consistencia"}

    def recargar_saldo(self, billetera_id: int, monto: float, metodo_pago_id: int) -> dict:
        if monto <= 0 or monto > MONTO_MAXIMO_RECARGA:
            return {"status": False, "mensaje": f"Monto inválido (entre S/.0.01 y S/.{MONTO_MAXIMO_RECARGA})"}
        if metodo_pago_id not in METODOS_PAGO_VALIDOS:
            return {"status": False, "mensaje": "Método de pago no válido"}
        sql_recarga = """
            UPDATE Billeteras SET saldo_actual = saldo_actual + %s
            WHERE id = %s AND estado_activa = TRUE RETURNING saldo_actual, umbral_alerta;
        """
        sql_auditoria = "INSERT INTO Recargas (billetera_id, metodo_pago_id, monto_ingresado) VALUES (%s, %s, %s);"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_recarga, (monto, billetera_id))
                fila = cur.fetchone()
                if not fila:
                    return {"status": False, "mensaje": "Billetera no encontrada o inactiva"}
                nuevo_saldo = float(fila["saldo_actual"])
                cur.execute(sql_auditoria, (billetera_id, metodo_pago_id, monto))
                logger.info(f"Recarga exitosa billetera={billetera_id} monto={monto}")
                return {"status": True, "mensaje": "Recarga exitosa", "nuevo_saldo": nuevo_saldo,
                         "saldo_bajo": nuevo_saldo <= float(fila["umbral_alerta"])}
        except Exception as e:
            logger.error(f"recargar_saldo: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD al recargar"}

    def obtener_historial(self, billetera_id: int, limite: int = 5) -> list:
        sql = """
            SELECT v.fecha_hora, ep.nombre AS origen, r.codigo_ruta AS ruta, t.monto * -1 AS monto
            FROM Viajes v
            JOIN Tarifas t ON t.id = v.tarifa_id
            JOIN Rutas r ON r.id = v.ruta_id
            JOIN Estaciones_Paraderos ep ON ep.id = v.estacion_origen_id
            WHERE v.billetera_id = %s
            UNION ALL
            SELECT r.fecha_hora, 'Recarga Virtual' AS origen, 'App' AS ruta, r.monto_ingresado AS monto
            FROM Recargas r WHERE r.billetera_id = %s
            ORDER BY fecha_hora DESC LIMIT %s;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (billetera_id, billetera_id, limite))
                return [{"fecha_hora": f["fecha_hora"].strftime("%d/%m/%Y %H:%M"), "origen": f["origen"],
                         "ruta": f["ruta"], "monto": float(f["monto"])} for f in cur.fetchall()]
        except Exception as e:
            logger.error(f"obtener_historial: {type(e).__name__}: {e}")
            return []

    def obtener_rutas_populares(self) -> list:
        sql = """
            SELECT ep.nombre AS estacion, r.codigo_ruta, COUNT(v.id) AS total_viajes
            FROM Viajes v
            JOIN Estaciones_Paraderos ep ON v.estacion_origen_id = ep.id
            JOIN Rutas r ON v.ruta_id = r.id
            GROUP BY ep.nombre, r.codigo_ruta ORDER BY total_viajes DESC LIMIT 5;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception as e:
            logger.error(f"obtener_rutas_populares: {type(e).__name__}: {e}")
            return []


dao_transacciones = DAOTransacciones()
