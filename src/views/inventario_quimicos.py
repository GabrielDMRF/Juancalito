#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Inventario de Químicos - Versión Mejorada y Completa
Funcionalidades añadidas:
- Mejor manejo de errores
- Funciones de backup y restauración
- Gráficos de estadísticas
- Sistema de notificaciones
- Exportación a múltiples formatos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, date, timedelta
import sqlite3
import csv
import json
from pathlib import Path
import threading
import time

# Intentar importar librerías opcionales
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class SistemaInventarioQuimicos:
    """Sistema principal mejorado"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧪 Sistema Avanzado de Inventario - QUÍMICOS AGRÍCOLAS")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Variables del sistema
        self.conn = None
        self.notification_queue = []
        self.auto_backup_enabled = True
        
        # Configurar sistema
        self.setup_system()
        self.setup_database()
        self.configurar_estilos()
        
        # Crear interfaz principal
        self.create_main_interface()
        
        # Inicializar datos
        self.initialize_data()
        
        # Configurar notificaciones automáticas
        self.setup_notifications()
        
        # Centrar ventana
        self.center_window()
    
    def setup_system(self):
        """Configurar sistema y directorios"""
        try:
            # Crear directorios necesarios
            self.base_dir = Path("inventario_quimicos_sistema")
            self.base_dir.mkdir(exist_ok=True)
            
            self.db_dir = self.base_dir / "database"
            self.backup_dir = self.base_dir / "backups"
            self.reports_dir = self.base_dir / "reportes"
            self.logs_dir = self.base_dir / "logs"
            
            for directory in [self.db_dir, self.backup_dir, self.reports_dir, self.logs_dir]:
                directory.mkdir(exist_ok=True)
            
            # Configurar logging básico
            self.log_file = self.logs_dir / f"sistema_{datetime.now().strftime('%Y%m%d')}.log"
            
            print(f"✅ Sistema configurado en: {self.base_dir}")
            
        except Exception as e:
            print(f"❌ Error configurando sistema: {e}")
            messagebox.showerror("Error", f"Error configurando sistema: {e}")
    
    def setup_database(self):
        """Configurar base de datos mejorada"""
        try:
            db_path = self.db_dir / 'inventario_quimicos_avanzado.db'
            self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Crear tablas mejoradas
            self.crear_tablas_avanzadas()
            
            print("✅ Base de datos configurada")
            
        except Exception as e:
            print(f"❌ Error en base de datos: {e}")
            messagebox.showerror("Error", f"Error configurando base de datos: {e}")
    
    def crear_tablas_avanzadas(self):
        """Crear tablas con funcionalidades avanzadas"""
        cursor = self.conn.cursor()
        
        # Tabla principal de productos químicos mejorada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos_quimicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                clase TEXT NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                saldo_real INTEGER DEFAULT 0,
                unidad TEXT NOT NULL,
                valor_unitario REAL NOT NULL,
                stock_minimo INTEGER DEFAULT 0,
                stock_maximo INTEGER DEFAULT 1000,
                ubicacion TEXT,
                proveedor TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                nivel_peligrosidad TEXT DEFAULT 'MEDIO',
                ingrediente_activo TEXT,
                concentracion TEXT,
                numero_registro TEXT,
                fecha_vencimiento DATE,
                lote TEXT,
                activo BOOLEAN DEFAULT 1,
                notas TEXT
            )
        ''')
        
        # Tabla de movimientos mejorada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_quimicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                tipo TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                cantidad_anterior INTEGER,
                cantidad_nueva INTEGER,
                fecha DATE NOT NULL,
                hora TIME DEFAULT CURRENT_TIME,
                factura TEXT,
                orden_compra TEXT,
                proveedor TEXT,
                destino TEXT,
                area_aplicacion TEXT,
                cultivo TEXT,
                valor_unitario REAL,
                valor_total REAL,
                observaciones TEXT,
                responsable TEXT,
                autorizado_por TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos_quimicos (id)
            )
        ''')
        
        # Tabla de alertas del sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                nivel TEXT DEFAULT 'INFO',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                leida BOOLEAN DEFAULT 0,
                producto_id INTEGER,
                datos_json TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos_quimicos (id)
            )
        ''')
        
        # Tabla de configuraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuraciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT UNIQUE NOT NULL,
                valor TEXT,
                descripcion TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de backup log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archivo TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tamaño INTEGER,
                tipo TEXT DEFAULT 'AUTO',
                estado TEXT DEFAULT 'EXITOSO'
            )
        ''')
        
        # Triggers para auditoría
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS actualizar_fecha_producto
            AFTER UPDATE ON productos_quimicos
            BEGIN
                UPDATE productos_quimicos 
                SET fecha_actualizacion = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END;
        ''')
        
        self.conn.commit()
        self.insertar_configuraciones_default()
    
    def insertar_configuraciones_default(self):
        """Insertar configuraciones por defecto"""
        cursor = self.conn.cursor()
        
        configs_default = [
            ('auto_backup_intervalo', '24', 'Intervalo de backup automático en horas'),
            ('stock_alerta_dias', '7', 'Días de anticipación para alertas de stock'),
            ('vencimiento_alerta_dias', '30', 'Días de anticipación para alertas de vencimiento'),
            ('empresa_nombre', 'Empresa Agrícola', 'Nombre de la empresa'),
            ('responsable_default', 'Administrador', 'Responsable por defecto'),
            ('moneda', 'COP', 'Moneda del sistema'),
            ('backup_auto_enabled', '1', 'Backup automático habilitado')
        ]
        
        for clave, valor, desc in configs_default:
            cursor.execute('''
                INSERT OR IGNORE INTO configuraciones (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', (clave, valor, desc))
        
        self.conn.commit()
    
    def configurar_estilos(self):
        """Configurar estilos mejorados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del tema armónicos
        self.colores = {
            'primary': '#27ae60',      # Verde esmeralda principal
            'secondary': '#2ecc71',     # Verde claro
            'success': '#27ae60',       # Verde esmeralda
            'warning': '#e67e22',       # Naranja suave
            'danger': '#e74c3c',        # Rojo coral
            'info': '#3498db',          # Azul cielo
            'dark': '#2c3e50',          # Azul oscuro
            'light': '#ecf0f1',         # Gris claro
            'background': '#f8f9fa'     # Gris muy claro
        }
        
        # Estilos específicos
        style.configure('Quimicos.Treeview',
                       background='#ffffff',
                       foreground=self.colores['dark'],
                       fieldbackground='#ffffff',
                       font=('Segoe UI', 9),
                       rowheight=28)
        
        style.configure('Quimicos.Treeview.Heading',
                       background=self.colores['primary'],
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'),
                       relief='flat')
        
        # Estilos para notebooks
        style.configure('TNotebook.Tab',
                       background=self.colores['light'],
                       foreground=self.colores['dark'],
                       padding=[12, 8])
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colores['primary'])],
                 foreground=[('selected', 'white')])
    
    def create_main_interface(self):
        """Crear interfaz principal mejorada"""
        # Header principal
        self.create_header()
        
        # Contenedor principal con notebook
        self.main_container = tk.Frame(self.root, bg=self.colores['background'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Pestañas principales
        self.create_inventory_tab()
        self.create_movements_tab()
        self.create_reports_tab()
        self.create_alerts_tab()
        self.create_settings_tab()
        
        # Panel de estado
        self.create_status_panel()
    
    def create_header(self):
        """Crear header principal mejorado"""
        header = tk.Frame(self.root, bg=self.colores['primary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colores['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Lado izquierdo - Logo y título
        left_frame = tk.Frame(header_content, bg=self.colores['primary'])
        left_frame.pack(side=tk.LEFT)
        
        # Logo
        logo_label = tk.Label(left_frame, text="🧪", font=('Arial', 28), 
                             bg=self.colores['primary'], fg='white')
        logo_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Títulos
        title_container = tk.Frame(left_frame, bg=self.colores['primary'])
        title_container.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_container, text="Sistema Avanzado de Inventario", 
                              font=('Segoe UI', 20, 'bold'), 
                              bg=self.colores['primary'], fg='white')
        title_label.pack(anchor='w')
        
        subtitle = tk.Label(title_container, text="Gestión Profesional de Químicos Agrícolas", 
                           font=('Segoe UI', 11), 
                           bg=self.colores['primary'], fg=self.colores['light'])
        subtitle.pack(anchor='w')
        
        # Lado derecho - Información del sistema
        right_frame = tk.Frame(header_content, bg=self.colores['primary'])
        right_frame.pack(side=tk.RIGHT)
        
        # Fecha y hora actual (reloj en tiempo real)
        self.datetime_label = tk.Label(right_frame, text=datetime.now().strftime("%d/%m/%Y - %H:%M"), 
                                      font=('Segoe UI', 12, 'bold'),
                                      bg=self.colores['primary'], fg='white')
        self.datetime_label.pack(anchor='e')
        
        # Iniciar actualización del reloj
        self.update_clock_quimicos()
        
        # Estadísticas rápidas
        self.quick_stats_label = tk.Label(right_frame, text="Cargando estadísticas...", 
                                         font=('Segoe UI', 10),
                                         bg=self.colores['primary'], fg=self.colores['light'])
        self.quick_stats_label.pack(anchor='e')
        
        # Actualizar cada minuto
        self.update_header_info()
    
    def create_inventory_tab(self):
        """Crear pestaña de inventario mejorada"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="📦 Inventario")
        
        # Crear layout principal (sidebar + contenido)
        main_layout = tk.Frame(inventory_frame, bg=self.colores['background'])
        main_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar izquierdo
        self.create_inventory_sidebar(main_layout)
        
        # Área de contenido principal
        self.create_inventory_content(main_layout)
    
    def create_inventory_sidebar(self, parent):
        """Crear sidebar mejorado para inventario"""
        sidebar = tk.Frame(parent, bg='white', width=320, relief='solid', bd=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Título del sidebar
        sidebar_title = tk.Label(sidebar, text="🎛️ Panel de Control", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg='white', fg=self.colores['dark'])
        sidebar_title.pack(anchor='w', padx=20, pady=(20, 15))
        
        # Estadísticas mejoradas
        self.create_enhanced_stats(sidebar)
        
        # Filtros avanzados
        self.create_advanced_filters(sidebar)
        
        # Acciones rápidas
        self.create_quick_actions(sidebar)
    
    def create_enhanced_stats(self, parent):
        """Crear estadísticas mejoradas"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        stats_title = tk.Label(stats_frame, text="📊 Estadísticas en Tiempo Real", 
                              font=('Segoe UI', 12, 'bold'),
                              bg='white', fg=self.colores['dark'])
        stats_title.pack(anchor='w', pady=(0, 10))
        
        # Container para cards de estadísticas
        self.stats_container = tk.Frame(stats_frame, bg='white')
        self.stats_container.pack(fill=tk.X)
        
        # Actualizar estadísticas
        self.update_statistics()
    
    def create_advanced_filters(self, parent):
        """Crear filtros avanzados"""
        filters_frame = tk.Frame(parent, bg='white')
        filters_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        filters_title = tk.Label(filters_frame, text="🔍 Filtros Avanzados", 
                                font=('Segoe UI', 12, 'bold'),
                                bg='white', fg=self.colores['dark'])
        filters_title.pack(anchor='w', pady=(0, 10))
        
        # Búsqueda inteligente
        search_frame = tk.Frame(filters_frame, bg='white')
        search_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(search_frame, text="Búsqueda inteligente:", 
                font=('Segoe UI', 9), bg='white', fg='#7f8c8d').pack(anchor='w')
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_filter_change)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=('Segoe UI', 10), relief='solid', bd=1)
        search_entry.pack(fill=tk.X, pady=(3, 0))
        
        # Filtros específicos
        filter_configs = [
            ("Clase química:", "filter_clase", ["Todas", "ACARICIDA", "FUNGICIDA", "INSECTICIDA", "HERBICIDA", "FERTILIZANTE", "REGULADOR"]),
            ("Nivel de riesgo:", "filter_riesgo", ["Todos", "ALTO", "MEDIO", "BAJO"]),
            ("Estado de stock:", "filter_stock", ["Todos", "Normal", "Bajo", "Crítico", "Agotado"]),
            ("Proveedor:", "filter_proveedor", ["Todos"]),
            ("Vencimiento:", "filter_vencimiento", ["Todos", "Próximo a vencer", "Vencidos", "Sin fecha"])
        ]
        
        self.filter_vars = {}
        for label_text, var_name, values in filter_configs:
            filter_frame = tk.Frame(filters_frame, bg='white')
            filter_frame.pack(fill=tk.X, pady=3)
            
            tk.Label(filter_frame, text=label_text, 
                    font=('Segoe UI', 9), bg='white', fg='#7f8c8d').pack(anchor='w')
            
            var = tk.StringVar(value=values[0])
            var.trace('w', self.on_filter_change)
            self.filter_vars[var_name] = var
            
            combo = ttk.Combobox(filter_frame, textvariable=var,
                                values=values, state="readonly", 
                                font=('Segoe UI', 9))
            combo.pack(fill=tk.X, pady=(3, 0))
        
        # Botón limpiar filtros
        clear_btn = tk.Button(filters_frame, text="🗑️ Limpiar Filtros", 
                             command=self.clear_filters,
                             bg='#95a5a6', fg='white', font=('Segoe UI', 9),
                             relief='flat', bd=0, pady=8, cursor='hand2')
        clear_btn.pack(fill=tk.X, pady=(10, 0))
    
    def create_quick_actions(self, parent):
        """Crear acciones rápidas mejoradas"""
        actions_frame = tk.Frame(parent, bg='white')
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        actions_title = tk.Label(actions_frame, text="⚡ Acciones Rápidas", 
                                font=('Segoe UI', 12, 'bold'),
                                bg='white', fg=self.colores['dark'])
        actions_title.pack(anchor='w', pady=(0, 15))
        
        # Botones de acción con colores armónicos
        actions = [
            ("➕ Nuevo Químico", self.nuevo_producto, '#27ae60'),           # Verde esmeralda
            ("📥 Entrada de Stock", lambda: self.movimiento_entrada(), '#3498db'),  # Azul cielo
            ("📤 Salida de Stock", lambda: self.movimiento_salida(), '#e67e22'),    # Naranja suave
            ("📋 Historial Movimientos", lambda: self.ver_historial_movimientos(), '#8e44ad'),  # Púrpura
            ("⚠️ Ver Alertas", self.show_alerts_summary, '#e74c3c'),        # Rojo coral
            ("📊 Dashboard", self.show_dashboard, '#16a085'),              # Verde azulado
            ("🔄 Actualizar Todo", self.refresh_all_data, '#7f8c8d'),       # Gris azulado
            ("💾 Backup Manual", self.manual_backup, '#2c3e50'),           # Azul oscuro
            ("📋 Exportar Datos", self.export_data_dialog, '#34495e')      # Azul grisáceo
        ]
        
        for text, command, color in actions:
            btn = tk.Button(actions_frame, text=text, command=command,
                           bg=color, fg='white', font=('Segoe UI', 10),
                           relief='flat', bd=0, pady=10, cursor='hand2')
            btn.pack(fill=tk.X, pady=2)
            self.add_hover_effect(btn, color)
    
    def create_inventory_content(self, parent):
        """Crear área de contenido principal"""
        content_area = tk.Frame(parent, bg='white', relief='solid', bd=1)
        content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header del contenido
        content_header = tk.Frame(content_area, bg='white', height=60)
        content_header.pack(fill=tk.X)
        content_header.pack_propagate(False)
        
        header_content = tk.Frame(content_header, bg='white')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Título y contador
        title_label = tk.Label(header_content, text="🧪 Inventario de Productos Químicos", 
                              font=('Segoe UI', 16, 'bold'),
                              bg='white', fg=self.colores['dark'])
        title_label.pack(side=tk.LEFT)
        
        self.inventory_count_label = tk.Label(header_content, text="", 
                                            font=('Segoe UI', 11),
                                            bg='white', fg='#7f8c8d')
        self.inventory_count_label.pack(side=tk.RIGHT)
        
        # Tabla mejorada
        self.create_enhanced_table(content_area)
    
    def create_enhanced_table(self, parent):
        """Crear tabla mejorada con más funcionalidades"""
        table_container = tk.Frame(parent, bg='white')
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Definir columnas mejoradas
        columns = ('Código', 'Clase', 'Producto', 'Stock', 'Unidad', 'Valor/U', 
                  'Stock Mín.', 'Riesgo', 'Proveedor', 'Vence', 'Estado')
        
        self.inventory_tree = ttk.Treeview(table_container, columns=columns, 
                                          show='headings', height=20, 
                                          style='Quimicos.Treeview')
        
        # Configurar columnas con anchos optimizados
        column_config = {
            'Código': {'width': 80, 'anchor': 'center'},
            'Clase': {'width': 100, 'anchor': 'center'},
            'Producto': {'width': 220, 'anchor': 'w'},
            'Stock': {'width': 70, 'anchor': 'center'},
            'Unidad': {'width': 60, 'anchor': 'center'},
            'Valor/U': {'width': 80, 'anchor': 'e'},
            'Stock Mín.': {'width': 80, 'anchor': 'center'},
            'Riesgo': {'width': 80, 'anchor': 'center'},
            'Proveedor': {'width': 120, 'anchor': 'w'},
            'Vence': {'width': 80, 'anchor': 'center'},
            'Estado': {'width': 100, 'anchor': 'center'}
        }
        
        for col, config in column_config.items():
            self.inventory_tree.heading(col, text=col, 
                                      command=lambda c=col: self.sort_column(c))
            self.inventory_tree.column(col, width=config['width'], 
                                     anchor=config['anchor'])
        
        # Scrollbars mejoradas
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, 
                                   command=self.inventory_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, 
                                   command=self.inventory_tree.xview)
        
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set, 
                                     xscrollcommand=h_scrollbar.set)
        
        # Grid layout mejorado
        self.inventory_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Eventos mejorados
        self.inventory_tree.bind('<Double-1>', self.on_item_double_click)
        self.inventory_tree.bind('<Button-3>', self.show_context_menu)
        self.inventory_tree.bind('<Return>', self.on_item_double_click)
        
        # Cargar datos iniciales
        self.load_inventory_data()
    
    def create_movements_tab(self):
        """Crear pestaña de movimientos"""
        movements_frame = ttk.Frame(self.notebook)
        self.notebook.add(movements_frame, text="📊 Movimientos")
        
        # Crear contenido de movimientos
        tk.Label(movements_frame, text="🚧 Pestaña de Movimientos en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
    
    def create_reports_tab(self):
        """Crear pestaña de reportes"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📈 Reportes")
        
        # Crear contenido de reportes
        tk.Label(reports_frame, text="🚧 Pestaña de Reportes en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
    
    def create_alerts_tab(self):
        """Crear pestaña de alertas"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="⚠️ Alertas")
        
        # Crear contenido de alertas
        tk.Label(alerts_frame, text="🚧 Sistema de Alertas en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
    
    def create_settings_tab(self):
        """Crear pestaña de configuraciones"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Configuración")
        
        # Crear contenido de configuraciones
        tk.Label(settings_frame, text="🚧 Configuraciones en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
    
    def create_status_panel(self):
        """Crear panel de estado en la parte inferior"""
        status_panel = tk.Frame(self.root, bg=self.colores['dark'], height=30)
        status_panel.pack(fill=tk.X, side=tk.BOTTOM)
        status_panel.pack_propagate(False)
        
        # Información de estado
        self.status_label = tk.Label(status_panel, text="Sistema iniciado correctamente", 
                                    bg=self.colores['dark'], fg='white',
                                    font=('Segoe UI', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=6)
        
        # Información de conexión BD
        self.db_status_label = tk.Label(status_panel, text="🔗 BD: Conectada", 
                                       bg=self.colores['dark'], fg='#2ecc71',
                                       font=('Segoe UI', 9))
        self.db_status_label.pack(side=tk.RIGHT, padx=10, pady=6)
    
    # ============= FUNCIONES DE DATOS Y LÓGICA =============
    
    def initialize_data(self):
        """Inicializar datos del sistema"""
        try:
            self.log_activity("Inicializando sistema...")
            
            # Poblar datos si es necesario
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos_quimicos")
            count = cursor.fetchone()[0]
            
            if count == 0:
                self.populate_sample_data()
            
            # Cargar proveedores para filtros
            self.load_providers_for_filters()
            
            # Actualizar interfaz
            self.refresh_all_data()
            
            self.log_activity(f"Sistema inicializado - {count} productos cargados")
            
        except Exception as e:
            self.log_activity(f"Error inicializando: {e}", "ERROR")
            messagebox.showerror("Error", f"Error inicializando sistema: {e}")
    
    def populate_sample_data(self):
        """Poblar datos de ejemplo mejorados"""
        cursor = self.conn.cursor()
        
        productos_ejemplo = [
            # (codigo, clase, nombre, descripcion, saldo, unidad, valor_unit, stock_min, stock_max, ubicacion, proveedor, nivel_peligro, ingrediente_activo, concentracion, numero_registro, fecha_venc, lote)
            ('QM001', 'ACARICIDA', 'Abafed', 'Acaricida sistémico de amplio espectro', 32000, 'C.C', 80, 5000, 50000, 'A-01', 'AGROQUIMICOS ANDINOS', 'ALTO', 'Abamectina', '1.8% EC', 'ICA-001', '2025-12-31', 'LT2024001'),
            ('QM002', 'FUNGICIDA', 'Mancozeb 80 WP', 'Fungicida preventivo de contacto', 15000, 'GR', 75, 2000, 25000, 'A-02', 'BAYER CROPSCIENCE', 'MEDIO', 'Mancozeb', '80% WP', 'ICA-002', '2025-10-15', 'LT2024002'),
            ('QM003', 'INSECTICIDA', 'Lambda Cyhalothrin', 'Insecticida piretroide de amplio espectro', 8500, 'C.C', 350, 1000, 15000, 'A-03', 'SYNGENTA', 'ALTO', 'Lambda-cihalotrina', '5% EC', 'ICA-003', '2025-08-20', 'LT2024003'),
            ('QM004', 'HERBICIDA', 'Glifosato 48%', 'Herbicida sistémico no selectivo', 25000, 'ML', 45, 3000, 40000, 'B-01', 'MONSANTO', 'MEDIO', 'Glifosato', '48% SL', 'ICA-004', '2026-03-10', 'LT2024004'),
            ('QM005', 'FERTILIZANTE', 'Urea 46%', 'Fertilizante nitrogenado de liberación rápida', 50000, 'KG', 2.5, 10000, 100000, 'C-01', 'YARA COLOMBIA', 'BAJO', 'Nitrógeno', '46% N', 'ICA-005', None, 'LT2024005'),
            ('QM006', 'REGULADOR', 'Ácido Giberélico', 'Regulador de crecimiento vegetal', 500, 'GR', 850, 100, 2000, 'D-01', 'VALENT BIOSCIENCES', 'MEDIO', 'Ácido giberélico', '10% SP', 'ICA-006', '2025-06-30', 'LT2024006'),
            ('QM007', 'ACARICIDA', 'Citroemulsión', 'Acaricida orgánico a base de cítricos', 0, 'LT', 95, 500, 5000, 'A-04', 'PRODUCTOS NATURALES', 'BAJO', 'D-Limoneno', '6% EC', 'ICA-007', '2025-09-15', 'LT2024007'),
            ('QM008', 'FUNGICIDA', 'Propiconazole', 'Fungicida sistémico triazol', 3200, 'ML', 180, 500, 8000, 'A-05', 'CORTEVA AGRISCIENCE', 'ALTO', 'Propiconazol', '25% EC', 'ICA-008', '2025-11-28', 'LT2024008')
        ]
        
        for producto in productos_ejemplo:
            cursor.execute('''
                INSERT INTO productos_quimicos 
                (codigo, clase, nombre, descripcion, saldo_real, unidad, valor_unitario, 
                 stock_minimo, stock_maximo, ubicacion, proveedor, nivel_peligrosidad, 
                 ingrediente_activo, concentracion, numero_registro, fecha_vencimiento, lote)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', producto)
        
        self.conn.commit()
        print(f"✅ {len(productos_ejemplo)} productos de ejemplo creados")
    
    def load_providers_for_filters(self):
        """Cargar proveedores para filtros"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT DISTINCT proveedor FROM productos_quimicos WHERE proveedor IS NOT NULL ORDER BY proveedor")
            proveedores = ["Todos"] + [row[0] for row in cursor.fetchall()]
            
            if 'filter_proveedor' in self.filter_vars:
                combo = None
                # Encontrar el combo de proveedores y actualizar sus valores
                # (Esto requeriría una referencia al widget, se implementaría en versión completa)
                
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
    
    def load_inventory_data(self):
        """Cargar datos del inventario con filtros aplicados"""
        try:
            # Limpiar tabla actual
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            # Construir query con filtros
            query = """
                SELECT codigo, clase, nombre, saldo_real, unidad, valor_unitario, 
                       stock_minimo, nivel_peligrosidad, proveedor, fecha_vencimiento
                FROM productos_quimicos 
                WHERE activo = 1
            """
            params = []
            
            # Aplicar filtros (si existen)
            if hasattr(self, 'search_var') and self.search_var.get().strip():
                search_term = f"%{self.search_var.get().strip().lower()}%"
                query += " AND (LOWER(nombre) LIKE ? OR LOWER(codigo) LIKE ? OR LOWER(clase) LIKE ?)"
                params.extend([search_term, search_term, search_term])
            
            # Filtros adicionales se aplicarían aquí
            
            query += " ORDER BY clase, codigo"
            
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            productos_mostrados = 0
            productos_criticos = 0
            
            for row in cursor.fetchall():
                codigo, clase, nombre, saldo, unidad, valor_unit, stock_min, nivel_peligro, proveedor, fecha_venc = row
                
                # Determinar estado del stock
                if saldo == 0:
                    estado = "🔴 AGOTADO"
                    tags = ('agotado',)
                    productos_criticos += 1
                elif saldo <= stock_min:
                    estado = "🟡 STOCK BAJO"
                    tags = ('bajo',)
                    productos_criticos += 1
                else:
                    estado = "🟢 NORMAL"
                    tags = ('normal',)
                
                # Indicador de riesgo
                if nivel_peligro == 'ALTO':
                    riesgo_texto = "🔴 ALTO"
                    if 'normal' in tags:
                        tags = ('alto_riesgo',)
                    else:
                        tags += ('alto_riesgo',)
                elif nivel_peligro == 'MEDIO':
                    riesgo_texto = "🟡 MEDIO"
                else:
                    riesgo_texto = "🟢 BAJO"
                
                # Formatear fecha de vencimiento
                if fecha_venc:
                    try:
                        fecha_obj = datetime.strptime(fecha_venc, '%Y-%m-%d').date()
                        dias_para_vencer = (fecha_obj - date.today()).days
                        if dias_para_vencer < 0:
                            vence_texto = "🔴 VENCIDO"
                            tags += ('vencido',)
                        elif dias_para_vencer <= 30:
                            vence_texto = f"⚠️ {dias_para_vencer}d"
                            tags += ('por_vencer',)
                        else:
                            vence_texto = fecha_obj.strftime('%d/%m/%Y')
                    except:
                        vence_texto = "Sin fecha"
                else:
                    vence_texto = "Sin fecha"
                
                # Formatear valores
                valor_formateado = f"${valor_unit:,.0f}"
                proveedor_short = (proveedor[:15] + "...") if proveedor and len(proveedor) > 15 else (proveedor or "N/A")
                
                # Insertar en tabla
                self.inventory_tree.insert('', tk.END, values=(
                    codigo, clase, nombre, f"{saldo:,}", unidad, valor_formateado,
                    f"{stock_min:,}", riesgo_texto, proveedor_short, vence_texto, estado
                ), tags=tags)
                
                productos_mostrados += 1
            
            # Configurar colores de tags
            self.inventory_tree.tag_configure('agotado', background='#ffebee', foreground='#c62828')
            self.inventory_tree.tag_configure('bajo', background='#fff3e0', foreground='#ef6c00')
            self.inventory_tree.tag_configure('normal', background='#ffffff', foreground='#2e7d32')
            self.inventory_tree.tag_configure('alto_riesgo', background='#fff3e0', foreground='#d84315')
            self.inventory_tree.tag_configure('vencido', background='#ffebee', foreground='#b71c1c')
            self.inventory_tree.tag_configure('por_vencer', background='#fff8e1', foreground='#f57c00')
            
            # Actualizar contador
            if hasattr(self, 'inventory_count_label'):
                cursor.execute("SELECT COUNT(*) FROM productos_quimicos WHERE activo = 1")
                total = cursor.fetchone()[0]
                self.inventory_count_label.config(
                    text=f"Mostrando {productos_mostrados} de {total} productos • {productos_criticos} requieren atención"
                )
            
            return productos_mostrados
            
        except Exception as e:
            self.log_activity(f"Error cargando inventario: {e}", "ERROR")
            messagebox.showerror("Error", f"Error cargando inventario: {e}")
            return 0
    
    def update_statistics(self):
        """Actualizar estadísticas en tiempo real"""
        try:
            # Limpiar container actual
            for widget in self.stats_container.winfo_children():
                widget.destroy()
            
            cursor = self.conn.cursor()
            
            # Obtener estadísticas
            stats_queries = [
                ("SELECT COUNT(*) FROM productos_quimicos WHERE activo = 1", "Total Productos", "📦"),
                ("SELECT COUNT(*) FROM productos_quimicos WHERE saldo_real = 0 AND activo = 1", "Sin Stock", "🔴"),
                ("SELECT COUNT(*) FROM productos_quimicos WHERE saldo_real <= stock_minimo AND saldo_real > 0 AND activo = 1", "Stock Bajo", "🟡"),
                ("SELECT COUNT(*) FROM productos_quimicos WHERE nivel_peligrosidad = 'ALTO' AND activo = 1", "Alto Riesgo", "⚠️"),
                ("SELECT COALESCE(SUM(saldo_real * valor_unitario), 0) FROM productos_quimicos WHERE activo = 1", "Valor Total", "💰")
            ]
            
            colors = ['#3498db', '#e74c3c', '#f39c12', '#e67e22', '#27ae60']
            
            for i, (query, label, icon) in enumerate(stats_queries):
                cursor.execute(query)
                value = cursor.fetchone()[0]
                
                if label == "Valor Total":
                    value_text = f"${value:,.0f}"
                else:
                    value_text = f"{value:,}"
                
                # Crear card de estadística
                card = tk.Frame(self.stats_container, bg=colors[i], relief='solid', bd=1)
                card.pack(fill=tk.X, pady=4)
                
                card_content = tk.Frame(card, bg=colors[i])
                card_content.pack(fill=tk.BOTH, padx=12, pady=8)
                
                # Icono y valor
                header_frame = tk.Frame(card_content, bg=colors[i])
                header_frame.pack(fill=tk.X)
                
                icon_label = tk.Label(header_frame, text=icon, font=('Arial', 14),
                                     bg=colors[i], fg='white')
                icon_label.pack(side=tk.LEFT)
                
                value_label = tk.Label(header_frame, text=value_text, 
                                      font=('Segoe UI', 14, 'bold'),
                                      bg=colors[i], fg='white')
                value_label.pack(side=tk.RIGHT)
                
                # Etiqueta
                label_widget = tk.Label(card_content, text=label,
                                       font=('Segoe UI', 9),
                                       bg=colors[i], fg='white')
                label_widget.pack(anchor='w')
                
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def update_header_info(self):
        """Actualizar información del header periódicamente"""
        try:
            # Actualizar fecha y hora
            current_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
            
            # Actualizar estadísticas rápidas
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos_quimicos WHERE activo = 1")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM productos_quimicos WHERE saldo_real <= stock_minimo AND activo = 1")
            alertas = cursor.fetchone()[0]
            
            stats_text = f"📦 {total} productos • ⚠️ {alertas} alertas"
            
            # Actualizar labels si existen
            if hasattr(self, 'quick_stats_label'):
                self.quick_stats_label.config(text=stats_text)
            
            # Programar próxima actualización en 60 segundos
            self.root.after(60000, self.update_header_info)
            
        except Exception as e:
            print(f"Error actualizando header: {e}")
            # Reintentar en 60 segundos aunque haya error
            self.root.after(60000, self.update_header_info)
    
    # ============= FUNCIONES DE EVENTOS =============
    
    def on_filter_change(self, *args):
        """Manejar cambios en filtros"""
        self.load_inventory_data()
    
    def clear_filters(self):
        """Limpiar todos los filtros"""
        if hasattr(self, 'search_var'):
            self.search_var.set("")
        
        for var in self.filter_vars.values():
            # Establecer al primer valor (generalmente "Todos")
            values = var.trace_vinfo()
            if values:
                # Esto es una simplificación, en implementación real se manejaría mejor
                pass
    
    def on_item_double_click(self, event=None):
        """Manejar doble clic en item"""
        selection = self.inventory_tree.selection()
        if selection:
            self.edit_product()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        item = self.inventory_tree.identify_row(event.y)
        if item:
            self.inventory_tree.selection_set(item)
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="✏️ Editar Producto", command=self.edit_product)
            menu.add_command(label="📥 Registrar Entrada", command=lambda: self.movimiento_dialog('entrada'))
            menu.add_command(label="📤 Registrar Salida", command=lambda: self.movimiento_dialog('salida'))
            menu.add_separator()
            menu.add_command(label="👁️ Ver Detalles", command=self.view_product_details)
            menu.add_command(label="📊 Ver Historial", command=self.view_product_history)
            menu.add_separator()
            menu.add_command(label="🗑️ Desactivar", command=self.deactivate_product)
            
            menu.post(event.x_root, event.y_root)
    
    def sort_column(self, col):
        """Ordenar por columna"""
        try:
            data = [(self.inventory_tree.set(child, col), child) for child in self.inventory_tree.get_children('')]
            
            # Ordenar numéricamente si es posible
            try:
                # Intentar ordenar numéricamente
                data.sort(key=lambda x: float(x[0].replace(',', '').replace('$', '').replace('🔴', '').replace('🟡', '').replace('🟢', '').replace('⚠️', '').strip()))
            except:
                # Ordenar alfabéticamente
                data.sort()
            
            for index, (val, child) in enumerate(data):
                self.inventory_tree.move(child, '', index)
                
        except Exception as e:
            print(f"Error ordenando columna {col}: {e}")
    
    # ============= FUNCIONES DE ACCIONES =============
    
    def nuevo_producto(self):
        """Abrir ventana para nuevo producto"""
        ProductDialog(self.root, self, mode="create")
    
    def edit_product(self):
        """Editar producto seleccionado"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un producto para editar")
            return
        
        # Obtener código del producto
        item = self.inventory_tree.item(selection[0])
        codigo = item['values'][0]
        
        # Obtener datos completos del producto
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM productos_quimicos WHERE codigo = ?", (codigo,))
        producto = cursor.fetchone()
        
        if producto:
            ProductDialog(self.root, self, mode="edit", product_data=producto)
    
    def movimiento_entrada(self):
        """Abrir diálogo de entrada de stock"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from utils.movimientos_inventario import MovimientoInventarioDialog
            dialog = MovimientoInventarioDialog(self.root, 'quimicos', 'entrada')
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir entrada de stock: {e}")
    
    def movimiento_salida(self):
        """Abrir diálogo de salida de stock"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from utils.movimientos_inventario import MovimientoInventarioDialog
            dialog = MovimientoInventarioDialog(self.root, 'quimicos', 'salida')
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir salida de stock: {e}")
    
    def ver_historial_movimientos(self):
        """Ver historial de movimientos"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from utils.movimientos_inventario import HistorialMovimientosWindow
            dialog = HistorialMovimientosWindow(self.root, 'quimicos')
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir historial: {e}")
    
    def movimiento_dialog(self, tipo):
        """Abrir diálogo de movimiento (método legacy)"""
        if tipo == 'entrada':
            self.movimiento_entrada()
        else:
            self.movimiento_salida()
    
    def view_product_details(self):
        """Ver detalles completos del producto"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un producto")
            return
        
        # Obtener código del producto y mostrar detalles
        item = self.inventory_tree.item(selection[0])
        codigo = item['values'][0]
        
        ProductDetailsWindow(self.root, self, codigo)
    
    def view_product_history(self):
        """Ver historial de movimientos del producto"""
        messagebox.showinfo("Historial", "Función de historial en desarrollo")
    
    def deactivate_product(self):
        """Desactivar producto seleccionado"""
        selection = self.inventory_tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Confirmar", "¿Desactivar este producto?\n\nNo se eliminará pero no aparecerá en el inventario activo."):
            item = self.inventory_tree.item(selection[0])
            codigo = item['values'][0]
            
            cursor = self.conn.cursor()
            cursor.execute("UPDATE productos_quimicos SET activo = 0 WHERE codigo = ?", (codigo,))
            self.conn.commit()
            
            self.refresh_all_data()
            messagebox.showinfo("Éxito", "Producto desactivado correctamente")
    
    def show_alerts_summary(self):
        """Mostrar resumen de alertas"""
        AlertsSummaryWindow(self.root, self)
    
    def show_dashboard(self):
        """Mostrar dashboard con gráficos"""
        if MATPLOTLIB_AVAILABLE:
            DashboardWindow(self.root, self)
        else:
            messagebox.showinfo("Dashboard", "Dashboard visual requiere matplotlib\n\nInstalar con: pip install matplotlib")
    
    def refresh_all_data(self):
        """Actualizar todos los datos"""
        try:
            self.load_inventory_data()
            self.update_statistics()
            self.log_activity("Datos actualizados correctamente")
            self.update_status("Datos actualizados correctamente")
        except Exception as e:
            self.log_activity(f"Error actualizando datos: {e}", "ERROR")
            messagebox.showerror("Error", f"Error actualizando datos: {e}")
    
    def manual_backup(self):
        """Realizar backup manual"""
        try:
            backup_file = self.create_backup("MANUAL")
            if backup_file:
                messagebox.showinfo("Backup", f"Backup creado exitosamente:\n{backup_file}")
                self.log_activity(f"Backup manual creado: {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creando backup: {e}")
    
    def export_data_dialog(self):
        """Abrir diálogo de exportación"""
        ExportDialog(self.root, self)
    
    # ============= FUNCIONES DE UTILIDAD =============
    
    def center_window(self):
        """Centrar ventana principal"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
    
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
            '#27ae60': '#229954',
            '#2ecc71': '#27ae60',
            '#3498db': '#2980b9',
            '#f39c12': '#e67e22',
            '#e74c3c': '#c0392b',
            '#8e44ad': '#7d3c98',
            '#16a085': '#138d75',
            '#34495e': '#2c3e50',
            '#95a5a6': '#7f8c8d'
        }
        return color_map.get(color, color)
    
    def log_activity(self, message, level="INFO"):
        """Registrar actividad en log"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {level}: {message}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            print(f"{level}: {message}")
            
        except Exception as e:
            print(f"Error escribiendo log: {e}")
    
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
        
        # Auto-limpiar después de 5 segundos
        self.root.after(5000, lambda: self.status_label.config(text="Sistema operativo"))
    
    def create_backup(self, tipo="AUTO"):
        """Crear backup de la base de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_quimicos_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Crear backup
            with open(self.conn.execute("PRAGMA database_list").fetchone()[2], 'rb') as source:
                with open(backup_path, 'wb') as backup:
                    backup.write(source.read())
            
            # Registrar en log de backups
            cursor = self.conn.cursor()
            file_size = backup_path.stat().st_size
            cursor.execute('''
                INSERT INTO backup_log (archivo, tamaño, tipo)
                VALUES (?, ?, ?)
            ''', (str(backup_path), file_size, tipo))
            self.conn.commit()
            
            return str(backup_path)
            
        except Exception as e:
            self.log_activity(f"Error creando backup: {e}", "ERROR")
            return None
    
    def setup_notifications(self):
        """Configurar sistema de notificaciones"""
        def check_notifications():
            try:
                # Verificar stock bajo
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM productos_quimicos 
                    WHERE saldo_real <= stock_minimo AND activo = 1
                """)
                stock_bajo = cursor.fetchone()[0]
                
                # Verificar productos por vencer
                cursor.execute("""
                    SELECT COUNT(*) FROM productos_quimicos 
                    WHERE fecha_vencimiento <= date('now', '+30 days') 
                    AND fecha_vencimiento > date('now') AND activo = 1
                """)
                por_vencer = cursor.fetchone()[0]
                
                # Generar notificaciones si es necesario
                if stock_bajo > 0:
                    self.create_alert("STOCK_BAJO", f"{stock_bajo} productos con stock bajo", "WARNING")
                
                if por_vencer > 0:
                    self.create_alert("VENCIMIENTO", f"{por_vencer} productos próximos a vencer", "WARNING")
                
            except Exception as e:
                self.log_activity(f"Error verificando notificaciones: {e}", "ERROR")
        
        # Verificar cada 30 minutos
        def schedule_check():
            check_notifications()
            self.root.after(1800000, schedule_check)  # 30 minutos
        
        # Primera verificación después de 5 segundos
        self.root.after(5000, schedule_check)
    
    def create_alert(self, tipo, mensaje, nivel="INFO"):
        """Crear alerta en el sistema"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alertas_sistema (tipo, titulo, mensaje, nivel)
                VALUES (?, ?, ?, ?)
            ''', (tipo, f"Alerta: {tipo}", mensaje, nivel))
            self.conn.commit()
            
        except Exception as e:
            print(f"Error creando alerta: {e}")
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            self.log_activity(f"Error ejecutando aplicación: {e}", "ERROR")
            messagebox.showerror("Error Fatal", f"Error ejecutando aplicación: {e}")
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        try:
            # Crear backup final si está habilitado
            if self.auto_backup_enabled:
                self.create_backup("CIERRE")
            
            # Cerrar conexión BD
            if self.conn:
                self.conn.close()
            
            self.log_activity("Sistema cerrado correctamente")
            self.root.destroy()
            
        except Exception as e:
            print(f"Error al cerrar: {e}")
            self.root.destroy()

    def update_clock_quimicos(self):
        """Actualizar el reloj en tiempo real"""
        try:
            if hasattr(self, 'datetime_label'):
                current_time = datetime.now().strftime("%d/%m/%Y - %H:%M")
                self.datetime_label.config(text=current_time)
            # Programar próxima actualización en 60 segundos
            self.root.after(60000, self.update_clock_quimicos)
        except Exception as e:
            print(f"Error actualizando reloj químicos: {e}")
            # Reintentar en 60 segundos aunque haya error
            self.root.after(60000, self.update_clock_quimicos)


# ============= VENTANAS AUXILIARES =============

class ProductDialog:
    """Diálogo para crear/editar productos"""
    
    def __init__(self, parent, main_app, mode="create", product_data=None):
        self.parent = parent
        self.main_app = main_app
        self.mode = mode
        self.product_data = product_data
        
        self.window = tk.Toplevel(parent)
        self.window.title("➕ Nuevo Producto" if mode == "create" else "✏️ Editar Producto")
        self.window.geometry("600x700")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        if mode == "edit" and product_data:
            self.load_product_data()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"600x700+{x}+{y}")
    
    def create_widgets(self):
        # Header
        header = tk.Frame(self.window, bg='#27ae60', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = "➕ Nuevo Producto Químico" if self.mode == "create" else "✏️ Editar Producto Químico"
        title_label = tk.Label(header, text=title,
                             font=('Segoe UI', 16, 'bold'),
                             bg='#27ae60', fg='white')
        title_label.pack(expand=True)
        
        # Contenido principal
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear formulario
        self.create_form(main_frame)
    
    def create_form(self, parent):
        # Campos del formulario mejorado
        campos = [
            ("Código*:", "codigo", "entry", None),
            ("Clase*:", "clase", "combo", ["ACARICIDA", "FUNGICIDA", "INSECTICIDA", "HERBICIDA", "FERTILIZANTE", "REGULADOR", "ADHERENTE", "OTRO"]),
            ("Nombre del Producto*:", "nombre", "entry", None),
            ("Descripción:", "descripcion", "text", None),
            ("Ingrediente Activo:", "ingrediente_activo", "entry", None),
            ("Concentración:", "concentracion", "entry", None),
            ("Número de Registro:", "numero_registro", "entry", None),
            ("Stock Actual*:", "saldo_real", "entry", None),
            ("Unidad*:", "unidad", "combo", ["C.C", "ML", "LT", "GR", "KG", "UND", "GAL"]),
            ("Valor Unitario*:", "valor_unitario", "entry", None),
            ("Stock Mínimo*:", "stock_minimo", "entry", None),
            ("Stock Máximo:", "stock_maximo", "entry", None),
            ("Ubicación:", "ubicacion", "entry", None),
            ("Proveedor:", "proveedor", "entry", None),
            ("Nivel de Peligrosidad*:", "nivel_peligrosidad", "combo", ["BAJO", "MEDIO", "ALTO"]),
            ("Fecha de Vencimiento:", "fecha_vencimiento", "entry", None),
            ("Lote:", "lote", "entry", None),
            ("Notas:", "notas", "text", None)
        ]
        
        self.widgets = {}
        row = 0
        
        for label_text, field_name, widget_type, options in campos:
            # Label
            label = tk.Label(parent, text=label_text,
                           font=('Segoe UI', 10, 'bold'),
                           bg='white', fg='#2c3e50')
            label.grid(row=row, column=0, sticky='nw', pady=8, padx=(0, 15))
            
            # Widget
            if widget_type == "entry":
                widget = tk.Entry(parent, width=50, font=('Segoe UI', 10),
                                relief='solid', bd=1)
                widget.grid(row=row, column=1, pady=8, sticky='ew')
            
            elif widget_type == "combo":
                widget = ttk.Combobox(parent, values=options, width=47, 
                                    font=('Segoe UI', 10))
                widget.grid(row=row, column=1, pady=8, sticky='ew')
            
            elif widget_type == "text":
                text_frame = tk.Frame(parent, bg='white')
                text_frame.grid(row=row, column=1, pady=8, sticky='ew')
                
                widget = tk.Text(text_frame, width=50, height=3, 
                               font=('Segoe UI', 10), relief='solid', bd=1)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                        command=widget.yview)
                widget.configure(yscrollcommand=scrollbar.set)
                
                widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.widgets[field_name] = widget
            row += 1
        
        parent.grid_columnconfigure(1, weight=1)
        
        # Botones
        self.create_buttons(parent, row)
    
    def create_buttons(self, parent, row):
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Botón guardar
        save_text = "💾 Actualizar" if self.mode == "edit" else "💾 Guardar"
        save_btn = tk.Button(btn_frame, text=save_text, command=self.save_product,
                           bg="#27ae60", fg="white", font=('Segoe UI', 12, 'bold'),
                           relief='flat', bd=0, padx=30, pady=12, cursor='hand2')
        save_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón cancelar
        cancel_btn = tk.Button(btn_frame, text="❌ Cancelar", command=self.window.destroy,
                             bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                             relief='flat', bd=0, padx=30, pady=12, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón limpiar (solo para nuevo)
        if self.mode == "create":
            clear_btn = tk.Button(btn_frame, text="🗑️ Limpiar", command=self.clear_form,
                                bg="#95a5a6", fg="white", font=('Segoe UI', 12, 'bold'),
                                relief='flat', bd=0, padx=30, pady=12, cursor='hand2')
            clear_btn.pack(side=tk.LEFT, padx=10)
    
    def load_product_data(self):
        if not self.product_data:
            return
        
        # Mapear campos de BD a widgets
        field_mapping = {
            1: 'codigo', 2: 'clase', 3: 'nombre', 4: 'descripcion', 5: 'saldo_real',
            6: 'unidad', 7: 'valor_unitario', 8: 'stock_minimo', 9: 'stock_maximo',
            10: 'ubicacion', 11: 'proveedor', 14: 'nivel_peligrosidad', 
            15: 'ingrediente_activo', 16: 'concentracion', 17: 'numero_registro',
            18: 'fecha_vencimiento', 19: 'lote', 21: 'notas'
        }
        
        for db_index, widget_name in field_mapping.items():
            if widget_name in self.widgets and db_index < len(self.product_data):
                value = self.product_data[db_index]
                widget = self.widgets[widget_name]
                
                if isinstance(widget, tk.Text):
                    widget.delete('1.0', tk.END)
                    if value:
                        widget.insert('1.0', str(value))
                elif isinstance(widget, ttk.Combobox):
                    widget.set(str(value) if value else "")
                else:
                    widget.delete(0, tk.END)
                    if value is not None:
                        widget.insert(0, str(value))
        
        # Deshabilitar código en modo edición
        if self.mode == "edit":
            self.widgets['codigo'].config(state='disabled')
    
    def clear_form(self):
        for widget_name, widget in self.widgets.items():
            if isinstance(widget, tk.Text):
                widget.delete('1.0', tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
    
    def save_product(self):
        try:
            # Validar campos obligatorios
            required_fields = ['codigo', 'clase', 'nombre', 'saldo_real', 'unidad', 'valor_unitario', 'stock_minimo', 'nivel_peligrosidad']
            
            for field in required_fields:
                widget = self.widgets[field]
                if isinstance(widget, tk.Text):
                    value = widget.get('1.0', tk.END).strip()
                else:
                    value = widget.get().strip()
                
                if not value:
                    messagebox.showerror("Error", f"El campo {field.replace('_', ' ').title()} es obligatorio")
                    widget.focus()
                    return
            
            # Validar valores numéricos
            try:
                saldo_real = int(self.widgets['saldo_real'].get())
                valor_unitario = float(self.widgets['valor_unitario'].get())
                stock_minimo = int(self.widgets['stock_minimo'].get())
                stock_maximo = int(self.widgets['stock_maximo'].get() or 1000)
            except ValueError:
                messagebox.showerror("Error", "Los valores numéricos no son válidos")
                return
            
            # Preparar datos
            data = {}
            for field_name, widget in self.widgets.items():
                if isinstance(widget, tk.Text):
                    data[field_name] = widget.get('1.0', tk.END).strip()
                else:
                    data[field_name] = widget.get().strip()
            
            cursor = self.main_app.conn.cursor()
            
            if self.mode == "create":
                # Verificar código único
                cursor.execute("SELECT id FROM productos_quimicos WHERE codigo = ?", (data['codigo'],))
                if cursor.fetchone():
                    messagebox.showerror("Error", "El código ya existe")
                    return
                
                # Insertar nuevo producto
                cursor.execute('''
                    INSERT INTO productos_quimicos 
                    (codigo, clase, nombre, descripcion, saldo_real, unidad, valor_unitario, 
                     stock_minimo, stock_maximo, ubicacion, proveedor, nivel_peligrosidad, 
                     ingrediente_activo, concentracion, numero_registro, fecha_vencimiento, lote, notas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['codigo'], data['clase'], data['nombre'], data['descripcion'],
                    saldo_real, data['unidad'], valor_unitario, stock_minimo, stock_maximo,
                    data['ubicacion'], data['proveedor'], data['nivel_peligrosidad'],
                    data['ingrediente_activo'], data['concentracion'], data['numero_registro'],
                    data['fecha_vencimiento'] or None, data['lote'], data['notas']
                ))
                
                mensaje = "Producto creado exitosamente"
                
            else:
                # Actualizar producto existente
                cursor.execute('''
                    UPDATE productos_quimicos SET 
                    clase=?, nombre=?, descripcion=?, saldo_real=?, unidad=?, valor_unitario=?, 
                    stock_minimo=?, stock_maximo=?, ubicacion=?, proveedor=?, nivel_peligrosidad=?, 
                    ingrediente_activo=?, concentracion=?, numero_registro=?, fecha_vencimiento=?, 
                    lote=?, notas=?
                    WHERE codigo=?
                ''', (
                    data['clase'], data['nombre'], data['descripcion'], saldo_real,
                    data['unidad'], valor_unitario, stock_minimo, stock_maximo,
                    data['ubicacion'], data['proveedor'], data['nivel_peligrosidad'],
                    data['ingrediente_activo'], data['concentracion'], data['numero_registro'],
                    data['fecha_vencimiento'] or None, data['lote'], data['notas'],
                    data['codigo']
                ))
                
                mensaje = "Producto actualizado exitosamente"
            
            self.main_app.conn.commit()
            
            # Log de actividad
            self.main_app.log_activity(f"Producto {data['codigo']} {'creado' if self.mode == 'create' else 'actualizado'}")
            
            messagebox.showinfo("Éxito", mensaje)
            
            # Actualizar datos principales
            self.main_app.refresh_all_data()
            
            if self.mode == "create":
                self.clear_form()
                self.widgets['codigo'].focus()
            else:
                self.window.destroy()
                
        except Exception as e:
            self.main_app.log_activity(f"Error guardando producto: {e}", "ERROR")
            messagebox.showerror("Error", f"Error guardando producto: {e}")




