#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging Avanzado
Proporciona logging estructurado para todo el sistema
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any

class SystemLogger:
    """Sistema de logging centralizado para el sistema de gestión"""
    
    def __init__(self, name: str = "SistemaGestionPersonal"):
        self.name = name
        self.loggers = {}
        self.log_dir = self._setup_log_directory()
        self._setup_root_logger()
    
    def _setup_log_directory(self) -> Path:
        """Configurar directorio de logs"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        log_dir = base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    def _setup_root_logger(self):
        """Configurar logger raíz del sistema"""
        # Configurar formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Handler para archivo principal
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "sistema_principal.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setFormatter(formatter)
        root_logger.addHandler(main_handler)
        
        # Handler para errores
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errores.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        # Handler para consola (solo en desarrollo)
        if self._is_development_mode():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
    
    def _is_development_mode(self) -> bool:
        """Verificar si estamos en modo desarrollo"""
        return os.environ.get('DEBUG', 'False').lower() == 'true'
    
    def get_logger(self, module_name: str) -> logging.Logger:
        """Obtener logger específico para un módulo"""
        if module_name not in self.loggers:
            logger = logging.getLogger(f"{self.name}.{module_name}")
            self.loggers[module_name] = logger
        return self.loggers[module_name]
    
    def log_user_action(self, user: str, action: str, details: Dict[str, Any] = None):
        """Registrar acciones del usuario"""
        logger = self.get_logger("user_actions")
        log_data = {
            "user": user,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        logger.info(f"USER_ACTION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_database_operation(self, operation: str, table: str, details: Dict[str, Any] = None):
        """Registrar operaciones de base de datos"""
        logger = self.get_logger("database")
        log_data = {
            "operation": operation,
            "table": table,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        logger.info(f"DB_OPERATION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_system_event(self, event_type: str, message: str, severity: str = "INFO"):
        """Registrar eventos del sistema"""
        logger = self.get_logger("system")
        log_data = {
            "event_type": event_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        if severity.upper() == "ERROR":
            logger.error(f"SYSTEM_EVENT: {json.dumps(log_data, ensure_ascii=False)}")
        elif severity.upper() == "WARNING":
            logger.warning(f"SYSTEM_EVENT: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            logger.info(f"SYSTEM_EVENT: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Registrar métricas de rendimiento"""
        logger = self.get_logger("performance")
        log_data = {
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        logger.info(f"PERFORMANCE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Limpiar logs antiguos"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                self.log_system_event(
                    "log_cleanup",
                    f"Eliminados {deleted_count} archivos de log antiguos",
                    "INFO"
                )
                
        except Exception as e:
            self.log_system_event(
                "log_cleanup_error",
                f"Error limpiando logs: {str(e)}",
                "ERROR"
            )

# Instancia global del logger
system_logger = SystemLogger()

def get_logger(module_name: str) -> logging.Logger:
    """Función helper para obtener logger"""
    return system_logger.get_logger(module_name)

def log_user_action(user: str, action: str, details: Dict[str, Any] = None):
    """Función helper para registrar acciones de usuario"""
    system_logger.log_user_action(user, action, details)

def log_database_operation(operation: str, table: str, details: Dict[str, Any] = None):
    """Función helper para registrar operaciones de BD"""
    system_logger.log_database_operation(operation, table, details)

def log_system_event(event_type: str, message: str, severity: str = "INFO"):
    """Función helper para registrar eventos del sistema"""
    system_logger.log_system_event(event_type, message, severity)

def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """Función helper para registrar métricas de rendimiento"""
    system_logger.log_performance(operation, duration, details) 