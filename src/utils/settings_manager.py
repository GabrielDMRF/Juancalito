#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Configuraciones del Sistema
Maneja todas las configuraciones del sistema de forma centralizada
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import threading
from .logger import get_logger, log_system_event

class SettingsManager:
    """Gestor centralizado de configuraciones del sistema"""
    
    def __init__(self):
        self.logger = get_logger("settings")
        self.config_file = self._get_config_path()
        self.settings_cache = {}
        self.lock = threading.Lock()
        self._load_settings()
    
    def _get_config_path(self) -> Path:
        """Obtener ruta del archivo de configuración"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_dir = base_dir / "config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "system_settings.json"
    
    def _load_settings(self):
        """Cargar configuraciones desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.settings_cache = json.load(f)
                self.logger.info("Configuraciones cargadas exitosamente")
            else:
                self._create_default_settings()
                
        except Exception as e:
            self.logger.error(f"Error cargando configuraciones: {e}")
            self._create_default_settings()
    
    def _create_default_settings(self):
        """Crear configuraciones por defecto"""
        self.settings_cache = {
            "system": {
                "version": "2.0.0",
                "language": "es",
                "theme": "default",
                "auto_backup": True,
                "backup_interval_hours": 24,
                "max_backups": 30,
                "enable_logging": True,
                "log_level": "INFO"
            },
            "database": {
                "auto_optimize": True,
                "optimize_interval_days": 7,
                "vacuum_on_startup": False,
                "connection_timeout": 30
            },
            "interface": {
                "window_width": 1100,
                "window_height": 700,
                "remember_position": True,
                "show_tooltips": True,
                "auto_refresh_interval": 30
            },
            "notifications": {
                "enable_desktop_notifications": True,
                "sound_enabled": True,
                "stock_alert_threshold": 10,
                "expiration_alert_days": 30,
                "contract_expiry_alert_days": 7
            },
            "reports": {
                "default_format": "PDF",
                "include_charts": True,
                "auto_open_reports": True,
                "save_reports": True,
                "reports_directory": "reports/generated"
            },
            "security": {
                "session_timeout_minutes": 30,
                "max_login_attempts": 3,
                "password_min_length": 8,
                "require_special_chars": True,
                "backup_encryption": False
            },
            "performance": {
                "cache_enabled": True,
                "cache_size_mb": 100,
                "auto_cleanup_cache": True,
                "cleanup_interval_hours": 24
            }
        }
        self._save_settings()
        self.logger.info("Configuraciones por defecto creadas")
    
    def _save_settings(self):
        """Guardar configuraciones en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_cache, f, indent=2, ensure_ascii=False)
            self.logger.info("Configuraciones guardadas exitosamente")
        except Exception as e:
            self.logger.error(f"Error guardando configuraciones: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        with self.lock:
            keys = key.split('.')
            value = self.settings_cache
            
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key: str, value: Any) -> bool:
        """Establecer valor de configuración"""
        try:
            with self.lock:
                keys = key.split('.')
                current = self.settings_cache
                
                # Navegar hasta el último nivel
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # Establecer valor
                current[keys[-1]] = value
                
                # Guardar cambios
                self._save_settings()
                
                # Registrar cambio
                log_system_event(
                    "setting_changed",
                    f"Configuración '{key}' actualizada a: {value}",
                    "INFO"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error estableciendo configuración '{key}': {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Obtener todas las configuraciones"""
        with self.lock:
            return self.settings_cache.copy()
    
    def update_multiple(self, settings: Dict[str, Any]) -> bool:
        """Actualizar múltiples configuraciones"""
        try:
            with self.lock:
                for key, value in settings.items():
                    keys = key.split('.')
                    current = self.settings_cache
                    
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    
                    current[keys[-1]] = value
                
                self._save_settings()
                self.logger.info(f"Actualizadas {len(settings)} configuraciones")
                return True
                
        except Exception as e:
            self.logger.error(f"Error actualizando configuraciones: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Restablecer configuraciones por defecto"""
        try:
            self._create_default_settings()
            log_system_event("settings_reset", "Configuraciones restablecidas por defecto", "WARNING")
            return True
        except Exception as e:
            self.logger.error(f"Error restableciendo configuraciones: {e}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """Exportar configuraciones a archivo"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings_cache, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuraciones exportadas a: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando configuraciones: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Importar configuraciones desde archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validar estructura básica
            required_sections = ['system', 'database', 'interface']
            for section in required_sections:
                if section not in imported_settings:
                    raise ValueError(f"Sección requerida '{section}' no encontrada")
            
            with self.lock:
                self.settings_cache = imported_settings
                self._save_settings()
            
            self.logger.info(f"Configuraciones importadas desde: {file_path}")
            log_system_event("settings_imported", f"Configuraciones importadas desde {file_path}", "INFO")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importando configuraciones: {e}")
            return False
    
    def get_database_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones específicas de base de datos"""
        return {
            "auto_optimize": self.get("database.auto_optimize", True),
            "optimize_interval_days": self.get("database.optimize_interval_days", 7),
            "vacuum_on_startup": self.get("database.vacuum_on_startup", False),
            "connection_timeout": self.get("database.connection_timeout", 30)
        }
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """Obtener configuraciones específicas de notificaciones"""
        return {
            "enable_desktop_notifications": self.get("notifications.enable_desktop_notifications", True),
            "sound_enabled": self.get("notifications.sound_enabled", True),
            "stock_alert_threshold": self.get("notifications.stock_alert_threshold", 10),
            "expiration_alert_days": self.get("notifications.expiration_alert_days", 30),
            "contract_expiry_alert_days": self.get("notifications.contract_expiry_alert_days", 7)
        }

# Instancia global del gestor de configuraciones
settings_manager = SettingsManager()

def get_setting(key: str, default: Any = None) -> Any:
    """Función helper para obtener configuración"""
    return settings_manager.get(key, default)

def set_setting(key: str, value: Any) -> bool:
    """Función helper para establecer configuración"""
    return settings_manager.set(key, value)

def get_all_settings() -> Dict[str, Any]:
    """Función helper para obtener todas las configuraciones"""
    return settings_manager.get_all() 