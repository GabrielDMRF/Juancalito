import os
import shutil
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import json
import zipfile
from pathlib import Path

class BackupManager:
    """Sistema de backup automático para la base de datos"""
    
    def __init__(self, db_path: str, backup_dir: str = None):
        self.db_path = db_path
        self.backup_dir = backup_dir or self._get_default_backup_dir()
        self.backup_config_file = os.path.join(self.backup_dir, 'backup_config.json')
        self.max_backups = 30  # Mantener máximo 30 backups
        self.backup_interval_hours = 24  # Backup diario
        
        # Crear directorio de backup si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Thread para backup automático
        self.backup_thread = None
        self.stop_backup = False
    
    def _get_default_backup_dir(self) -> str:
        """Obtener directorio de backup por defecto"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, 'database', 'backups')
    
    def _load_config(self) -> dict:
        """Cargar configuración de backup"""
        default_config = {
            'last_backup': None,
            'backup_count': 0,
            'auto_backup_enabled': True,
            'max_backups': self.max_backups,
            'backup_interval_hours': self.backup_interval_hours
        }
        
        if os.path.exists(self.backup_config_file):
            try:
                with open(self.backup_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Actualizar con valores por defecto si faltan
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"[ERROR] Error cargando configuración de backup: {e}")
                return default_config
        
        return default_config
    
    def _save_config(self):
        """Guardar configuración de backup"""
        try:
            with open(self.backup_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            print(f"[ERROR] Error guardando configuración de backup: {e}")
    
    def create_backup(self, backup_name: str = None) -> Tuple[bool, str]:
        """
        Crear backup de la base de datos
        Retorna: (exitoso, mensaje)
        """
        try:
            if not os.path.exists(self.db_path):
                return False, "La base de datos no existe"
            
            # Generar nombre del backup
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Crear backup usando SQLite
            with sqlite3.connect(self.db_path) as source_conn:
                with sqlite3.connect(backup_path) as backup_conn:
                    source_conn.backup(backup_conn)
            
            # Crear archivo de metadatos
            metadata = {
                'fecha_creacion': datetime.now().isoformat(),
                'tamaño_original': os.path.getsize(self.db_path),
                'tamaño_backup': os.path.getsize(backup_path),
                'version_sistema': '1.2',
                'descripcion': backup_name
            }
            
            metadata_path = backup_path.replace('.db', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Actualizar configuración
            self.config['last_backup'] = datetime.now().isoformat()
            self.config['backup_count'] += 1
            self._save_config()
            
            # Limpiar backups antiguos
            self._cleanup_old_backups()
            
            return True, f"Backup creado exitosamente: {backup_name}"
            
        except Exception as e:
            return False, f"Error creando backup: {e}"
    
    def restore_backup(self, backup_name: str) -> Tuple[bool, str]:
        """
        Restaurar backup de la base de datos
        Retorna: (exitoso, mensaje)
        """
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                return False, "El archivo de backup no existe"
            
            # Crear backup del estado actual antes de restaurar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = f"pre_restore_{timestamp}.db"
            pre_restore_path = os.path.join(self.backup_dir, pre_restore_backup)
            
            # Crear backup de seguridad
            with sqlite3.connect(self.db_path) as source_conn:
                with sqlite3.connect(pre_restore_path) as backup_conn:
                    source_conn.backup(backup_conn)
            
            # Restaurar backup
            with sqlite3.connect(backup_path) as source_conn:
                with sqlite3.connect(self.db_path) as restore_conn:
                    source_conn.backup(restore_conn)
            
            return True, f"Backup restaurado exitosamente. Backup de seguridad creado: {pre_restore_backup}"
            
        except Exception as e:
            return False, f"Error restaurando backup: {e}"
    
    def list_backups(self) -> List[dict]:
        """Listar todos los backups disponibles"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                if file.endswith('.db') and file.startswith('backup_'):
                    backup_path = os.path.join(self.backup_dir, file)
                    metadata_path = backup_path.replace('.db', '_metadata.json')
                    
                    backup_info = {
                        'nombre': file,
                        'ruta': backup_path,
                        'tamaño': os.path.getsize(backup_path),
                        'fecha_creacion': datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat(),
                        'metadata': None
                    }
                    
                    # Cargar metadatos si existen
                    if os.path.exists(metadata_path):
                        try:
                            with open(metadata_path, 'r', encoding='utf-8') as f:
                                backup_info['metadata'] = json.load(f)
                        except:
                            pass
                    
                    backups.append(backup_info)
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['fecha_creacion'], reverse=True)
            
        except Exception as e:
            print(f"[ERROR] Error listando backups: {e}")
        
        return backups
    
    def _cleanup_old_backups(self):
        """Eliminar backups antiguos según la configuración"""
        try:
            backups = self.list_backups()
            
            if len(backups) > self.config['max_backups']:
                # Eliminar los backups más antiguos
                backups_to_delete = backups[self.config['max_backups']:]
                
                for backup in backups_to_delete:
                    try:
                        # Eliminar archivo de backup
                        os.remove(backup['ruta'])
                        
                        # Eliminar archivo de metadatos
                        metadata_path = backup['ruta'].replace('.db', '_metadata.json')
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        
                        print(f"[INFO] Backup eliminado: {backup['nombre']}")
                        
                    except Exception as e:
                        print(f"[ERROR] Error eliminando backup {backup['nombre']}: {e}")
        
        except Exception as e:
            print(f"[ERROR] Error en limpieza de backups: {e}")
    
    def start_auto_backup(self):
        """Iniciar backup automático en segundo plano"""
        if self.backup_thread and self.backup_thread.is_alive():
            return False, "El backup automático ya está ejecutándose"
        
        self.stop_backup = False
        self.backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self.backup_thread.start()
        
        return True, "Backup automático iniciado"
    
    def stop_auto_backup(self):
        """Detener backup automático"""
        self.stop_backup = True
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        return True, "Backup automático detenido"
    
    def _auto_backup_loop(self):
        """Loop principal del backup automático"""
        while not self.stop_backup:
            try:
                # Verificar si es necesario hacer backup
                if self._should_create_backup():
                    print("[INFO] Iniciando backup automático...")
                    success, message = self.create_backup()
                    if success:
                        print(f"[OK] Backup automático completado: {message}")
                    else:
                        print(f"[ERROR] Error en backup automático: {message}")
                
                # Esperar 1 hora antes de verificar nuevamente
                time.sleep(3600)  # 1 hora
                
            except Exception as e:
                print(f"[ERROR] Error en loop de backup automático: {e}")
                time.sleep(3600)  # Esperar 1 hora antes de reintentar
    
    def _should_create_backup(self) -> bool:
        """Verificar si se debe crear un backup automático"""
        if not self.config['auto_backup_enabled']:
            return False
        
        if not self.config['last_backup']:
            return True
        
        try:
            last_backup = datetime.fromisoformat(self.config['last_backup'])
            hours_since_last = (datetime.now() - last_backup).total_seconds() / 3600
            
            return hours_since_last >= self.config['backup_interval_hours']
        
        except Exception:
            return True
    
    def get_backup_status(self) -> dict:
        """Obtener estado actual del sistema de backup"""
        backups = self.list_backups()
        
        return {
            'auto_backup_enabled': self.config['auto_backup_enabled'],
            'last_backup': self.config['last_backup'],
            'backup_count': self.config['backup_count'],
            'max_backups': self.config['max_backups'],
            'backup_interval_hours': self.config['backup_interval_hours'],
            'total_backups': len(backups),
            'backup_dir': self.backup_dir,
            'db_path': self.db_path,
            'is_running': self.backup_thread and self.backup_thread.is_alive()
        }
    
    def create_compressed_backup(self, include_metadata: bool = True) -> Tuple[bool, str]:
        """
        Crear backup comprimido con todos los archivos del sistema
        Retorna: (exitoso, mensaje)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_name = f"backup_completo_{timestamp}.zip"
            zip_path = os.path.join(self.backup_dir, zip_name)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Agregar base de datos
                zipf.write(self.db_path, os.path.basename(self.db_path))
                
                # Agregar archivos de empleados si existen
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                empleados_dir = os.path.join(base_dir, 'empleados_data')
                
                if os.path.exists(empleados_dir):
                    for root, dirs, files in os.walk(empleados_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, base_dir)
                            zipf.write(file_path, arc_name)
                
                # Agregar metadatos del backup
                if include_metadata:
                    metadata = {
                        'fecha_creacion': datetime.now().isoformat(),
                        'tipo': 'backup_completo',
                        'version_sistema': '1.2',
                        'archivos_incluidos': ['base_datos', 'empleados_data']
                    }
                    
                    zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
            
            return True, f"Backup comprimido creado: {zip_name}"
            
        except Exception as e:
            return False, f"Error creando backup comprimido: {e}"

# Funciones de conveniencia
def create_backup_simple() -> Tuple[bool, str]:
    """Función simple para crear backup"""
    from models.database import get_database_path
    db_path = get_database_path()
    backup_manager = BackupManager(db_path)
    return backup_manager.create_backup()

def get_backup_status_simple() -> dict:
    """Función simple para obtener estado de backup"""
    from models.database import get_database_path
    db_path = get_database_path()
    backup_manager = BackupManager(db_path)
    return backup_manager.get_backup_status()

def list_backups_simple() -> List[dict]:
    """Función simple para listar backups"""
    from models.database import get_database_path
    db_path = get_database_path()
    backup_manager = BackupManager(db_path)
    return backup_manager.list_backups() 