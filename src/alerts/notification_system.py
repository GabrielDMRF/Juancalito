# src/alerts/notification_system.py
"""
Sistema de Alertas y Notificaciones - Versión Mejorada
Monitorea el sistema y genera alertas automáticas
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import threading
import time
import json
from pathlib import Path
import pandas as pd

class AlertsManager:
    """Gestor central de alertas del sistema - Versión Mejorada"""
    
    def __init__(self):
        # Obtener directorio base del proyecto
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.database_dir = self.base_dir / "database"
        
        # Configurar rutas absolutas de las bases de datos
        self.db_paths = {
            'personal': str(self.database_dir / 'gestion_personal.db'),
            'quimicos': str(self.database_dir / 'inventario_quimicos.db'),
            'almacen': str(self.database_dir / 'inventario_almacen.db'),
            'poscosecha': str(self.database_dir / 'inventario_poscosecha.db')
        }
        
        self.alerts_db = str(self.database_dir / 'alerts_system.db')
        self.setup_alerts_database()
        
        # Configuración de alertas mejorada
        self.alert_config = {
            'stock_critico_threshold': 5,  # Stock crítico más bajo
            'stock_bajo_threshold': 15,    # Stock bajo
            'vencimiento_dias_alerta': 30,
            'contrato_dias_alerta': 60,    # Alertas de contratos
            'check_interval_minutes': 5,   # Verificar cada 5 minutos
            'enable_notifications': True,
            'max_alerts_per_type': 10      # Máximo alertas por tipo
        }
        
        # Lista de alertas activas
        self.active_alerts = []
        
        # Control de hilos
        self.monitoring_thread = None
        self.should_stop = False
        
        # Iniciar monitoreo automático
        self.start_monitoring()
    
    def setup_alerts_database(self):
        """Configurar base de datos de alertas mejorada"""
        # Crear directorio de base de datos si no existe
        self.database_dir.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.alerts_db)
        cursor = conn.cursor()
        
        # Tabla principal de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                source_system TEXT NOT NULL,
                source_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                data_json TEXT,
                priority INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de historial de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                action TEXT NOT NULL,
                user TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (alert_id) REFERENCES alerts (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_monitoring(self):
        """Iniciar monitoreo automático en hilo separado"""
        if self.alert_config['enable_notifications']:
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            print("[OK] Sistema de alertas iniciado")
    
    def monitoring_loop(self):
        """Bucle principal de monitoreo mejorado"""
        while not self.should_stop:
            try:
                # Verificar todas las condiciones de alerta
                self.check_stock_alerts()
                self.check_expiration_alerts()
                self.check_contract_alerts()
                self.check_system_health()
                
                # Limpiar alertas antiguas
                self.cleanup_old_alerts()
                
                # Esperar antes de la siguiente verificación
                for _ in range(self.alert_config['check_interval_minutes'] * 60):
                    if self.should_stop:
                        break
                    time.sleep(1)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                if not self.should_stop:
                    time.sleep(60)  # Esperar 1 minuto si hay error
    
    def check_stock_alerts(self):
        """Verificar alertas de stock crítico mejorado"""
        try:
            for system in ['quimicos', 'almacen', 'poscosecha']:
                if os.path.exists(self.db_paths[system]):
                    conn = sqlite3.connect(self.db_paths[system])
                    cursor = conn.cursor()
                    
                    # Verificar stock crítico
                    if system == 'quimicos':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, clase, valor_unitario
                            FROM productos_quimicos 
                            WHERE saldo <= ? AND activo = 1
                        """, (self.alert_config['stock_critico_threshold'],))
                    elif system == 'almacen':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, categoria, valor_unitario
                            FROM productos_almacen 
                            WHERE saldo <= ? AND activo = 1
                        """, (self.alert_config['stock_critico_threshold'],))
                    elif system == 'poscosecha':
                            cursor.execute("""
                            SELECT codigo, nombre, saldo, tipo, valor_unitario
                                FROM productos_poscosecha 
                            WHERE saldo <= ? AND activo = 1
                            """, (self.alert_config['stock_critico_threshold'],))
                    
                    productos_criticos = cursor.fetchall()
                    
                    # Verificar stock bajo
                    if system == 'quimicos':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, clase, valor_unitario
                            FROM productos_quimicos 
                            WHERE saldo <= ? AND saldo > ? AND activo = 1
                        """, (self.alert_config['stock_bajo_threshold'], self.alert_config['stock_critico_threshold']))
                    elif system == 'almacen':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, categoria, valor_unitario
                            FROM productos_almacen 
                            WHERE saldo <= ? AND saldo > ? AND activo = 1
                        """, (self.alert_config['stock_bajo_threshold'], self.alert_config['stock_critico_threshold']))
                    elif system == 'poscosecha':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, tipo, valor_unitario
                            FROM productos_poscosecha 
                            WHERE saldo <= ? AND saldo > ? AND activo = 1
                        """, (self.alert_config['stock_bajo_threshold'], self.alert_config['stock_critico_threshold']))
                    
                    productos_bajos = cursor.fetchall()
                    conn.close()
                    
                    # Crear alertas críticas
                    for producto in productos_criticos:
                        valor_total = producto[2] * (producto[4] or 0)
                        self.create_alert(
                            alert_type='STOCK_CRITICO',
                            severity='HIGH',
                            title=f'🚨 Stock Crítico - {system.title()}',
                            message=f'Producto {producto[1]} ({producto[0]}) tiene stock crítico: {producto[2]} unidades. Valor: ${valor_total:,.0f}',
                            source_system=system,
                            source_id=producto[0],
                            data={'saldo': producto[2], 'valor_unitario': producto[4]}
                        )
                    
                    # Crear alertas de stock bajo
                    for producto in productos_bajos:
                        valor_total = producto[2] * (producto[4] or 0)
                        self.create_alert(
                            alert_type='STOCK_BAJO',
                            severity='MEDIUM',
                            title=f'⚠️ Stock Bajo - {system.title()}',
                            message=f'Producto {producto[1]} ({producto[0]}) tiene stock bajo: {producto[2]} unidades. Valor: ${valor_total:,.0f}',
                            source_system=system,
                            source_id=producto[0],
                            data={'saldo': producto[2], 'valor_unitario': producto[4]}
                        )
                    
        except Exception as e:
            print(f"Error verificando stock: {e}")
    
    def check_expiration_alerts(self):
        """Verificar alertas de vencimiento mejorado"""
        try:
            # Solo químicos tienen fechas de vencimiento
            if os.path.exists(self.db_paths['quimicos']):
                conn = sqlite3.connect(self.db_paths['quimicos'])
                cursor = conn.cursor()
                
                # Verificar productos que vencen en los próximos días
                fecha_limite = datetime.now() + timedelta(days=self.alert_config['vencimiento_dias_alerta'])
                
                cursor.execute("""
                    SELECT codigo, nombre, fecha_vencimiento, saldo, valor_unitario
                    FROM productos_quimicos 
                    WHERE fecha_vencimiento <= ? AND activo = 1
                    AND fecha_vencimiento > date('now')
                    AND saldo > 0
                """, (fecha_limite.strftime('%Y-%m-%d'),))
                
                productos_vencen = cursor.fetchall()
                conn.close()
                
                for producto in productos_vencen:
                    dias_restantes = (datetime.strptime(producto[2], '%Y-%m-%d') - datetime.now()).days
                    valor_total = producto[3] * (producto[4] or 0)
                    
                    severity = 'HIGH' if dias_restantes <= 7 else 'MEDIUM' if dias_restantes <= 15 else 'LOW'
                    
                    self.create_alert(
                        alert_type='VENCIMIENTO',
                        severity=severity,
                        title=f'⏰ Vencimiento Próximo - Químicos',
                        message=f'Producto {producto[1]} ({producto[0]}) vence en {dias_restantes} días. Stock: {producto[3]}. Valor: ${valor_total:,.0f}',
                        source_system='quimicos',
                        source_id=producto[0],
                        data={'fecha_vencimiento': producto[2], 'dias_restantes': dias_restantes, 'saldo': producto[3]}
                    )
                
        except Exception as e:
            print(f"Error verificando vencimientos: {e}")
    
    def check_contract_alerts(self):
        """Verificar alertas de contratos mejorado"""
        try:
            if os.path.exists(self.db_paths['personal']):
                conn = sqlite3.connect(self.db_paths['personal'])
                cursor = conn.cursor()
                
                # Verificar contratos que vencen pronto
                fecha_limite = datetime.now() + timedelta(days=self.alert_config['contrato_dias_alerta'])
                
                cursor.execute("""
                    SELECT e.cedula, e.nombre_completo, c.fecha_fin, tc.nombre as tipo_contrato
                    FROM empleados e
                    JOIN contratos c ON e.id = c.empleado_id
                    JOIN tipos_contrato tc ON c.tipo_contrato_id = tc.id
                    WHERE c.fecha_fin <= ? AND c.estado = 'activo'
                    ORDER BY c.fecha_fin
                                """, (fecha_limite.strftime('%Y-%m-%d'),))
                
                contratos_vencen = cursor.fetchall()
                conn.close()
                
                for contrato in contratos_vencen:
                    dias_restantes = (datetime.strptime(contrato[2], '%Y-%m-%d') - datetime.now()).days
                    
                    severity = 'HIGH' if dias_restantes <= 15 else 'MEDIUM' if dias_restantes <= 30 else 'LOW'
                    
                    self.create_alert(
                        alert_type='CONTRATO',
                        severity=severity,
                        title=f'📋 Contrato Vence Pronto',
                        message=f'Contrato de {contrato[1]} ({contrato[0]}) vence en {dias_restantes} días. Tipo: {contrato[3]}.',
                        source_system='personal',
                        source_id=contrato[0],
                        data={'fecha_fin': contrato[2], 'dias_restantes': dias_restantes, 'tipo_contrato': contrato[3]}
                    )
                
        except Exception as e:
            print(f"Error verificando contratos: {e}")
    
    def check_system_health(self):
        """Verificar salud del sistema"""
        try:
            # Verificar bases de datos
            for system, db_path in self.db_paths.items():
                if not os.path.exists(db_path):
                        self.create_alert(
                        alert_type='SYSTEM',
                        severity='HIGH',
                        title=f'🔧 Base de Datos No Encontrada',
                        message=f'La base de datos de {system} no existe: {db_path}',
                            source_system='system',
                            source_id=system
                        )
                else:
                    # Verificar conectividad
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                        conn.close()
                    except Exception as e:
                        self.create_alert(
                            alert_type='SYSTEM',
                            severity='HIGH',
                            title=f'🔧 Error de Base de Datos',
                            message=f'Error conectando a {system}: {str(e)}',
                            source_system='system',
                            source_id=system
                        )
                
        except Exception as e:
            print(f"Error verificando salud del sistema: {e}")
    
    def create_alert(self, alert_type, severity, title, message, source_system, source_id=None, data=None):
        """Crear una nueva alerta mejorada"""
        try:
            # Verificar si ya existe una alerta similar
            if self.alert_exists(alert_type, source_system, source_id):
                return
            
            # Limitar número de alertas por tipo
            if self.get_alert_count_by_type(alert_type) >= self.alert_config['max_alerts_per_type']:
                return
            
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, title, message, source_system, source_id, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_type, severity, title, message, source_system, source_id,
                json.dumps(data) if data else None
            ))
            
            conn.commit()
            conn.close()
            
            print(f"[ALERTA {severity}] {title}")
            
        except Exception as e:
            print(f"Error creando alerta: {e}")
    
    def alert_exists(self, alert_type, source_system, source_id):
        """Verificar si ya existe una alerta similar"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            # Verificar si existe una alerta activa del mismo tipo y fuente
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE alert_type = ? AND source_system = ? AND source_id = ? AND is_active = 1
            ''', (alert_type, source_system, source_id))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"Error verificando alerta existente: {e}")
            return False
    
    def get_alert_count_by_type(self, alert_type):
        """Obtener cantidad de alertas activas por tipo"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE alert_type = ? AND is_active = 1
            ''', (alert_type,))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"Error contando alertas: {e}")
            return 0
    
    def get_active_alerts(self, limit=50):
        """Obtener alertas activas ordenadas por prioridad"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, alert_type, severity, title, message, source_system, 
                       source_id, created_at, data_json
                FROM alerts 
                WHERE is_active = 1 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            return alerts
            
        except Exception as e:
            print(f"Error obteniendo alertas: {e}")
            return []
    
    def resolve_alert(self, alert_id):
        """Resolver una alerta"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET is_active = 0, resolved_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (alert_id,))
            
            # Registrar en historial
            cursor.execute('''
                INSERT INTO alert_history (alert_id, action, user)
                VALUES (?, ?, ?)
            ''', (alert_id, 'RESOLVED', 'SYSTEM'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error resolviendo alerta: {e}")
    
    def get_alerts_summary(self):
        """Obtener resumen de alertas mejorado"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            # Contar por severidad
            cursor.execute('''
                SELECT severity, COUNT(*) 
                FROM alerts 
                WHERE is_active = 1 
                GROUP BY severity
            ''')
            
            severity_counts = dict(cursor.fetchall())
            
            # Total de alertas activas
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE is_active = 1')
            total_active = cursor.fetchone()[0]
            
            # Alertas por sistema
            cursor.execute('''
                SELECT source_system, COUNT(*) 
                FROM alerts 
                WHERE is_active = 1 
                GROUP BY source_system
            ''')
            
            system_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'critical': severity_counts.get('HIGH', 0),
                'high': severity_counts.get('MEDIUM', 0),
                'medium': severity_counts.get('LOW', 0),
                'total_active': total_active,
                'by_system': system_counts
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen: {e}")
            return {'critical': 0, 'high': 0, 'medium': 0, 'total_active': 0, 'by_system': {}}
    
    def cleanup_old_alerts(self):
        """Limpiar alertas antiguas resueltas"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            # Eliminar alertas resueltas de más de 30 días
            cursor.execute('''
                DELETE FROM alerts 
                WHERE is_active = 0 AND resolved_at < date('now', '-30 days')
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error limpiando alertas: {e}")
    
    def stop_monitoring(self):
        """Detener el monitoreo automático"""
        self.should_stop = True
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2)  # Esperar máximo 2 segundos
            print("[OK] Sistema de alertas detenido")

