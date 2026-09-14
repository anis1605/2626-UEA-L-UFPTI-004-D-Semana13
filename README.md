# Proyecto Integrador U4 - Avance 13/16: Uso de Bases de Datos Relacionales (MySQL)

**Asignatura:** Desarrollo de Aplicaciones Web  
**Curso:** 2626-UEA-L-UFPTI-004-D  
**Semana:** 13 (Unidad 4: Gestión de Datos y Desarrollo de la Aplicación Web)  
**Estudiante:** Clara Anahí González Apolo  
**Tema:** Ferretería "El Tornillo Dorado"  
**Despliegue Frontend (GitHub Pages):** [https://anis1605.github.io/2626-UEA-L-UFPTI-004-D-Semana13/](https://anis1605.github.io/2626-UEA-L-UFPTI-004-D-Semana13/)  
**Repositorio GitHub:** [https://github.com/anis1605/2626-UEA-L-UFPTI-004-D-Semana13](https://github.com/anis1605/2626-UEA-L-UFPTI-004-D-Semana13)

---

## 📌 Descripción del Avance

En este avance de la **Semana 13**, la aplicación web desarrollada en **Flask** evolucionó desde la persistencia local en SQLite hacia el uso de un motor de base de datos relacional cliente-servidor: **MySQL**.

Se implementó el ciclo de vida completo de gestión de datos (**CRUD / Listar, Agregar, Modificar y Eliminar**) mediante consultas SQL parametrizadas, garantizando persistencia relacional, integridad referencial y protección contra inyecciones SQL.

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.12
- **Framework Web:** Flask 3.1.0
- **Formularios & Validaciones:** Flask-WTF 1.2.2 / WTForms 3.2.1
- **Motor de Base de Datos:** MySQL 8.0+
- **Conector:** `mysql-connector-python` 9.3.0
- **Frontend:** Jinja2, HTML5 semántico, CSS3 personalizado, JavaScript interactivo y Bootstrap 5.3
- **Control de Versiones y Despliegue:** Git, GitHub, GitHub Pages

---

## 🗄️ Modelo Relacional y Esquema SQL (`sql/esquema.sql`)

El sistema modela 4 entidades principales con claves primarias (`PRIMARY KEY`) y relaciones mediante claves foráneas (`FOREIGN KEY`):

1. **`proveedores`**:
   - `ruc` (VARCHAR(13), PK)
   - `nombre`, `contacto`, `telefono`, `correo`, `direccion`, `categoria`
2. **`productos`**:
   - `id` (VARCHAR(20), PK)
   - `nombre`, `categoria`, `unidad`, `stock`, `precio`
   - `proveedor_ruc` (VARCHAR(13), **FK** -> `proveedores(ruc)`)
3. **`clientes`**:
   - `ruc` (VARCHAR(13), PK)
   - `nombre`, `telefono`, `correo`, `direccion`, `tipo_cliente`
4. **`facturas`**:
   - `numero` (VARCHAR(20), PK)
   - `cliente_ruc` (VARCHAR(13), **FK** -> `clientes(ruc)`)
   - `fecha`, `metodo_pago`, `subtotal`, `iva`, `total`

### Consultas SQL Parametrizadas Implementadas

- **SELECT con JOIN:**
  ```sql
  SELECT p.*, pr.nombre AS proveedor_nombre 
  FROM productos p 
  LEFT JOIN proveedores pr ON p.proveedor_ruc = pr.ruc 
  ORDER BY p.id DESC;
  ```
- **INSERT (Agregar):**
  ```sql
  INSERT INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc) 
  VALUES (%s, %s, %s, %s, %s, %s, %s);
  ```
- **UPDATE (Modificar con WHERE):**
  ```sql
  UPDATE productos 
  SET nombre=%s, categoria=%s, unidad=%s, stock=%s, precio=%s, proveedor_ruc=%s 
  WHERE id=%s;
  ```
- **DELETE (Eliminar con WHERE):**
  ```sql
  DELETE FROM productos WHERE id=%s;
  ```

---

## 📁 Estructura del Proyecto

```text
2626-UEA-L-UFPTI-004-D-Semana13/
├── app.py                     # Controlador Flask con rutas y operaciones CRUD MySQL
├── requirements.txt           # Dependencias (Flask, Flask-WTF, mysql-connector-python)
├── test_app.py                # Suite de pruebas unitarias y de integración CRUD
├── index.html                 # Página de bienvenida para despliegue en GitHub Pages
├── conexion/
│   ├── __init__.py
│   └── conexion.py            # Módulo centralizado de conexión MySQL e inicialización
├── sql/
│   └── esquema.sql            # Script DDL completo con tablas, PK, FK y datos semilla
├── forms/
│   ├── __init__.py
│   ├── producto_form.py       # Formulario Flask-WTF con FK proveedor dinámico
│   ├── cliente_form.py
│   ├── proveedor_form.py
│   └── facturacion_form.py
├── templates/
│   ├── base.html              # Plantilla base Jinja2 con Bootstrap y componentes
│   ├── index.html             # Dashboard principal
│   ├── productos.html         # Listado de productos (SELECT + JOIN) y botón Eliminar
│   ├── formulario_producto.html # Formulario de registro y edición (INSERT / UPDATE)
│   ├── clientes.html
│   ├── formulario_cliente.html
│   ├── proveedores.html
│   ├── formulario_proveedor.html
│   ├── facturacion.html
│   ├── formulario_facturacion.html
│   └── components/
│       ├── navbar.html
│       └── footer.html
└── static/
    ├── css/style.css          # Estilos personalizados y tema industrial
    ├── js/script.js           # Interacciones JS y confirmación de eliminación
    └── img/                   # Recursos visuales del proyecto
```

---

## 🚀 Instrucciones de Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/anis1605/2626-UEA-L-UFPTI-004-D-Semana13.git
cd 2626-UEA-L-UFPTI-004-D-Semana13
```

### 2. Crear y activar entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar MySQL
Asegurarse de tener el servicio MySQL en ejecución y crear la base de datos `ferreteria_db`:
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ferreteria_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p ferreteria_db < sql/esquema.sql
```

*(Opcional: puede configurar variables de entorno `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` si sus credenciales difieren de las estándar).*

### 5. Ejecutar la aplicación Flask
```bash
python app.py
```
Acceder en el navegador a: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Ejecutar las pruebas automatizadas
```bash
pytest test_app.py -v   # o bien: python test_app.py
```
