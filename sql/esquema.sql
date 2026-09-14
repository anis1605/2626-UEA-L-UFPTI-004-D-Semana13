-- ==============================================================================
-- PROYECTO INTEGRADOR U4 - AVANCE 13/16 (SEMANA 13)
-- SISTEMA DE GESTIÓN: FERRETERÍA EL CONSTRUCTOR
-- Esquema de base de datos relacional MySQL con Claves Primarias y Foráneas
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS ferreteria_db 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE ferreteria_db;

-- ------------------------------------------------------------------------------
-- 1. TABLA: proveedores
-- Entidad que almacena los distribuidores y casas comerciales mayoristas.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proveedores (
    ruc VARCHAR(13) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (ruc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. TABLA: productos
-- Entidad central del inventario, relacionada mediante FK con proveedores.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS productos (
    id VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    precio DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    proveedor_ruc VARCHAR(13) NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_productos_proveedor 
        FOREIGN KEY (proveedor_ruc) 
        REFERENCES proveedores(ruc) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. TABLA: clientes
-- Entidad que registra clientes frecuentes, corporativos y de ocasión.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    ruc VARCHAR(13) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    PRIMARY KEY (ruc)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. TABLA: facturas
-- Comprobantes emitidos con relación de clave foránea hacia clientes.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS facturas (
    numero VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    cliente_ruc VARCHAR(13) NULL,
    cliente_nombre VARCHAR(100) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    iva DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    PRIMARY KEY (numero),
    CONSTRAINT fk_facturas_cliente 
        FOREIGN KEY (cliente_ruc) 
        REFERENCES clientes(ruc) 
        ON DELETE SET NULL 
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- INSERCIÓN DE DATOS DEMOSTRATIVOS INICIALES
-- ==============================================================================

-- Datos de Proveedores
INSERT IGNORE INTO proveedores (ruc, empresa, categoria, contacto, telefono, ciudad, activo) VALUES
('1790012345001', 'Holcim Ecuador S.A.', 'Cementos y Hormigon', 'Ing. Ricardo Gómez', '02-2987654', 'Guayaquil', 1),
('1790056789001', 'Adelca C.A.', 'Acero y Varillas', 'Lic. Sofía Ramírez', '02-3991100', 'Quito', 1),
('1890011223001', 'Canteras del Pastaza', 'Agregados y Grava', 'Sr. Manuel Torres', '03-2884422', 'Puyo', 1),
('1790099887001', 'Maderera El Bosque', 'Carpinteria y Tablas', 'Ing. Fernando Castro', '02-2443311', 'Tena', 0);

-- Datos de Productos (con relaciones FK hacia proveedores)
INSERT IGNORE INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc) VALUES
('PROD-001', 'Cemento Selvalegre 50kg', 'Estructural', 'Saco', 250, 10.50, '1790012345001'),
('PROD-002', 'Arena Fina de Río', 'Agregados', 'Metro Cubico', 120, 15.00, '1890011223001'),
('PROD-003', 'Grava Triturada 3/4', 'Agregados', 'Metro Cubico', 0, 18.00, '1890011223001'),
('PROD-004', 'Varilla Corrugada 12mm x 12m', 'Acero', 'Unidad', 400, 12.80, '1790056789001'),
('PROD-005', 'Madera de Encofrado (Tabla 3m)', 'Carpinteria', 'Pieza', 4, 6.50, '1790099887001'),
('PROD-006', 'Ladrillo Mambrón', 'Mamposteria', 'Millar', 15, 140.00, '1890011223001'),
('PROD-007', 'Pintura Látex Blanca 5 Galones', 'Acabados', 'Caneca', 0, 45.00, '1790012345001');

-- Datos de Clientes
INSERT IGNORE INTO clientes (ruc, nombre, tipo, telefono, email, direccion) VALUES
('1723456789', 'Carlos Alberto Mendoza', 'Frecuente', '0998765432', 'carlos.mendoza@email.com', 'Av. Amazonas N24-12, Quito'),
('1712345678001', 'Constructora los Andes S.A.', 'Corporativo', '0991234567', 'contacto@losandes.com.ec', 'Calle 10 de Agosto y Bolívar, Ambato'),
('1600987654', 'María Elena Paredes', 'Ocasion', '0981122334', 'maria.paredes@gmail.com', 'Barrio Central, Puyo'),
('1804561239001', 'Ingeniería y Diseños del Pastaza', 'Corporativo', '0976543210', 'info@idpastaza.com', 'Av. Alberto Zambrano, Puyo');

-- Datos de Facturas (con relaciones FK hacia clientes)
INSERT IGNORE INTO facturas (numero, fecha, cliente_ruc, cliente_nombre, subtotal, iva, total, estado) VALUES
('FAC-00101', '2026-08-10', '1723456789', 'Carlos Alberto Mendoza', 105.00, 15.75, 120.75, 'Pagada'),
('FAC-00102', '2026-08-12', '1712345678001', 'Constructora los Andes S.A.', 1280.00, 192.00, 1472.00, 'Pagada'),
('FAC-00103', '2026-08-15', '1600987654', 'María Elena Paredes', 54.00, 8.10, 62.10, 'Pendiente'),
('FAC-00104', '2026-08-20', '1804561239001', 'Ingeniería y Diseños del Pastaza', 450.00, 67.50, 517.50, 'Anulada');
