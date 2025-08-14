#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Unificado de Movimientos de Inventario
Maneja entradas y salidas con fecha y hora automática
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class MovimientoInventarioDialog:
    """Diálogo unificado para registrar movimientos de inventario"""
    
    def __init__(self, parent, sistema, tipo):
        self.parent = parent
        self.sistema = sistema  # 'quimicos', 'almacen', 'poscosecha'
        self.tipo = tipo  # 'entrada' o 'salida'
        
        # Configurar base de datos
        self.setup_database()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.create_interface()
        
        # Cargar productos
        self.load_products()
    
    def setup_database(self):
        """Configurar conexión a base de datos"""
        db_paths = {
            'quimicos': 'database/inventario_quimicos.db',
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
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                saldo_anterior INTEGER,
                saldo_nuevo INTEGER,
                responsable TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        self.window.geometry("500x450")
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
        y = (self.window.winfo_screenheight() // 2) - (450 // 2)
        self.window.geometry(f"500x450+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz completa"""
        # Header
        self.create_header()
        
        # Formulario
        self.create_form()
        
        # Botones
        self.create_buttons()
    
    def create_header(self):
        """Crear header con información del movimiento"""
        header_frame = tk.Frame(self.window, bg=self.header_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=self.header_color)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Título
        title_text = f"{'Entrada' if self.tipo == 'entrada' else 'Salida'} de Stock"
        title_label = tk.Label(header_content, text=title_text,
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.header_color, fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Fecha y hora actual
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        time_label = tk.Label(header_content, text=f"📅 {current_time}",
                             font=('Segoe UI', 10),
                             bg=self.header_color, fg='white')
        time_label.pack(side=tk.RIGHT)
    
    def create_form(self):
        """Crear formulario de movimiento"""
        form_frame = tk.Frame(self.window, bg='#f8f9fa')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Variables
        self.producto_var = tk.StringVar()
        self.cantidad_var = tk.StringVar()
        self.responsable_var = tk.StringVar()
        self.observaciones_var = tk.StringVar()
        
        # Producto
        tk.Label(form_frame, text="Producto:", font=('Segoe UI', 10, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        self.producto_combo = ttk.Combobox(form_frame, textvariable=self.producto_var,
                                          font=('Segoe UI', 10), width=40, state="readonly")
        self.producto_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.producto_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        
        # Información del producto seleccionado
        self.producto_info_label = tk.Label(form_frame, text="",
                                           font=('Segoe UI', 9),
                                           bg='#f8f9fa', fg='#7f8c8d')
        self.producto_info_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        # Cantidad
        tk.Label(form_frame, text="Cantidad:", font=('Segoe UI', 10, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').grid(row=2, column=0, sticky='w', pady=5)
        
        cantidad_entry = tk.Entry(form_frame, textvariable=self.cantidad_var,
                                 font=('Segoe UI', 10), width=20)
        cantidad_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        cantidad_entry.bind('<KeyRelease>', self.validate_quantity)
        
        # Responsable
        tk.Label(form_frame, text="Responsable:", font=('Segoe UI', 10, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').grid(row=3, column=0, sticky='w', pady=5)
        
        responsable_entry = tk.Entry(form_frame, textvariable=self.responsable_var,
                                    font=('Segoe UI', 10), width=30)
        responsable_entry.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Observaciones
        tk.Label(form_frame, text="Observaciones:", font=('Segoe UI', 10, 'bold'),
                bg='#f8f9fa', fg='#2c3e50').grid(row=4, column=0, sticky='w', pady=5)
        
        observaciones_text = tk.Text(form_frame, height=3, width=30,
                                    font=('Segoe UI', 10))
        observaciones_text.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.observaciones_text = observaciones_text
        
        # Configurar grid
        form_frame.columnconfigure(1, weight=1)
    
    def create_buttons(self):
        """Crear botones de acción"""
        buttons_frame = tk.Frame(self.window, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Botón guardar
        save_color = '#27ae60' if self.tipo == 'entrada' else '#e74c3c'
        save_btn = tk.Button(buttons_frame, text="💾 Guardar Movimiento",
                            command=self.save_movement,
                            bg=save_color, fg='white',
                            font=('Segoe UI', 12, 'bold'),
                            relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón cancelar
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar",
                              command=self.window.destroy,
                              bg='#95a5a6', fg='white',
                              font=('Segoe UI', 12, 'bold'),
                              relief='flat', bd=0, padx=20, pady=10, cursor='hand2')
        cancel_btn.pack(side=tk.LEFT)
    
    def load_products(self):
        """Cargar productos en el combobox"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener productos según el sistema
            if self.sistema == 'quimicos':
                cursor.execute("SELECT codigo, nombre, saldo FROM productos_quimicos ORDER BY nombre")
            elif self.sistema == 'almacen':
                cursor.execute("SELECT codigo, nombre, saldo FROM productos_almacen ORDER BY nombre")
            else:  # poscosecha
                cursor.execute("SELECT codigo, nombre, saldo FROM productos_poscosecha ORDER BY nombre")
            
            productos = cursor.fetchall()
            conn.close()
            
            # Crear lista para combobox
            productos_list = [f"{codigo} - {nombre}" for codigo, nombre, saldo in productos]
            self.productos_data = {f"{codigo} - {nombre}": (codigo, nombre, saldo) 
                                  for codigo, nombre, saldo in productos}
            
            self.producto_combo['values'] = productos_list
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {e}")
    
    def on_product_selected(self, event=None):
        """Cuando se selecciona un producto"""
        selected = self.producto_var.get()
        if selected in self.productos_data:
            codigo, nombre, saldo = self.productos_data[selected]
            self.producto_info_label.config(
                text=f"📦 Stock actual: {saldo} unidades | Código: {codigo}"
            )
    
    def validate_quantity(self, event=None):
        """Validar cantidad ingresada"""
        try:
            cantidad = int(self.cantidad_var.get())
            if cantidad <= 0:
                self.cantidad_var.set("")
        except ValueError:
            if self.cantidad_var.get() != "":
                self.cantidad_var.set("")
        except:
            pass
    
    def save_movement(self):
        """Guardar movimiento"""
        try:
            # Validar campos
            if not self.producto_var.get():
                messagebox.showerror("Error", "Selecciona un producto")
                return
            
            if not self.cantidad_var.get():
                messagebox.showerror("Error", "Ingresa una cantidad")
                return
            
            if not self.responsable_var.get():
                messagebox.showerror("Error", "Ingresa el responsable")
                return
            
            # Obtener datos
            selected = self.producto_var.get()
            codigo, nombre, saldo_actual = self.productos_data[selected]
            cantidad = int(self.cantidad_var.get())
            responsable = self.responsable_var.get()
            observaciones = self.observaciones_text.get("1.0", tk.END).strip()
            
            # Validar stock para salidas
            if self.tipo == 'salida' and cantidad > saldo_actual:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {saldo_actual}")
                return
            
            # Calcular nuevo saldo
            if self.tipo == 'entrada':
                nuevo_saldo = saldo_actual + cantidad
            else:
                nuevo_saldo = saldo_actual - cantidad
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insertar movimiento
            table_name = f"movimientos_{self.sistema}"
            cursor.execute(f'''
                INSERT INTO {table_name} 
                (producto_codigo, producto_nombre, tipo, cantidad, fecha_hora, 
                 saldo_anterior, saldo_nuevo, responsable, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo, nombre, self.tipo, cantidad, datetime.now(),
                  saldo_actual, nuevo_saldo, responsable, observaciones))
            
            # Actualizar stock del producto
            if self.sistema == 'quimicos':
                cursor.execute("UPDATE productos_quimicos SET saldo = ? WHERE codigo = ?", 
                              (nuevo_saldo, codigo))
            elif self.sistema == 'almacen':
                cursor.execute("UPDATE productos_almacen SET saldo = ? WHERE codigo = ?", 
                              (nuevo_saldo, codigo))
            else:  # poscosecha
                cursor.execute("UPDATE productos_poscosecha SET saldo = ? WHERE codigo = ?", 
                              (nuevo_saldo, codigo))
            
            conn.commit()
            conn.close()
            
            # Mostrar confirmación
            tipo_text = "Entrada" if self.tipo == 'entrada' else "Salida"
            messagebox.showinfo("Éxito", 
                              f"{tipo_text} registrada exitosamente\n"
                              f"Producto: {nombre}\n"
                              f"Cantidad: {cantidad}\n"
                              f"Nuevo saldo: {nuevo_saldo}")
            
            # Cerrar ventana
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando movimiento: {e}")


# Funciones para abrir desde otros módulos
def abrir_movimiento_entrada(parent, sistema):
    """Abrir diálogo de entrada"""
    MovimientoInventarioDialog(parent, sistema, 'entrada')

def abrir_movimiento_salida(parent, sistema):
    """Abrir diálogo de salida"""
    MovimientoInventarioDialog(parent, sistema, 'salida')

def abrir_historial_movimientos(parent, sistema):
    """Abrir historial de movimientos"""
    HistorialMovimientosWindow(parent, sistema)


class HistorialMovimientosWindow:
    """Ventana para ver historial de movimientos"""
    
    def __init__(self, parent, sistema):
        self.parent = parent
        self.sistema = sistema
        
        # Configurar base de datos
        db_paths = {
            'quimicos': 'database/inventario_quimicos.db',
            'almacen': 'database/inventario_almacen.db',
            'poscosecha': 'database/inventario_poscosecha.db'
        }
        
        self.db_path = db_paths.get(sistema)
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showerror("Error", f"Base de datos de {sistema} no encontrada")
            return
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.create_interface()
        self.load_movements()
    
    def setup_window(self):
        """Configurar ventana"""
        sistemas_text = {
            'quimicos': 'Químicos',
            'almacen': 'Almacén',
            'poscosecha': 'Poscosecha'
        }
        
        title = f"📋 Historial de Movimientos - {sistemas_text.get(self.sistema, '')}"
        self.window.title(title)
        self.window.geometry("1000x600")
        self.window.configure(bg='#f8f9fa')
        
        # Centrar ventana
        self.center_window()
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def center_window(self):
        """Centrar ventana"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"1000x600+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz"""
        # Header
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg='#2c3e50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(header_content, text="📋 Historial de Movimientos",
                              font=('Segoe UI', 16, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Botón cerrar
        close_btn = tk.Button(header_content, text="❌ Cerrar",
                             command=self.window.destroy,
                             bg='#e74c3c', fg='white',
                             font=('Segoe UI', 10, 'bold'),
                             relief='flat', bd=0, padx=15, pady=5, cursor='hand2')
        close_btn.pack(side=tk.RIGHT)
        
        # Tabla de movimientos
        self.create_movements_table()
    
    def create_movements_table(self):
        """Crear tabla de movimientos"""
        table_frame = tk.Frame(self.window, bg='#f8f9fa')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TreeView para movimientos
        columns = ('Fecha/Hora', 'Tipo', 'Producto', 'Cantidad', 'Saldo Anterior', 'Saldo Nuevo', 'Responsable', 'Observaciones')
        self.movements_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        column_config = {
            'Fecha/Hora': {'width': 150, 'anchor': 'center'},
            'Tipo': {'width': 80, 'anchor': 'center'},
            'Producto': {'width': 200, 'anchor': 'w'},
            'Cantidad': {'width': 80, 'anchor': 'center'},
            'Saldo Anterior': {'width': 100, 'anchor': 'center'},
            'Saldo Nuevo': {'width': 100, 'anchor': 'center'},
            'Responsable': {'width': 120, 'anchor': 'w'},
            'Observaciones': {'width': 200, 'anchor': 'w'}
        }
        
        for col, config in column_config.items():
            self.movements_tree.heading(col, text=col)
            self.movements_tree.column(col, width=config['width'], anchor=config['anchor'])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.movements_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.movements_tree.xview)
        self.movements_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.movements_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def load_movements(self):
        """Cargar movimientos en la tabla"""
        try:
            # Limpiar tabla
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)
            
            # Conectar a base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener movimientos
            table_name = f"movimientos_{self.sistema}"
            cursor.execute(f'''
                SELECT fecha_hora, tipo, producto_nombre, cantidad, saldo_anterior, 
                       saldo_nuevo, responsable, observaciones
                FROM {table_name}
                ORDER BY fecha_hora DESC
                LIMIT 1000
            ''')
            
            movements = cursor.fetchall()
            conn.close()
            
            # Insertar en tabla
            for movement in movements:
                fecha_hora, tipo, producto, cantidad, saldo_anterior, saldo_nuevo, responsable, observaciones = movement
                
                # Formatear fecha
                try:
                    fecha_obj = datetime.fromisoformat(fecha_hora.replace('Z', '+00:00'))
                    fecha_formateada = fecha_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    fecha_formateada = fecha_hora
                
                # Formatear tipo con emoji
                tipo_emoji = "📥" if tipo == 'entrada' else "📤"
                tipo_formateado = f"{tipo_emoji} {tipo.title()}"
                
                # Insertar en tabla
                self.movements_tree.insert('', 'end', values=(
                    fecha_formateada,
                    tipo_formateado,
                    producto,
                    cantidad,
                    saldo_anterior,
                    saldo_nuevo,
                    responsable or "No especificado",
                    observaciones or "Sin observaciones"
                ))
            
            # Mostrar contador
            total_movements = len(movements)
            self.window.title(f"📋 Historial de Movimientos - {total_movements} registros")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando movimientos: {e}") 