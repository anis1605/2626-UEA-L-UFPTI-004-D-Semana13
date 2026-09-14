import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from conexion import obtener_conexion, inicializar_base_datos
from forms import ProductoForm, ClienteForm, ProveedorForm, FacturacionForm

app = Flask(__name__)

# Configuración de clave secreta para la gestión de sesiones y protección CSRF con Flask-WTF
app.config['SECRET_KEY'] = 'clave_secreta_super_segura_ferreteria_el_constructor_2026_semana13'
csrf = CSRFProtect(app)

# Información general del sistema (variables globales inyectadas a plantillas)
SISTEMA_INFO = {
    "empresa": "Ferretería El Constructor",
    "desarrollador": "Clara Anahi Gonzalez Apolo",
    "asignatura": "Desarrollo de Aplicaciones Web",
    "periodo": "2026-2026",
    "sucursal_principal": "Terminal Terrestre de Puyo",
    "telefono_contacto": "+123 456 7890",
    "email_contacto": "ferreteriaelconstructor@ferreterias.com"
}

# Inicializar esquema relacional en MySQL al iniciar la aplicación
inicializar_base_datos()


@app.context_processor
def inject_global_vars():
    """Inyecta la información general del sistema en todas las plantillas Jinja2."""
    return dict(sistema=SISTEMA_INFO)


# ==============================================================================
# RUTA PRINCIPAL (DASHBOARD CON CONSULTAS MYSQL)
# ==============================================================================
@app.route('/')
def index():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS total FROM productos')
    total_productos = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM clientes')
    total_clientes = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM proveedores')
    total_proveedores = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM facturas')
    total_facturas = cursor.fetchone()['total']

    cursor.close()
    conn.close()

    resumen = {
        "total_productos": total_productos,
        "total_clientes": total_clientes,
        "total_proveedores": total_proveedores,
        "total_facturas": total_facturas
    }
    return render_template('index.html', resumen=resumen)


# ==============================================================================
# MÓDULO DE PRODUCTOS (CRUD COMPLETO CON MYSQL: SELECT, INSERT, UPDATE, DELETE)
# ==============================================================================

@app.route('/productos')
def productos():
    """
    OPERACIÓN SELECT (LISTAR):
    Recupera los productos desde MySQL aplicando LEFT JOIN con la tabla proveedores
    para evidenciar relaciones entre tablas mediante Clave Foránea (FK).
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT p.id, p.nombre, p.categoria, p.unidad, p.stock, p.precio, p.proveedor_ruc,
               pr.empresa AS proveedor_empresa
        FROM productos p
        LEFT JOIN proveedores pr ON p.proveedor_ruc = pr.ruc
        ORDER BY p.id ASC
    """
    cursor.execute(query)
    productos_db = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('productos.html', productos=productos_db)


