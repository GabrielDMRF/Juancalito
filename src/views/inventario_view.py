#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo Principal de Inventarios - inventario_view.py
Este archivo es el punto de entrada principal para todos los sistemas de inventario
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Agregar path para importar otros módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

class ModernInventarioWindow:
    """Ventana principal moderna de inventarios - Punto de entrada único"""
    
    def __init__(self, parent, main_window=None):
        self.parent = parent
        self.main_window = main_window
        
        # Crear ventana principal
        self.window = tk.Toplevel(parent)
        self.window.title("📦 Centro de Inventarios - Sistema Integrado")
        self.window.geometry("1300x800")
        self.window.configure(bg='#f8f9fa')
        
        # Configurar ventana
        self.window.resizable(True, True)
        self.window.minsize(1200, 700)
        
        # Centrar ventana
        self.center_window()
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Configurar estilos
        self.configure_styles()
        
        # Variables del sistema
        self.active_systems = self.check_available_systems()
        
        # Crear interfaz
        self.create_main_interface()
        
        # Actualizar estadísticas iniciales
        self.update_all_stats()
    
    def configure_styles(self):
        """Configurar estilos del sistema"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del tema
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'success': '#27ae60',
            'info': '#3498db', 
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'quimicos': '#27ae60',
            'almacen': '#3498db',
            'poscosecha': '#16a085'
        }
    
    def center_window(self):
        """Centrar ventana en pantalla"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1300x800+{x}+{y}")
    
    def check_available_systems(self):
        """Verificar qué sistemas de inventario están disponibles"""
        systems = {
            'quimicos': False,
            'almacen': False, 
            'poscosecha': False
        }
        
        # Verificar archivos de sistemas
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        system_files = {
            'quimicos': 'inventario_quimicos.py',
            'almacen': 'inventario_almacen.py',
            'poscosecha': 'inventario_poscosecha.py'
        }
        
        for system, filename in system_files.items():
            file_path = os.path.join(base_path, filename)
            if os.path.exists(file_path):
                systems[system] = True
                print(f"✅ Sistema {system} disponible")
            else:
                print(f"❌ Sistema {system} no encontrado: {filename}")
        
        return systems
    
    def create_main_interface(self):
        """Crear interfaz principal"""
        # Header del sistema
        self.create_header()
        
        # Contenedor principal
        main_container = tk.Frame(self.window, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear contenido principal
        self.create_content_area(main_container)
        
        # Footer con información
        self.create_footer()
    
    def create_header(self):
        """Crear header principal"""
        header = tk.Frame(self.window, bg=self.colors['primary'], height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Lado izquierdo - Logo y título
        left_section = tk.Frame(header_content, bg=self.colors['primary'])
        left_section.pack(side=tk.LEFT)
        
        # Logo
        logo_label = tk.Label(left_section, text="📦", font=('Arial', 32), 
                             bg=self.colors['primary'], fg='white')
        logo_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Títulos
        title_container = tk.Frame(left_section, bg=self.colors['primary'])
        title_container.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_container, text="Centro de Inventarios", 
                              font=('Segoe UI', 22, 'bold'), 
                              bg=self.colors['primary'], fg='white')
        title_label.pack(anchor='w')
        
        subtitle = tk.Label(title_container, text="Gestión Integrada de Químicos, Almacén y Poscosecha", 
                           font=('Segoe UI', 12), 
                           bg=self.colors['primary'], fg='#bdc3c7')
        subtitle.pack(anchor='w')
        
        # Lado derecho - Información del sistema
        right_section = tk.Frame(header_content, bg=self.colors['primary'])
        right_section.pack(side=tk.RIGHT)
        
        # Fecha y hora
        datetime_label = tk.Label(right_section, text=datetime.now().strftime("%d/%m/%Y • %H:%M"), 
                                 font=('Segoe UI', 12, 'bold'),
                                 bg=self.colors['primary'], fg='white')
        datetime_label.pack(anchor='e')
        
        # Estadísticas rápidas
        self.quick_stats_label = tk.Label(right_section, text="Cargando...", 
                                         font=('Segoe UI', 10),
                                         bg=self.colors['primary'], fg='#bdc3c7')
        self.quick_stats_label.pack(anchor='e', pady=(5, 0))
        
        # Botones rápidos
        quick_buttons = tk.Frame(right_section, bg=self.colors['primary'])
        quick_buttons.pack(anchor='e', pady=(10, 0))
        
        buttons = [
            ("🔄", self.refresh_all, self.colors['success']),
            ("📊", self.show_dashboard, self.colors['info']),
            ("❌", self.close_window, self.colors['danger'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(quick_buttons, text=text, command=command,
                           bg=color, fg='white', font=('Segoe UI', 10, 'bold'),
                           relief='flat', bd=0, width=3, height=1, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=2)
            self.add_hover_effect(btn, color)
    
    def create_content_area(self, parent):
        """Crear área de contenido principal"""
        content_area = tk.Frame(parent, bg='#f8f9fa')
        content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel de estadísticas generales
        self.create_stats_panel(content_area)
        
        # Panel principal de sistemas
        self.create_systems_panel(content_area)
        
        # Panel de acciones rápidas
        self.create_actions_panel(content_area)
    
    def create_stats_panel(self, parent):
        """Crear panel de estadísticas generales"""
        stats_frame = tk.LabelFrame(parent, text="📊 Resumen General de Inventarios", 
                                   font=('Segoe UI', 14, 'bold'),
                                   bg='#f8f9fa', fg=self.colors['primary'], 
                                   padx=20, pady=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Container para las estadísticas
        stats_container = tk.Frame(stats_frame, bg='#f8f9fa')
        stats_container.pack(fill=tk.X)
        
        # Crear cards de estadísticas
        self.stats_cards = {}
        self.create_summary_cards(stats_container)
    
    def create_summary_cards(self, parent):
        """Crear cards de resumen"""
        # Datos de las cards
        cards_data = [
            ("🧪 QUÍMICOS", "chemicals", self.colors['quimicos'], "Productos químicos agrícolas"),
            ("🏭 ALMACÉN", "warehouse", self.colors['almacen'], "Productos de almacén general"),
            ("🥬 POSCOSECHA", "postharvest", self.colors['poscosecha'], "Productos post-cosecha"),
            ("📊 TOTAL", "total", "#9b59b6", "Resumen general del sistema")
        ]
        
        for i, (title, key, color, description) in enumerate(cards_data):
            # Card principal
            card = tk.Frame(parent, bg='white', relief='solid', bd=1)
            card.grid(row=0, column=i, sticky='ew', padx=8, pady=8)
            
            # Contenido de la card
            card_content = tk.Frame(card, bg='white')
            card_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Título
            title_label = tk.Label(card_content, text=title, 
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='white', fg=color)
            title_label.pack(anchor='w')
            
            # Descripción
            desc_label = tk.Label(card_content, text=description, 
                                 font=('Segoe UI', 8),
                                 bg='white', fg='#7f8c8d')
            desc_label.pack(anchor='w', pady=(2, 8))
            
            # Valor principal
            value_label = tk.Label(card_content, text="0", 
                                  font=('Segoe UI', 16, 'bold'),
                                  bg='white', fg=self.colors['primary'])
            value_label.pack(anchor='w')
            
            # Estado del sistema
            status_label = tk.Label(card_content, text="Verificando...", 
                                   font=('Segoe UI', 8),
                                   bg='white', fg='#95a5a6')
            status_label.pack(anchor='w', pady=(5, 0))
            
            # Guardar referencias
            self.stats_cards[key] = {
                'value': value_label,
                'status': status_label
            }
        
        # Configurar grid
        for i in range(4):
            parent.grid_columnconfigure(i, weight=1)
    
    def create_systems_panel(self, parent):
        """Crear panel principal de sistemas"""
        systems_frame = tk.LabelFrame(parent, text="🗂️ Sistemas de Inventario Disponibles", 
                                     font=('Segoe UI', 14, 'bold'),
                                     bg='#f8f9fa', fg=self.colors['primary'], 
                                     padx=20, pady=15)
        systems_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Container para los sistemas
        systems_container = tk.Frame(systems_frame, bg='#f8f9fa')
        systems_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear cards de sistemas
        self.create_system_cards(systems_container)
    
    def create_system_cards(self, parent):
        """Crear cards para cada sistema de inventario"""
        systems_data = [
            {
                'name': 'Químicos Agrícolas',
                'key': 'quimicos',
                'icon': '🧪',
                'color': self.colors['quimicos'],
                'description': 'Gestión especializada de productos químicos para agricultura.\nControl de seguridad, clasificación por tipos y monitoreo de riesgos.',
                'features': ['Control de seguridad', 'Clasificación por tipos', 'Alertas de vencimiento', 'Niveles de peligrosidad'],
                'open_func': self.open_quimicos_system
            },
            {
                'name': 'Almacén General',
                'key': 'almacen', 
                'icon': '🏭',
                'color': self.colors['almacen'],
                'description': 'Inventario de productos de almacén general.\nControl de ubicaciones, proveedores y stock mínimo.',
                'features': ['Control de ubicaciones', 'Gestión de proveedores', 'Stock mínimo', 'Movimientos detallados'],
                'open_func': self.open_almacen_system
            },
            {
                'name': 'Poscosecha',
                'key': 'poscosecha',
                'icon': '🥬', 
                'color': self.colors['poscosecha'],
                'description': 'Productos para procesamiento post-cosecha.\nEmpaque, tratamientos, etiquetas y herramientas.',
                'features': ['Control de empaque', 'Tratamientos químicos', 'Gestión de etiquetas', 'Herramientas especializadas'],
                'open_func': self.open_poscosecha_system
            }
        ]
        
        for i, system_data in enumerate(systems_data):
            # Card del sistema
            card = tk.Frame(parent, bg='white', relief='solid', bd=1)
            card.grid(row=0, column=i, sticky='nsew', padx=10, pady=5)
            
            # Header de la card
            header = tk.Frame(card, bg=system_data['color'], height=60)
            header.pack(fill=tk.X)
            header.pack_propagate(False)
            
            header_content = tk.Frame(header, bg=system_data['color'])
            header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Icono y título
            icon_label = tk.Label(header_content, text=system_data['icon'], 
                                 font=('Arial', 20),
                                 bg=system_data['color'], fg='white')
            icon_label.pack(side=tk.LEFT)
            
            title_label = tk.Label(header_content, text=system_data['name'], 
                                  font=('Segoe UI', 14, 'bold'),
                                  bg=system_data['color'], fg='white')
            title_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Contenido de la card
            content = tk.Frame(card, bg='white')
            content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Descripción
            desc_label = tk.Label(content, text=system_data['description'], 
                                 font=('Segoe UI', 10),
                                 bg='white', fg='#2c3e50', justify=tk.LEFT)
            desc_label.pack(anchor='w', pady=(0, 10))
            
            # Características
            features_label = tk.Label(content, text="Características:", 
                                     font=('Segoe UI', 9, 'bold'),
                                     bg='white', fg=system_data['color'])
            features_label.pack(anchor='w')
            
            for feature in system_data['features']:
                feature_label = tk.Label(content, text=f"• {feature}", 
                                        font=('Segoe UI', 8),
                                        bg='white', fg='#7f8c8d')
                feature_label.pack(anchor='w', padx=(10, 0))
            
            # Estado del sistema
            is_available = self.active_systems.get(system_data['key'], False)
            status_text = "✅ Disponible" if is_available else "❌ No disponible"
            status_color = self.colors['success'] if is_available else self.colors['danger']
            
            status_label = tk.Label(content, text=status_text, 
                                   font=('Segoe UI', 9, 'bold'),
                                   bg='white', fg=status_color)
            status_label.pack(anchor='w', pady=(10, 10))
            
            # Botón de acceso
            if is_available:
                access_btn = tk.Button(content, text="🚀 Abrir Sistema", 
                                      command=system_data['open_func'],
                                      bg=system_data['color'], fg='white', 
                                      font=('Segoe UI', 11, 'bold'),
                                      relief='flat', bd=0, pady=10, cursor='hand2')
                access_btn.pack(fill=tk.X)
                self.add_hover_effect(access_btn, system_data['color'])
            else:
                unavailable_btn = tk.Button(content, text="⚠️ Sistema No Disponible", 
                                           state='disabled',
                                           bg='#95a5a6', fg='white', 
                                           font=('Segoe UI', 11),
                                           relief='flat', bd=0, pady=10)
                unavailable_btn.pack(fill=tk.X)
        
        # Configurar grid para expansión
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)
        parent.grid_rowconfigure(0, weight=1)
    
    def create_actions_panel(self, parent):
        """Crear panel de acciones rápidas"""
        actions_frame = tk.LabelFrame(parent, text="⚡ Acciones Rápidas", 
                                     font=('Segoe UI', 14, 'bold'),
                                     bg='#f8f9fa', fg=self.colors['primary'], 
                                     padx=20, pady=15)
        actions_frame.pack(fill=tk.X)
        
        # Container para acciones
        actions_container = tk.Frame(actions_frame, bg='#f8f9fa')
        actions_container.pack(fill=tk.X, pady=10)
        
        # Definir acciones disponibles
        actions_data = [
            ("📊 Dashboard Integrado", self.show_dashboard, self.colors['info']),
            ("🔍 Búsqueda Global", self.global_search, "#9b59b6"),
            ("📈 Reportes Generales", self.show_reports, "#e67e22"),
            ("💾 Backup Completo", self.create_full_backup, self.colors['secondary']),
            ("⚙️ Configuración", self.show_settings, "#95a5a6"),
            ("❓ Ayuda", self.show_help, "#f39c12")
        ]
        
        # Crear botones de acciones en grid 2x3
        for i, (text, command, color) in enumerate(actions_data):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(actions_container, text=text, command=command,
                           bg=color, fg='white', font=('Segoe UI', 10, 'bold'),
                           relief='flat', bd=0, height=2, cursor='hand2')
            btn.grid(row=row, column=col, sticky='ew', padx=5, pady=5)
            self.add_hover_effect(btn, color)
        
        # Configurar expansión del grid
        for i in range(3):
            actions_container.grid_columnconfigure(i, weight=1)
    
    def create_footer(self):
        """Crear footer con información del sistema"""
        footer = tk.Frame(self.window, bg=self.colors['secondary'], height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        footer_content = tk.Frame(footer, bg=self.colors['secondary'])
        footer_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # Información del sistema
        system_info = tk.Label(footer_content, text="Centro de Inventarios v1.0 • Sistema Integrado", 
                              bg=self.colors['secondary'], fg='white', font=('Segoe UI', 9))
        system_info.pack(side=tk.LEFT)
        
        # Estado de conexión
        connection_status = tk.Label(footer_content, text="🟢 Sistemas activos", 
                                    bg=self.colors['secondary'], fg='#2ecc71', font=('Segoe UI', 9))
        connection_status.pack(side=tk.LEFT, padx=20)
        
        # Última actualización
        last_update = tk.Label(footer_content, text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}", 
                              bg=self.colors['secondary'], fg='#bdc3c7', font=('Segoe UI', 9))
        last_update.pack(side=tk.RIGHT)
    
    # ================= FUNCIONES DE LÓGICA =================
    
    def update_all_stats(self):
        """Actualizar todas las estadísticas"""
        try:
            # Actualizar estadísticas de cada sistema
            self.update_system_stats()
            
            # Actualizar estadísticas rápidas
            self.update_quick_stats()
            
            print("📊 Estadísticas actualizadas")
            
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def update_system_stats(self):
        """Actualizar estadísticas de cada sistema"""
        import sqlite3
        
        # Configuración de bases de datos
        db_configs = [
            ('chemicals', 'database/inventario_quimicos_avanzado.db', 'productos_quimicos', 'saldo_real'),
            ('warehouse', 'database/inventario_almacen.db', 'productos_almacen', 'saldo'), 
            ('postharvest', 'database/inventario_poscosecha.db', 'productos_poscosecha', 'saldo')
        ]
        
        total_products = 0
        
        for key, db_path, table, saldo_col in db_configs:
            try:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Contar productos
                    if key == 'chemicals':
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE activo = 1")
                    else:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    
                    count = cursor.fetchone()[0]
                    total_products += count
                    
                    # Actualizar UI
                    if key in self.stats_cards:
                        self.stats_cards[key]['value'].config(text=str(count))
                        self.stats_cards[key]['status'].config(text="✅ Conectado", fg=self.colors['success'])
                    
                    conn.close()
                    
                else:
                    # Base de datos no existe
                    if key in self.stats_cards:
                        self.stats_cards[key]['value'].config(text="0")
                        self.stats_cards[key]['status'].config(text="❌ No disponible", fg=self.colors['danger'])
                        
            except Exception as e:
                print(f"Error actualizando {key}: {e}")
                if key in self.stats_cards:
                    self.stats_cards[key]['value'].config(text="Error")
                    self.stats_cards[key]['status'].config(text="⚠️ Error", fg=self.colors['warning'])
        
        # Actualizar total
        if 'total' in self.stats_cards:
            self.stats_cards['total']['value'].config(text=str(total_products))
            self.stats_cards['total']['status'].config(text="📊 Sistema activo", fg=self.colors['info'])
    
    def update_quick_stats(self):
        """Actualizar estadísticas rápidas en header"""
        try:
            # Contar sistemas activos
            active_count = sum(1 for active in self.active_systems.values() if active)
            total_systems = len(self.active_systems)
            
            stats_text = f"Sistemas: {active_count}/{total_systems} activos"
            
            if hasattr(self, 'quick_stats_label'):
                self.quick_stats_label.config(text=stats_text)
                
        except Exception as e:
            print(f"Error actualizando stats rápidas: {e}")
    
    # ================= FUNCIONES DE SISTEMAS =================
    
    def open_quimicos_system(self):
        """Abrir sistema de químicos"""
        try:
            if not self.active_systems.get('quimicos', False):
                messagebox.showerror("Error", "Sistema de químicos no disponible")
                return
            
            # Intentar importar y abrir el sistema de químicos
            from inventario_quimicos import SistemaInventarioQuimicos
            
            # Crear nueva ventana del sistema
            sistema = SistemaInventarioQuimicos()
            sistema.run()
            
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el sistema de químicos:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo sistema de químicos:\n{e}")
    
    def open_almacen_system(self):
        """Abrir sistema de almacén"""
        try:
            if not self.active_systems.get('almacen', False):
                messagebox.showerror("Error", "Sistema de almacén no disponible")
                return
            
            from inventario_almacen import InventarioAlmacenWindow
            InventarioAlmacenWindow(self.window, self)
            
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el sistema de almacén:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo sistema de almacén:\n{e}")
    
    def open_poscosecha_system(self):
        """Abrir sistema de poscosecha"""
        try:
            if not self.active_systems.get('poscosecha', False):
                messagebox.showerror("Error", "Sistema de poscosecha no disponible")
                return
            
            from inventario_poscosecha import InventarioPoscosechaWindow
            InventarioPoscosechaWindow(self.window, self)
            
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudo cargar el sistema de poscosecha:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo sistema de poscosecha:\n{e}")
    
    # ================= FUNCIONES DE ACCIONES =================
    
    def show_dashboard(self):
        """Mostrar dashboard integrado"""
        try:
            # Crear ventana moderna de dashboard integrado
            DashboardIntegradoWindow(self.window, self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo dashboard:\n{e}")
    
    def global_search(self):
        """Búsqueda global en todos los sistemas"""
        GlobalSearchWindow(self.window, self)
    
    def show_reports(self):
        """Mostrar centro de reportes"""
        ReportsWindow(self.window, self)
    
    def create_full_backup(self):
        """Crear backup completo de todos los sistemas"""
        try:
            import shutil
            from datetime import datetime
            
            # Crear directorio de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_completo_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Listar bases de datos a respaldar
            db_files = [
                'database/inventario_quimicos_avanzado.db',
                'database/inventario_almacen.db',
                'database/inventario_poscosecha.db',
                'database/gestion_personal.db'
            ]
            
            backed_up = 0
            for db_file in db_files:
                if os.path.exists(db_file):
                    try:
                        shutil.copy2(db_file, backup_dir)
                        backed_up += 1
                        print(f"✅ Respaldado: {db_file}")
                    except Exception as e:
                        print(f"❌ Error respaldando {db_file}: {e}")
            
            # Mostrar resultado
            messagebox.showinfo("Backup Completo", 
                               f"Backup creado exitosamente\n\n" +
                               f"📁 Directorio: {backup_dir}\n" + 
                               f"📊 Archivos respaldados: {backed_up}\n" +
                               f"🕐 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando backup completo:\n{e}")
    
    def show_settings(self):
        """Mostrar configuraciones del sistema"""
        SettingsWindow(self.window, self)
    
    def show_help(self):
        """Mostrar ayuda del sistema"""
        HelpWindow(self.window, self)
    
    def refresh_all(self):
        """Actualizar todos los datos"""
        try:
            self.update_all_stats()
            messagebox.showinfo("Actualizado", "Todas las estadísticas han sido actualizadas")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando datos:\n{e}")
    
    # ================= FUNCIONES DE UTILIDAD =================
    
    def add_hover_effect(self, button, color):
        """Agregar efecto hover a botón"""
        def on_enter(e):
            button.config(bg=self.darken_color(color))
        def on_leave(e):
            button.config(bg=color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def darken_color(self, color):
        """Oscurecer color para efecto hover"""
        color_map = {
            '#27ae60': '#229954', '#3498db': '#2980b9', '#f39c12': '#e67e22',
            '#e74c3c': '#c0392b', '#8e44ad': '#7d3c98', '#16a085': '#138d75',
            '#2c3e50': '#1a252f', '#34495e': '#2c3e50', '#95a5a6': '#7f8c8d',
            '#9b59b6': '#8e44ad', '#e67e22': '#d35400'
        }
        return color_map.get(color, color)
    
    def close_window(self):
        """Cerrar ventana principal"""
        self.window.destroy()


# ================= VENTANAS AUXILIARES =================

class DashboardIntegradoWindow:
    """Dashboard integrado de todos los sistemas"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Dashboard Integrado")
        self.window.geometry("1200x800")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1200x800+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#3498db', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="📊 Dashboard Integrado de Inventarios",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#3498db', fg='white')
        title_label.pack(expand=True)
        
        # Contenido
        content = tk.Frame(self.window, bg='#f8f9fa')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mensaje temporal
        message_label = tk.Label(content, text="🚧 Dashboard Integrado en Desarrollo\n\nAquí se mostrarán gráficos y estadísticas\ndetalladas de todos los sistemas de inventario", 
                               font=('Segoe UI', 14), bg='#f8f9fa', fg='#7f8c8d',
                               justify=tk.CENTER)
        message_label.pack(expand=True)
        
        # Botón cerrar
        close_btn = tk.Button(content, text="❌ Cerrar", command=self.window.destroy,
                             bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack(pady=20)


class GlobalSearchWindow:
    """Ventana de búsqueda global"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🔍 Búsqueda Global")
        self.window.geometry("800x600")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#9b59b6', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="🔍 Búsqueda Global en Inventarios",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#9b59b6', fg='white')
        title_label.pack(expand=True)
        
        # Contenido
        content = tk.Frame(self.window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campo de búsqueda
        search_frame = tk.Frame(content, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        search_label = tk.Label(search_frame, text="Buscar en todos los inventarios:",
                               font=('Segoe UI', 12, 'bold'),
                               bg='white', fg='#2c3e50')
        search_label.pack(anchor='w', pady=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=('Segoe UI', 12), relief='solid', bd=1)
        search_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Botón buscar
        search_btn = tk.Button(search_frame, text="🔍 Buscar",
                              command=self.perform_search,
                              bg='#9b59b6', fg='white', font=('Segoe UI', 12, 'bold'),
                              relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        search_btn.pack()
        
        # Área de resultados
        results_label = tk.Label(content, text="Resultados de búsqueda:",
                                font=('Segoe UI', 12, 'bold'),
                                bg='white', fg='#2c3e50')
        results_label.pack(anchor='w', pady=(20, 5))
        
        # Lista de resultados
        self.results_listbox = tk.Listbox(content, height=15,
                                         font=('Segoe UI', 10),
                                         bg='#f8f9fa', fg='#2c3e50',
                                         relief='solid', bd=1)
        self.results_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Botón cerrar
        close_btn = tk.Button(content, text="❌ Cerrar", command=self.window.destroy,
                             bg="#95a5a6", fg="white", font=('Segoe UI', 11, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack()
    
    def perform_search(self):
        """Realizar búsqueda global"""
        search_term = self.search_var.get().strip()
        if not search_term:
            messagebox.showwarning("Advertencia", "Ingresa un término de búsqueda")
            return
        
        # Limpiar resultados
        self.results_listbox.delete(0, tk.END)
        self.results_listbox.insert(tk.END, f"Buscando '{search_term}' en todos los sistemas...")
        
        # Simular búsqueda
        self.window.after(1500, lambda: self.show_mock_results(search_term))
    
    def show_mock_results(self, search_term):
        """Mostrar resultados simulados"""
        self.results_listbox.delete(0, tk.END)
        
        # Resultados simulados
        results = [
            f"🧪 QUÍMICOS - Encontrados 2 productos que contienen '{search_term}'",
            f"🏭 ALMACÉN - Encontrado 1 producto que contiene '{search_term}'",
            f"🥬 POSCOSECHA - No se encontraron productos con '{search_term}'",
            "",
            "✅ Búsqueda completada en todos los sistemas"
        ]
        
        for result in results:
            self.results_listbox.insert(tk.END, result)


class ReportsWindow:
    """Ventana de reportes"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("📈 Centro de Reportes")
        self.window.geometry("900x700")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"900x700+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#e67e22', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="📈 Centro de Reportes Integrados",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#e67e22', fg='white')
        title_label.pack(expand=True)
        
        # Contenido
        content = tk.Frame(self.window, bg='#f8f9fa')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Lista de reportes disponibles
        reports_label = tk.Label(content, text="Reportes Disponibles:",
                                font=('Segoe UI', 14, 'bold'),
                                bg='#f8f9fa', fg='#2c3e50')
        reports_label.pack(anchor='w', pady=(0, 15))
        
        # Grid de reportes
        reports_grid = tk.Frame(content, bg='#f8f9fa')
        reports_grid.pack(fill=tk.BOTH, expand=True)
        
        # Definir reportes
        reports_data = [
            ("📊 Reporte General", "Resumen completo de inventarios", self.generate_general),
            ("🧪 Reporte Químicos", "Inventario de productos químicos", self.generate_chemicals),
            ("🏭 Reporte Almacén", "Inventario de almacén general", self.generate_warehouse),
            ("🥬 Reporte Poscosecha", "Inventario de poscosecha", self.generate_postharvest),
            ("⚠️ Productos Críticos", "Stock bajo y productos agotados", self.generate_critical),
            ("💰 Valorización Total", "Valor monetario de inventarios", self.generate_valuation)
        ]
        
        # Crear cards de reportes
        for i, (title, description, command) in enumerate(reports_data):
            row = i // 2
            col = i % 2
            
            # Card del reporte
            card = tk.Frame(reports_grid, bg='white', relief='solid', bd=1)
            card.grid(row=row, column=col, sticky='ew', padx=10, pady=10)
            
            card_content = tk.Frame(card, bg='white')
            card_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Título
            title_label = tk.Label(card_content, text=title,
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='white', fg='#2c3e50')
            title_label.pack(anchor='w')
            
            # Descripción
            desc_label = tk.Label(card_content, text=description,
                                 font=('Segoe UI', 10),
                                 bg='white', fg='#7f8c8d')
            desc_label.pack(anchor='w', pady=(5, 15))
            
            # Botón generar
            generate_btn = tk.Button(card_content, text="📋 Generar Reporte",
                                    command=command,
                                    bg='#e67e22', fg='white', font=('Segoe UI', 10, 'bold'),
                                    relief='flat', bd=0, padx=15, pady=8, cursor='hand2')
            generate_btn.pack(anchor='w')
        
        # Configurar grid
        for i in range(2):
            reports_grid.grid_columnconfigure(i, weight=1)
        
        # Botón cerrar
        close_btn = tk.Button(content, text="❌ Cerrar", command=self.window.destroy,
                             bg="#95a5a6", fg="white", font=('Segoe UI', 11, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack(pady=(20, 0))
    
    # Funciones de generación de reportes (simuladas)
    def generate_general(self):
        messagebox.showinfo("Reporte", "Generando reporte general integrado...")
    
    def generate_chemicals(self):
        messagebox.showinfo("Reporte", "Generando reporte de químicos...")
    
    def generate_warehouse(self):
        messagebox.showinfo("Reporte", "Generando reporte de almacén...")
    
    def generate_postharvest(self):
        messagebox.showinfo("Reporte", "Generando reporte de poscosecha...")
    
    def generate_critical(self):
        messagebox.showinfo("Reporte", "Generando reporte de productos críticos...")
    
    def generate_valuation(self):
        messagebox.showinfo("Reporte", "Generando reporte de valorización...")


class SettingsWindow:
    """Ventana de configuraciones"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configuraciones del Sistema")
        self.window.geometry("600x500")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#95a5a6', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="⚙️ Configuraciones del Sistema",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#95a5a6', fg='white')
        title_label.pack(expand=True)
        
        # Contenido
        content = tk.Frame(self.window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mensaje temporal
        message_label = tk.Label(content, text="🚧 Panel de Configuraciones en Desarrollo\n\nAquí podrás configurar:\n\n• Parámetros de los sistemas\n• Alertas y notificaciones\n• Conexiones de base de datos\n• Configuraciones de reportes\n• Preferencias de usuario", 
                               font=('Segoe UI', 12), bg='white', fg='#7f8c8d',
                               justify=tk.CENTER)
        message_label.pack(expand=True)
        
        # Botón cerrar
        close_btn = tk.Button(content, text="❌ Cerrar", command=self.window.destroy,
                             bg="#95a5a6", fg="white", font=('Segoe UI', 12, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack(pady=20)


class HelpWindow:
    """Ventana de ayuda"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("❓ Ayuda del Sistema")
        self.window.geometry("700x600")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#f39c12', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="❓ Ayuda y Documentación",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#f39c12', fg='white')
        title_label.pack(expand=True)
        
        # Contenido
        content = tk.Frame(self.window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Texto de ayuda
        help_text = """
📦 CENTRO DE INVENTARIOS - GUÍA RÁPIDA

🎯 DESCRIPCIÓN GENERAL:
El Centro de Inventarios es un sistema integrado que permite gestionar tres tipos de inventarios:
• 🧪 Químicos Agrícolas: Productos químicos para agricultura
• 🏭 Almacén General: Productos de almacén y herramientas  
• 🥬 Poscosecha: Productos para procesamiento post-cosecha

⚡ FUNCIONES PRINCIPALES:
• Dashboard integrado con estadísticas en tiempo real
• Búsqueda global en todos los sistemas
• Reportes generales y específicos por sistema
• Backup completo de todas las bases de datos
• Configuraciones centralizadas

🚀 CÓMO USAR:
1. Selecciona el sistema de inventario que necesites
2. Usa las acciones rápidas para tareas comunes
3. Consulta el dashboard para ver estadísticas generales
4. Genera reportes desde el centro de reportes

🔧 SISTEMAS DISPONIBLES:
• Químicos: Control de seguridad y clasificación
• Almacén: Gestión de ubicaciones y proveedores
• Poscosecha: Control de empaque y tratamientos

📊 CARACTERÍSTICAS:
• Interfaz moderna e intuitiva
• Estadísticas en tiempo real
• Alertas automáticas de stock bajo
• Búsqueda global unificada
• Reportes exportables

❓ SOPORTE:
Para más información consulta la documentación técnica o contacta al administrador del sistema.
        """
        
        # Área de texto con scroll
        text_frame = tk.Frame(content, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        help_textbox = tk.Text(text_frame, wrap=tk.WORD, bg='#f8f9fa', 
                              fg='#2c3e50', font=('Segoe UI', 10),
                              relief='solid', bd=1)
        help_textbox.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=help_textbox.yview)
        help_textbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insertar texto
        help_textbox.insert('1.0', help_text)
        help_textbox.config(state='disabled')
        
        # Botón cerrar
        close_btn = tk.Button(content, text="❌ Cerrar", command=self.window.destroy,
                             bg="#95a5a6", fg="white", font=('Segoe UI', 12, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack()


# ================= FUNCIÓN PRINCIPAL =================

if __name__ == "__main__":
    # Para pruebas independientes
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    app = ModernInventarioWindow(root)
    root.mainloop()