class ProductDetailsWindow:
    """Ventana de detalles del producto"""
    
    def __init__(self, parent, main_app, codigo):
        self.parent = parent
        self.main_app = main_app
        self.codigo = codigo
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"👁️ Detalles del Producto - {codigo}")
        self.window.geometry("700x600")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        self.create_widgets()
        self.load_product_details()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
    
    def create_widgets(self):
        # Implementación simplificada de detalles
        tk.Label(self.window, text=f"🚧 Detalles de {self.codigo} en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
        
        tk.Button(self.window, text="❌ Cerrar", command=self.window.destroy,
                 bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10, cursor='hand2').pack(pady=20)
    
    def load_product_details(self):
        pass


class AlertsSummaryWindow:
    """Ventana de resumen de alertas"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("⚠️ Resumen de Alertas")
        self.window.geometry("800x600")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
    
    def create_widgets(self):
        # Implementación simplificada de alertas
        tk.Label(self.window, text="🚧 Sistema de Alertas en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
        
        tk.Button(self.window, text="❌ Cerrar", command=self.window.destroy,
                 bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10, cursor='hand2').pack(pady=20)


class DashboardWindow:
    """Ventana de dashboard con gráficos"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Dashboard Ejecutivo")
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
        # Implementación simplificada de dashboard
        tk.Label(self.window, text="🚧 Dashboard con Gráficos en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
        
        tk.Button(self.window, text="❌ Cerrar", command=self.window.destroy,
                 bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10, cursor='hand2').pack(pady=20)


class ExportDialog:
    """Diálogo de exportación de datos"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Exportar Datos")
        self.window.geometry("500x400")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
    
    def create_widgets(self):
        # Implementación simplificada de exportación
        tk.Label(self.window, text="🚧 Sistema de Exportación en Desarrollo", 
                font=('Segoe UI', 16), fg='#7f8c8d').pack(expand=True)
        
        tk.Button(self.window, text="❌ Cerrar", command=self.window.destroy,
                 bg="#e74c3c", fg="white", font=('Segoe UI', 12, 'bold'),
                 relief='flat', bd=0, padx=20, pady=10, cursor='hand2').pack(pady=20)


# ============= FUNCIÓN PRINCIPAL =============

def main():
    """Función principal para ejecutar el sistema"""
    try:
        print("🧪 Iniciando Sistema Avanzado de Inventario de Químicos...")
        print("=" * 60)
        
        # Verificar dependencias opcionales
        if not OPENPYXL_AVAILABLE:
            print("⚠️  Advertencia: openpyxl no disponible - funciones de Excel limitadas")
        
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  Advertencia: matplotlib no disponible - gráficos no disponibles")
        
        print("✅ Iniciando aplicación...")
        
        # Crear y ejecutar aplicación
        app = SistemaInventarioQuimicos()
        app.run()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        messagebox.showerror("Error Fatal", f"Error iniciando aplicación:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# ============= MOVIMIENTO FUNCIONAL =============
class MovementDialog:
    """
    Diálogo para registrar movimientos (Entrada/Salida)
    """
    def __init__(self, parent, app, tipo):
        self.app = app
        self.tipo = tipo  # 'entrada' o 'salida'
        self.window = tk.Toplevel(parent)
        title = "📥 Entrada de Químicos" if tipo == 'entrada' else "📤 Salida de Químicos"
        self.window.title(title)
        self.window.geometry("400x300")
        self.window.grab_set()
        self.create_widgets()

    def create_widgets(self):
        frm = tk.Frame(self.window, padx=10, pady=10)
        frm.pack(fill=tk.BOTH, expand=True)

        tk.Label(frm, text="Producto:").grid(row=0, column=0, sticky='w')
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT id, codigo, nombre FROM productos_quimicos WHERE activo=1")
        productos = cursor.fetchall()
        self.map = {f"{codigo} - {nombre}": pid for pid, codigo, nombre in productos}
        self.combo = ttk.Combobox(frm, values=list(self.map.keys()), state='readonly')
        self.combo.grid(row=0, column=1, pady=5)

        tk.Label(frm, text="Cantidad:").grid(row=1, column=0, sticky='w')
        self.qty_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.qty_var).grid(row=1, column=1, pady=5)

        tk.Label(frm, text="Responsable:").grid(row=2, column=0, sticky='w')
        self.resp_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.resp_var).grid(row=2, column=1, pady=5)

        tk.Button(frm, text="💾 Guardar", bg=self.app.colores['success'], fg='white',
                  command=self.save_movement).grid(row=3, column=0, columnspan=2, pady=15)

    def save_movement(self):
        sel = self.combo.get()
        if not sel:
            messagebox.showerror("Error", "Selecciona un producto")
            return
        try:
            qty = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
        pid = self.map[sel]
        cursor = self.app.conn.cursor()
        cursor.execute("SELECT saldo_real FROM productos_quimicos WHERE id=?", (pid,))
        antes = cursor.fetchone()[0]
        nuevo = antes + qty if self.tipo == 'entrada' else antes - qty
        if nuevo < 0:
            messagebox.showerror("Error", "Stock insuficiente")
            return
        cursor.execute(
            "INSERT INTO movimientos_quimicos "
            "(producto_id, tipo, cantidad, cantidad_anterior, cantidad_nueva, responsable) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pid, self.tipo, qty, antes, nuevo, self.resp_var.get())
        )
        cursor.execute("UPDATE productos_quimicos SET saldo_real=? WHERE id=?", (nuevo, pid))
        self.app.conn.commit()
        messagebox.showinfo("Éxito", f"{'Entrada' if self.tipo=='entrada' else 'Salida'} registrada con éxito")
        self.app.refresh_all_data()
        self.window.destroy()

