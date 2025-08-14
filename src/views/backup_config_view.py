import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import os

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.backup_manager import BackupManager
from utils.validators import DataValidator
from models.database import get_database_path

class BackupConfigWindow:
    """Ventana de configuración para backup y validación"""
    
    def __init__(self, parent):
        self.parent = parent
        self.backup_manager = BackupManager(get_database_path())
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración de Seguridad y Backup")
        self.window.geometry("800x600")
        self.window.configure(bg='#f8f9fa')
        
        # Configurar ventana
        self.window.resizable(True, True)
        self.window.minsize(700, 500)
        
        # Centrar ventana
        self.center_window()
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar estado actual
        self.load_current_status()
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
    
    def create_interface(self):
        """Crear la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title = tk.Label(main_frame, text="Configuración de Seguridad y Backup", 
                        font=('Segoe UI', 16, 'bold'), bg='#f8f9fa', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Pestaña de Backup
        self.create_backup_tab(notebook)
        
        # Pestaña de Validación
        self.create_validation_tab(notebook)
        
        # Pestaña de Estado
        self.create_status_tab(notebook)
        
        # Botones de acción
        self.create_action_buttons(main_frame)
        
        # Configurar expansión
        main_frame.rowconfigure(1, weight=1)
    
    def create_backup_tab(self, notebook):
        """Crear pestaña de configuración de backup"""
        backup_frame = ttk.Frame(notebook, padding="20")
        notebook.add(backup_frame, text="Backup Automático")
        
        # Configuración de backup automático
        backup_config_frame = ttk.LabelFrame(backup_frame, text="Configuración de Backup Automático", padding="15")
        backup_config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Habilitar backup automático
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_config_frame, text="Habilitar backup automático", 
                       variable=self.auto_backup_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Intervalo de backup
        ttk.Label(backup_config_frame, text="Intervalo de backup (horas):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="24")
        interval_spinbox = ttk.Spinbox(backup_config_frame, from_=1, to=168, width=10, 
                                     textvariable=self.interval_var)
        interval_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Máximo número de backups
        ttk.Label(backup_config_frame, text="Máximo número de backups:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_backups_var = tk.StringVar(value="30")
        max_backups_spinbox = ttk.Spinbox(backup_config_frame, from_=5, to=100, width=10, 
                                        textvariable=self.max_backups_var)
        max_backups_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Directorio de backup
        ttk.Label(backup_config_frame, text="Directorio de backup:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.backup_dir_var = tk.StringVar()
        backup_dir_entry = ttk.Entry(backup_config_frame, textvariable=self.backup_dir_var, width=40)
        backup_dir_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(backup_config_frame, text="Carpeta", width=8, 
                  command=self.select_backup_directory).grid(row=3, column=2, pady=5)
        
        # Acciones de backup manual
        manual_backup_frame = ttk.LabelFrame(backup_frame, text="Backup Manual", padding="15")
        manual_backup_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Botones de backup
        ttk.Button(manual_backup_frame, text="Crear Backup Ahora", 
                  command=self.create_backup_now).grid(row=0, column=0, padx=(0, 10), pady=5)
        ttk.Button(manual_backup_frame, text="Backup Completo", 
                  command=self.create_compressed_backup).grid(row=0, column=1, padx=(0, 10), pady=5)
        ttk.Button(manual_backup_frame, text="Restaurar Backup", 
                  command=self.restore_backup).grid(row=0, column=2, pady=5)
        
        # Lista de backups
        backups_frame = ttk.LabelFrame(backup_frame, text="Backups Disponibles", padding="15")
        backups_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Treeview para backups
        columns = ('fecha', 'tamaño', 'estado')
        self.backups_tree = ttk.Treeview(backups_frame, columns=columns, show='headings', height=8)
        
        self.backups_tree.heading('fecha', text='Fecha')
        self.backups_tree.heading('tamaño', text='Tamaño')
        self.backups_tree.heading('estado', text='Estado')
        
        self.backups_tree.column('fecha', width=150)
        self.backups_tree.column('tamaño', width=100)
        self.backups_tree.column('estado', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(backups_frame, orient=tk.VERTICAL, command=self.backups_tree.yview)
        self.backups_tree.configure(yscrollcommand=scrollbar.set)
        
        self.backups_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar expansión
        backup_frame.columnconfigure(0, weight=1)
        backup_frame.rowconfigure(2, weight=1)
        backups_frame.columnconfigure(0, weight=1)
        backups_frame.rowconfigure(0, weight=1)
    
    def create_validation_tab(self, notebook):
        """Crear pestaña de configuración de validación"""
        validation_frame = ttk.Frame(notebook, padding="20")
        notebook.add(validation_frame, text="Validación de Datos")
        
        # Configuración de validación
        validation_config_frame = ttk.LabelFrame(validation_frame, text="Configuración de Validación", padding="15")
        validation_config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Habilitar validación estricta
        self.strict_validation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Habilitar validación estricta de datos", 
                       variable=self.strict_validation_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Validación de cédula
        self.validate_cedula_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Validar algoritmo de cédula colombiana", 
                       variable=self.validate_cedula_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Validación de email
        self.validate_email_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Validar formato de email", 
                       variable=self.validate_email_var).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Validación de teléfono
        self.validate_phone_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Validar formato de teléfono colombiano", 
                       variable=self.validate_phone_var).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Prevención de duplicados
        self.prevent_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Prevenir empleados duplicados por cédula", 
                       variable=self.prevent_duplicates_var).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Validación de archivos
        self.validate_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(validation_config_frame, text="Validar tipos de archivo subidos", 
                       variable=self.validate_files_var).grid(row=5, column=0, sticky=tk.W, pady=5)
        
        # Pruebas de validación
        test_frame = ttk.LabelFrame(validation_frame, text="Pruebas de Validación", padding="15")
        test_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Campos de prueba
        ttk.Label(test_frame, text="Cédula de prueba:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.test_cedula_var = tk.StringVar()
        ttk.Entry(test_frame, textvariable=self.test_cedula_var, width=20).grid(row=0, column=1, padx=(10, 5), pady=5)
        ttk.Button(test_frame, text="Validar", command=self.test_cedula_validation).grid(row=0, column=2, pady=5)
        
        ttk.Label(test_frame, text="Email de prueba:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.test_email_var = tk.StringVar()
        ttk.Entry(test_frame, textvariable=self.test_email_var, width=30).grid(row=1, column=1, padx=(10, 5), pady=5)
        ttk.Button(test_frame, text="Validar", command=self.test_email_validation).grid(row=1, column=2, pady=5)
        
        ttk.Label(test_frame, text="Teléfono de prueba:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.test_phone_var = tk.StringVar()
        ttk.Entry(test_frame, textvariable=self.test_phone_var, width=20).grid(row=2, column=1, padx=(10, 5), pady=5)
        ttk.Button(test_frame, text="Validar", command=self.test_phone_validation).grid(row=2, column=2, pady=5)
        
        # Resultado de validación
        self.validation_result_var = tk.StringVar(value="Ingrese datos para probar la validación")
        ttk.Label(test_frame, textvariable=self.validation_result_var, 
                 font=('Segoe UI', 9)).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def create_status_tab(self, notebook):
        """Crear pestaña de estado del sistema"""
        status_frame = ttk.Frame(notebook, padding="20")
        notebook.add(status_frame, text="Estado del Sistema")
        
        # Estado del backup
        backup_status_frame = ttk.LabelFrame(status_frame, text="Estado del Backup", padding="15")
        backup_status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Variables de estado
        self.last_backup_var = tk.StringVar()
        self.backup_count_var = tk.StringVar()
        self.auto_backup_status_var = tk.StringVar()
        self.total_backups_var = tk.StringVar()
        
        # Campos de estado
        ttk.Label(backup_status_frame, text="Último backup:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(backup_status_frame, textvariable=self.last_backup_var, font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(backup_status_frame, text="Total de backups:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(backup_status_frame, textvariable=self.total_backups_var, font=('Segoe UI', 9, 'bold')).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(backup_status_frame, text="Backup automático:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(backup_status_frame, textvariable=self.auto_backup_status_var, font=('Segoe UI', 9, 'bold')).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(backup_status_frame, text="Contador de backups:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(backup_status_frame, textvariable=self.backup_count_var, font=('Segoe UI', 9, 'bold')).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Información del sistema
        system_info_frame = ttk.LabelFrame(status_frame, text="Información del Sistema", padding="15")
        system_info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Variables de información del sistema
        self.db_path_var = tk.StringVar()
        self.db_size_var = tk.StringVar()
        self.backup_dir_var_status = tk.StringVar()
        
        ttk.Label(system_info_frame, text="Ruta de BD:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(system_info_frame, textvariable=self.db_path_var, font=('Segoe UI', 8)).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(system_info_frame, text="Tamaño de BD:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(system_info_frame, textvariable=self.db_size_var, font=('Segoe UI', 8)).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(system_info_frame, text="Directorio backup:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(system_info_frame, textvariable=self.backup_dir_var_status, font=('Segoe UI', 8)).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Botón de actualizar estado
        ttk.Button(status_frame, text="Actualizar Estado", 
                  command=self.load_current_status).grid(row=2, column=0, pady=20)
    
    def create_action_buttons(self, main_frame):
        """Crear botones de acción principales"""
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Guardar Configuración", 
                  command=self.save_configuration).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Iniciar Backup Automático", 
                  command=self.start_auto_backup).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Detener Backup Automático", 
                  command=self.stop_auto_backup).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Cerrar", 
                  command=self.window.destroy).grid(row=0, column=3)
    
    def load_current_status(self):
        """Cargar estado actual del sistema"""
        try:
            # Obtener estado del backup
            status = self.backup_manager.get_backup_status()
            
            # Actualizar variables de estado
            if status['last_backup']:
                last_backup = datetime.fromisoformat(status['last_backup'])
                self.last_backup_var.set(last_backup.strftime("%d/%m/%Y %H:%M:%S"))
            else:
                self.last_backup_var.set("Nunca")
            
            self.total_backups_var.set(str(status['total_backups']))
            self.backup_count_var.set(str(status['backup_count']))
            
            if status['is_running']:
                self.auto_backup_status_var.set("Ejecutándose")
            else:
                self.auto_backup_status_var.set("Detenido")
            
            # Información del sistema
            self.db_path_var.set(status['db_path'])
            self.backup_dir_var_status.set(status['backup_dir'])
            
            # Tamaño de la base de datos
            if os.path.exists(status['db_path']):
                size = os.path.getsize(status['db_path'])
                self.db_size_var.set(f"{size / 1024:.1f} KB")
            else:
                self.db_size_var.set("No existe")
            
            # Cargar lista de backups
            self.load_backups_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando estado: {e}")
    
    def load_backups_list(self):
        """Cargar lista de backups en el treeview"""
        try:
            # Limpiar lista actual
            for item in self.backups_tree.get_children():
                self.backups_tree.delete(item)
            
            # Obtener backups
            backups = self.backup_manager.list_backups()
            
            # Agregar a la lista
            for backup in backups:
                fecha = datetime.fromisoformat(backup['fecha_creacion']).strftime("%d/%m/%Y %H:%M")
                tamaño = f"{backup['tamaño'] / 1024:.1f} KB"
                estado = "Válido" if backup['metadata'] else "Sin metadatos"
                
                self.backups_tree.insert('', 'end', values=(fecha, tamaño, estado))
        
        except Exception as e:
            print(f"Error cargando lista de backups: {e}")
    
    def select_backup_directory(self):
        """Seleccionar directorio de backup"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de backup")
        if directory:
            self.backup_dir_var.set(directory)
    
    def create_backup_now(self):
        """Crear backup manual"""
        def backup_thread():
            try:
                success, message = self.backup_manager.create_backup()
                if success:
                    messagebox.showinfo("Éxito", f"Backup creado exitosamente:\n{message}")
                else:
                    messagebox.showerror("Error", f"Error creando backup:\n{message}")
                
                # Actualizar estado
                self.load_current_status()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")
        
        # Ejecutar en thread separado para no bloquear la UI
        thread = threading.Thread(target=backup_thread, daemon=True)
        thread.start()
    
    def create_compressed_backup(self):
        """Crear backup comprimido"""
        def backup_thread():
            try:
                success, message = self.backup_manager.create_compressed_backup()
                if success:
                    messagebox.showinfo("Éxito", f"Backup comprimido creado:\n{message}")
                else:
                    messagebox.showerror("Error", f"Error creando backup comprimido:\n{message}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")
        
        thread = threading.Thread(target=backup_thread, daemon=True)
        thread.start()
    
    def restore_backup(self):
        """Restaurar backup"""
        # Obtener backup seleccionado
        selection = self.backups_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un backup para restaurar")
            return
        
        # Obtener nombre del backup
        item = self.backups_tree.item(selection[0])
        fecha = item['values'][0]
        
        # Buscar el backup correspondiente
        backups = self.backup_manager.list_backups()
        backup_to_restore = None
        
        for backup in backups:
            backup_fecha = datetime.fromisoformat(backup['fecha_creacion']).strftime("%d/%m/%Y %H:%M")
            if backup_fecha == fecha:
                backup_to_restore = backup
                break
        
        if not backup_to_restore:
            messagebox.showerror("Error", "No se encontró el backup seleccionado")
            return
        
        # Confirmar restauración
        if not messagebox.askyesno("Confirmar", 
                                 f"¿Está seguro de restaurar el backup del {fecha}?\n"
                                 "Se creará un backup del estado actual antes de restaurar."):
            return
        
        def restore_thread():
            try:
                success, message = self.backup_manager.restore_backup(backup_to_restore['nombre'])
                if success:
                    messagebox.showinfo("Éxito", f"Backup restaurado exitosamente:\n{message}")
                else:
                    messagebox.showerror("Error", f"Error restaurando backup:\n{message}")
                
                # Actualizar estado
                self.load_current_status()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")
        
        thread = threading.Thread(target=restore_thread, daemon=True)
        thread.start()
    
    def start_auto_backup(self):
        """Iniciar backup automático"""
        success, message = self.backup_manager.start_auto_backup()
        if success:
            messagebox.showinfo("Éxito", "Backup automático iniciado")
        else:
            messagebox.showerror("Error", f"Error iniciando backup automático: {message}")
        
        self.load_current_status()
    
    def stop_auto_backup(self):
        """Detener backup automático"""
        success, message = self.backup_manager.stop_auto_backup()
        if success:
            messagebox.showinfo("Éxito", "Backup automático detenido")
        else:
            messagebox.showerror("Error", f"Error deteniendo backup automático: {message}")
        
        self.load_current_status()
    
    def save_configuration(self):
        """Guardar configuración"""
        try:
            # Actualizar configuración del backup
            self.backup_manager.config['auto_backup_enabled'] = self.auto_backup_var.get()
            self.backup_manager.config['backup_interval_hours'] = int(self.interval_var.get())
            self.backup_manager.config['max_backups'] = int(self.max_backups_var.get())
            
            # Guardar configuración
            self.backup_manager._save_config()
            
            messagebox.showinfo("Éxito", "Configuración guardada exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")
    
    def test_cedula_validation(self):
        """Probar validación de cédula"""
        cedula = self.test_cedula_var.get().strip()
        if not cedula:
            self.validation_result_var.set("Ingrese una cédula para probar")
            return
        
        es_valida, mensaje = DataValidator.validar_cedula_colombiana(cedula)
        if es_valida:
            self.validation_result_var.set(f"Cédula válida: {cedula}")
        else:
            self.validation_result_var.set(f"Cédula inválida: {mensaje}")
    
    def test_email_validation(self):
        """Probar validación de email"""
        email = self.test_email_var.get().strip()
        if not email:
            self.validation_result_var.set("Ingrese un email para probar")
            return
        
        es_valido, mensaje = DataValidator.validar_email(email)
        if es_valido:
            self.validation_result_var.set(f"Email válido: {email}")
        else:
            self.validation_result_var.set(f"Email inválido: {mensaje}")
    
    def test_phone_validation(self):
        """Probar validación de teléfono"""
        telefono = self.test_phone_var.get().strip()
        if not telefono:
            self.validation_result_var.set("Ingrese un teléfono para probar")
            return
        
        es_valido, mensaje = DataValidator.validar_telefono(telefono)
        if es_valido:
            self.validation_result_var.set(f"Teléfono válido: {telefono}")
        else:
            self.validation_result_var.set(f"Teléfono inválido: {mensaje}")

def abrir_configuracion_seguridad(parent):
    """Función para abrir la ventana de configuración de seguridad"""
    BackupConfigWindow(parent) 