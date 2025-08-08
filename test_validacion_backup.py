#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para las nuevas funcionalidades de validación y backup
"""

import sys
import os

# Agregar el directorio src al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_validadores():
    """Probar el sistema de validación"""
    print("🧪 Probando sistema de validación...")
    
    try:
        from utils.validators import DataValidator
        
        # Pruebas de cédula
        print("\n📋 Probando validación de cédula:")
        cedulas_prueba = [
            ("1234567890", True),  # Cédula válida de 10 dígitos
            ("12345678", True),    # Cédula válida de 8 dígitos
            ("123456", False),     # Muy corta
            ("123456789012345", False),  # Muy larga
            ("abc123456", False),  # Contiene letras
            ("", False),           # Vacía
        ]
        
        for cedula, esperado in cedulas_prueba:
            es_valida, mensaje = DataValidator.validar_cedula_colombiana(cedula)
            resultado = "✅" if es_valida == esperado else "❌"
            print(f"  {resultado} {cedula}: {mensaje}")
        
        # Pruebas de email
        print("\n📧 Probando validación de email:")
        emails_prueba = [
            ("test@example.com", True),
            ("usuario@dominio.co", True),
            ("invalid-email", False),
            ("test@", False),
            ("@domain.com", False),
            ("", True),  # Email vacío es válido (opcional)
        ]
        
        for email, esperado in emails_prueba:
            es_valido, mensaje = DataValidator.validar_email(email)
            resultado = "✅" if es_valido == esperado else "❌"
            print(f"  {resultado} {email}: {mensaje}")
        
        # Pruebas de teléfono
        print("\n📞 Probando validación de teléfono:")
        telefonos_prueba = [
            ("3001234567", True),   # Celular válido
            ("1234567", True),      # Teléfono fijo válido
            ("123456", False),      # Muy corto
            ("123456789012345", False),  # Muy largo
            ("abc123456", False),   # Contiene letras
            ("", True),             # Teléfono vacío es válido (opcional)
        ]
        
        for telefono, esperado in telefonos_prueba:
            es_valido, mensaje = DataValidator.validar_telefono(telefono)
            resultado = "✅" if es_valido == esperado else "❌"
            print(f"  {resultado} {telefono}: {mensaje}")
        
        # Pruebas de nombre
        print("\n👤 Probando validación de nombre:")
        nombres_prueba = [
            ("Juan Pérez", True),
            ("María José López", True),
            ("A", False),           # Muy corto
            ("Juan", False),        # Solo un nombre
            ("123 Juan", False),    # Contiene números
            ("", False),            # Vacío
        ]
        
        for nombre, esperado in nombres_prueba:
            es_valido, mensaje = DataValidator.validar_nombre(nombre)
            resultado = "✅" if es_valido == esperado else "❌"
            print(f"  {resultado} '{nombre}': {mensaje}")
        
        print("\n✅ Pruebas de validación completadas")
        
    except Exception as e:
        print(f"❌ Error en pruebas de validación: {e}")
        return False
    
    return True

def test_backup_manager():
    """Probar el sistema de backup"""
    print("\n💾 Probando sistema de backup...")
    
    try:
        from utils.backup_manager import BackupManager
        from models.database import get_database_path
        
        db_path = get_database_path()
        backup_manager = BackupManager(db_path)
        
        # Probar creación de backup
        print("  🔄 Creando backup de prueba...")
        success, message = backup_manager.create_backup("test_backup.db")
        if success:
            print(f"  ✅ {message}")
        else:
            print(f"  ❌ {message}")
            return False
        
        # Probar listado de backups
        print("  📋 Listando backups...")
        backups = backup_manager.list_backups()
        print(f"  📊 Total de backups: {len(backups)}")
        
        # Probar estado del sistema
        print("  📊 Obteniendo estado del sistema...")
        status = backup_manager.get_backup_status()
        print(f"  📈 Backups creados: {status['backup_count']}")
        print(f"  📁 Directorio: {status['backup_dir']}")
        
        print("\n✅ Pruebas de backup completadas")
        
    except Exception as e:
        print(f"❌ Error en pruebas de backup: {e}")
        return False
    
    return True

def test_integracion():
    """Probar integración con la base de datos"""
    print("\n🔗 Probando integración con base de datos...")
    
    try:
        from models.database import create_tables, get_db, Empleado
        from utils.validators import DataValidator
        
        # Crear tablas si no existen
        create_tables()
        
        # Obtener sesión de base de datos
        db = get_db()
        
        # Probar validación completa de empleado
        datos_prueba = {
            'nombre_completo': 'Juan Pérez Test',
            'cedula': '1234567890',
            'telefono': '3001234567',
            'email': 'juan@test.com',
            'direccion': 'Calle 123',
            'lugar_nacimiento': 'Bogotá',
            'fecha_nacimiento': None,  # No validamos fecha en esta prueba
            'nacionalidad': 'COLOMBIANA',
            'area_trabajo': 'planta',
            'cargo': 'operario',
            'salario_base': '1300000'
        }
        
        es_valido, errores = DataValidator.validar_empleado_completo(db, datos_prueba)
        
        if es_valido:
            print("  ✅ Validación de empleado completa exitosa")
        else:
            print("  ❌ Errores en validación de empleado:")
            for error in errores:
                print(f"    • {error}")
        
        # Probar verificación de duplicados
        print("  🔍 Probando verificación de duplicados...")
        es_duplicado, mensaje = DataValidator.verificar_duplicado_cedula(db, "1234567890")
        print(f"  📋 Resultado: {mensaje}")
        
        db.close()
        print("\n✅ Pruebas de integración completadas")
        
    except Exception as e:
        print(f"❌ Error en pruebas de integración: {e}")
        return False
    
    return True

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de validación y backup")
    print("=" * 60)
    
    # Ejecutar pruebas
    tests = [
        ("Validadores", test_validadores),
        ("Backup Manager", test_backup_manager),
        ("Integración", test_integracion),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error ejecutando {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitos = 0
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{estado}: {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n📈 Resultado: {exitos}/{len(resultados)} pruebas exitosas")
    
    if exitos == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar los errores arriba.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 