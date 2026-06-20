CREATE TABLE Pasajeros (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(8) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    clave VARCHAR(255) NOT NULL
);

CREATE TABLE Operadores (
    id SERIAL PRIMARY KEY,
    nombre_empresa VARCHAR(100) NOT NULL
);

CREATE TABLE Tarifas (
    id SERIAL PRIMARY KEY,
    tipo_pasajero VARCHAR(50) NOT NULL,
    monto DECIMAL(5,2) NOT NULL
);

CREATE TABLE Metodos_Pago (
    id SERIAL PRIMARY KEY,
    nombre_tipo_pago VARCHAR(50) NOT NULL
);

CREATE TABLE Estaciones_Paraderos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8)
);

CREATE TABLE Billeteras (
    id SERIAL PRIMARY KEY,
    pasajero_id INT UNIQUE NOT NULL REFERENCES Pasajeros(id) ON DELETE CASCADE,
    saldo_actual DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    estado_activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE Rutas (
    id SERIAL PRIMARY KEY,
    operador_id INT NOT NULL REFERENCES Operadores(id),
    codigo_ruta VARCHAR(20) NOT NULL
);

CREATE TABLE Buses (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(10) UNIQUE NOT NULL,
    operador_id INT NOT NULL REFERENCES Operadores(id)
);

CREATE TABLE Recargas (
    id SERIAL PRIMARY KEY,
    billetera_id INT NOT NULL REFERENCES Billeteras(id),
    metodo_pago_id INT NOT NULL REFERENCES Metodos_Pago(id),
    monto_ingresado DECIMAL(10,2) NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Viajes (
    id SERIAL PRIMARY KEY,
    billetera_id INT NOT NULL REFERENCES Billeteras(id),
    bus_id INT NOT NULL REFERENCES Buses(id),
    ruta_id INT NOT NULL REFERENCES Rutas(id),
    tarifa_id INT NOT NULL REFERENCES Tarifas(id),
    estacion_origen_id INT NOT NULL REFERENCES Estaciones_Paraderos(id),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- INSERCIÓN DE CATÁLOGOS ESTÁTICOS (REALISMO EXTENDIDO)
-- ==========================================
INSERT INTO Operadores (nombre_empresa) VALUES 
('ATU - Metropolitano'),
('ATU - Corredor Rojo'),
('ATU - Corredor Azul'),
('ATU - Corredor Morado'),
('ETUCHISA (Los Chinos)'),
('Consorcio Roma'),
('Empresa de Transportes 50');

INSERT INTO Tarifas (tipo_pasajero, monto) VALUES 
('General - Metropolitano', 3.20),
('Medio - Metropolitano', 1.60),
('General - Corredores', 2.20),
('Medio - Corredores', 1.10),
('Urbano Tradicional - Directo', 3.00),
('Urbano Tradicional - Intermedio', 2.00);

INSERT INTO Metodos_Pago (nombre_tipo_pago) VALUES 
('Yape'), ('Plin'), ('Tarjeta Visa/Mastercard'), ('Agente Físico');

INSERT INTO Estaciones_Paraderos (nombre, latitud, longitud) VALUES 
('Terminal Naranjal', -11.975482, -77.060134),
('Estación Tomas Valle', -12.008921, -77.054312),
('Estación UNI', -12.019485, -77.049832),
('Estación Central', -12.057345, -77.037512),
('Estación Javier Prado', -12.091123, -77.026456),
('Estación Angamos', -12.111832, -77.021098),
('Terminal Matellini', -12.170245, -77.015264),
('Paradero Óvalo Huarochirí (Rojo)', -12.062837, -76.945182),
('Paradero Universidad de Lima (Rojo)', -12.083745, -76.971234),
('Paradero Amancaes (Azul)', -12.016584, -77.036921);

INSERT INTO Rutas (operador_id, codigo_ruta) VALUES 
(1, 'Regular A'), (1, 'Regular B'), (1, 'Regular C'),
(1, 'Expreso 1'), (1, 'Expreso 2'), (1, 'Expreso 3'), 
(1, 'Expreso 4'), (1, 'Expreso 5'), (1, 'Super Expreso Norte'),
(2, 'Servicio 201'), (2, 'Servicio 204'), (2, 'Servicio 206'), (2, 'Servicio 209'),
(3, 'Servicio 301'), (3, 'Servicio 303'), (3, 'Servicio 305'),
(4, 'Servicio 404'), (4, 'Servicio 405'),
(5, 'Ruta A (Ancón - VES)'), (5, 'Ruta C (Ancón - VES)'),
(6, 'Ruta IO-47 (Roma)'),
(7, 'Ruta IO-50 (La 50)');

INSERT INTO Buses (placa, operador_id) VALUES 
-- Metropolitano (Articulados)
('A1T-001', 1), ('A1T-045', 1), ('A1T-089', 1), ('A1T-112', 1), ('A1T-156', 1),
-- Corredor Rojo
('B2R-201', 2), ('B2R-202', 2), ('B2R-203', 2), ('B2R-204', 2),
-- Corredor Azul
('C3A-301', 3), ('C3A-302', 3), ('C3A-303', 3),
-- Etuchisa (Los Chinos)
('D4L-401', 5), ('D4L-402', 5), ('D4L-403', 5), ('D4L-404', 5),
-- Consorcio Roma / La 50
('E5R-501', 6), ('E5R-502', 6), ('F6L-601', 7), ('F6L-602', 7);