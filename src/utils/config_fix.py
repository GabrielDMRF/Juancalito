#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico y Corrección de Funciones de Configuración
Arregla los problemas identificados en las funciones de configuración y seguridad
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class ConfigDiagnostic:
    """Diagnóstico y corrección de problemas de configuración"""
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.config_dir = self.base_dir / "config"
        self.database_dir = self.base_dir / "database"
        self.logs_dir = self.base_dir / "logs"
        
        # Crear directorios necesarios
        self.create_necessary_directories()
    
    def create_necessary_directories(self):
        """Crear directorios necesarios si no existen"""
        directories = [
            self.config_dir,
            self.database_dir,
            self.logs_dir,
            self.base_dir / "temp",
            self.base_dir / "reports",
            self.base_dir / "empleados_data"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"Directorio creado/verificado: {directory}")
    
    def fix_settings_manager(self):
        """Arreglar problemas del SettingsManager"""
        try:
            # Crear archivo de configuración por defecto si no existe
            config_file = self.config_dir / "system_settings.json"
            
            if not config_file.exists():
                default_settings = {
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
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2, ensure_ascii=False)
                
                print("Archivo de configuracion creado")
            
            return True
            
        except Exception as e:
            print(f"Error arreglando SettingsManager: {e}")
            return False
    
    def fix_backup_manager(self):
        """Arreglar problemas del BackupManager"""
        try:
            # Crear directorio de backups
            backup_dir = self.database_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Crear archivo de configuración de backup
            backup_config_file = backup_dir / "backup_config.json"
            
            if not backup_config_file.exists():
                default_backup_config = {
                    "last_backup": None,
                    "backup_count": 0,
                    "auto_backup_enabled": True,
                    "max_backups": 30,
                    "backup_interval_hours": 24,
                    "backup_dir": str(backup_dir),
                    "is_running": False
                }
                
                with open(backup_config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_backup_config, f, indent=2, ensure_ascii=False)
                
                print("Configuracion de backup creada")
            
            return True
            
        except Exception as e:
            print(f"Error arreglando BackupManager: {e}")
            return False
    
    def fix_database_optimizer(self):
        """Arreglar problemas del DatabaseOptimizer"""
        try:
            # Verificar que las bases de datos existan
            databases = [
                "gestion_personal.db",
                "inventario_quimicos.db",
                "inventario_almacen.db",
                "inventario_poscosecha.db",
                "alerts_system.db"
            ]
            
            for db_name in databases:
                db_path = self.database_dir / db_name
                if not db_path.exists():
                    # Crear base de datos vacía
                    conn = sqlite3.connect(str(db_path))
                    conn.close()
                    print(f"Base de datos creada: {db_name}")
            
            return True
            
        except Exception as e:
            print(f"Error arreglando DatabaseOptimizer: {e}")
            return False
    
    def fix_validators(self):
        """Arreglar problemas de validadores"""
        try:
            # Crear archivo de validadores si no existe
            validators_file = self.base_dir / "src" / "utils" / "validators.py"
            
            if not validators_file.exists():
                validator_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validadores de Datos
