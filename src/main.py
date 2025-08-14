import tkinter as tk
import sys
import os
import time
os.environ["PYTHONIOENCODING"] = "utf-8"

# Agregar directorios al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow
from models.database import create_tables
from utils.logger import get_logger, log_system_event, log_performance
from utils.settings_manager import settings_manager
from utils.database_optimizer import database_optimizer

def main():
    start_time = time.time()
    logger = get_logger("main")
    
    try:
        # Registrar inicio del sistema (reducido para mejor rendimiento)
        # log_system_event("system_startup", "Iniciando Sistema de Gestión de Personal", "INFO")
        
        # Inicializar configuraciones
        # logger.info("Cargando configuraciones del sistema...")
        
        # Crear tablas si no existen
        # logger.info("Inicializando base de datos...")
        create_tables()
        
        # Optimización de base de datos al inicio si está configurada
        # Comentado temporalmente para mejorar rendimiento de inicio
        # if settings_manager.get("database.vacuum_on_startup", False):
        #     logger.info("Ejecutando optimización de base de datos al inicio...")
        #     database_optimizer.vacuum_on_startup_if_needed()
        
        # Crear ventana principal
        logger.info("Creando interfaz principal...")
        root = tk.Tk()
        app = MainWindow(root)
        
        # Calcular tiempo de inicio
        startup_duration = time.time() - start_time
        # log_performance("system_startup", startup_duration, {"version": "2.0.0"})
        
        # logger.info(f"Sistema iniciado correctamente en {startup_duration:.2f} segundos")
        # log_system_event("system_ready", "Sistema listo para uso", "INFO")
        
        # Configurar cierre limpio
        def on_closing():
            log_system_event("system_shutdown", "Cerrando sistema", "INFO")
            try:
                # Detener optimización automática
                database_optimizer.stop_auto_optimization()
                logger.info("Sistema cerrado correctamente")
            except Exception as e:
                logger.error(f"Error durante el cierre: {e}")
            finally:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("[OK] Sistema iniciado correctamente")
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Error al iniciar el sistema: {e}"
        logger.error(error_msg)
        log_system_event("system_startup_error", error_msg, "ERROR")
        print(f"[ERROR] {error_msg}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()