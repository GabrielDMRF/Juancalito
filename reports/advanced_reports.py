# src/reports/advanced_reports.py
"""
Sistema de Reportes Avanzados
Genera reportes detallados para todos los módulos del sistema
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class AdvancedReportsSystem:
    """Sistema avanzado de reportes para todos los módulos"""
    
    def __init__(self):
        self.reports_dir = Path('reports')
        self.reports_dir.mkdir(exist_ok=True)
        
        self.db_paths = {
            'personal': 'database/gestion_personal.db',
            'quimicos': 'database/inventario_quimicos_avanzado.db', 
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
    
    def generate_personal_report(self, export_format='excel'):
        """Generar reporte completo de personal"""
        try:
            if not os.path.exists(self.db_paths['personal']):
                return {'success': False, 'error': 'Base de datos de personal no encontrada'}
            
            conn = sqlite3.connect(self.db_paths['personal'])
            
            # Consultas para el reporte
            queries = {
                'empleados': """
                    SELECT id, nombre_completo, cedula, telefono, email, 
                           area_trabajo, cargo, salario_base, estado,
                           fecha_creacion
                    FROM empleados 
                    ORDER BY nombre_completo
                """,
                'contratos': """
                    SELECT c.numero_contrato, e.nombre_completo, c.tipo_contrato,
                           c.fecha_inicio, c.fecha_fin, c.salario_base, c.estado
                    FROM contratos c
                    JOIN empleados e ON c.empleado_id = e.id
                    ORDER BY c.fecha_creacion DESC
                """,
                'estadisticas': """
                    SELECT 
                        COUNT(*) as total_empleados,
                        SUM(CASE WHEN estado = 1 THEN 1 ELSE 0 END) as activos,
                        SUM(CASE WHEN estado = 0 THEN 1 ELSE 0 END) as inactivos,
                        COUNT(DISTINCT area_trabajo) as areas,
                        AVG(salario_base) as salario_promedio
                    FROM empleados
                """
            }
            
            # Ejecutar consultas y crear DataFrames
            data = {}
            for name, query in queries.items():
                data[name] = pd.read_sql_query(query, conn)
            
            conn.close()
            
            # Generar archivo según formato
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == 'excel':
                filename = f'reporte_personal_{timestamp}.xlsx'
                filepath = self.reports_dir / filename
                
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    data['empleados'].to_excel(writer, sheet_name='Empleados', index=False)
                    data['contratos'].to_excel(writer, sheet_name='Contratos', index=False)
                    data['estadisticas'].to_excel(writer, sheet_name='Estadisticas', index=False)
                    
                    # Hoja de resumen
                    resumen = self.create_personal_summary(data)
                    resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            elif export_format == 'csv':
                filename = f'reporte_personal_{timestamp}.csv'
                filepath = self.reports_dir / filename
                data['empleados'].to_csv(filepath, index=False, encoding='utf-8')
            
            return {
                'success': True,
                'filepath': str(filepath),
                'records': len(data['empleados']),
                'message': f'Reporte generado: {filename}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_inventory_report(self, inventory_type='all', export_format='excel'):
        """Generar reporte de inventarios"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_inventario_{inventory_type}_{timestamp}.xlsx'
            filepath = self.reports_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Reporte por tipo de inventario
                inventory_types = ['quimicos', 'almacen', 'poscosecha'] if inventory_type == 'all' else [inventory_type]
                
                total_products = 0
                
                for inv_type in inventory_types:
                    if os.path.exists(self.db_paths[inv_type]):
                        conn = sqlite3.connect(self.db_paths[inv_type])
                        
                        # Query específica según tipo
                        if inv_type == 'quimicos':
                            query = """
                                SELECT codigo, clase, nombre, saldo_real as saldo, unidad,
                                       valor_unitario, ubicacion, proveedor, nivel_peligrosidad,
                                       fecha_vencimiento, (saldo_real * valor_unitario) as valor_total
                                FROM productos_quimicos 
                                WHERE activo = 1
                                ORDER BY clase, codigo
                            """
                        elif inv_type == 'almacen':
                            query = """
                                SELECT codigo, nombre, saldo, unidad, valor_unitario,
                                       stock_minimo, ubicacion, proveedor,
                                       (saldo * valor_unitario) as valor_total
                                FROM productos_almacen
                                ORDER BY codigo
                            """
                        else:  # poscosecha
                            query = """
                                SELECT codigo, categoria, nombre, saldo, unidad,
                                       valor_unitario, stock_minimo, ubicacion, 
                                       proveedor, tipo_producto,
                                       (saldo * valor_unitario) as valor_total
                                FROM productos_poscosecha
                                ORDER BY categoria, codigo
                            """
                        
                        df = pd.read_sql_query(query, conn)
                        df.to_excel(writer, sheet_name=inv_type.title(), index=False)
                        total_products += len(df)
                        
                        conn.close()
                
                # Hoja de resumen general
                resumen_general = self.create_inventory_summary()
                resumen_general.to_excel(writer, sheet_name='Resumen_General', index=False)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'total_products': total_products,
                'message': f'Reporte de inventario generado: {filename}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_financial_report(self):
        """Generar reporte financiero"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_financiero_{timestamp}.xlsx'
            filepath = self.reports_dir / filename
            
            financial_data = {
                'valoracion_inventarios': self.get_inventory_valuations(),
                'costos_personal': self.get_personnel_costs(),
                'resumen_financiero': self.get_financial_summary()
            }
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, data in financial_data.items():
                    if isinstance(data, pd.DataFrame):
                        data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'message': f'Reporte financiero generado: {filename}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_personal_summary(self, data):
        """Crear resumen de personal"""
        stats = data['estadisticas'].iloc[0]
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total Empleados', int(stats['total_empleados'])],
            ['Empleados Activos', int(stats['activos'])],
            ['Empleados Inactivos', int(stats['inactivos'])],
            ['Áreas de Trabajo', int(stats['areas'])],
            ['Salario Promedio', f"${stats['salario_promedio']:,.0f}" if stats['salario_promedio'] else 'N/A'],
            ['Fecha Reporte', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
        ]
        
        return pd.DataFrame(summary_data)
    
    def create_inventory_summary(self):
        """Crear resumen de inventarios"""
        summary_data = []
        
        for inv_type in ['quimicos', 'almacen', 'poscosecha']:
            if os.path.exists(self.db_paths[inv_type]):
                conn = sqlite3.connect(self.db_paths[inv_type])
                cursor = conn.cursor()
                
                if inv_type == 'quimicos':
                    cursor.execute("SELECT COUNT(*), SUM(saldo_real * valor_unitario) FROM productos_quimicos WHERE activo = 1")
                elif inv_type == 'almacen':
                    cursor.execute("SELECT COUNT(*), SUM(saldo * valor_unitario) FROM productos_almacen")
                else:
                    cursor.execute("SELECT COUNT(*), SUM(saldo * valor_unitario) FROM productos_poscosecha")
                
                count, value = cursor.fetchone()
                summary_data.append([inv_type.title(), count or 0, f"${value:,.0f}" if value else "$0"])
                conn.close()
        
        return pd.DataFrame(summary_data, columns=['Sistema', 'Productos', 'Valor Total'])
    
    def get_inventory_valuations(self):
        """Obtener valoraciones de inventarios"""
        valuations = []
        
        for inv_type in ['quimicos', 'almacen', 'poscosecha']:
            if os.path.exists(self.db_paths[inv_type]):
                conn = sqlite3.connect(self.db_paths[inv_type])
                
                if inv_type == 'quimicos':
                    query = """
                        SELECT clase as categoria, COUNT(*) as productos,
                               SUM(saldo_real) as stock_total,
                               SUM(saldo_real * valor_unitario) as valor_total
                        FROM productos_quimicos 
                        WHERE activo = 1
                        GROUP BY clase
                    """
                elif inv_type == 'almacen':
                    query = """
                        SELECT 'ALMACEN' as categoria, COUNT(*) as productos,
                               SUM(saldo) as stock_total,
                               SUM(saldo * valor_unitario) as valor_total
                        FROM productos_almacen
                    """
                else:
                    query = """
                        SELECT categoria, COUNT(*) as productos,
                               SUM(saldo) as stock_total,
                               SUM(saldo * valor_unitario) as valor_total
                        FROM productos_poscosecha
                        GROUP BY categoria
                    """
                
                df = pd.read_sql_query(query, conn)
                df['sistema'] = inv_type.title()
                valuations.append(df)
                conn.close()
        
        if valuations:
            return pd.concat(valuations, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_personnel_costs(self):
        """Obtener costos de personal"""
        if not os.path.exists(self.db_paths['personal']):
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_paths['personal'])
        query = """
            SELECT area_trabajo as area, 
                   COUNT(*) as empleados,
                   SUM(salario_base) as nomina_mensual,
                   AVG(salario_base) as salario_promedio
            FROM empleados 
            WHERE estado = 1 AND salario_base > 0
            GROUP BY area_trabajo
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_financial_summary(self):
        """Obtener resumen financiero"""
        summary = []
        
        # Valor total inventarios
        total_inventory = 0
        for inv_type in ['quimicos', 'almacen', 'poscosecha']:
            if os.path.exists(self.db_paths[inv_type]):
                conn = sqlite3.connect(self.db_paths[inv_type])
                cursor = conn.cursor()
                
                if inv_type == 'quimicos':
                    cursor.execute("SELECT SUM(saldo_real * valor_unitario) FROM productos_quimicos WHERE activo = 1")
                elif inv_type == 'almacen':
                    cursor.execute("SELECT SUM(saldo * valor_unitario) FROM productos_almacen")
                else:
                    cursor.execute("SELECT SUM(saldo * valor_unitario) FROM productos_poscosecha")
                
                value = cursor.fetchone()[0] or 0
                total_inventory += value
                conn.close()
        
        # Costo nómina mensual
        total_payroll = 0
        if os.path.exists(self.db_paths['personal']):
            conn = sqlite3.connect(self.db_paths['personal'])
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(salario_base) FROM empleados WHERE estado = 1")
            total_payroll = cursor.fetchone()[0] or 0
            conn.close()
        
        summary_data = [
            ['Concepto', 'Valor'],
            ['Valor Total Inventarios', f"${total_inventory:,.0f}"],
            ['Nómina Mensual', f"${total_payroll:,.0f}"],
            ['Nómina Anual Proyectada', f"${total_payroll * 12:,.0f}"],
            ['Relación Inventario/Nómina', f"{total_inventory / (total_payroll * 12) if total_payroll > 0 else 0:.2f}"],
            ['Fecha Análisis', datetime.now().strftime('%d/%m/%Y')]
        ]
        
        return pd.DataFrame(summary_data)


