#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Movimientos de Inventario
Maneja entradas y salidas de productos para todos los sistemas
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import os

class MovimientoInventarioWindow:
    """Ventana para registrar movimientos de inventario"""
    
    def __init__(self, parent, inventory_window, tipo, sistema):
        self.parent = parent
        self.inventory_window = inventory_window
        self.tipo = tipo  # 'entrada' o 'salida'
        self.sistema = sistema  # 'quimicos', 'almacen' o 'poscosecha'
        
        # Configurar base de datos
        self.setup_database()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.setup_window()
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar productos
        self.load_products()
    
    def setup_database(self):
        """Configurar conexión a base de datos"""
        db_paths = {
            'quimicos': 'database/inventario_quimicos_avanzado.db',
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
        
        self.db_path = db_paths.get(self.sistema)
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showerror("Error", f"Base de datos de {self.sistema} no encontrada")
            self.window.destroy()
            return
        
        # Crear tabla de movimientos si no existe
        self.create_movements_table()
    
    def create_movements_table(self):
        """Crear tabla de movimientos si no existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_name = f"movimientos_{self.sistema}"
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_codigo TEXT NOT NULL,
                producto_nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha DATE NOT NULL,
                hora TIME DEFAULT CURRENT_TIME,
                saldo_anterior INTEGER,
                saldo_nuevo INTEGER,
                responsable TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_codigo) REFERENCES productos_{self.sistema} (codigo)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_window(self):
        """Configurar ventana"""
        # Título según tipo y sistema
        icons = {'entrada': '📥', 'salida': '📤'}
        colors = {'entrada': '#27ae60', 'salida': '#e74c3c'}
        sistemas_text = {
            'quimicos': 'Químicos',
            'almacen': 'Almacén',
            'poscosecha': 'Poscosecha'
        }
        
        title = f"{icons.get(self.tipo, '')} {self.tipo.title()} - {sistemas_text.get(self.sistema, '')}"
        self.window.title(title)
        self.window.geometry("500x400")
        self.window.configure(bg='#f8f9fa')
        
        # Color del header según tipo
        self.header_color = colors.get(self.tipo, '#3498db')
        
        # Centrar ventana
        self.center_window()
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def center_window(self):
        """Centrar ventana"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz principal"""
        # Header
        self.create_header()
        
        # Formulario
        self.create_form()
        
        # Botones
        self.create_buttons()
    
    def create_header(self):
        """Crear header"""
        header = tk.Frame(self.window, bg=self.header_color, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.header_color)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Título
        title_text = f"Registrar {self.tipo.title()}"
        title_label = tk.Label(header_content, text=title_text,
                             font=('Segoe UI', 16, 'bold'),
                             bg=self.header_color, fg='white')
        title_label.pack()
        
        # Subtítulo con sistema
        subtitle_text = f"Sistema: {self.sistema.title()}"
        subtitle_label = tk.Label(header_content, text=subtitle_text,
                                font=('Segoe UI', 10),
                                bg=self.header_color, fg='#ecf0f1')
        subtitle_label.pack()
    
    def create_form(self):
        """Crear formulario"""
        # Frame principal del formulario
        form_frame = tk.Frame(self.window, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 1. Selección de producto
        tk.Label(form_frame, text="Producto:", 
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(form_frame, textvariable=self.product_var,
                                        width=40, font=('Segoe UI', 10),
                                        state='readonly')
        self.product_combo.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky='ew')
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        # 2. Información del producto seleccionado
        info_frame = tk.LabelFrame(form_frame, text="Información del Producto",
                                  font=('Segoe UI', 9, 'bold'),
                                  bg='white', fg='#2c3e50')
        info_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky='ew')
        
        # Stock actual
        tk.Label(info_frame, text="Stock Actual:", 
                font=('Segoe UI', 9),
                bg='white', fg='#7f8c8d').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.stock_label = tk.Label(info_frame, text="--", 
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='white', fg='#2c3e50')
        self.stock_label.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Unidad
        tk.Label(info_frame, text="Unidad:", 
                font=('Segoe UI', 9),
                bg='white', fg='#7f8c8d').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        self.unit_label = tk.Label(info_frame, text="--", 
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='white', fg='#2c3e50')
        self.unit_label.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # 3. Cantidad del movimiento
        tk.Label(form_frame, text="Cantidad:", 
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        self.quantity_var = tk.StringVar()
        self.quantity_entry = tk.Entry(form_frame, textvariable=self.quantity_var,
                                     font=('Segoe UI', 11), width=20)
        self.quantity_entry.grid(row=4, column=0, pady=(0, 15), sticky='w')
        self.quantity_entry.bind('<KeyRelease>', self.validate_quantity)
        
        # Label de cantidad válida
        self.quantity_status_label = tk.Label(form_frame, text="", 
                                            font=('Segoe UI', 8),
                                            bg='white')
        self.quantity_status_label.grid(row=4, column=1, pady=(0, 15), sticky='w', padx=10)
        
        # 4. Fecha del movimiento
        tk.Label(form_frame, text="Fecha:", 
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=5, column=0, sticky='w', pady=(0, 5))
        
        date_frame = tk.Frame(form_frame, bg='white')
        date_frame.grid(row=6, column=0, columnspan=2, pady=(0, 15), sticky='w')
        
        # Fecha actual por defecto
        self.date_var = tk.StringVar(value=date.today().strftime('%d/%m/%Y'))
        self.date_entry = tk.Entry(date_frame, textvariable=self.date_var,
                                 font=('Segoe UI', 11), width=15)
        self.date_entry.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text="(DD/MM/AAAA)", 
                font=('Segoe UI', 8),
                bg='white', fg='#7f8c8d').pack(side=tk.LEFT, padx=10)
        
        # 5. Responsable
        tk.Label(form_frame, text="Responsable:", 
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=7, column=0, sticky='w', pady=(0, 5))
        
        self.responsible_var = tk.StringVar()
        self.responsible_entry = tk.Entry(form_frame, textvariable=self.responsible_var,
                                        font=('Segoe UI', 10), width=30)
        self.responsible_entry.grid(row=8, column=0, pady=(0, 15), sticky='w')
        
        # 6. Observaciones
        tk.Label(form_frame, text="Observaciones (opcional):", 
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=9, column=0, sticky='w', pady=(0, 5))
        
        self.observations_text = tk.Text(form_frame, font=('Segoe UI', 10),
                                       width=40, height=3)
        self.observations_text.grid(row=10, column=0, columnspan=2, pady=(0, 10), sticky='ew')
        
        # Configurar expansión de columnas
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
    
    def create_buttons(self):
        """Crear botones de acción"""
        button_frame = tk.Frame(self.window, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Botón registrar
        register_btn = tk.Button(button_frame, 
                               text=f"✓ Registrar {self.tipo.title()}",
                               command=self.register_movement,
                               bg=self.header_color, fg='white',
                               font=('Segoe UI', 11, 'bold'),
                               relief='flat', bd=0, padx=20, pady=10,
                               cursor='hand2')
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón cancelar
        cancel_btn = tk.Button(button_frame, text="✕ Cancelar",
                             command=self.window.destroy,
                             bg='#95a5a6', fg='white',
                             font=('Segoe UI', 11, 'bold'),
                             relief='flat', bd=0, padx=20, pady=10,
                             cursor='hand2')
        cancel_btn.pack(side=tk.LEFT)
    
    def load_products(self):
        """Cargar productos disponibles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query según sistema
            if self.sistema == 'quimicos':
                cursor.execute("""
                    SELECT codigo, nombre, saldo_real, unidad 
                    FROM productos_quimicos 
                    WHERE activo = 1 
                    ORDER BY nombre
                """)
            elif self.sistema == 'almacen':
                cursor.execute("""
                    SELECT codigo, nombre, saldo, unidad 
                    FROM productos_almacen 
                    ORDER BY nombre
                """)
            else:  # poscosecha
                cursor.execute("""
                    SELECT codigo, nombre, saldo, unidad 
                    FROM productos_poscosecha 
                    ORDER BY nombre
                """)
            
            # Crear lista de productos para combobox
            products = []
            self.products_data = {}
            
            for row in cursor.fetchall():
                codigo, nombre, saldo, unidad = row
                display_text = f"{codigo} - {nombre}"
                products.append(display_text)
                self.products_data[display_text] = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'saldo': saldo,
                    'unidad': unidad
                }
            
            self.product_combo['values'] = products
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {e}")
    
    def on_product_selected(self, event):
        """Manejar selección de producto"""
        selected = self.product_var.get()
        if selected in self.products_data:
            product_info = self.products_data[selected]
            
            # Actualizar información del producto
            self.stock_label.config(text=f"{product_info['saldo']:,}")
            self.unit_label.config(text=product_info['unidad'])
            
            # Validar cantidad si ya hay algo escrito
            self.validate_quantity()
    
    def validate_quantity(self, event=None):
        """Validar cantidad ingresada"""
        try:
            quantity = int(self.quantity_var.get())
            
            if quantity <= 0:
                self.quantity_status_label.config(
                    text="⚠ La cantidad debe ser mayor a 0",
                    fg='#e74c3c'
                )
                return False
            
            # Para salidas, verificar stock disponible
            if self.tipo == 'salida':
                selected = self.product_var.get()
                if selected in self.products_data:
                    current_stock = self.products_data[selected]['saldo']
                    if quantity > current_stock:
                        self.quantity_status_label.config(
                            text=f"⚠ Stock insuficiente (máx: {current_stock})",
                            fg='#e74c3c'
                        )
                        return False
            
            # Cantidad válida
            self.quantity_status_label.config(
                text="✓ Cantidad válida",
                fg='#27ae60'
            )
            return True
            
        except ValueError:
            if self.quantity_var.get():
                self.quantity_status_label.config(
                    text="⚠ Ingrese un número válido",
                    fg='#e74c3c'
                )
            else:
                self.quantity_status_label.config(text="")
            return False
    
    def validate_date(self, date_str):
        """Validar formato de fecha"""
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False
    
    def register_movement(self):
        """Registrar el movimiento"""
        try:
            # Validaciones
            if not self.product_var.get():
                messagebox.showerror("Error", "Seleccione un producto")
                return
            
            if not self.quantity_var.get() or not self.validate_quantity():
                messagebox.showerror("Error", "Ingrese una cantidad válida")
                self.quantity_entry.focus()
                return
            
            if not self.date_var.get() or not self.validate_date(self.date_var.get()):
                messagebox.showerror("Error", "Ingrese una fecha válida (DD/MM/AAAA)")
                self.date_entry.focus()
                return
            
            if not self.responsible_var.get().strip():
                messagebox.showerror("Error", "Ingrese el nombre del responsable")
                self.responsible_entry.focus()
                return
            
            # Obtener datos
            selected_product = self.product_var.get()
            product_info = self.products_data[selected_product]
            quantity = int(self.quantity_var.get())
            movement_date = datetime.strptime(self.date_var.get(), '%d/%m/%Y').date()
            responsible = self.responsible_var.get().strip()
            observations = self.observations_text.get('1.0', tk.END).strip()
            
            # Calcular nuevo saldo
            current_stock = product_info['saldo']
            if self.tipo == 'entrada':
                new_stock = current_stock + quantity
            else:  # salida
                new_stock = current_stock - quantity
            
            # Registrar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Registrar movimiento
            table_name = f"movimientos_{self.sistema}"
            cursor.execute(f'''
                INSERT INTO {table_name} 
                (producto_codigo, producto_nombre, tipo, cantidad, fecha, 
                 saldo_anterior, saldo_nuevo, responsable, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_info['codigo'],
                product_info['nombre'],
                self.tipo,
                quantity,
                movement_date,
                current_stock,
                new_stock,
                responsible,
                observations
            ))
            
            # 2. Actualizar saldo del producto
            if self.sistema == 'quimicos':
                cursor.execute('''
                    UPDATE productos_quimicos 
                    SET saldo_real = ? 
                    WHERE codigo = ?
                ''', (new_stock, product_info['codigo']))
            elif self.sistema == 'almacen':
                cursor.execute('''
                    UPDATE productos_almacen 
                    SET saldo = ? 
                    WHERE codigo = ?
                ''', (new_stock, product_info['codigo']))
            else:  # poscosecha
                cursor.execute('''
                    UPDATE productos_poscosecha 
                    SET saldo = ? 
                    WHERE codigo = ?
                ''', (new_stock, product_info['codigo']))
            
            conn.commit()
            conn.close()
            
            # Mensaje de éxito
            tipo_text = "Entrada" if self.tipo == 'entrada' else "Salida"
            messagebox.showinfo("Éxito", 
                f"{tipo_text} registrada exitosamente\n\n" +
                f"Producto: {product_info['nombre']}\n" +
                f"Cantidad: {quantity} {product_info['unidad']}\n" +
                f"Stock anterior: {current_stock}\n" +
                f"Stock nuevo: {new_stock}")
            
            # Actualizar tabla principal si existe
            if hasattr(self.inventory_window, 'cargar_inventario'):
                self.inventory_window.cargar_inventario()
            elif hasattr(self.inventory_window, 'load_data'):
                self.inventory_window.load_data()
            
            # Cerrar ventana
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error registrando movimiento: {e}")


class HistorialMovimientosWindow:
    """Ventana para ver historial de movimientos"""
    
    def __init__(self, parent, sistema):
        self.parent = parent
        self.sistema = sistema
        
        # Configurar base de datos
        db_paths = {
            'quimicos': 'database/inventario_quimicos_avanzado.db',
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
        self.db_path = db_paths.get(sistema)
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title(f"📊 Historial de Movimientos - {sistema.title()}")
        self.window.geometry("1000x600")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        
        # Crear interfaz
        self.create_interface()
        
        # Cargar historial
        self.load_history()
    
    def center_window(self):
        """Centrar ventana"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"1000x600+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz"""
        # Header
        header = tk.Frame(self.window, bg='#34495e', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text=f"📊 Historial de Movimientos - {self.sistema.title()}",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#34495e', fg='white')
        title_label.pack(expand=True)
        
        # Filtros
        filter_frame = tk.Frame(self.window, bg='white')
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Filtro por tipo
        tk.Label(filter_frame, text="Tipo:", bg='white').pack(side=tk.LEFT, padx=5)
        self.type_filter = ttk.Combobox(filter_frame, values=['Todos', 'entrada', 'salida'],
                                      width=15, state='readonly')
        self.type_filter.set('Todos')
        self.type_filter.pack(side=tk.LEFT, padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', lambda e: self.load_history())
        
        # Filtro por fecha
        tk.Label(filter_frame, text="Desde:", bg='white').pack(side=tk.LEFT, padx=(20, 5))
        self.date_from = tk.Entry(filter_frame, width=12)
        self.date_from.pack(side=tk.LEFT, padx=5)
        
        tk.Label(filter_frame, text="Hasta:", bg='white').pack(side=tk.LEFT, padx=5)
        self.date_to = tk.Entry(filter_frame, width=12)
        self.date_to.pack(side=tk.LEFT, padx=5)
        
        # Botón filtrar
        filter_btn = tk.Button(filter_frame, text="🔍 Filtrar",
                             command=self.load_history,
                             bg='#3498db', fg='white',
                             relief='flat', padx=15, pady=5)
        filter_btn.pack(side=tk.LEFT, padx=20)
        
        # Tabla de historial
        table_frame = tk.Frame(self.window, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # TreeView
        columns = ('Fecha', 'Hora', 'Tipo', 'Producto', 'Cantidad', 'Stock Ant.', 
                  'Stock Nuevo', 'Responsable', 'Observaciones')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        column_widths = {
            'Fecha': 80, 'Hora': 60, 'Tipo': 60, 'Producto': 200,
            'Cantidad': 80, 'Stock Ant.': 80, 'Stock Nuevo': 80,
            'Responsable': 120, 'Observaciones': 200
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Botón cerrar
        close_btn = tk.Button(self.window, text="✕ Cerrar",
                            command=self.window.destroy,
                            bg='#e74c3c', fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat', bd=0, padx=20, pady=10)
        close_btn.pack(pady=(0, 20))
    
    def load_history(self):
        """Cargar historial de movimientos"""
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not os.path.exists(self.db_path):
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query base
            table_name = f"movimientos_{self.sistema}"
            query = f"SELECT * FROM {table_name} WHERE 1=1"
            params = []
            
            # Aplicar filtros
            if self.type_filter.get() != 'Todos':
                query += " AND tipo = ?"
                params.append(self.type_filter.get())
            
            # TODO: Implementar filtros de fecha
            
            query += " ORDER BY fecha DESC, hora DESC"
            
            cursor.execute(query, params)
            
            # Cargar datos
            for row in cursor.fetchall():
                # Formatear datos
                fecha = row[5] if row[5] else ''
                hora = row[6] if row[6] else ''
                tipo = row[3].upper()
                
                # Color según tipo
                if tipo == 'ENTRADA':
                    tags = ('entrada',)
                else:
                    tags = ('salida',)
                
                self.tree.insert('', tk.END, values=(
                    fecha, hora, tipo, row[2], row[4],
                    row[7], row[8], row[9], row[10]
                ), tags=tags)
            
            # Configurar colores
            self.tree.tag_configure('entrada', foreground='#27ae60')
            self.tree.tag_configure('salida', foreground='#e74c3c')
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando historial: {e}")


# Funciones para integrar en las ventanas existentes

def abrir_movimiento_quimicos(parent, inventory_window, tipo):
    """Abrir ventana de movimiento para químicos"""
    MovimientoInventarioWindow(parent, inventory_window, tipo, 'quimicos')

def abrir_movimiento_almacen(parent, inventory_window, tipo):
    """Abrir ventana de movimiento para almacén"""
    MovimientoInventarioWindow(parent, inventory_window, tipo, 'almacen')

def abrir_movimiento_poscosecha(parent, inventory_window, tipo):
    """Abrir ventana de movimiento para poscosecha"""
    MovimientoInventarioWindow(parent, inventory_window, tipo, 'poscosecha')

def abrir_historial_movimientos(parent, sistema):
    """Abrir ventana de historial de movimientos"""
    HistorialMovimientosWindow(parent, sistema)