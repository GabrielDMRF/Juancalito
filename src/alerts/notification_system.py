# src/alerts/notification_system.py
"""
Sistema de Alertas y Notificaciones
Monitorea el sistema y genera alertas automáticas
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os
import threading
import time
import json

class AlertsManager:
    """Gestor central de alertas del sistema"""
    
    def __init__(self):
        self.db_paths = {
            'personal': 'database/gestion_personal.db',
            'quimicos': 'database/inventario_quimicos.db',
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
        
        self.alerts_db = 'database/alerts_system.db'
        self.setup_alerts_database()
        
        # Configuración de alertas
        self.alert_config = {
            'stock_critico_threshold': 10,
            'vencimiento_dias_alerta': 30,
            'check_interval_minutes': 30,
            'enable_notifications': True
        }
        
        # Lista de alertas activas
        self.active_alerts = []
        
        # Iniciar monitoreo automático
        self.start_monitoring()
    
    def setup_alerts_database(self):
        """Configurar base de datos de alertas"""
        os.makedirs('database', exist_ok=True)
        
        conn = sqlite3.connect(self.alerts_db)
        cursor = conn.cursor()
        
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
                data_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_monitoring(self):
        """Iniciar monitoreo automático en hilo separado"""
        if self.alert_config['enable_notifications']:
            monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            monitor_thread.start()
            print("[OK] Sistema de alertas iniciado")
    
    def monitoring_loop(self):
        """Bucle principal de monitoreo"""
        while True:
            try:
                # Verificar todas las condiciones de alerta
                self.check_stock_alerts()
                self.check_expiration_alerts()
                self.check_contract_alerts()
                self.check_system_health()
                
                # Esperar antes del próximo check
                time.sleep(self.alert_config['check_interval_minutes'] * 60)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
                time.sleep(300)  # Esperar 5 minutos en caso de error
    
    def check_stock_alerts(self):
        """Verificar alertas de stock crítico"""
        try:
            for system in ['quimicos', 'almacen', 'poscosecha']:
                if os.path.exists(self.db_paths[system]):
                    conn = sqlite3.connect(self.db_paths[system])
                    cursor = conn.cursor()
                    
                    if system == 'quimicos':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, clase
                            FROM productos_quimicos 
                            WHERE saldo <= ?
                        """, (self.alert_config['stock_critico_threshold'],))
                    elif system == 'almacen':
                        cursor.execute("""
                            SELECT codigo, nombre, saldo, stock_minimo
                            FROM productos_almacen 
                            WHERE saldo <= stock_minimo OR saldo <= ?
                        """, (self.alert_config['stock_critico_threshold'],))
                    else:  # poscosecha
                        # Verificar si la tabla existe
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos_poscosecha'")
                        if cursor.fetchone():
                            cursor.execute("""
                                SELECT codigo, nombre, saldo, stock_minimo
                                FROM productos_poscosecha 
                                WHERE saldo <= stock_minimo OR saldo <= ?
                            """, (self.alert_config['stock_critico_threshold'],))
                        else:
                            continue  # Saltar si la tabla no existe
                    
                    critical_products = cursor.fetchall()
                    
                    for product in critical_products:
                        self.create_alert(
                            alert_type='STOCK_CRITICO',
                            severity='HIGH',
                            title=f'Stock Crítico - {system.title()}',
                            message=f'Producto {product[0]} ({product[1]}) tiene stock crítico: {product[2]} unidades',
                            source_system=system,
                            source_id=product[0],
                            data={'product_code': product[0], 'current_stock': product[2]}
                        )
                    
                    conn.close()
                    
        except Exception as e:
            print(f"Error verificando stock: {e}")
    
    def check_expiration_alerts(self):
        """Verificar alertas de vencimiento"""
        try:
            if os.path.exists(self.db_paths['quimicos']):
                conn = sqlite3.connect(self.db_paths['quimicos'])
                cursor = conn.cursor()
                
                # Productos que vencen en los próximos N días
                cutoff_date = (datetime.now() + timedelta(days=self.alert_config['vencimiento_dias_alerta'])).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT codigo, nombre, fecha_vencimiento, clase
                    FROM productos_quimicos 
                    WHERE fecha_vencimiento <= ? AND fecha_vencimiento IS NOT NULL
                """, (cutoff_date,))
                
                expiring_products = cursor.fetchall()
                
                for product in expiring_products:
                    exp_date = datetime.strptime(product[2], '%Y-%m-%d')
                    days_until_exp = (exp_date - datetime.now()).days
                    
                    severity = 'CRITICAL' if days_until_exp <= 7 else 'HIGH'
                    
                    self.create_alert(
                        alert_type='VENCIMIENTO',
                        severity=severity,
                        title=f'Producto Próximo a Vencer',
                        message=f'Químico {product[0]} ({product[1]}) vence en {days_until_exp} días ({product[2]})',
                        source_system='quimicos',
                        source_id=product[0],
                        data={'expiration_date': product[2], 'days_until_exp': days_until_exp}
                    )
                
                conn.close()
                
        except Exception as e:
            print(f"Error verificando vencimientos: {e}")
    
    def check_contract_alerts(self):
        """Verificar alertas de contratos"""
        try:
            if os.path.exists(self.db_paths['personal']):
                conn = sqlite3.connect(self.db_paths['personal'])
                cursor = conn.cursor()
                
                # Contratos que vencen pronto
                cutoff_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT c.numero_contrato, e.nombre_completo, c.fecha_fin, tc.nombre as tipo_contrato
                    FROM contratos c
                    JOIN empleados e ON c.empleado_id = e.id
                    LEFT JOIN tipos_contrato tc ON c.tipo_contrato_id = tc.id
                    WHERE c.fecha_fin <= ? AND c.fecha_fin IS NOT NULL AND c.estado = 'activo'
                """, (cutoff_date,))
                
                expiring_contracts = cursor.fetchall()
                
                for contract in expiring_contracts:
                    end_date = datetime.strptime(contract[2], '%Y-%m-%d')
                    days_until_end = (end_date - datetime.now()).days
                    
                    severity = 'CRITICAL' if days_until_end <= 7 else 'HIGH'
                    
                    self.create_alert(
                        alert_type='CONTRATO_VENCE',
                        severity=severity,
                        title=f'Contrato Próximo a Vencer',
                        message=f'Contrato {contract[0]} de {contract[1]} vence en {days_until_end} días',
                        source_system='personal',
                        source_id=contract[0],
                        data={'employee': contract[1], 'days_until_end': days_until_end}
                    )
                
                conn.close()
                
        except Exception as e:
            print(f"Error verificando contratos: {e}")
    
    def check_system_health(self):
        """Verificar salud general del sistema"""
        try:
            # Verificar acceso a bases de datos
            for system, db_path in self.db_paths.items():
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        conn.close()
                    except Exception:
                        self.create_alert(
                            alert_type='SISTEMA',
                            severity='CRITICAL',
                            title=f'Error de Base de Datos',
                            message=f'No se puede acceder a la base de datos de {system}',
                            source_system='system',
                            source_id=system
                        )
                else:
                    self.create_alert(
                        alert_type='SISTEMA',
                        severity='HIGH',
                        title=f'Base de Datos No Encontrada',
                        message=f'La base de datos de {system} no existe: {db_path}',
                        source_system='system',
                        source_id=system
                    )
            
            # Verificar espacio en disco
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            
            if free_gb < 1:  # Menos de 1GB libre
                self.create_alert(
                    alert_type='SISTEMA',
                    severity='HIGH',
                    title='Espacio en Disco Bajo',
                    message=f'Quedan solo {free_gb}GB libres en disco',
                    source_system='system',
                    source_id='disk_space',
                    data={'free_space_gb': free_gb}
                )
                
        except Exception as e:
            print(f"Error verificando salud del sistema: {e}")
    
    def create_alert(self, alert_type, severity, title, message, source_system, source_id=None, data=None):
        """Crear nueva alerta"""
        try:
            # Verificar si ya existe una alerta similar activa
            if self.alert_exists(alert_type, source_system, source_id):
                return
            
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, severity, title, message, source_system, source_id, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_type, severity, title, message, source_system, 
                source_id, json.dumps(data) if data else None
            ))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Agregar a lista activa
            self.active_alerts.append({
                'id': alert_id,
                'type': alert_type,
                'severity': severity,
                'title': title,
                'message': message,
                'created_at': datetime.now()
            })
            
            print(f"[ALERTA {severity}] {title}")


            
        except Exception as e:
            print(f"Error creando alerta: {e}")
    
    def alert_exists(self, alert_type, source_system, source_id):
        """Verificar si ya existe una alerta similar activa"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id FROM alerts 
                WHERE alert_type = ? AND source_system = ? AND source_id = ? 
                AND is_active = 1 AND created_at > datetime('now', '-1 hour')
            ''', (alert_type, source_system, source_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            print(f"Error verificando alerta existente: {e}")
            return False
    
    def get_active_alerts(self, limit=50):
        """Obtener alertas activas"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, alert_type, severity, title, message, source_system, 
                       created_at, data_json
                FROM alerts 
                WHERE is_active = 1 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': alert[0],
                    'type': alert[1],
                    'severity': alert[2],
                    'title': alert[3],
                    'message': alert[4],
                    'source_system': alert[5],
                    'created_at': alert[6],
                    'data': json.loads(alert[7]) if alert[7] else {}
                }
                for alert in alerts
            ]
            
        except Exception as e:
            print(f"Error obteniendo alertas: {e}")
            return []
    
    def resolve_alert(self, alert_id):
        """Marcar alerta como resuelta"""
        try:
            conn = sqlite3.connect(self.alerts_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE alerts 
                SET is_active = 0, resolved_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            # Remover de lista activa
            self.active_alerts = [a for a in self.active_alerts if a['id'] != alert_id]
            
            return True
            
        except Exception as e:
            print(f"Error resolviendo alerta: {e}")
            return False
    
    def get_alerts_summary(self):
        """Obtener resumen de alertas"""
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
            
            # Contar por tipo
            cursor.execute('''
                SELECT alert_type, COUNT(*) 
                FROM alerts 
                WHERE is_active = 1 
                GROUP BY alert_type
            ''')
            type_counts = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_active': sum(severity_counts.values()),
                'critical': severity_counts.get('CRITICAL', 0),
                'high': severity_counts.get('HIGH', 0),
                'medium': severity_counts.get('MEDIUM', 0),
                'low': severity_counts.get('LOW', 0),
                'by_type': type_counts
            }
            
        except Exception as e:
            print(f"Error obteniendo resumen: {e}")
            return {'total_active': 0}


