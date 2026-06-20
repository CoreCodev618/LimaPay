import logging
import psycopg2
from backend.config_db import db

logger = logging.getLogger("limapay.transacciones")

TARIFA_POR_OPERADOR = {
    1: 1,
    2: 2,
}

class DAOTransacciones:

    def obtener_saldo(self, billetera_id: int) -> float:
        sql = "SELECT saldo_actual FROM Billeteras WHERE id = %s AND estado_activa = TRUE LIMIT 1;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (billetera_id,))
                fila = cur.fetchone()
                if not fila:
                    return -1.0
                return float(fila["saldo_actual"])
        except Exception as e:
            logger.error(f"Error en obtener_saldo billetera_id={billetera_id}: {type(e).__name__}: {e}")
            return -1.0

    def procesar_pago(self, billetera_id: int, bus_id: int) -> dict:
        sql_bloquear = """
            SELECT b.saldo_actual, b.estado_activa, bs.operador_id
            FROM Billeteras AS b
            JOIN Buses AS bs ON bs.id = %s
            WHERE b.id = %s
            FOR UPDATE OF b;
        """
        sql_monto = "SELECT monto FROM Tarifas WHERE id = %s;"
        sql_desc = """
            UPDATE Billeteras
            SET saldo_actual = saldo_actual - %s
            WHERE id = %s
            RETURNING saldo_actual;
        """
        sql_viaje = """
            INSERT INTO Viajes (billetera_id, bus_id, ruta_id, tarifa_id, estacion_origen_id)
            VALUES (%s, %s, %s, %s, %s);
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_bloquear, (bus_id, billetera_id))
                fila = cur.fetchone()
                if not fila:
                    return {"status": False, "mensaje": "Bus o billetera no encontrado"}
                saldo_actual = float(fila["saldo_actual"])
                operador_id = int(fila["operador_id"])
                if not fila["estado_activa"]:
                    return {"status": False, "mensaje": "Billetera inactiva"}
                tarifa_id = TARIFA_POR_OPERADOR.get(operador_id, 3)
                cur.execute(sql_monto, (tarifa_id,))
                monto_tarifa = float(cur.fetchone()["monto"])
                if saldo_actual < monto_tarifa:
                    return {"status": False, "mensaje": f"Saldo insuficiente (S/.{saldo_actual:.2f})"}
                cur.execute(sql_desc, (monto_tarifa, billetera_id))
                nuevo_saldo = float(cur.fetchone()["saldo_actual"])
                cur.execute("SELECT id FROM Rutas WHERE operador_id = %s LIMIT 1;", (operador_id,))
                fila_ruta = cur.fetchone()
                ruta_id = fila_ruta["id"] if fila_ruta else 1
                cur.execute(sql_viaje, (billetera_id, bus_id, ruta_id, tarifa_id, 1))
                logger.info(f"Viaje autorizado: billetera={billetera_id}, nuevo_saldo={nuevo_saldo}")
                return {"status": True, "mensaje": "Viaje Autorizado", "nuevo_saldo": nuevo_saldo}
        except Exception as e:
            logger.error(f"Error en procesar_pago: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de Consistencia"}

    def recargar_saldo(self, billetera_id: int, monto: float, metodo_pago_id: int) -> dict:
        if monto <= 0 or monto > 500:
            return {"status": False, "mensaje": "Monto inválido (entre S/.0.01 y S/.500)"}
        if metodo_pago_id not in (1, 2, 3, 4):
            return {"status": False, "mensaje": "Método de pago no válido"}
        sql_recarga = """
            UPDATE Billeteras SET saldo_actual = saldo_actual + %s
            WHERE id = %s AND estado_activa = TRUE
            RETURNING saldo_actual;
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
                logger.info(f"Recarga exitosa: billetera={billetera_id}, monto={monto}")
                return {"status": True, "mensaje": "Recarga exitosa", "nuevo_saldo": nuevo_saldo}
        except Exception as e:
            logger.error(f"Error en recargar_saldo: {type(e).__name__}: {e}")
            return {"status": False, "mensaje": "Error de BD al recargar"}

    def obtener_historial(self, billetera_id: int, limite: int = 5) -> list:
        sql = """
            SELECT v.fecha_hora, ep.nombre AS origen, r.codigo_ruta AS ruta, t.monto * -1 AS monto
            FROM Viajes v
            JOIN Tarifas t ON t.id = v.tarifa_id
            JOIN Rutas r ON r.id = v.ruta_id
            JOIN Estaciones_Paraderos ep ON ep.id = v.estacion_origen_id
            WHERE v.billetera_id = %s
            ORDER BY v.fecha_hora DESC
            LIMIT %s;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (billetera_id, limite))
                filas = cur.fetchall()
                return [{"fecha_hora": f["fecha_hora"].strftime("%d/%m/%Y %H:%M"), "origen": f["origen"], "ruta": f["ruta"], "monto": float(f["monto"])} for f in filas]
        except Exception as e:
            logger.error(f"Error en obtener_historial: {type(e).__name__}: {e}")
            return []

dao_transacciones = DAOTransacciones()
