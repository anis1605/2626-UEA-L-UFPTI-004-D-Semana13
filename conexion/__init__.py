"""
Módulo de conexión a la base de datos relacional para el Proyecto Integrador.
"""

from .conexion import obtener_conexion, inicializar_base_datos

__all__ = ['obtener_conexion', 'inicializar_base_datos']
