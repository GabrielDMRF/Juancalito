# src/utils/data_integration.py
"""
Gestor de Integración de Datos para el Sistema
Maneja la sincronización entre diferentes módulos
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

class DataIntegrationManager:
    """Gestor central para integración de datos entre módulos"""
    
    def __init__(self):
        self.db_paths = {
            'personal': 'database/gestion_personal.db',
            'quimicos': 'database/inventario_quimicos_avanzado.db',
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
        self.ensure_databases()
    
    def ensure_databases(self):
        """Asegurar que existan todas las bases de datos"""
        os.makedirs('database', exist_ok=True)
        for db_name, db_path in self.db_paths.items():
            if not os.path.exists(db_path):
                print(f"⚠️ Creando base de datos: {db_name}")
                self.create_database(db_name, db_path)
    
    def create_database(self, db_name, db_path):
        """Crear base de datos con estructura básica"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if db_name == 'personal':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY,
                    nombre_completo TEXT,
                    cedula TEXT UNIQUE,
                    area_trabajo TEXT,
                    estado BOOLEAN DEFAULT 1
                )
            ''')
        elif db_name == 'quimicos':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos_quimicos (
                    id INTEGER PRIMARY KEY,
                    codigo TEXT UNIQUE,
                    nombre TEXT,
                    clase TEXT,
                    saldo_real INTEGER DEFAULT 0,
                    activo BOOLEAN DEFAULT 1
                )
            ''')
        # Agregar más estructuras según necesidad
        
        conn.commit()
        conn.close()
    
    def get_global_statistics(self):
        """Obtener estadísticas globales del sistema"""
        stats = {
            'empleados_activos': 0,
            'total_productos': 0,
            'productos_criticos': 0,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Estadísticas de personal
            if os.path.exists(self.db_paths['personal']):
                conn = sqlite3.connect(self.db_paths['personal'])
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM empleados WHERE estado = 1")
                stats['empleados_activos'] = cursor.fetchone()[0]
                conn.close()
            
            # Estadísticas de inventarios
            for inv_type in ['quimicos', 'almacen', 'poscosecha']:
                if os.path.exists(self.db_paths[inv_type]):
                    conn = sqlite3.connect(self.db_paths[inv_type])
                    cursor = conn.cursor()
                    
                    if inv_type == 'quimicos':
                        cursor.execute("SELECT COUNT(*) FROM productos_quimicos WHERE activo = 1")
                        stats['total_productos'] += cursor.fetchone()[0]
                        
                        cursor.execute("SELECT COUNT(*) FROM productos_quimicos WHERE saldo_real <= 100 AND activo = 1")
                        stats['productos_criticos'] += cursor.fetchone()[0]
                    
                    conn.close()
                    
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
        
        return stats
    
    def import_excel_data(self, file_path, target_system):
        """Importar datos desde Excel a sistema específico"""
        try:
            print(f"📁 Importando desde: {file_path}")
            
            # Leer Excel
            df = pd.read_excel(file_path, engine='openpyxl')
            print(f"📊 Filas encontradas: {len(df)}")
            
            # Procesar según sistema objetivo
            if target_system == 'quimicos':
                return self.process_quimicos_excel(df)
            elif target_system == 'almacen':
                return self.process_almacen_excel(df)
            elif target_system == 'poscosecha':
                return self.process_poscosecha_excel(df)
            
        except Exception as e:
            print(f"❌ Error importando Excel: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_quimicos_excel(self, df):
        """Procesar datos de químicos desde Excel"""
        try:
            conn = sqlite3.connect(self.db_paths['quimicos'])
            imported = 0
            
            for index, row in df.iterrows():
                # Lógica de procesamiento específica para químicos
                # Adaptar según estructura real del Excel
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO productos_quimicos 
                        (codigo, nombre, clase, saldo_real) 
                        VALUES (?, ?, ?, ?)
                    ''', (
                        f"QM{imported+1:03d}",
                        str(row.iloc[0]) if not pd.isna(row.iloc[0]) else "Producto",
                        "QUIMICO",
                        int(row.iloc[1]) if not pd.isna(row.iloc[1]) and str(row.iloc[1]).isdigit() else 0
                    ))
                    imported += 1
                except Exception as e:
                    print(f"Error procesando fila {index}: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            return {
                'success': True, 
                'imported': imported,
                'message': f'Se importaron {imported} productos químicos'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_almacen_excel(self, df):
        """Procesar datos de almacén desde Excel"""
        # Implementación similar para almacén
        return {'success': True, 'imported': 0, 'message': 'Función en desarrollo'}
    
    def process_poscosecha_excel(self, df):
        """Procesar datos de poscosecha desde Excel"""
        # Implementación similar para poscosecha
        return {'success': True, 'imported': 0, 'message': 'Función en desarrollo'}
    
    def create_backup(self):
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = f'backups/backup_{timestamp}'
            os.makedirs(backup_dir, exist_ok=True)
            
            backed_files = []
            for db_name, db_path in self.db_paths.items():
                if os.path.exists(db_path):
                    import shutil
                    backup_path = os.path.join(backup_dir, f'{db_name}.db')
                    shutil.copy2(db_path, backup_path)
                    backed_files.append(db_name)
            
            return {
                'success': True,
                'backup_dir': backup_dir,
                'files': backed_files,
                'timestamp': timestamp
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_global_report(self):
        """Generar reporte global del sistema"""
        stats = self.get_global_statistics()
        
        report = f"""
=== REPORTE GLOBAL DEL SISTEMA ===
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

PERSONAL:
- Empleados activos: {stats['empleados_activos']}

INVENTARIOS:
- Total productos: {stats['total_productos']}
- Productos críticos: {stats['productos_criticos']}

ESTADO DEL SISTEMA:
- Última actualización: {stats['ultima_actualizacion']}
- Bases de datos activas: {len([p for p in self.db_paths.values() if os.path.exists(p)])}
"""
        
        return report

# Instancia global del gestor
integration_manager = DataIntegrationManager()