@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    """
    OPERACIÓN INSERT (AGREGAR):
    Valida los datos con Flask-WTF y realiza un INSERT parametrizado con marcadores %s.
    """
    form = ProductoForm()

    # Cargar dinámicamente los proveedores disponibles para la selección de la FK
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ruc, empresa FROM proveedores WHERE activo = 1 ORDER BY empresa ASC")
    proveedores_disponibles = cursor.fetchall()
    form.proveedor_ruc.choices = [('', '-- Sin proveedor asignado --')] + [
        (p['ruc'], f"{p['empresa']} ({p['ruc']})") for p in proveedores_disponibles
    ]

    if form.validate_on_submit():
        id_ingresado = form.id.data.strip().upper()

        # Verificar unicidad de Clave Primaria en MySQL
        cursor.execute("SELECT id FROM productos WHERE id = %s", (id_ingresado,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"El código de producto '{id_ingresado}' ya se encuentra registrado en MySQL.", "warning")
            return render_template('formulario_producto.html', form=form, titulo="Registrar Nuevo Producto", es_edicion=False)

        nombre = form.nombre.data.strip()
        categoria = form.categoria.data
        unidad = form.unidad.data
        stock = form.stock.data
        precio = float(form.precio.data)
        proveedor_ruc = form.proveedor_ruc.data if form.proveedor_ruc.data else None

        # Consulta SQL INSERT parametrizada
        insert_query = """
            INSERT INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (id_ingresado, nombre, categoria, unidad, stock, precio, proveedor_ruc))
        conn.commit()

        cursor.close()
        conn.close()

        flash(f"Producto '{nombre}' registrado exitosamente en MySQL con código {id_ingresado}.", "success")
        return redirect(url_for('productos'))

    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, titulo="Registrar Nuevo Producto", es_edicion=False)


@app.route('/productos/editar/<id>', methods=['GET', 'POST'])
def editar_producto(id):
    """
    OPERACIÓN UPDATE (MODIFICAR):
    Recupera el registro seleccionado con WHERE id = %s, carga los datos en el formulario
    y aplica los cambios mediante UPDATE con WHERE para garantizar precisión.
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        flash(f"El producto con código '{id}' no fue encontrado en MySQL.", "danger")
        return redirect(url_for('productos'))

    # Cargar proveedores para el campo FK
    cursor.execute("SELECT ruc, empresa FROM proveedores ORDER BY empresa ASC")
    proveedores_disponibles = cursor.fetchall()
    choices_proveedores = [('', '-- Sin proveedor asignado --')] + [
        (p['ruc'], f"{p['empresa']} ({p['ruc']})") for p in proveedores_disponibles
    ]

    form = ProductoForm(data=producto)
    form.proveedor_ruc.choices = choices_proveedores

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        categoria = form.categoria.data
        unidad = form.unidad.data
        stock = form.stock.data
        precio = float(form.precio.data)
        proveedor_ruc = form.proveedor_ruc.data if form.proveedor_ruc.data else None

        update_query = """
            UPDATE productos 
            SET nombre = %s, categoria = %s, unidad = %s, stock = %s, precio = %s, proveedor_ruc = %s 
            WHERE id = %s
        """
        cursor.execute(update_query, (nombre, categoria, unidad, stock, precio, proveedor_ruc, id))
        conn.commit()

        cursor.close()
        conn.close()

        flash(f"Producto '{id}' modificado y actualizado correctamente en MySQL.", "success")
        return redirect(url_for('productos'))

    cursor.close()
    conn.close()
    return render_template('formulario_producto.html', form=form, titulo=f"Editar Producto ({producto['id']})", es_edicion=True)


@app.route('/productos/eliminar/<id>', methods=['POST'])
def eliminar_producto(id):
    """
    OPERACIÓN DELETE (ELIMINAR):
    Elimina físicamente el producto seleccionado mediante una consulta DELETE FROM con cláusula WHERE.
    Ejecuta commit() inmediatamente y comprueba la eliminación en la base de datos MySQL.
    """
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    # Verificar existencia antes de eliminar
    cursor.execute("SELECT id, nombre FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if not producto:
        cursor.close()
        conn.close()
        flash(f"El producto con código '{id}' no existe en MySQL.", "warning")
        return redirect(url_for('productos'))

    nombre_prod = producto['nombre']
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash(f"Producto '{nombre_prod}' ({id}) eliminado permanentemente de la base de datos MySQL.", "success")
    return redirect(url_for('productos'))


# ==============================================================================
# MÓDULO DE CLIENTES (CONEXIÓN MYSQL)
# ==============================================================================
@app.route('/clientes')
def clientes():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes ORDER BY nombre ASC")
    clientes_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes_db)


@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        ruc_ingresado = form.ruc.data.strip()

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ruc FROM clientes WHERE ruc = %s", (ruc_ingresado,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"El cliente con Cédula/RUC '{ruc_ingresado}' ya se encuentra registrado en MySQL.", "warning")
            return render_template('formulario_cliente.html', form=form, titulo="Registrar Nuevo Cliente", es_edicion=False)

        nombre = form.nombre.data.strip()
        tipo = form.tipo.data
        telefono = form.telefono.data.strip()
        email = form.email.data.strip().lower()
        direccion = form.direccion.data.strip()

        insert_query = """
            INSERT INTO clientes (ruc, nombre, tipo, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ruc_ingresado, nombre, tipo, telefono, email, direccion))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Cliente '{nombre}' registrado exitosamente en MySQL.", "success")
        return redirect(url_for('clientes'))

    return render_template('formulario_cliente.html', form=form, titulo="Registrar Nuevo Cliente", es_edicion=False)


@app.route('/clientes/editar/<ruc>', methods=['GET', 'POST'])
def editar_cliente(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE ruc = %s", (ruc,))
    cliente = cursor.fetchone()

    if not cliente:
        cursor.close()
        conn.close()
        flash(f"El cliente con Cédula/RUC '{ruc}' no fue encontrado.", "danger")
        return redirect(url_for('clientes'))

    form = ClienteForm(data=cliente)

    if form.validate_on_submit():
        nombre = form.nombre.data.strip()
        tipo = form.tipo.data
        telefono = form.telefono.data.strip()
        email = form.email.data.strip().lower()
        direccion = form.direccion.data.strip()

        update_query = """
            UPDATE clientes 
            SET nombre = %s, tipo = %s, telefono = %s, email = %s, direccion = %s 
            WHERE ruc = %s
        """
        cursor.execute(update_query, (nombre, tipo, telefono, email, direccion, ruc))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Datos del cliente '{nombre}' actualizados correctamente en MySQL.", "success")
        return redirect(url_for('clientes'))

    cursor.close()
    conn.close()
    return render_template('formulario_cliente.html', form=form, titulo=f"Editar Cliente ({cliente['ruc']})", es_edicion=True)


@app.route('/clientes/eliminar/<ruc>', methods=['POST'])
def eliminar_cliente(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM clientes WHERE ruc = %s", (ruc,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Cliente con RUC '{ruc}' eliminado correctamente de MySQL.", "success")
    return redirect(url_for('clientes'))


# ==============================================================================
# MÓDULO DE PROVEEDORES (CONEXIÓN MYSQL)
# ==============================================================================
@app.route('/proveedores')
def proveedores():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores ORDER BY empresa ASC")
    proveedores_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('proveedores.html', proveedores=proveedores_db)


@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        ruc_ingresado = form.ruc.data.strip()

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ruc FROM proveedores WHERE ruc = %s", (ruc_ingresado,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"El proveedor con RUC '{ruc_ingresado}' ya se encuentra registrado en MySQL.", "warning")
            return render_template('formulario_proveedor.html', form=form, titulo="Registrar Nuevo Proveedor", es_edicion=False)

        empresa = form.empresa.data.strip()
        categoria = form.categoria.data
        contacto = form.contacto.data.strip()
        telefono = form.telefono.data.strip()
        ciudad = form.ciudad.data.strip()
        activo = 1 if form.activo.data else 0

        insert_query = """
            INSERT INTO proveedores (ruc, empresa, categoria, contacto, telefono, ciudad, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ruc_ingresado, empresa, categoria, contacto, telefono, ciudad, activo))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Proveedor '{empresa}' registrado exitosamente en MySQL.", "success")
        return redirect(url_for('proveedores'))

    return render_template('formulario_proveedor.html', form=form, titulo="Registrar Nuevo Proveedor", es_edicion=False)


