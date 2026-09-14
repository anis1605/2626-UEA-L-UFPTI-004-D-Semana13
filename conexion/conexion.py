import os
import mysql.connector
from mysql.connector import Error

# Parámetros de configuración de la base de datos relacional MySQL
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '12345')
DB_NAME = os.environ.get('DB_NAME', 'ferreteria_db')
DB_PORT = int(os.environ.get('DB_PORT', 3306))


def obtener_conexion():
    """
    Establece y retorna una conexión activa al servidor MySQL.
    Utiliza parámetros de configuración seguros y charset utf8mb4.
    """
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexion
    except Error as e:
        print(f"[ERROR CONEXION MYSQL]: No se pudo conectar a la base de datos '{DB_NAME}': {e}")
        raise e


def inicializar_base_datos():
    """
    Inicializa el servidor MySQL y ejecuta el script DDL sql/esquema.sql
    en caso de que la base de datos o las tablas no existan previamente.
    """
    try:
        # Conectar al servidor sin especificar base de datos inicialmente
        conn_server = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            charset='utf8mb4'
        )
        cursor = conn_server.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn_server.close()

        # Conectar a la base de datos y ejecutar esquema.sql si hace falta
        ruta_esquema = os.path.join(os.path.dirname(__file__), '..', 'sql', 'esquema.sql')
        if os.path.exists(ruta_esquema):
            conn_db = obtener_conexion()
            cursor_db = conn_db.cursor()

            with open(ruta_esquema, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Separar y ejecutar cada sentencia del archivo
            sentencias = sql_content.split(';')
            for sentencia in sentencias:
                sentencia_limpia = sentencia.strip()
                if sentencia_limpia:
                    cursor_db.execute(sentencia_limpia)

            conn_db.commit()
            cursor_db.close()
            conn_db.close()
            print(f"[INFO MYSQL]: Base de datos '{DB_NAME}' inicializada y sincronizada correctamente.")

    except Error as e:
        print(f"[ADVERTENCIA MYSQL]: Error durante la verificación inicial del esquema: {e}")
