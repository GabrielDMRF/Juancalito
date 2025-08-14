#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana de Configuración Avanzada
Interfaz para gestionar todas las configuraciones del sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path
from utils.settings_manager import settings_manager, get_setting, set_setting
from utils.logger import get_logger, log_user_action
from utils.database_optimizer import get_optimization_status, optimize_all_databases

class AdvancedSettingsWindow:
    """Ventana de configuración avanzada del sistema"""
    
    def __init__(self, parent):
        self.parent = parent
        self.logger = get_logger("advanced_settings")
        self.settings = settings_manager.get_all()
        
        self.create_window()
        self.create_interface()
        self.load_current_settings()
    
    def create_window(self):
        """Crear ventana principal"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("⚙️ Configuración Avanzada del Sistema")
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
        self.create_interface_tab()
        self.create_notifications_tab()
        self.create_reports_tab()
        self.create_security_tab()
        self.create_performance_tab()
        
        # Botones de acción
        self.create_action_buttons(main_frame)
    
    def create_system_tab(self):
        """Crear pestaña de configuración del sistema"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖥️ Sistema")
        
        # Configuraciones del sistema
        settings_frame = ttk.LabelFrame(frame, text="Configuración General", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Idioma
        ttk.Label(settings_frame, text="Idioma:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.language_var = tk.StringVar()
        language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, 
                                     values=["es", "en"], state="readonly", width=15)
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Tema
        ttk.Label(settings_frame, text="Tema:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                  values=["default", "dark", "light"], state="readonly", width=15)
        theme_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Backup automático
        self.auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Backup automático", 
                       variable=self.auto_backup_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de backup
        ttk.Label(settings_frame, text="Intervalo de backup (horas):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.backup_interval_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.backup_interval_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Logging
        self.enable_logging_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Habilitar logging", 
                       variable=self.enable_logging_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Nivel de log
        ttk.Label(settings_frame, text="Nivel de log:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(settings_frame, textvariable=self.log_level_var,
                                values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=15)
        log_combo.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def create_database_tab(self):
        """Crear pestaña de configuración de base de datos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🗄️ Base de Datos")
        
        # Configuraciones de BD
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Base de Datos", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Optimización automática
        self.auto_optimize_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Optimización automática", 
                       variable=self.auto_optimize_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de optimización
        ttk.Label(settings_frame, text="Intervalo de optimización (días):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.optimize_interval_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.optimize_interval_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # VACUUM al inicio
        self.vacuum_startup_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="VACUUM al inicio", 
                       variable=self.vacuum_startup_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Timeout de conexión
        ttk.Label(settings_frame, text="Timeout de conexión (segundos):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.connection_timeout_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.connection_timeout_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Botón para optimización manual
        ttk.Button(settings_frame, text="🔄 Optimizar Ahora", 
                  command=self.optimize_databases_now).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Estado de optimización
        status_frame = ttk.LabelFrame(frame, text="Estado de Optimización", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.optimization_status_text = tk.Text(status_frame, height=8, width=70)
        self.optimization_status_text.pack(fill=tk.X)
        
        # Botón para actualizar estado
        ttk.Button(status_frame, text="🔄 Actualizar Estado", 
                  command=self.update_optimization_status).pack(pady=5)
    
    def create_interface_tab(self):
        """Crear pestaña de configuración de interfaz"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖥️ Interfaz")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Interfaz", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tamaño de ventana
        ttk.Label(settings_frame, text="Ancho de ventana:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.window_width_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.window_width_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(settings_frame, text="Alto de ventana:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.window_height_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.window_height_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Recordar posición
        self.remember_position_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Recordar posición de ventana", 
                       variable=self.remember_position_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Mostrar tooltips
        self.show_tooltips_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Mostrar tooltips", 
                       variable=self.show_tooltips_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de auto-refresh
        ttk.Label(settings_frame, text="Intervalo de auto-refresh (segundos):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.auto_refresh_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.auto_refresh_var, width=15).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def create_notifications_tab(self):
        """Crear pestaña de configuración de notificaciones"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔔 Notificaciones")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Notificaciones", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Notificaciones de escritorio
        self.desktop_notifications_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Notificaciones de escritorio", 
                       variable=self.desktop_notifications_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Sonido
        self.sound_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Habilitar sonido", 
                       variable=self.sound_enabled_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Umbral de stock crítico
        ttk.Label(settings_frame, text="Umbral de stock crítico:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.stock_threshold_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.stock_threshold_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Días de alerta de vencimiento
        ttk.Label(settings_frame, text="Días de alerta de vencimiento:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.expiration_days_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.expiration_days_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Días de alerta de contrato
        ttk.Label(settings_frame, text="Días de alerta de contrato:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.contract_days_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.contract_days_var, width=15).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def create_reports_tab(self):
        """Crear pestaña de configuración de reportes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Reportes")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Reportes", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Formato por defecto
        ttk.Label(settings_frame, text="Formato por defecto:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.report_format_var = tk.StringVar()
        format_combo = ttk.Combobox(settings_frame, textvariable=self.report_format_var,
                                   values=["PDF", "Excel", "CSV"], state="readonly", width=15)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Incluir gráficos
        self.include_charts_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Incluir gráficos", 
                       variable=self.include_charts_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Abrir automáticamente
        self.auto_open_reports_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Abrir reportes automáticamente", 
                       variable=self.auto_open_reports_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Guardar reportes
        self.save_reports_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Guardar reportes", 
                       variable=self.save_reports_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_security_tab(self):
        """Crear pestaña de configuración de seguridad"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔒 Seguridad")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Seguridad", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Timeout de sesión
        ttk.Label(settings_frame, text="Timeout de sesión (minutos):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.session_timeout_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.session_timeout_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Intentos máximos de login
        ttk.Label(settings_frame, text="Intentos máximos de login:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_login_attempts_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.max_login_attempts_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Longitud mínima de contraseña
        ttk.Label(settings_frame, text="Longitud mínima de contraseña:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_min_length_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.password_min_length_var, width=15).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Requerir caracteres especiales
        self.require_special_chars_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Requerir caracteres especiales", 
                       variable=self.require_special_chars_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Encriptación de backup
        self.backup_encryption_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Encriptar backups", 
                       variable=self.backup_encryption_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    def create_performance_tab(self):
        """Crear pestaña de configuración de rendimiento"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚡ Rendimiento")
        
        settings_frame = ttk.LabelFrame(frame, text="Configuración de Rendimiento", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Cache habilitado
        self.cache_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Habilitar cache", 
                       variable=self.cache_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Tamaño de cache
        ttk.Label(settings_frame, text="Tamaño de cache (MB):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cache_size_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.cache_size_var, width=15).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Limpieza automática de cache
        self.auto_cleanup_cache_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Limpieza automática de cache", 
                       variable=self.auto_cleanup_cache_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Intervalo de limpieza
        ttk.Label(settings_frame, text="Intervalo de limpieza (horas):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.cleanup_interval_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.cleanup_interval_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botones
        ttk.Button(button_frame, text="💾 Guardar", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Restablecer", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📤 Exportar", command=self.export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 Importar", command=self.import_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cerrar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_current_settings(self):
        """Cargar configuraciones actuales"""
        try:
            # Sistema
            self.language_var.set(get_setting("system.language", "es"))
            self.theme_var.set(get_setting("system.theme", "default"))
            self.auto_backup_var.set(get_setting("system.auto_backup", True))
            self.backup_interval_var.set(str(get_setting("system.backup_interval_hours", 24)))
            self.enable_logging_var.set(get_setting("system.enable_logging", True))
            self.log_level_var.set(get_setting("system.log_level", "INFO"))
            
            # Base de datos
            self.auto_optimize_var.set(get_setting("database.auto_optimize", True))
            self.optimize_interval_var.set(str(get_setting("database.optimize_interval_days", 7)))
            self.vacuum_startup_var.set(get_setting("database.vacuum_on_startup", False))
            self.connection_timeout_var.set(str(get_setting("database.connection_timeout", 30)))
            
            # Interfaz
            self.window_width_var.set(str(get_setting("interface.window_width", 1100)))
            self.window_height_var.set(str(get_setting("interface.window_height", 700)))
            self.remember_position_var.set(get_setting("interface.remember_position", True))
            self.show_tooltips_var.set(get_setting("interface.show_tooltips", True))
            self.auto_refresh_var.set(str(get_setting("interface.auto_refresh_interval", 30)))
            
            # Notificaciones
            self.desktop_notifications_var.set(get_setting("notifications.enable_desktop_notifications", True))
            self.sound_enabled_var.set(get_setting("notifications.sound_enabled", True))
            self.stock_threshold_var.set(str(get_setting("notifications.stock_alert_threshold", 10)))
            self.expiration_days_var.set(str(get_setting("notifications.expiration_alert_days", 30)))
            self.contract_days_var.set(str(get_setting("notifications.contract_expiry_alert_days", 7)))
            
            # Reportes
            self.report_format_var.set(get_setting("reports.default_format", "PDF"))
            self.include_charts_var.set(get_setting("reports.include_charts", True))
            self.auto_open_reports_var.set(get_setting("reports.auto_open_reports", True))
            self.save_reports_var.set(get_setting("reports.save_reports", True))
            
            # Seguridad
            self.session_timeout_var.set(str(get_setting("security.session_timeout_minutes", 30)))
            self.max_login_attempts_var.set(str(get_setting("security.max_login_attempts", 3)))
            self.password_min_length_var.set(str(get_setting("security.password_min_length", 8)))
            self.require_special_chars_var.set(get_setting("security.require_special_chars", True))
            self.backup_encryption_var.set(get_setting("security.backup_encryption", False))
            
            # Rendimiento
            self.cache_enabled_var.set(get_setting("performance.cache_enabled", True))
            self.cache_size_var.set(str(get_setting("performance.cache_size_mb", 100)))
            self.auto_cleanup_cache_var.set(get_setting("performance.auto_cleanup_cache", True))
            self.cleanup_interval_var.set(str(get_setting("performance.cleanup_interval_hours", 24)))
            
            # Actualizar estado de optimización
            self.update_optimization_status()
            
        except Exception as e:
            self.logger.error(f"Error cargando configuraciones: {e}")
            messagebox.showerror("Error", f"Error cargando configuraciones: {e}")
    
    def save_settings(self):
        """Guardar configuraciones"""
        try:
            # Recopilar todas las configuraciones
            settings = {
                "system.language": self.language_var.get(),
                "system.theme": self.theme_var.get(),
                "system.auto_backup": self.auto_backup_var.get(),
                "system.backup_interval_hours": int(self.backup_interval_var.get()),
                "system.enable_logging": self.enable_logging_var.get(),
                "system.log_level": self.log_level_var.get(),
                
                "database.auto_optimize": self.auto_optimize_var.get(),
                "database.optimize_interval_days": int(self.optimize_interval_var.get()),
                "database.vacuum_on_startup": self.vacuum_startup_var.get(),
                "database.connection_timeout": int(self.connection_timeout_var.get()),
                
                "interface.window_width": int(self.window_width_var.get()),
                "interface.window_height": int(self.window_height_var.get()),
                "interface.remember_position": self.remember_position_var.get(),
                "interface.show_tooltips": self.show_tooltips_var.get(),
                "interface.auto_refresh_interval": int(self.auto_refresh_var.get()),
                
                "notifications.enable_desktop_notifications": self.desktop_notifications_var.get(),
                "notifications.sound_enabled": self.sound_enabled_var.get(),
                "notifications.stock_alert_threshold": int(self.stock_threshold_var.get()),
                "notifications.expiration_alert_days": int(self.expiration_days_var.get()),
                "notifications.contract_expiry_alert_days": int(self.contract_days_var.get()),
                
                "reports.default_format": self.report_format_var.get(),
                "reports.include_charts": self.include_charts_var.get(),
                "reports.auto_open_reports": self.auto_open_reports_var.get(),
                "reports.save_reports": self.save_reports_var.get(),
                
                "security.session_timeout_minutes": int(self.session_timeout_var.get()),
                "security.max_login_attempts": int(self.max_login_attempts_var.get()),
                "security.password_min_length": int(self.password_min_length_var.get()),
                "security.require_special_chars": self.require_special_chars_var.get(),
                "security.backup_encryption": self.backup_encryption_var.get(),
                
                "performance.cache_enabled": self.cache_enabled_var.get(),
                "performance.cache_size_mb": int(self.cache_size_var.get()),
                "performance.auto_cleanup_cache": self.auto_cleanup_cache_var.get(),
                "performance.cleanup_interval_hours": int(self.cleanup_interval_var.get())
            }
            
            # Guardar configuraciones
            success = settings_manager.update_multiple(settings)
            
            if success:
                messagebox.showinfo("Éxito", "Configuraciones guardadas correctamente")
                log_user_action("admin", "settings_saved", {"settings_count": len(settings)})
            else:
                messagebox.showerror("Error", "Error guardando configuraciones")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Error de validación: {e}")
        except Exception as e:
            self.logger.error(f"Error guardando configuraciones: {e}")
            messagebox.showerror("Error", f"Error guardando configuraciones: {e}")
    
    def reset_settings(self):
        """Restablecer configuraciones por defecto"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres restablecer todas las configuraciones por defecto?"):
            try:
                success = settings_manager.reset_to_defaults()
                if success:
                    self.load_current_settings()
                    messagebox.showinfo("Éxito", "Configuraciones restablecidas por defecto")
                    log_user_action("admin", "settings_reset", {})
                else:
                    messagebox.showerror("Error", "Error restableciendo configuraciones")
            except Exception as e:
                self.logger.error(f"Error restableciendo configuraciones: {e}")
                messagebox.showerror("Error", f"Error restableciendo configuraciones: {e}")
    
    def export_settings(self):
        """Exportar configuraciones"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exportar Configuraciones"
            )
            
            if file_path:
                success = settings_manager.export_settings(file_path)
                if success:
                    messagebox.showinfo("Éxito", f"Configuraciones exportadas a: {file_path}")
                    log_user_action("admin", "settings_exported", {"file_path": file_path})
                else:
                    messagebox.showerror("Error", "Error exportando configuraciones")
                    
        except Exception as e:
            self.logger.error(f"Error exportando configuraciones: {e}")
            messagebox.showerror("Error", f"Error exportando configuraciones: {e}")
    
    def import_settings(self):
        """Importar configuraciones"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Importar Configuraciones"
            )
            
            if file_path:
                if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres importar configuraciones? Esto sobrescribirá las configuraciones actuales."):
                    success = settings_manager.import_settings(file_path)
                    if success:
                        self.load_current_settings()
                        messagebox.showinfo("Éxito", f"Configuraciones importadas desde: {file_path}")
                        log_user_action("admin", "settings_imported", {"file_path": file_path})
                    else:
                        messagebox.showerror("Error", "Error importando configuraciones")
                        
        except Exception as e:
            self.logger.error(f"Error importando configuraciones: {e}")
            messagebox.showerror("Error", f"Error importando configuraciones: {e}")
    
    def optimize_databases_now(self):
        """Optimizar bases de datos ahora"""
        try:
            if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres optimizar todas las bases de datos ahora? Esto puede tomar varios minutos."):
                self.logger.info("Iniciando optimización manual de bases de datos")
                
                # Mostrar progreso
                progress_window = tk.Toplevel(self.window)
                progress_window.title("Optimizando Bases de Datos")
                progress_window.geometry("400x150")
                progress_window.transient(self.window)
                progress_window.grab_set()
                
                ttk.Label(progress_window, text="Optimizando bases de datos...").pack(pady=20)
                progress = ttk.Progressbar(progress_window, mode='indeterminate')
                progress.pack(pady=10)
                progress.start()
                
                # Ejecutar optimización en hilo separado
                def optimize_thread():
                    try:
                        results = optimize_all_databases()
                        progress_window.destroy()
                        
                        # Mostrar resultados
                        success_count = sum(1 for success, _ in results.values() if success)
                        total_count = len(results)
                        
                        messagebox.showinfo("Optimización Completada", 
                                          f"Optimización completada.\n"
                                          f"Exitosas: {success_count}/{total_count}")
                        
                        # Actualizar estado
                        self.update_optimization_status()
                        
                    except Exception as e:
                        progress_window.destroy()
                        messagebox.showerror("Error", f"Error durante la optimización: {e}")
                
                import threading
                thread = threading.Thread(target=optimize_thread, daemon=True)
                thread.start()
                
        except Exception as e:
            self.logger.error(f"Error iniciando optimización: {e}")
            messagebox.showerror("Error", f"Error iniciando optimización: {e}")
    
    def update_optimization_status(self):
        """Actualizar estado de optimización"""
        try:
            status = get_optimization_status()
            
            status_text = f"""Estado de Optimización de Base de Datos:

📊 Información General:
• Optimización automática: {'Habilitada' if status['auto_optimize_enabled'] else 'Deshabilitada'}
• Intervalo de optimización: {status['optimize_interval_days']} días
• Total de bases de datos: {status['databases_count']}
• Tamaño total: {status['total_size_mb']:.2f} MB
• Fragmentación promedio: {status['average_fragmentation']:.2f}%

📅 Última Optimización:
"""
            
            if status['last_optimization']:
                last_opt = status['last_optimization']
                status_text += f"""• Fecha: {last_opt.get('timestamp', 'N/A')}
• Bases procesadas: {last_opt.get('databases_processed', 0)}
• Exitosas: {last_opt.get('successful', 0)}
• Fallidas: {last_opt.get('failed', 0)}
"""
            else:
                status_text += "• No se ha realizado optimización aún\n"
            
            status_text += "\n📋 Análisis por Base de Datos:\n"
            
            for db_path, analysis in status['databases_analysis'].items():
                if 'error' not in analysis:
                    db_name = Path(db_path).name
                    status_text += f"""• {db_name}:
  - Tamaño: {analysis.get('size_mb', 0):.2f} MB
  - Tablas: {analysis.get('tables_count', 0)}
  - Fragmentación: {analysis.get('fragmentation_percent', 0):.2f}%
  - Integridad: {analysis.get('integrity', 'N/A')}
"""
                else:
                    db_name = Path(db_path).name
                    status_text += f"• {db_name}: Error - {analysis['error']}\n"
            
            self.optimization_status_text.delete(1.0, tk.END)
            self.optimization_status_text.insert(1.0, status_text)
            
        except Exception as e:
            self.logger.error(f"Error actualizando estado de optimización: {e}")
            self.optimization_status_text.delete(1.0, tk.END)
            self.optimization_status_text.insert(1.0, f"Error obteniendo estado: {e}")

def abrir_configuracion_avanzada(parent):
    """Función para abrir la ventana de configuración avanzada"""
    AdvancedSettingsWindow(parent) 