@app.route('/proveedores/editar/<ruc>', methods=['GET', 'POST'])
def editar_proveedor(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM proveedores WHERE ruc = %s", (ruc,))
    proveedor = cursor.fetchone()

    if not proveedor:
        cursor.close()
        conn.close()
        flash(f"El proveedor con RUC '{ruc}' no fue encontrado en MySQL.", "danger")
        return redirect(url_for('proveedores'))

    datos_dict = dict(proveedor)
    datos_dict['activo'] = bool(datos_dict['activo'])
    form = ProveedorForm(data=datos_dict)

    if form.validate_on_submit():
        empresa = form.empresa.data.strip()
        categoria = form.categoria.data
        contacto = form.contacto.data.strip()
        telefono = form.telefono.data.strip()
        ciudad = form.ciudad.data.strip()
        activo = 1 if form.activo.data else 0

        update_query = """
            UPDATE proveedores 
            SET empresa = %s, categoria = %s, contacto = %s, telefono = %s, ciudad = %s, activo = %s 
            WHERE ruc = %s
        """
        cursor.execute(update_query, (empresa, categoria, contacto, telefono, ciudad, activo, ruc))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Proveedor '{empresa}' actualizado correctamente en MySQL.", "success")
        return redirect(url_for('proveedores'))

    cursor.close()
    conn.close()
    return render_template('formulario_proveedor.html', form=form, titulo=f"Editar Proveedor ({proveedor['ruc']})", es_edicion=True)


@app.route('/proveedores/eliminar/<ruc>', methods=['POST'])
def eliminar_proveedor(ruc):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM proveedores WHERE ruc = %s", (ruc,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Proveedor con RUC '{ruc}' eliminado correctamente de MySQL.", "success")
    return redirect(url_for('proveedores'))


