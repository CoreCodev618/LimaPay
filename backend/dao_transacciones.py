import psycopg2
from backend.config_db import db

class DAOTransacciones:
    def obtener_saldo(self,billetera_id:int)->float:
        sql="SELECT saldo_actual FROM Billeteras WHERE id=%s AND estado_activa=TRUE LIMIT 1;"
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql,(billetera_id,))
                fila=cur.fetchone()
                if not fila:
                    return -1.0
                return float(fila["saldo_actual"])
        except Exception as e:
            return -1.0

    def procesar_pago(self,billetera_id:int,bus_id:int)->dict:
        TARIFA_POR_OPERADOR={1:1,2:3,3:3,4:3,5:5,6:5,7:5}
        sql_bloquear="""
            SELECT b.saldo_actual, b.estado_activa, bs.operador_id
            FROM Billeteras b, Buses bs
            WHERE b.id=%s AND bs.id=%s
            FOR UPDATE OF b;
        """
        sql_desc="UPDATE Billeteras SET saldo_actual=saldo_actual-(SELECT monto FROM Tarifas WHERE id=%s) WHERE id=%s RETURNING saldo_actual;"
        sql_viaje="INSERT INTO Viajes (billetera_id,bus_id,ruta_id,tarifa_id,estacion_origen_id) VALUES (%s,%s,%s,%s,%s);"
        
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_bloquear,(billetera_id,bus_id))
                fila=cur.fetchone()
                if not fila:
                    raise ValueError("Error de Consistencia")
                
                saldo_actual=float(fila["saldo_actual"])
                operador_id=int(fila["operador_id"])
                
                if not fila["estado_activa"]:
                    return {"status":False,"mensaje":"Billetera inactiva","nuevo_saldo":saldo_actual}
                
                tarifa_id=TARIFA_POR_OPERADOR.get(operador_id,5)
                cur.execute("SELECT monto FROM Tarifas WHERE id=%s;",(tarifa_id,))
                monto_tarifa=float(cur.fetchone()["monto"])
                
                if saldo_actual<monto_tarifa:
                    return {"status":False,"mensaje":"Saldo Insuficiente","nuevo_saldo":saldo_actual}
                
                cur.execute("SELECT id FROM Rutas WHERE operador_id=%s LIMIT 1;",(operador_id,))
                r=cur.fetchone()
                ruta_id=int(r["id"]) if r else 1
                
                cur.execute("SELECT id FROM Estaciones_Paraderos LIMIT 1;")
                e=cur.fetchone()
                estacion_id=int(e["id"]) if e else 1
                
                cur.execute(sql_desc,(tarifa_id,billetera_id))
                nuevo_saldo=float(cur.fetchone()["saldo_actual"])
                cur.execute(sql_viaje,(billetera_id,bus_id,ruta_id,tarifa_id,estacion_id))
                
                return {"status":True,"mensaje":"Viaje Autorizado","nuevo_saldo":nuevo_saldo}
        except ValueError as ve:
            return {"status":False,"mensaje":str(ve),"nuevo_saldo":0.0}
        except Exception as e:
            return {"status":False,"mensaje":"Error de Consistencia","nuevo_saldo":0.0}

    def recargar_saldo(self,billetera_id:int,monto:float,metodo_pago_id:int)->dict:
        if not isinstance(monto,(int,float)) or monto<1.0:
            return {"status":False,"mensaje":"Monto inválido"}
        if metodo_pago_id not in (1,2,3,4):
            return {"status":False,"mensaje":"Método inválido"}
        
        monto=round(float(monto),2)
        sql_upd="UPDATE Billeteras SET saldo_actual=saldo_actual+%s WHERE id=%s AND estado_activa=TRUE RETURNING saldo_actual;"
        sql_ins="INSERT INTO Recargas (billetera_id,metodo_pago_id,monto_ingresado) VALUES (%s,%s,%s);"
        
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql_upd,(monto,billetera_id))
                fila=cur.fetchone()
                if not fila:
                    raise ValueError("Billetera inválida")
                nuevo_saldo=float(fila["saldo_actual"])
                cur.execute(sql_ins,(billetera_id,metodo_pago_id,monto))
                return {"status":True,"mensaje":"Recarga exitosa","nuevo_saldo":nuevo_saldo}
        except ValueError as ve:
            return {"status":False,"mensaje":str(ve)}
        except Exception as e:
            return {"status":False,"mensaje":"Error interno"}

    def obtener_historial(self,billetera_id:int,limite:int=5)->list:
        if limite<1: limite=5
        sql="""
            SELECT TO_CHAR(v.fecha_hora,'DD/MM/YYYY HH24:MI') AS fecha_hora, ep.nombre AS origen, r.codigo_ruta AS ruta, -t.monto AS monto
            FROM Viajes v
            JOIN Tarifas t ON t.id=v.tarifa_id
            JOIN Rutas r ON r.id=v.ruta_id
            JOIN Estaciones_Paraderos ep ON ep.id=v.estacion_origen_id
            WHERE v.billetera_id=%s
            UNION ALL
            SELECT TO_CHAR(rc.fecha_hora,'DD/MM/YYYY HH24:MI') AS fecha_hora, 'Recarga Virtual' AS origen, mp.nombre_tipo_pago AS ruta, rc.monto_ingresado AS monto
            FROM Recargas rc
            JOIN Metodos_Pago mp ON mp.id=rc.metodo_pago_id
            WHERE rc.billetera_id=%s
            ORDER BY fecha_hora DESC LIMIT %s;
        """
        try:
            with db.obtener_cursor() as cur:
                cur.execute(sql,(billetera_id,billetera_id,limite))
                return [{"fecha_hora":str(f["fecha_hora"]),"origen":str(f["origen"]),"ruta":str(f["ruta"]),"monto":float(f["monto"])} for f in cur.fetchall()]
        except Exception as e:
            return []

dao_transacciones=DAOTransacciones()