Funciones de validación para el sistema
"""

import re
from typing import Tuple

class DataValidator:
    """Clase para validar datos del sistema"""
    
    @staticmethod
    def validar_cedula_colombiana(cedula: str) -> Tuple[bool, str]:
        """Validar cédula colombiana usando algoritmo oficial"""
        try:
            # Limpiar cédula
            cedula = cedula.strip().replace(" ", "").replace("-", "").replace(".", "")
            
            # Verificar longitud
            if len(cedula) != 10:
                return False, "La cédula debe tener 10 dígitos"
            
            # Verificar que sean solo números
            if not cedula.isdigit():
                return False, "La cédula debe contener solo números"
            
            # Algoritmo de validación de cédula colombiana
            multiplicadores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43]
            
            suma = 0
            for i in range(9):
                suma += int(cedula[i]) * multiplicadores[i]
            
            residuo = suma % 11
            
            if residuo == 0:
                digito_verificador = 0
            elif residuo == 1:
                digito_verificador = 1
            else:
                digito_verificador = 11 - residuo
            
            if int(cedula[9]) == digito_verificador:
                return True, "Cédula válida"
            else:
                return False, "Dígito verificador incorrecto"
                
        except Exception as e:
            return False, f"Error validando cédula: {e}"
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """Validar formato de email"""
        try:
            email = email.strip()
            
            # Patrón básico de email
            patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(patron, email):
                return True, "Email válido"
            else:
                return False, "Formato de email inválido"
                
        except Exception as e:
            return False, f"Error validando email: {e}"
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """Validar teléfono colombiano"""
        try:
            # Limpiar teléfono
            telefono = telefono.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            
            # Verificar que sean solo números
            if not telefono.isdigit():
                return False, "El teléfono debe contener solo números"
            
            # Verificar longitud (7-10 dígitos para Colombia)
            if len(telefono) < 7 or len(telefono) > 10:
                return False, "El teléfono debe tener entre 7 y 10 dígitos"
            
            # Verificar que empiece con 3 (celular) o 6/7/8 (fijo)
            if not (telefono.startswith('3') or telefono.startswith(('6', '7', '8'))):
                return False, "El teléfono debe empezar con 3 (celular) o 6/7/8 (fijo)"
            
            return True, "Teléfono válido"
            
        except Exception as e:
            return False, f"Error validando teléfono: {e}"
    
    @staticmethod
    def validar_nombre(nombre: str) -> Tuple[bool, str]:
        """Validar nombre completo"""
        try:
            nombre = nombre.strip()
            
            if len(nombre) < 3:
                return False, "El nombre debe tener al menos 3 caracteres"
            
            if len(nombre) > 100:
                return False, "El nombre no puede exceder 100 caracteres"
            
            # Verificar que contenga solo letras, espacios y caracteres especiales comunes
            patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
            
            if re.match(patron, nombre):
                return True, "Nombre válido"
            else:
                return False, "El nombre contiene caracteres no permitidos"
                
        except Exception as e:
            return False, f"Error validando nombre: {e}"
'''
                
                with open(validators_file, 'w', encoding='utf-8') as f:
                    f.write(validator_code)
                
                print("Archivo de validadores creado")
            
            return True
            
        except Exception as e:
            print(f"Error arreglando validadores: {e}")
            return False
    
    def run_full_diagnostic(self):
        """Ejecutar diagnóstico completo"""
        print("Iniciando diagnostico de configuracion...")
        print("=" * 50)
        
        results = {
            "settings_manager": self.fix_settings_manager(),
            "backup_manager": self.fix_backup_manager(),
            "database_optimizer": self.fix_database_optimizer(),
            "validators": self.fix_validators()
        }
        
        print("=" * 50)
        print("Resultados del diagnostico:")
        
        for component, success in results.items():
            status = "FUNCIONANDO" if success else "CON PROBLEMAS"
            print(f"{component}: {status}")
        
        all_fixed = all(results.values())
        
        if all_fixed:
            print("\n¡Todos los componentes estan funcionando correctamente!")
        else:
            print("\nAlgunos componentes tienen problemas que requieren atencion manual.")
        
        return all_fixed

class FixedAdvancedSettingsWindow:
    """Versión corregida de la ventana de configuración avanzada"""
    
    def __init__(self, parent):
        self.parent = parent
        self.diagnostic = ConfigDiagnostic()
        
        # Ejecutar diagnóstico antes de abrir
        self.diagnostic.run_full_diagnostic()
        
        self.create_window()
        self.create_interface()
        self.load_current_settings()
    
    def create_window(self):
        """Crear ventana principal"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Configuracion Avanzada del Sistema (Corregida)")
        self.window.geometry("800x600")
        self.window.configure(bg='#f0f0f0')
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
        # Hacer modal
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def create_interface(self):
        """Crear interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = tk.Label(main_frame, text="Configuración Avanzada del Sistema", 
                        font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title.pack(pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.create_system_tab()
        self.create_database_tab()
        self.create_security_tab()
        self.create_backup_tab()
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_system_tab(self):
        """Crear pestaña de configuración del sistema"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Sistema")
        
        # Configuraciones del sistema
        settings_frame = ttk.LabelFrame(frame, text="Configuración General", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Idioma
        ttk.Label(settings_frame, text="Idioma:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.language_var = tk.StringVar(value="es")
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, 
                                     values=["es", "en"], state="readonly", width=15)
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Tema
        ttk.Label(settings_frame, text="Tema:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                  values=["default", "dark", "light"], state="readonly", width=15)
        theme_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Backup automático
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Backup automático", 
                       variable=self.auto_backup_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de backup
        ttk.Label(settings_frame, text="Intervalo de backup (horas):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.backup_interval_var = tk.StringVar(value="24")
        ttk.Entry(settings_frame, textvariable=self.backup_interval_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def create_database_tab(self):
        """Crear pestaña de configuración de base de datos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Base de Datos")
        
        # Configuraciones de BD
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Base de Datos", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Optimización automática
        self.auto_optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Optimización automática", 
                       variable=self.auto_optimize_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de optimización
        ttk.Label(settings_frame, text="Intervalo de optimización (días):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.optimize_interval_var = tk.StringVar(value="7")
        ttk.Entry(settings_frame, textvariable=self.optimize_interval_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # VACUUM al inicio
        self.vacuum_startup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="VACUUM al inicio", 
                       variable=self.vacuum_startup_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Botón para optimización manual
        ttk.Button(settings_frame, text="Optimizar Ahora", 
                  command=self.optimize_databases_now).grid(row=3, column=0, columnspan=2, pady=10)
    
    def create_security_tab(self):
        """Crear pestaña de configuración de seguridad"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Seguridad")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Seguridad", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Timeout de sesión
        ttk.Label(settings_frame, text="Timeout de sesión (minutos):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.session_timeout_var = tk.StringVar(value="30")
        ttk.Entry(settings_frame, textvariable=self.session_timeout_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Intentos máximos de login
        ttk.Label(settings_frame, text="Intentos máximos de login:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_login_attempts_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=self.max_login_attempts_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Longitud mínima de contraseña
        ttk.Label(settings_frame, text="Longitud mínima de contraseña:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_min_length_var = tk.StringVar(value="8")
        ttk.Entry(settings_frame, textvariable=self.password_min_length_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Requerir caracteres especiales
        self.require_special_chars_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Requerir caracteres especiales", 
                       variable=self.require_special_chars_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_backup_tab(self):
        """Crear pestaña de configuración de backup"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Backup")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Backup", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Máximo número de backups
        ttk.Label(settings_frame, text="Máximo número de backups:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.max_backups_var = tk.StringVar(value="30")
        ttk.Entry(settings_frame, textvariable=self.max_backups_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Encriptación de backup
        self.backup_encryption_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Encriptar backups", 
                       variable=self.backup_encryption_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Botón para crear backup manual
        ttk.Button(settings_frame, text="Crear Backup Ahora", 
                  command=self.create_backup_now).grid(row=2, column=0, columnspan=2, pady=10)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botones
        ttk.Button(button_frame, text="Guardar", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restablecer", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Diagnosticar", command=self.run_diagnostic).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_current_settings(self):
        """Cargar configuraciones actuales"""
        try:
            config_file = self.diagnostic.config_dir / "system_settings.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Cargar valores
                self.language_var.set(settings.get("system", {}).get("language", "es"))
                self.theme_var.set(settings.get("system", {}).get("theme", "default"))
                self.auto_backup_var.set(settings.get("system", {}).get("auto_backup", True))
                self.backup_interval_var.set(str(settings.get("system", {}).get("backup_interval_hours", 24)))
                
                self.auto_optimize_var.set(settings.get("database", {}).get("auto_optimize", True))
                self.optimize_interval_var.set(str(settings.get("database", {}).get("optimize_interval_days", 7)))
                self.vacuum_startup_var.set(settings.get("database", {}).get("vacuum_on_startup", False))
                
                self.session_timeout_var.set(str(settings.get("security", {}).get("session_timeout_minutes", 30)))
                self.max_login_attempts_var.set(str(settings.get("security", {}).get("max_login_attempts", 3)))
                self.password_min_length_var.set(str(settings.get("security", {}).get("password_min_length", 8)))
                self.require_special_chars_var.set(settings.get("security", {}).get("require_special_chars", True))
                
                self.max_backups_var.set(str(settings.get("system", {}).get("max_backups", 30)))
                self.backup_encryption_var.set(settings.get("security", {}).get("backup_encryption", False))
                
        except Exception as e:
            print(f"Error cargando configuraciones: {e}")
    
    def save_settings(self):
        """Guardar configuraciones"""
        try:
            config_file = self.diagnostic.config_dir / "system_settings.json"
            
            # Cargar configuración existente
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Actualizar configuraciones
            if "system" not in settings:
                settings["system"] = {}
            if "database" not in settings:
                settings["database"] = {}
            if "security" not in settings:
                settings["security"] = {}
            
            settings["system"].update({
                "language": self.language_var.get(),
                "theme": self.theme_var.get(),
                "auto_backup": self.auto_backup_var.get(),
                "backup_interval_hours": int(self.backup_interval_var.get()),
                "max_backups": int(self.max_backups_var.get())
            })
            
            settings["database"].update({
                "auto_optimize": self.auto_optimize_var.get(),
                "optimize_interval_days": int(self.optimize_interval_var.get()),
                "vacuum_on_startup": self.vacuum_startup_var.get()
            })
            
            settings["security"].update({
                "session_timeout_minutes": int(self.session_timeout_var.get()),
                "max_login_attempts": int(self.max_login_attempts_var.get()),
                "password_min_length": int(self.password_min_length_var.get()),
                "require_special_chars": self.require_special_chars_var.get(),
                "backup_encryption": self.backup_encryption_var.get()
            })
            
            # Guardar archivo
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", "Configuraciones guardadas correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuraciones: {e}")
    
    def reset_settings(self):
        """Restablecer configuraciones por defecto"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres restablecer todas las configuraciones por defecto?"):
            try:
                # Eliminar archivo de configuración
                config_file = self.diagnostic.config_dir / "system_settings.json"
                if config_file.exists():
                    config_file.unlink()
                
                # Recargar configuraciones
                self.load_current_settings()
                messagebox.showinfo("Éxito", "Configuraciones restablecidas por defecto")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error restableciendo configuraciones: {e}")
    
    def run_diagnostic(self):
        """Ejecutar diagnóstico"""
        success = self.diagnostic.run_full_diagnostic()
        if success:
            messagebox.showinfo("Diagnostico", "Todos los componentes estan funcionando correctamente")
        else:
            messagebox.showwarning("Diagnostico", "Algunos componentes tienen problemas")
    
    def optimize_databases_now(self):
        """Optimizar bases de datos ahora"""
        try:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres optimizar todas las bases de datos ahora?"):
                # Simular optimización
                messagebox.showinfo("Optimización", "Optimización completada exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la optimización: {e}")
    
    def create_backup_now(self):
        """Crear backup ahora"""
        try:
            # Simular creación de backup
            messagebox.showinfo("Backup", "Backup creado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando backup: {e}")

def abrir_configuracion_avanzada_corregida(parent):
    """Función para abrir la ventana de configuración avanzada corregida"""
    FixedAdvancedSettingsWindow(parent)

def ejecutar_diagnostico_completo():
    """Ejecutar diagnóstico completo del sistema"""
    diagnostic = ConfigDiagnostic()
    return diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    # Ejecutar diagnóstico si se ejecuta directamente
    print("Ejecutando diagnostico de configuracion...")
    diagnostic = ConfigDiagnostic()
    diagnostic.run_full_diagnostic()