class AlertsWindow:
    """Ventana para gestionar alertas - Versión Mejorada"""
    
    def __init__(self, parent):
        self.parent = parent
        self.alerts_manager = AlertsManager()
        
        self.window = tk.Toplevel(parent)
        self.window.title("🚨 Centro de Alertas - Sistema de Gestión")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
        self.load_alerts()
        
        # Auto-refresh cada 30 segundos
        self.auto_refresh()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"1000x700+{x}+{y}")
    
    def create_interface(self):
        # Header mejorado
        header = tk.Frame(self.window, bg='#e74c3c', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#e74c3c')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(header_content, text="🚨 Centro de Alertas",
                              font=('Arial', 18, 'bold'),
                              bg='#e74c3c', fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Contador de alertas
        self.alert_count_label = tk.Label(header_content, text="",
                                         font=('Arial', 14, 'bold'),
                                         bg='#e74c3c', fg='white')
        self.alert_count_label.pack(side=tk.RIGHT)
        
        # Panel de resumen
        self.create_summary_panel()
        
        # Lista de alertas
        self.create_alerts_list()
        
        # Botones de acción
        self.create_action_buttons()
    
    def create_summary_panel(self):
        """Crear panel de resumen mejorado"""
        summary_frame = tk.Frame(self.window, bg='#f8f9fa')
        summary_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(summary_frame, text="📊 Resumen de Alertas",
                font=('Arial', 14, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')
        
        # Cards de resumen
        self.summary_cards_frame = tk.Frame(summary_frame, bg='#f8f9fa')
        self.summary_cards_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.create_summary_cards()
    
    def create_summary_cards(self):
        """Crear cards de resumen mejoradas"""
        # Limpiar cards existentes
        for widget in self.summary_cards_frame.winfo_children():
            widget.destroy()
        
        summary = self.alerts_manager.get_alerts_summary()
        
        cards_data = [
            ("🚨 CRÍTICAS", summary.get('critical', 0), "#c0392b"),
            ("⚠️ ALTAS", summary.get('high', 0), "#e67e22"),
            ("📊 MEDIAS", summary.get('medium', 0), "#f39c12"),
            ("📈 TOTAL", summary.get('total_active', 0), "#7f8c8d")
        ]
        
        for i, (label, count, color) in enumerate(cards_data):
            card = tk.Frame(self.summary_cards_frame, bg=color, relief='solid', bd=1)
            card.grid(row=0, column=i, sticky='ew', padx=5)
            
            count_label = tk.Label(card, text=str(count),
                                  font=('Arial', 20, 'bold'),
                                  bg=color, fg='white')
            count_label.pack(pady=(15, 5))
            
            label_widget = tk.Label(card, text=label,
                                   font=('Arial', 10, 'bold'),
                                   bg=color, fg='white')
            label_widget.pack(pady=(0, 15))
        
        # Configurar grid
        for i in range(4):
            self.summary_cards_frame.grid_columnconfigure(i, weight=1)
    
    def create_alerts_list(self):
        """Crear lista de alertas mejorada"""
        list_frame = tk.Frame(self.window, bg='#f8f9fa')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título de la lista
        tk.Label(list_frame, text="📋 Alertas Activas",
                                  font=('Arial', 12, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w', pady=(0, 10))
        
        # Frame para la tabla
        table_frame = tk.Frame(list_frame, bg='white', relief='solid', bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear TreeView
        columns = ('ID', 'Tipo', 'Severidad', 'Título', 'Sistema', 'Fecha')
        self.alerts_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.alerts_tree.heading('ID', text='ID')
        self.alerts_tree.heading('Tipo', text='Tipo')
        self.alerts_tree.heading('Severidad', text='Severidad')
        self.alerts_tree.heading('Título', text='Título')
        self.alerts_tree.heading('Sistema', text='Sistema')
        self.alerts_tree.heading('Fecha', text='Fecha')
        
        # Configurar anchos
        self.alerts_tree.column('ID', width=50)
        self.alerts_tree.column('Tipo', width=100)
        self.alerts_tree.column('Severidad', width=80)
        self.alerts_tree.column('Título', width=300)
        self.alerts_tree.column('Sistema', width=100)
        self.alerts_tree.column('Fecha', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.alerts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Eventos
        self.alerts_tree.bind('<Double-1>', self.view_alert_details)
    
    def create_action_buttons(self):
        """Crear botones de acción mejorados"""
        buttons_frame = tk.Frame(self.window, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # Botones
        buttons = [
            ("🔄 Actualizar", self.refresh_alerts, "#3498db"),
            ("✅ Resolver Seleccionada", self.resolve_selected_alert, "#27ae60"),
            ("📊 Generar Reporte", self.generate_alerts_report, "#f39c12"),
            ("🧹 Limpiar Resueltas", self.cleanup_resolved_alerts, "#e74c3c")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(buttons_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', bd=0, padx=15, pady=8, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_alerts(self):
        """Cargar alertas en la tabla"""
        try:
            # Limpiar tabla
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # Obtener alertas
            alerts = self.alerts_manager.get_active_alerts()
            
            # Insertar en tabla
            for alert in alerts:
                alert_id, alert_type, severity, title, message, source_system, source_id, created_at, data_json = alert
                
                # Formatear fecha
                fecha = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                
                # Color según severidad
                tags = (severity.lower(),)
                
                self.alerts_tree.insert('', 'end', values=(
                    alert_id, alert_type, severity, title, source_system, fecha
                ), tags=tags)
            
            # Actualizar contador
            self.alert_count_label.config(text=f"{len(alerts)} alertas activas")
            
            # Actualizar cards de resumen
            self.create_summary_cards()
            
        except Exception as e:
            print(f"Error cargando alertas: {e}")
    
    def refresh_alerts(self):
        """Actualizar alertas manualmente"""
        self.load_alerts()
        messagebox.showinfo("Actualizado", "Alertas actualizadas correctamente")
    
    def resolve_selected_alert(self):
        """Resolver alerta seleccionada"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor seleccione una alerta para resolver")
            return
        
        item = self.alerts_tree.item(selection[0])
        alert_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea resolver esta alerta?"):
            self.alerts_manager.resolve_alert(alert_id)
            self.load_alerts()
            messagebox.showinfo("Resuelta", "Alerta resuelta correctamente")
    
    def view_alert_details(self, event=None):
        """Ver detalles de la alerta"""
        selection = self.alerts_tree.selection()
        if not selection:
            return
        
        item = self.alerts_tree.item(selection[0])
        alert_id = item['values'][0]
        
        # Obtener detalles completos
        alerts = self.alerts_manager.get_active_alerts()
        alert_details = None
        
        for alert in alerts:
            if alert[0] == alert_id:
                alert_details = alert
                break
        
        if alert_details:
            alert_id, alert_type, severity, title, message, source_system, source_id, created_at, data_json = alert_details
            
            details_window = tk.Toplevel(self.window)
            details_window.title(f"Detalles de Alerta #{alert_id}")
            details_window.geometry("500x400")
            details_window.configure(bg='#f8f9fa')
            
            # Centrar ventana
            details_window.update_idletasks()
            x = (details_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (details_window.winfo_screenheight() // 2) - (400 // 2)
            details_window.geometry(f"500x400+{x}+{y}")
            
            # Contenido
            content = tk.Frame(details_window, bg='#f8f9fa', padx=20, pady=20)
            content.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            fields = [
                ("ID:", str(alert_id)),
                ("Tipo:", alert_type),
                ("Severidad:", severity),
                ("Título:", title),
                ("Mensaje:", message),
                ("Sistema:", source_system),
                ("ID Fuente:", source_id or "N/A"),
                ("Fecha:", created_at)
            ]
            
            for i, (label, value) in enumerate(fields):
                tk.Label(content, text=label, font=('Arial', 10, 'bold'),
                        bg='#f8f9fa', fg='#2c3e50').grid(row=i, column=0, sticky='w', pady=2)
                tk.Label(content, text=value, font=('Arial', 10),
                        bg='#f8f9fa', fg='#34495e').grid(row=i, column=1, sticky='w', pady=2, padx=(10, 0))
            
            # Botón cerrar
            tk.Button(content, text="Cerrar", command=details_window.destroy,
                     bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                     relief='flat', padx=20, pady=5).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def generate_alerts_report(self):
        """Generar reporte de alertas"""
        try:
            summary = self.alerts_manager.get_alerts_summary()
            alerts = self.alerts_manager.get_active_alerts()
            
            # Crear contenido del reporte
            report_content = "REPORTE DE ALERTAS DEL SISTEMA\n"
            report_content += "=" * 50 + "\n\n"
            report_content += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            report_content += f"RESUMEN:\n"
            report_content += f"- Alertas Críticas: {summary.get('critical', 0)}\n"
            report_content += f"- Alertas Altas: {summary.get('high', 0)}\n"
            report_content += f"- Alertas Medias: {summary.get('medium', 0)}\n"
            report_content += f"- Total Activas: {summary.get('total_active', 0)}\n\n"
            
            if alerts:
                report_content += f"DETALLES DE ALERTAS:\n"
                report_content += "-" * 30 + "\n"
                
                for alert in alerts:
                    alert_id, alert_type, severity, title, message, source_system, source_id, created_at, data_json = alert
                    report_content += f"ID: {alert_id} | Tipo: {alert_type} | Severidad: {severity}\n"
                    report_content += f"Título: {title}\n"
                    report_content += f"Sistema: {source_system} | Fecha: {created_at}\n"
                    report_content += f"Mensaje: {message}\n"
                    report_content += "-" * 30 + "\n"
            
            # Guardar reporte
            file_path = filedialog.asksaveasfilename(
                title="Guardar Reporte de Alertas",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                messagebox.showinfo("Reporte Generado", 
                                  f"Reporte guardado exitosamente en:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def cleanup_resolved_alerts(self):
        """Limpiar alertas resueltas"""
        if messagebox.askyesno("Confirmar Limpieza", 
                              "¿Está seguro de que desea limpiar todas las alertas resueltas?\n\nEsta acción no se puede deshacer."):
            try:
                # Ejecutar limpieza
                self.alerts_manager.cleanup_old_alerts()
                messagebox.showinfo("Limpieza Exitosa", "Alertas resueltas limpiadas correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error en limpieza: {e}")
    
    def auto_refresh(self):
        """Auto-refresh cada 30 segundos"""
        self.load_alerts()
        self.window.after(30000, self.auto_refresh)

def abrir_centro_alertas(parent):
    """Función para abrir el centro de alertas"""
    try:
        AlertsWindow(parent)
    except Exception as e:
        messagebox.showerror("Error", f"Error abriendo centro de alertas: {e}")
        print(f"Error abriendo centro de alertas: {e}")