class AlertsWindow:
    """Ventana para gestionar alertas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.alerts_manager = AlertsManager()
        
        self.window = tk.Toplevel(parent)
        self.window.title("🚨 Centro de Alertas")
        self.window.geometry("800x600")
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
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
    
    def create_interface(self):
        # Header
        header = tk.Frame(self.window, bg='#e74c3c', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#e74c3c')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(header_content, text="🚨 Centro de Alertas",
                              font=('Arial', 16, 'bold'),
                              bg='#e74c3c', fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Contador de alertas
        self.alert_count_label = tk.Label(header_content, text="",
                                         font=('Arial', 12, 'bold'),
                                         bg='#e74c3c', fg='white')
        self.alert_count_label.pack(side=tk.RIGHT)
        
        # Panel de resumen
        self.create_summary_panel()
        
        # Lista de alertas
        self.create_alerts_list()
        
        # Botones de acción
        self.create_action_buttons()
    
    def create_summary_panel(self):
        """Crear panel de resumen"""
        summary_frame = tk.Frame(self.window, bg='#f8f9fa')
        summary_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(summary_frame, text="📊 Resumen de Alertas",
                font=('Arial', 12, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').pack(anchor='w')
        
        # Cards de resumen
        self.summary_cards_frame = tk.Frame(summary_frame, bg='#f8f9fa')
        self.summary_cards_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.create_summary_cards()
    
    def create_summary_cards(self):
        """Crear cards de resumen"""
        # Limpiar cards existentes
        for widget in self.summary_cards_frame.winfo_children():
            widget.destroy()
        
        summary = self.alerts_manager.get_alerts_summary()
        
        cards_data = [
            ("CRÍTICAS", summary.get('critical', 0), "#c0392b"),
            ("ALTAS", summary.get('high', 0), "#e67e22"),
            ("MEDIAS", summary.get('medium', 0), "#f39c12"),
            ("TOTAL", summary.get('total_active', 0), "#7f8c8d")
        ]
        
        for i, (label, count, color) in enumerate(cards_data):
            card = tk.Frame(self.summary_cards_frame, bg=color, relief='solid', bd=1)
            card.grid(row=0, column=i, sticky='ew', padx=5)
            
            count_label = tk.Label(card, text=str(count),
                                  font=('Arial', 18, 'bold'),
                                  bg=color, fg='white')
            count_label.pack(pady=(10, 5))
            
            label_widget = tk.Label(card, text=label,
                                   font=('Arial', 9, 'bold'),
                                   bg=color, fg='white')
            label_widget.pack(pady=(0, 10))
        
        # Configurar grid
        for i in range(4):
            self.summary_cards_frame.grid_columnconfigure(i, weight=1)
    
    def create_alerts_list(self):
        """Crear lista de alertas"""
        list_frame = tk.LabelFrame(self.window, text="📋 Alertas Activas",
                                  font=('Arial', 12, 'bold'),
                                  bg='#f8f9fa', fg='#2c3e50', padx=15, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # TreeView para alertas
        columns = ('Severidad', 'Tipo', 'Título', 'Sistema', 'Fecha')
        self.alerts_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        column_widths = {
            'Severidad': 100, 'Tipo': 120, 'Título': 250, 'Sistema': 100, 'Fecha': 150
        }
        
        for col in columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=column_widths[col])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.alerts_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.alerts_tree.bind('<Double-1>', self.view_alert_details)
    
    def create_action_buttons(self):
        """Crear botones de acción"""
        actions_frame = tk.Frame(self.window, bg='#f8f9fa')
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        buttons = [
            ("🔄 Actualizar", self.load_alerts, "#3498db"),
            ("✅ Resolver Seleccionada", self.resolve_selected_alert, "#27ae60"),
            ("👁️ Ver Detalles", self.view_alert_details, "#f39c12"),
            ("❌ Cerrar", self.window.destroy, "#e74c3c")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(actions_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', bd=0, padx=15, pady=8, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=5)
    
    def load_alerts(self):
        """Cargar alertas en la lista"""
        try:
            # Limpiar lista
            for item in self.alerts_tree.get_children():
                self.alerts_tree.delete(item)
            
            # Obtener alertas activas
            alerts = self.alerts_manager.get_active_alerts()
            
            for alert in alerts:
                # Formatear fecha
                created_at = datetime.fromisoformat(alert['created_at'].replace('Z', '+00:00'))
                date_str = created_at.strftime('%d/%m/%Y %H:%M')
                
                # Agregar emoji según severidad
                severity_emoji = {
                    'CRITICAL': '🔴 CRÍTICA',
                    'HIGH': '🟡 ALTA',
                    'MEDIUM': '🟠 MEDIA',
                    'LOW': '🔵 BAJA'
                }
                
                severity_display = severity_emoji.get(alert['severity'], alert['severity'])
                
                self.alerts_tree.insert('', tk.END, values=(
                    severity_display,
                    alert['type'],
                    alert['title'],
                    alert['source_system'].title(),
                    date_str
                ), tags=(alert['severity'].lower(),))
            
            # Configurar colores por severidad
            self.alerts_tree.tag_configure('critical', background='#ffebee', foreground='#c62828')
            self.alerts_tree.tag_configure('high', background='#fff3e0', foreground='#ef6c00')
            self.alerts_tree.tag_configure('medium', background='#fff8e1', foreground='#f57c00')
            self.alerts_tree.tag_configure('low', background='#e3f2fd', foreground='#1976d2')
            
            # Actualizar contador
            total_alerts = len(alerts)
            self.alert_count_label.config(text=f"Total: {total_alerts} alertas")
            
            # Actualizar cards de resumen
            self.create_summary_cards()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando alertas: {e}")
    
    def resolve_selected_alert(self):
        """Resolver alerta seleccionada"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una alerta para resolver")
            return
        
        # Obtener ID de la alerta (necesitarías modificar para incluir el ID)
        if messagebox.askyesno("Confirmar", "¿Marcar esta alerta como resuelta?"):
            # Aquí implementarías la resolución
            messagebox.showinfo("Éxito", "Alerta marcada como resuelta")
            self.load_alerts()
    
    def view_alert_details(self, event=None):
        """Ver detalles de la alerta"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una alerta")
            return
        
        item = self.alerts_tree.item(selection[0])
        values = item['values']
        
        details = f"""
DETALLES DE LA ALERTA

Severidad: {values[0]}
Tipo: {values[1]}
Título: {values[2]}
Sistema: {values[3]}
Fecha: {values[4]}

Esta funcionalidad se expandirá con más detalles específicos de cada alerta.
"""
        
        messagebox.showinfo("Detalles de Alerta", details)
    
    def auto_refresh(self):
        """Auto-refrescar alertas cada 30 segundos"""
        self.load_alerts()
        self.window.after(30000, self.auto_refresh)  # 30 segundos

# Instancia global del gestor de alertas
alerts_manager = AlertsManager()

# Función para integrar en main_window.py
def abrir_centro_alertas(parent):
    """Función para abrir centro de alertas desde main_window"""
    AlertsWindow(parent)