import qrcode
import os
from backend.qr_seguridad import generar_codigo_qr

# Crea una carpeta para mantener limpio tu proyecto
carpeta_salida = "qrs_buses"
os.makedirs(carpeta_salida, exist_ok=True)

# Todas las placas extraídas de tu base de datos (schema.sql)
buses_por_operador = {
    "Metropolitano": ['A1T-001', 'A1T-045', 'A1T-089', 'A1T-112', 'A1T-156'],
    "Corredor_Rojo": ['B2R-201', 'B2R-202', 'B2R-203', 'B2R-204'],
    "Corredor_Azul": ['C3A-301', 'C3A-302', 'C3A-303'],
    "Los_Chinos": ['D4L-401', 'D4L-402', 'D4L-403', 'D4L-404'],
    "Consorcio_Roma": ['E5R-501', 'E5R-502'],
    "La_50": ['F6L-601', 'F6L-602']
}

total = 0
print("Generando lote de códigos QR de LimaPay...\n")

for operador, placas in buses_por_operador.items():
    print(f"--- {operador} ---")
    for placa in placas:
        # Genera el string seguro: PLACA|CHECKSUM
        texto_qr = generar_codigo_qr(placa)
        
        # Crea y guarda la imagen
        imagen = qrcode.make(texto_qr)
        nombre_archivo = f"{carpeta_salida}/{operador}_{placa}.png"
        imagen.save(nombre_archivo)
        
        print(f" ✓ {placa} -> {texto_qr}")
        total += 1
    print("")

print(f"¡Listo! Se generaron {total} códigos QR en la carpeta '{carpeta_salida}'.")