class ReportsWindow:
    """Ventana para generar reportes"""
    
    def __init__(self, parent):
        self.parent = parent
        self.reports_system = AdvancedReportsSystem()
        
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Centro de Reportes Avanzados")
        self.window.geometry("600x500")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
    
    def create_interface(self):
        # Header
        header = tk.Frame(self.window, bg='#2c3e50', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="📊 Centro de Reportes Avanzados",
                              font=('Arial', 16, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(expand=True)
        
        # Contenido principal
        content = tk.Frame(self.window, bg='#f8f9fa')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Secciones de reportes
        self.create_reports_sections(content)
    
    def create_reports_sections(self, parent):
        # Reportes de Personal
        personal_frame = tk.LabelFrame(parent, text="📋 Reportes de Personal",
                                      font=('Arial', 12, 'bold'),
                                      bg='#f8f9fa', fg='#2c3e50', padx=15, pady=10)
        personal_frame.pack(fill=tk.X, pady=(0, 15))
        
        personal_btn = tk.Button(personal_frame, text="Generar Reporte de Personal",
                               command=self.generate_personal_report,
                               bg='#8e44ad', fg='white', font=('Arial', 10, 'bold'),
                               relief='flat', bd=0, pady=8, cursor='hand2')
        personal_btn.pack(fill=tk.X, pady=5)
        
        # Reportes de Inventario
        inventory_frame = tk.LabelFrame(parent, text="📦 Reportes de Inventario",
                                       font=('Arial', 12, 'bold'),
                                       bg='#f8f9fa', fg='#2c3e50', padx=15, pady=10)
        inventory_frame.pack(fill=tk.X, pady=(0, 15))
        
        inv_buttons = [
            ("Reporte Completo de Inventarios", lambda: self.generate_inventory_report('all')),
            ("Reporte de Químicos", lambda: self.generate_inventory_report('quimicos')),
            ("Reporte de Almacén", lambda: self.generate_inventory_report('almacen')),
            ("Reporte de Poscosecha", lambda: self.generate_inventory_report('poscosecha'))
        ]
        
        for text, command in inv_buttons:
            btn = tk.Button(inventory_frame, text=text, command=command,
                           bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', bd=0, pady=6, cursor='hand2')
            btn.pack(fill=tk.X, pady=2)
        
        # Reportes Financieros
        financial_frame = tk.LabelFrame(parent, text="💰 Reportes Financieros",
                                       font=('Arial', 12, 'bold'),
                                       bg='#f8f9fa', fg='#2c3e50', padx=15, pady=10)
        financial_frame.pack(fill=tk.X, pady=(0, 15))
        
        financial_btn = tk.Button(financial_frame, text="Generar Reporte Financiero",
                                command=self.generate_financial_report,
                                bg='#e67e22', fg='white', font=('Arial', 10, 'bold'),
                                relief='flat', bd=0, pady=8, cursor='hand2')
        financial_btn.pack(fill=tk.X, pady=5)
        
        # Botones de acción
        actions_frame = tk.Frame(parent, bg='#f8f9fa')
        actions_frame.pack(fill=tk.X, pady=(15, 0))
        
        close_btn = tk.Button(actions_frame, text="❌ Cerrar",
                             command=self.window.destroy,
                             bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        close_btn.pack(side=tk.RIGHT)
        
        open_dir_btn = tk.Button(actions_frame, text="📁 Abrir Carpeta Reportes",
                                command=self.open_reports_directory,
                                bg='#3498db', fg='white', font=('Arial', 11, 'bold'),
                                relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        open_dir_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def generate_personal_report(self):
        """Generar reporte de personal"""
        try:
            result = self.reports_system.generate_personal_report()
            if result['success']:
                messagebox.showinfo("Éxito", 
                                   f"{result['message']}\n"
                                   f"Registros: {result['records']}\n"
                                   f"Archivo: {result['filepath']}")
            else:
                messagebox.showerror("Error", result['error'])
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def generate_inventory_report(self, inv_type):
        """Generar reporte de inventario"""
        try:
            result = self.reports_system.generate_inventory_report(inv_type)
            if result['success']:
                messagebox.showinfo("Éxito",
                                   f"{result['message']}\n"
                                   f"Productos: {result['total_products']}\n"
                                   f"Archivo: {result['filepath']}")
            else:
                messagebox.showerror("Error", result['error'])
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def generate_financial_report(self):
        """Generar reporte financiero"""
        try:
            result = self.reports_system.generate_financial_report()
            if result['success']:
                messagebox.showinfo("Éxito",
                                   f"{result['message']}\n"
                                   f"Archivo: {result['filepath']}")
            else:
                messagebox.showerror("Error", result['error'])
        except Exception as e:
            messagebox.showerror("Error", f"Error generando reporte: {e}")
    
    def open_reports_directory(self):
        """Abrir directorio de reportes"""
        import subprocess
        import platform
        
        reports_path = Path('reports').resolve()
        
        if platform.system() == 'Windows':
            subprocess.run(['explorer', str(reports_path)])
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', str(reports_path)])
        else:  # Linux
            subprocess.run(['xdg-open', str(reports_path)])

# Función para integrar en main_window.py
def abrir_centro_reportes(parent):
    """Función para abrir centro de reportes desde main_window"""
    ReportsWindow(parent)