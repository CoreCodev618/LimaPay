CREATE TABLE Pasajeros (
    id          SERIAL PRIMARY KEY,
    dni         VARCHAR(8)   UNIQUE NOT NULL,
    nombre      VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    clave       VARCHAR(64)  NOT NULL
);
CREATE TABLE Billeteras (
    id            SERIAL PRIMARY KEY,
    pasajero_id   INT REFERENCES Pasajeros(id) ON DELETE CASCADE,
    saldo_actual  DECIMAL(10,2) DEFAULT 0.00 NOT NULL,
    estado_activa BOOLEAN       DEFAULT TRUE  NOT NULL
);
CREATE TABLE Metodos_Pago (
    id               SERIAL PRIMARY KEY,
    nombre_tipo_pago VARCHAR(50)
);
CREATE TABLE Recargas (
    id              SERIAL PRIMARY KEY,
    billetera_id    INT REFERENCES Billeteras(id),
    metodo_pago_id  INT REFERENCES Metodos_Pago(id),
    monto_ingresado DECIMAL(10,2),
    fecha_hora      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Tarifas (
    id    SERIAL PRIMARY KEY,
    monto DECIMAL(10,2) NOT NULL
);
CREATE TABLE Operadores (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(50)
);
CREATE TABLE Buses (
    id          SERIAL PRIMARY KEY,
    operador_id INT REFERENCES Operadores(id)
);
CREATE TABLE Rutas (
    id          SERIAL PRIMARY KEY,
    operador_id INT REFERENCES Operadores(id),
    codigo_ruta VARCHAR(50)
);
CREATE TABLE Estaciones_Paraderos (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(100)
);
CREATE TABLE Viajes (
    id                 SERIAL PRIMARY KEY,
    billetera_id       INT REFERENCES Billeteras(id),
    bus_id             INT REFERENCES Buses(id),
    ruta_id            INT REFERENCES Rutas(id),
    tarifa_id          INT REFERENCES Tarifas(id),
    estacion_origen_id INT REFERENCES Estaciones_Paraderos(id),
    fecha_hora         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO Tarifas (id, monto) VALUES (1, 3.20), (2, 2.20), (3, 1.50);
INSERT INTO Metodos_Pago (id, nombre_tipo_pago) VALUES (1,'Yape'),(2,'Plin'),(3,'Tarjeta'),(4,'Efectivo');
INSERT INTO Operadores (id, nombre) VALUES (1,'Metropolitano'),(2,'Corredor Rojo');
INSERT INTO Buses (id, operador_id) VALUES (1,1),(2,1),(3,2),(4,2);
INSERT INTO Rutas (id, operador_id, codigo_ruta) VALUES (1,1,'Expreso 4'),(2,2,'Ruta 201');
INSERT INTO Estaciones_Paraderos (id, nombre) VALUES (1,'Estación Central'),(2,'Javier Prado'),(3,'Naranjal'),(4,'Tomas Valle');
SELECT setval('tarifas_id_seq', (SELECT MAX(id) FROM Tarifas));
SELECT setval('metodos_pago_id_seq', (SELECT MAX(id) FROM Metodos_Pago));
SELECT setval('operadores_id_seq', (SELECT MAX(id) FROM Operadores));
SELECT setval('buses_id_seq', (SELECT MAX(id) FROM Buses));
SELECT setval('rutas_id_seq', (SELECT MAX(id) FROM Rutas));
SELECT setval('estaciones_paraderos_id_seq', (SELECT MAX(id) FROM Estaciones_Paraderos));
