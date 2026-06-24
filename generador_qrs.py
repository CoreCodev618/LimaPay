import qrcode
import os
from backend.config_db import db
from backend.qr_seguridad import generar_codigo_qr

carpeta_salida = "qrs_todos_buses"
os.makedirs(carpeta_salida, exist_ok=True)

def generar_todo():
    sql = """
        SELECT b.placa, r.id AS ruta_id, r.codigo_ruta, ep.id AS estacion_id, ep.nombre AS estacion
        FROM Buses b
        JOIN Operadores o ON b.operador_id = o.id
        JOIN Rutas r ON r.operador_id = o.id
        CROSS JOIN Estaciones_Paraderos ep;
    """
    
    print("Conectando a la base de datos para extraer rutas y buses...")
    try:
        with db.obtener_cursor() as cur:
            cur.execute(sql)
            resultados = cur.fetchall()
            
            print(f"Se encontraron {len(resultados)} combinaciones para generar.\n")
            
            for fila in resultados:
                placa = fila["placa"]
                ruta_id = fila["ruta_id"]
                estacion_id = fila["estacion_id"]
                
                # Generar el contenido del QR
                texto_qr = generar_codigo_qr(placa, ruta_id, estacion_id)
                
                # Crear la imagen
                imagen = qrcode.make(texto_qr)
                nombre_archivo = f"{carpeta_salida}/{placa}_R{ruta_id}_E{estacion_id}.png"
                imagen.save(nombre_archivo)
                
                print(f" ✓ Generado: {nombre_archivo}")
                
        print(f"\n¡Proceso completado! Todos los QRs están en '{carpeta_salida}'.")
        
    except Exception as e:
        print(f"Error al conectar con la BD: {e}")

if __name__ == "__main__":
    generar_todo()