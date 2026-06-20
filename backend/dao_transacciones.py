import logging
import psycopg2
from backend.config_db import db

logger = logging.getLogger("limapay.transacciones")
logger.setLevel(logging.DEBUG)

TARIFA_POR_OPERADOR = {
    # operador_id: {"General": nombre_tarifa, "Medio": nombre_tarifa}
    1: {"General": "General - Metropolitano", "Medio": "Medio - Metropolitano"},
    2: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    3: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    4: {"General": "General - Corredores", "Medio": "Medio - Corredores"},
    5: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
    6: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
    7: {"General": "Urbano Tradicional - Directo", "Medio": "Medio - Urbano Tradicional"},
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

    def procesar_pago(self, billetera_id: int, placa_bus: str, tipo_pasajero: str = "General") -> dict:
        sql_bus = "SELECT id, operador_id FROM Buses WHERE placa = %s LIMIT 1;"
        sql_bloquear = "SELECT saldo_actual, estado_activa FROM Billeteras WHERE id = %s FOR UPDATE;"
        sql_tarifa = "SELECT id, monto FROM Tarifas WHERE tipo_pasajero = %s LIMIT 1;"
        sql_desc = "UPDATE Billeteras SET saldo_actual = saldo_actual - %s WHERE id = %s RETURNING saldo_actual;"
        sql_viaje = "INSERT INTO Viajes (billetera_id, bus_id, ruta_id, tarifa_id, estacion_origen_id) VALUES (%s, %s, %s, %s, %s);"

        if tipo_pasajero not in ("General", "Medio"):
            tipo_pasajero = "General"

        try:
            with db.obtener_cursor() as cur:
                # 1. Buscar Bus por Placa
                cur.execute(sql_bus, (placa_bus.strip().upper(),))
                fila_bus = cur.fetchone()
                if not fila_bus:
                    return {"status": False, "mensaje": "Placa de bus no registrada en el sistema."}
                bus_id = fila_bus["id"]
                operador_id = fila_bus["operador_id"]

                # 2. Bloquear Billetera para evitar cobros dobles
                cur.execute(sql_bloquear, (billetera_id,))
                fila_billetera = cur.fetchone()
                if not fila_billetera or not fila_billetera["estado_activa"]:
                    return {"status": False, "mensaje": "Billetera inactiva."}
                saldo_actual = float(fila_billetera["saldo_actual"])

                # 3. Calcular Tarifa según el operador del bus Y el tipo de pasajero
                nombres_tarifa = TARIFA_POR_OPERADOR.get(operador_id, TARIFA_POR_OPERADOR[3])
                nombre_tarifa = nombres_tarifa.get(tipo_pasajero, nombres_tarifa["General"])
                cur.execute(sql_tarifa, (nombre_tarifa,))
                fila_tarifa = cur.fetchone()
                if not fila_tarifa:
                    return {"status": False, "mensaje": "Tarifa no configurada para este operador."}
                tarifa_id = fila_tarifa["id"]
                monto_tarifa = float(fila_tarifa["monto"])

                if saldo_actual < monto_tarifa:
                    return {"status": False, "mensaje": f"Saldo insuficiente (S/ {saldo_actual:.2f})"}

                # 4. Descontar Saldo y Registrar Viaje
                cur.execute(sql_desc, (monto_tarifa, billetera_id))
                nuevo_saldo = float(cur.fetchone()["saldo_actual"])
                
                cur.execute("SELECT id FROM Rutas WHERE operador_id = %s LIMIT 1;", (operador_id,))
                fila_ruta = cur.fetchone()
                ruta_id = fila_ruta["id"] if fila_ruta else 1
                
                cur.execute(sql_viaje, (billetera_id, bus_id, ruta_id, tarifa_id, 1))
                logger.info(f"Viaje autorizado: placa={placa_bus}, tipo_pasajero={tipo_pasajero}, nuevo_saldo={nuevo_saldo}")
                
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
            
            UNION ALL
            
            SELECT r.fecha_hora, 'Recarga Virtual' AS origen, 'App' AS ruta, r.monto_ingresado AS monto
            FROM Recargas r
            WHERE r.billetera_id = %s
            
            ORDER BY fecha_hora DESC
            LIMIT %s;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql, (billetera_id, billetera_id, limite))
                filas = cur.fetchall()
                return [{"fecha_hora": f["fecha_hora"].strftime("%d/%m/%Y %H:%M"), "origen": f["origen"], "ruta": f["ruta"], "monto": float(f["monto"])} for f in filas]
        except Exception as e:
            logger.error(f"Error en obtener_historial: {type(e).__name__}: {e}")
            return []
        
    def obtener_rutas_populares(self) -> list:
        sql = """
            SELECT ep.nombre AS estacion, r.codigo_ruta, COUNT(v.id) as total_viajes
            FROM Viajes v
            JOIN Estaciones_Paraderos ep ON v.estacion_origen_id = ep.id
            JOIN Rutas r ON v.ruta_id = r.id
            GROUP BY ep.nombre, r.codigo_ruta
            ORDER BY total_viajes DESC
            LIMIT 5;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception:
            return []

dao_transacciones = DAOTransacciones()