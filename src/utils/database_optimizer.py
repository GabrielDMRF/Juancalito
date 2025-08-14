#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizador de Base de Datos
Mantiene las bases de datos optimizadas y con buen rendimiento
"""

import sqlite3
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .logger import get_logger, log_system_event, log_performance
from .settings_manager import get_setting

class DatabaseOptimizer:
    """Sistema de optimización automática para bases de datos SQLite"""
    
    def __init__(self):
        self.logger = get_logger("database_optimizer")
        self.optimization_thread = None
        self.stop_optimization = False
        self.last_optimization = {}
        
        # Configuraciones
        self.auto_optimize = get_setting("database.auto_optimize", True)
        self.optimize_interval_days = get_setting("database.optimize_interval_days", 7)
        self.vacuum_on_startup = get_setting("database.vacuum_on_startup", False)
        
        # Iniciar optimización automática si está habilitada
        if self.auto_optimize:
            self.start_auto_optimization()
    
    def get_database_paths(self) -> List[str]:
        """Obtener rutas de todas las bases de datos del sistema"""
        base_dir = Path(__file__).resolve().parent.parent.parent
        db_dir = base_dir / "database"
        
        databases = [
            str(db_dir / "gestion_personal.db"),
            str(db_dir / "inventario_quimicos.db"),
            str(db_dir / "inventario_almacen.db"),
            str(db_dir / "inventario_poscosecha.db"),
            str(db_dir / "alerts_system.db")
        ]
        
        # Filtrar solo las que existen
        return [db for db in databases if os.path.exists(db)]
    
    def analyze_database(self, db_path: str) -> Dict[str, any]:
        """Analizar el estado de una base de datos"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obtener información de la base de datos
            cursor.execute("PRAGMA database_list")
            db_info = cursor.fetchall()
            
            # Obtener tamaño de la base de datos
            db_size = os.path.getsize(db_path)
            
            # Obtener información de tablas
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()
            
            # Obtener estadísticas de fragmentación
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            # Obtener información de índices
            cursor.execute("""
                SELECT name, tbl_name FROM sqlite_master 
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            indexes = cursor.fetchall()
            
            # Calcular fragmentación aproximada
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            theoretical_size = page_count * page_size
            fragmentation = ((db_size - theoretical_size) / db_size * 100) if db_size > 0 else 0
            
            conn.close()
            
            return {
                "path": db_path,
                "size_bytes": db_size,
                "size_mb": round(db_size / (1024 * 1024), 2),
                "tables_count": len(tables),
                "indexes_count": len(indexes),
                "fragmentation_percent": round(fragmentation, 2),
                "integrity": integrity,
                "page_count": page_count,
                "page_size": page_size,
                "last_analyzed": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando base de datos {db_path}: {e}")
            return {
                "path": db_path,
                "error": str(e),
                "last_analyzed": datetime.now().isoformat()
            }
    
    def optimize_database(self, db_path: str, vacuum: bool = True) -> Tuple[bool, str]:
        """Optimizar una base de datos específica"""
        start_time = time.time()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Análisis antes de la optimización
            before_analysis = self.analyze_database(db_path)
            
            # Ejecutar ANALYZE para actualizar estadísticas
            cursor.execute("ANALYZE")
            
            # Ejecutar VACUUM si está habilitado
            if vacuum:
                cursor.execute("VACUUM")
            
            # Reindexar índices
            cursor.execute("REINDEX")
            
            conn.commit()
            conn.close()
            
            # Análisis después de la optimización
            after_analysis = self.analyze_database(db_path)
            
            # Calcular mejoras
            size_reduction = before_analysis.get("size_mb", 0) - after_analysis.get("size_mb", 0)
            fragmentation_reduction = before_analysis.get("fragmentation_percent", 0) - after_analysis.get("fragmentation_percent", 0)
            
            duration = time.time() - start_time
            
            # Registrar métricas
            log_performance(
                "database_optimization",
                duration,
                {
                    "database": os.path.basename(db_path),
                    "size_reduction_mb": round(size_reduction, 2),
                    "fragmentation_reduction": round(fragmentation_reduction, 2),
                    "vacuum_performed": vacuum
                }
            )
            
            # Registrar evento
            log_system_event(
                "database_optimized",
                f"Base de datos {os.path.basename(db_path)} optimizada. "
                f"Reducción: {round(size_reduction, 2)}MB, "
                f"Fragmentación: {round(fragmentation_reduction, 2)}%",
                "INFO"
            )
            
            return True, f"Optimización exitosa. Reducción: {round(size_reduction, 2)}MB"
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error optimizando {db_path}: {e}"
            self.logger.error(error_msg)
            
            log_performance(
                "database_optimization_error",
                duration,
                {"database": os.path.basename(db_path), "error": str(e)}
            )
            
            return False, error_msg
    
    def optimize_all_databases(self) -> Dict[str, Tuple[bool, str]]:
        """Optimizar todas las bases de datos del sistema"""
        results = {}
        databases = self.get_database_paths()
        
        self.logger.info(f"Iniciando optimización de {len(databases)} bases de datos")
        
        for db_path in databases:
            success, message = self.optimize_database(db_path)
            results[db_path] = (success, message)
            
            # Pequeña pausa entre optimizaciones
            time.sleep(1)
        
        # Actualizar timestamp de última optimización
        self.last_optimization = {
            "timestamp": datetime.now().isoformat(),
            "databases_processed": len(databases),
            "successful": sum(1 for success, _ in results.values() if success),
            "failed": sum(1 for success, _ in results.values() if not success)
        }
        
        return results
    
    def should_optimize_database(self, db_path: str) -> bool:
        """Verificar si una base de datos necesita optimización"""
        try:
            # Verificar si nunca se ha optimizado
            if db_path not in self.last_optimization:
                return True
            
            # Verificar intervalo de tiempo
            last_time = datetime.fromisoformat(self.last_optimization["timestamp"])
            days_since_last = (datetime.now() - last_time).days
            
            return days_since_last >= self.optimize_interval_days
            
        except Exception as e:
            self.logger.error(f"Error verificando necesidad de optimización: {e}")
            return True
    
    def start_auto_optimization(self):
        """Iniciar optimización automática en hilo separado"""
        if self.optimization_thread and self.optimization_thread.is_alive():
            return
        
        self.stop_optimization = False
        self.optimization_thread = threading.Thread(
            target=self._auto_optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        
        self.logger.info("Optimización automática iniciada")
    
    def stop_auto_optimization(self):
        """Detener optimización automática"""
        self.stop_optimization = True
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        
        self.logger.info("Optimización automática detenida")
    
    def _auto_optimization_loop(self):
        """Bucle principal de optimización automática"""
        while not self.stop_optimization:
            try:
                # Verificar si es momento de optimizar
                databases_to_optimize = [
                    db for db in self.get_database_paths()
                    if self.should_optimize_database(db)
                ]
                
                if databases_to_optimize:
                    self.logger.info(f"Optimizando {len(databases_to_optimize)} bases de datos automáticamente")
                    self.optimize_all_databases()
                
                # Esperar hasta la próxima verificación (24 horas)
                time.sleep(24 * 60 * 60)
                
            except Exception as e:
                self.logger.error(f"Error en bucle de optimización automática: {e}")
                time.sleep(60 * 60)  # Esperar 1 hora antes de reintentar
    
    def get_optimization_status(self) -> Dict[str, any]:
        """Obtener estado de optimización del sistema"""
        databases = self.get_database_paths()
        analysis_results = {}
        
        for db_path in databases:
            analysis_results[db_path] = self.analyze_database(db_path)
        
        return {
            "auto_optimize_enabled": self.auto_optimize,
            "optimize_interval_days": self.optimize_interval_days,
            "last_optimization": self.last_optimization,
            "databases_count": len(databases),
            "databases_analysis": analysis_results,
            "total_size_mb": sum(
                analysis.get("size_mb", 0) 
                for analysis in analysis_results.values()
            ),
            "average_fragmentation": sum(
                analysis.get("fragmentation_percent", 0) 
                for analysis in analysis_results.values()
            ) / len(analysis_results) if analysis_results else 0
        }
    
    def vacuum_on_startup_if_needed(self):
        """Ejecutar VACUUM al inicio si está configurado"""
        if not self.vacuum_on_startup:
            return
        
        self.logger.info("Ejecutando VACUUM al inicio del sistema")
        
        for db_path in self.get_database_paths():
            try:
                success, message = self.optimize_database(db_path, vacuum=True)
                if success:
                    self.logger.info(f"VACUUM exitoso en {os.path.basename(db_path)}")
                else:
                    self.logger.warning(f"VACUUM falló en {os.path.basename(db_path)}: {message}")
            except Exception as e:
                self.logger.error(f"Error en VACUUM de {db_path}: {e}")

# Instancia global del optimizador
database_optimizer = DatabaseOptimizer()

def optimize_database(db_path: str, vacuum: bool = True) -> Tuple[bool, str]:
    """Función helper para optimizar una base de datos"""
    return database_optimizer.optimize_database(db_path, vacuum)

def optimize_all_databases() -> Dict[str, Tuple[bool, str]]:
    """Función helper para optimizar todas las bases de datos"""
    return database_optimizer.optimize_all_databases()

def get_optimization_status() -> Dict[str, any]:
    """Función helper para obtener estado de optimización"""
    return database_optimizer.get_optimization_status() 