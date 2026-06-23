-- Migración: agrega verificación de medio pasaje, recuperación de clave y alerta de saldo bajo.
-- Ejecutar UNA VEZ sobre una base de datos LimaPay ya existente (creada con el schema.sql anterior).

ALTER TABLE Pasajeros
    ADD COLUMN IF NOT EXISTS medio_pasaje_verificado BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS pregunta_seguridad VARCHAR(100),
    ADD COLUMN IF NOT EXISTS respuesta_seguridad VARCHAR(255);

ALTER TABLE Billeteras
    ADD COLUMN IF NOT EXISTS umbral_alerta DECIMAL(10,2) DEFAULT 5.00 NOT NULL;

CREATE TABLE IF NOT EXISTS Solicitudes_Medio_Pasaje (
    id SERIAL PRIMARY KEY,
    pasajero_id INT NOT NULL REFERENCES Pasajeros(id) ON DELETE CASCADE,
    codigo_institucional VARCHAR(30) NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Aprobado', 'Rechazado')),
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP
);

-- Los pasajeros "General" existentes no necesitan verificación; los "Medio" quedan
-- marcados como no verificados hasta que pasen por el flujo de verificación.
UPDATE Pasajeros SET medio_pasaje_verificado = TRUE WHERE tipo_pasajero = 'General';
