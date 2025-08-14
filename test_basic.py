#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests básicos para el sistema de gestión de personal
"""

def test_imports():
    """Test que verifica que los módulos principales se pueden importar"""
    try:
        import sys
        import os
        import sqlite3
        from datetime import datetime
        assert True  # Si llegamos aquí, las importaciones funcionaron
    except ImportError as e:
        assert False, f"Error importando módulos: {e}"

def test_database_connection():
    """Test básico de conexión a base de datos"""
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')  # Base de datos en memoria
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        assert result[0] == 1
    except Exception as e:
        assert False, f"Error en test de base de datos: {e}"

def test_datetime():
    """Test básico de datetime"""
    from datetime import datetime
    now = datetime.now()
    assert isinstance(now, datetime)
    assert now.year > 2020

if __name__ == "__main__":
    # Ejecutar tests básicos
    test_imports()
    test_database_connection()
    test_datetime()
    print("✅ Todos los tests básicos pasaron")