# ==============================================================================
# MÓDULO DE FACTURACIÓN (CONEXIÓN MYSQL)
# ==============================================================================
@app.route('/facturacion')
def facturacion():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas ORDER BY fecha DESC, numero DESC")
    facturas_db = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('facturacion.html', facturas=facturas_db)


@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    form = FacturacionForm()
    if form.validate_on_submit():
        num_ingresado = form.numero.data.strip().upper()

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT numero FROM facturas WHERE numero = %s", (num_ingresado,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash(f"La factura con número '{num_ingresado}' ya fue emitida previamente en MySQL.", "warning")
            return render_template('formulario_facturacion.html', form=form, titulo="Emitir Nueva Factura", es_edicion=False)

        subtotal = float(form.subtotal.data)
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)
        fecha_str = form.fecha.data.strftime('%Y-%m-%d') if hasattr(form.fecha.data, 'strftime') else str(form.fecha.data)
        cliente = form.cliente.data.strip()
        estado = form.estado.data

        # Buscar si coincide con cliente_ruc existente
        cursor.execute("SELECT ruc FROM clientes WHERE nombre LIKE %s LIMIT 1", (f"%{cliente}%",))
        cli_match = cursor.fetchone()
        cliente_ruc = cli_match['ruc'] if cli_match else None

        insert_query = """
            INSERT INTO facturas (numero, fecha, cliente_ruc, cliente_nombre, subtotal, iva, total, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (num_ingresado, fecha_str, cliente_ruc, cliente, subtotal, iva, total, estado))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Factura '{num_ingresado}' emitida correctamente por un total de ${total:.2f} en MySQL.", "success")
        return redirect(url_for('facturacion'))

    if request.method == 'GET' and not form.fecha.data:
        form.fecha.data = datetime.date.today()

    return render_template('formulario_facturacion.html', form=form, titulo="Emitir Nueva Factura", es_edicion=False)


@app.route('/facturacion/editar/<numero>', methods=['GET', 'POST'])
def editar_factura(numero):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM facturas WHERE numero = %s", (numero,))
    factura = cursor.fetchone()

    if not factura:
        cursor.close()
        conn.close()
        flash(f"La factura con número '{numero}' no fue encontrada en MySQL.", "danger")
        return redirect(url_for('facturacion'))

    datos_form = dict(factura)
    datos_form['cliente'] = factura['cliente_nombre']
    if isinstance(datos_form.get('fecha'), str):
        try:
            datos_form['fecha'] = datetime.datetime.strptime(datos_form['fecha'], '%Y-%m-%d').date()
        except ValueError:
            pass

    form = FacturacionForm(data=datos_form)

    if form.validate_on_submit():
        subtotal = float(form.subtotal.data)
        iva = round(subtotal * 0.15, 2)
        total = round(subtotal + iva, 2)
        fecha_str = form.fecha.data.strftime('%Y-%m-%d') if hasattr(form.fecha.data, 'strftime') else str(form.fecha.data)
        cliente = form.cliente.data.strip()
        estado = form.estado.data

        update_query = """
            UPDATE facturas 
            SET fecha = %s, cliente_nombre = %s, subtotal = %s, iva = %s, total = %s, estado = %s 
            WHERE numero = %s
        """
        cursor.execute(update_query, (fecha_str, cliente, subtotal, iva, total, estado, numero))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Factura '{numero}' actualizada correctamente en MySQL.", "success")
        return redirect(url_for('facturacion'))

    cursor.close()
    conn.close()
    return render_template('formulario_facturacion.html', form=form, titulo=f"Editar Factura ({factura['numero']})", es_edicion=True)


@app.route('/facturacion/eliminar/<numero>', methods=['POST'])
def eliminar_factura(numero):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("DELETE FROM facturas WHERE numero = %s", (numero,))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f"Factura '{numero}' eliminada correctamente de MySQL.", "success")
    return redirect(url_for('facturacion'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
