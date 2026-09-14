"""
Suite exhaustiva de pruebas automatizadas para el Avance 13/16 (Semana 13).
Verifica:
1. Conexión a la base de datos relacional MySQL (ferreteria_db).
2. Esquema relacional y restricciones de Clave Foránea (FK).
3. Operación SELECT (Listar con LEFT JOIN de Proveedor).
4. Operación INSERT (Agregar registro validado mediante Flask-WTF).
5. Operación UPDATE (Modificar registro existente con cláusula WHERE).
6. Operación DELETE (Eliminar físicamente registro con cláusula WHERE).
7. Validaciones del lado del servidor con WTForms.
8. Integración relacional de Clientes, Proveedores y Facturación.
9. Protección contra ataques CSRF.
"""

import unittest
from app import app
from conexion import obtener_conexion


class MySQLRelationalCRUDTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def tearDown(self):
        """Limpia registros de prueba insertados durante la ejecución."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id IN ('PROD-CRUD-01', 'PROD-CRUD-02', 'PROD-CSRF-OK', 'PROD-CSRF-ERR', 'PROD-NEG')")
        cursor.execute("DELETE FROM clientes WHERE ruc = '1799112233001'")
        cursor.execute("DELETE FROM proveedores WHERE ruc = '1799881122001'")
        cursor.execute("DELETE FROM facturas WHERE numero = 'FAC-00777'")
        conn.commit()
        cursor.close()
        conn.close()

    def test_01_conexion_mysql_and_schema(self):
        """Verifica conexión a MySQL y existencia de tablas y claves foráneas."""
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'ferreteria_db'")
        tablas = [r['TABLE_NAME'].lower() for r in cursor.fetchall()]
        self.assertIn('productos', tablas)
        self.assertIn('proveedores', tablas)
        self.assertIn('clientes', tablas)
        self.assertIn('facturas', tablas)

        # Verificar restricción de clave foránea
        cursor.execute("""
            SELECT constraint_name, table_name, referenced_table_name 
            FROM information_schema.referential_constraints 
            WHERE constraint_schema = 'ferreteria_db' AND table_name = 'productos'
        """)
        fk = cursor.fetchone()
        self.assertIsNotNone(fk, "Debe existir al menos una clave foránea en la tabla productos.")
        self.assertEqual(fk['REFERENCED_TABLE_NAME'].lower(), 'proveedores')

        cursor.close()
        conn.close()

    def test_02_index_metrics_mysql(self):
        """Verifica que el dashboard recupere métricas cuantitativas desde MySQL."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ferretería El Constructor'.encode('utf-8'), response.data)
        self.assertIn('Semana 13'.encode('utf-8'), response.data)
        self.assertIn('Items en MySQL'.encode('utf-8'), response.data)

    def test_03_productos_select_with_join(self):
        """Verifica la operación SELECT (Listar) con LEFT JOIN entre productos y proveedores."""
        response = self.client.get('/productos')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cemento Selvalegre'.encode('utf-8'), response.data)
        self.assertIn('PROD-001'.encode('utf-8'), response.data)
        # Verificar que el proveedor relacionado mediante JOIN se renderice
        self.assertIn('Holcim Ecuador'.encode('utf-8'), response.data)

    def test_04_producto_insert_operation(self):
        """Verifica la operación INSERT (Agregar) con validación y FK hacia proveedores."""
        nuevo_id = 'PROD-CRUD-01'
        nombre_prod = 'Taladro Percutor 650W Bosch'
        proveedor_fk = '1790056789001'  # Adelca C.A.

        response = self.client.post('/productos/nuevo', data={
            'id': nuevo_id,
            'nombre': nombre_prod,
            'categoria': 'Herramientas',
            'unidad': 'Unidad',
            'stock': '25',
            'precio': '89.99',
            'proveedor_ruc': proveedor_fk
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(nombre_prod.encode('utf-8'), response.data)

        # Comprobar físicamente en MySQL
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (nuevo_id,))
        prod_mysql = cursor.fetchone()
        cursor.close()
        conn.close()

        self.assertIsNotNone(prod_mysql, "El producto debe existir en la base de datos MySQL.")
        self.assertEqual(prod_mysql['nombre'], nombre_prod)
        self.assertEqual(prod_mysql['stock'], 25)
        self.assertEqual(float(prod_mysql['precio']), 89.99)
        self.assertEqual(prod_mysql['proveedor_ruc'], proveedor_fk)

    def test_05_producto_update_operation(self):
        """Verifica la operación UPDATE (Modificar) con cláusula WHERE id = %s."""
        target_id = 'PROD-CRUD-02'
        nombre_editado = 'Amoladora Angular 4-1/2 DeWalt Profesional'

        # Insertar registro previo en MySQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (id, nombre, categoria, unidad, stock, precio, proveedor_ruc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
        """, (target_id, 'Amoladora Inicial', 'Herramientas', 'Unidad', 10, 65.00, None))
        conn.commit()
        cursor.close()
        conn.close()

        # Enviar formulario de edición (POST)
        response = self.client.post(f'/productos/editar/{target_id}', data={
            'nombre': nombre_editado,
            'categoria': 'Herramientas',
            'unidad': 'Unidad',
            'stock': '18',
            'precio': '74.50',
            'proveedor_ruc': '1790012345001'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verificar actualización en MySQL
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (target_id,))
        prod_upd = cursor.fetchone()
        cursor.close()
        conn.close()

        self.assertIsNotNone(prod_upd)
        self.assertEqual(prod_upd['nombre'], nombre_editado)
        self.assertEqual(prod_upd['stock'], 18)
        self.assertEqual(float(prod_upd['precio']), 74.50)
        self.assertEqual(prod_upd['proveedor_ruc'], '1790012345001')

    def test_06_producto_delete_operation(self):
        """
        Verifica la operación DELETE (Eliminar):
        Elimina el producto seleccionado con DELETE FROM ... WHERE id = %s y confirma que desaparezca de MySQL.
        """
        del_id = 'PROD-CRUD-01'

        # Asegurar existencia previa
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (id, nombre, categoria, unidad, stock, precio)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)
        """, (del_id, 'Producto para Eliminar', 'Herramientas', 'Unidad', 5, 20.0))
        conn.commit()
        cursor.close()
        conn.close()

        # Enviar petición POST para eliminar
        response = self.client.post(f'/productos/eliminar/{del_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('eliminado permanentemente de la base de datos MySQL'.encode('utf-8'), response.data)

        # Comprobar que dejó de existir físicamente en MySQL
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM productos WHERE id = %s", (del_id,))
        existe = cursor.fetchone()
        cursor.close()
        conn.close()

        self.assertIsNone(existe, "El producto debe haber sido eliminado completamente de MySQL.")

    def test_07_producto_validation_rejects_empty_and_negative(self):
        """Verifica que el formulario rechace entradas inválidas y no afecte a MySQL."""
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        count_before = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        # Enviar valores negativos e inválidos
        response = self.client.post('/productos/nuevo', data={
            'id': 'PROD-NEG',
            'nombre': 'Material Erroneo',
            'categoria': 'Acabados',
            'unidad': 'Unidad',
            'stock': '-10',
            'precio': '-50.0'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('El stock debe ser un valor entero no negativo'.encode('utf-8'), response.data)

        # Comprobar que la cantidad de registros en MySQL se mantuvo inalterada
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        count_after = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        self.assertEqual(count_before, count_after)

    def test_08_clientes_crud(self):
        """Verifica inserción, listado y eliminación de clientes en MySQL."""
        ruc = '1799112233001'
        nombre = 'Constructora Manabí & Pastaza'

        # Insertar
        resp = self.client.post('/clientes/nuevo', data={
            'ruc': ruc,
            'nombre': nombre,
            'tipo': 'Corporativo',
            'telefono': '05-2667788',
            'email': 'contacto@manabipastaza.com',
            'direccion': 'Av. 10 de Agosto y Tarqui'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Consultar en MySQL
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes WHERE ruc = %s", (ruc,))
        cli = cursor.fetchone()
        self.assertIsNotNone(cli)
        self.assertEqual(cli['nombre'], nombre)

        # Eliminar
        cursor.execute("DELETE FROM clientes WHERE ruc = %s", (ruc,))
        conn.commit()
        cursor.close()
        conn.close()

    def test_09_proveedores_crud(self):
        """Verifica inserción, consulta y eliminación de proveedores en MySQL."""
        ruc = '1799881122001'
        empresa = 'Aceros Nacionales S.A.'

        resp = self.client.post('/proveedores/nuevo', data={
            'ruc': ruc,
            'empresa': empresa,
            'categoria': 'Acero y Varillas',
            'contacto': 'Ing. Roberto Paz',
            'telefono': '02-2349900',
            'ciudad': 'Quito',
            'activo': 'y'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM proveedores WHERE ruc = %s", (ruc,))
        prov = cursor.fetchone()
        self.assertIsNotNone(prov)
        self.assertEqual(prov['empresa'], empresa)

        cursor.execute("DELETE FROM proveedores WHERE ruc = %s", (ruc,))
        conn.commit()
        cursor.close()
        conn.close()

    def test_10_facturas_crud_with_fk(self):
        """Verifica emisión de factura con relación de clave foránea hacia clientes."""
        numero = 'FAC-00777'

        resp = self.client.post('/facturacion/nueva', data={
            'numero': numero,
            'fecha': '2026-09-13',
            'cliente': 'Constructora los Andes S.A.',
            'subtotal': '500.00',
            'estado': 'Pagada'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM facturas WHERE numero = %s", (numero,))
        fac = cursor.fetchone()
        self.assertIsNotNone(fac)
        self.assertEqual(float(fac['subtotal']), 500.00)
        self.assertEqual(float(fac['iva']), 75.00)
        self.assertEqual(float(fac['total']), 575.00)
        self.assertEqual(fac['cliente_ruc'], '1712345678001')  # FK asignada automáticamente

        cursor.execute("DELETE FROM facturas WHERE numero = %s", (numero,))
        conn.commit()
        cursor.close()
        conn.close()

    def test_11_csrf_protection(self):
        """Verifica la protección contra ataques CSRF en formularios."""
        self.app.config['WTF_CSRF_ENABLED'] = True
        import re

        resp_get = self.client.get('/productos/nuevo')
        self.assertEqual(resp_get.status_code, 200)
        match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', resp_get.data.decode('utf-8'))
        self.assertIsNotNone(match)
        csrf_token = match.group(1)

        # POST sin token CSRF -> rechazo 400 Bad Request
        resp_bad = self.client.post('/productos/nuevo', data={
            'id': 'PROD-CSRF-ERR',
            'nombre': 'Sin Token',
            'categoria': 'Herramientas',
            'unidad': 'Unidad',
            'stock': 5,
            'precio': 10.0
        })
        self.assertEqual(resp_bad.status_code, 400)

        # POST con token CSRF válido -> procesamiento exitoso 200 OK
        resp_good = self.client.post('/productos/nuevo', data={
            'csrf_token': csrf_token,
            'id': 'PROD-CSRF-OK',
            'nombre': 'Con Token Valido',
            'categoria': 'Herramientas',
            'unidad': 'Unidad',
            'stock': 10,
            'precio': 20.0
        }, follow_redirects=True)
        self.assertEqual(resp_good.status_code, 200)
        self.assertIn('Con Token Valido'.encode('utf-8'), resp_good.data)


if __name__ == '__main__':
    unittest.main()
