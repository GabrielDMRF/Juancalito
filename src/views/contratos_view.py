import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, date

# Agregar path para importar modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db, Empleado, Contrato, TipoContrato

class ContratosWindow:
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.db = get_db()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("🔖 Gestión de Contratos")
        self.window.geometry("1000x700")
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
        
        # Cargar datos
        self.cargar_contratos()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title = tk.Label(main_frame, text="📋 Gestión de Contratos", 
                        font=('Arial', 18, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Botones principales - SECCIÓN CORREGIDA
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(0, 20))
        
        buttons_info = [
            ("➕ Nuevo Contrato", self.nuevo_contrato, "#27ae60"),
            ("✏️ Editar Contrato", self.editar_contrato, "#3498db"),
            ("👁️ Ver Detalles", self.ver_contrato, "#f39c12"),
            ("📄 Generar Excel", self.generar_contrato_excel, "#16a085"),  # COMA CORREGIDA
            ("❌ Cerrar", self.window.destroy, "#e74c3c")
        ]
        
        for text, command, color in buttons_info:
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', padx=15, pady=8, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=8)
        
        # Lista de contratos
        contratos_frame = ttk.LabelFrame(main_frame, text="📄 Lista de Contratos", padding="15")
        contratos_frame.grid(row=2, column=0, columnspan=4, pady=(20, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # TreeView para contratos
        columns = ('ID', 'Número', 'Empleado', 'Tipo', 'Inicio', 'Fin', 'Salario', 'Estado')
        self.tree = ttk.Treeview(contratos_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'ID': 50, 'Número': 120, 'Empleado': 180, 'Tipo': 100, 
                        'Inicio': 100, 'Fin': 100, 'Salario': 120, 'Estado': 100}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(contratos_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Doble click para ver detalles
        self.tree.bind('<Double-1>', lambda e: self.ver_contrato())
        
        # Configurar grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        contratos_frame.columnconfigure(0, weight=1)
        contratos_frame.rowconfigure(0, weight=1)
    
    def cargar_contratos(self):
        """Cargar contratos en el TreeView"""
        try:
            # Limpiar datos existentes
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar contratos
            contratos = self.db.query(Contrato).join(Empleado).all()
            
            for contrato in contratos:
                fecha_inicio = contrato.fecha_inicio.strftime("%d/%m/%Y") if contrato.fecha_inicio else "No definida"
                fecha_fin = contrato.fecha_fin.strftime("%d/%m/%Y") if contrato.fecha_fin else "No definida"
                salario = f"${contrato.salario_base:,}" if contrato.salario_base else "No definido"
                
                # Emoji para estado
                estado_emoji = {
                    'borrador': '📝 Borrador',
                    'activo': '✅ Activo', 
                    'vencido': '⏰ Vencido',
                    'terminado': '❌ Terminado'
                }.get(contrato.estado, contrato.estado)
                
                self.tree.insert('', 'end', values=(
                    contrato.id,
                    contrato.numero_contrato or "Sin número",
                    contrato.empleado.nombre_completo,
                    contrato.tipo_contrato or "No definido",
                    fecha_inicio,
                    fecha_fin,
                    salario,
                    estado_emoji
                ))
            
            total = len(contratos)
            print(f"Se cargaron {total} contratos")
            
        except Exception as e:
            print(f"Error al cargar contratos: {e}")
            messagebox.showerror("Error", f"Error al cargar contratos: {e}")
    
    def get_selected_contrato(self):
        """Obtener contrato seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un contrato")
            return None
        
        item = self.tree.item(selection[0])
        contrato_id = item['values'][0]
        return self.db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    def nuevo_contrato(self):
        """Abrir ventana para nuevo contrato"""
        NuevoContratoWindow(self.window, self)
    
    def editar_contrato(self):
        """Editar contrato seleccionado"""
        contrato = self.get_selected_contrato()
        if contrato:
            NuevoContratoWindow(self.window, self, contrato=contrato)
    
    def ver_contrato(self):
        """Ver detalles del contrato"""
        contrato = self.get_selected_contrato()
        if contrato:
            DetallesContratoWindow(self.window, contrato)
    
    # MÉTODO NUEVO AGREGADO
    def generar_contrato_excel(self):
        """Generar contrato en Excel"""
        contrato = self.get_selected_contrato()
        if contrato:
            try:
                # Intentar importar y usar el generador de Excel
                from utils.contrato_excel_generator import abrir_generador_contratos_excel
                abrir_generador_contratos_excel(self.window, self, contrato)
            except ImportError:
                # Si no está el módulo, mostrar mensaje informativo
                messagebox.showinfo("Generar Excel", 
                    f"Funcionalidad de generación de contratos Excel.\n\n" +
                    f"Contrato seleccionado: {contrato.numero_contrato}\n" +
                    f"Empleado: {contrato.empleado.nombre_completo}\n\n" +
                    "Para activar esta función:\n" +
                    "1. Instalar: pip install openpyxl\n" +
                    "2. Agregar archivo contrato_excel_generator.py en utils/")
            except Exception as e:
                messagebox.showerror("Error", f"Error abriendo generador Excel: {e}")


class NuevoContratoWindow:
    def __init__(self, parent, contratos_window, contrato=None):
        self.parent = parent
        self.contratos_window = contratos_window
        self.db = get_db()
        self.contrato = contrato
        self.is_edit = contrato is not None
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        titulo = "✏️ Editar Contrato" if self.is_edit else "➕ Nuevo Contrato"
        self.window.title(titulo)
        self.window.geometry("600x500")
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
        
        if self.is_edit:
            self.cargar_datos_contrato()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo_texto = "✏️ Editar Contrato" if self.is_edit else "➕ Nuevo Contrato"
        title = tk.Label(main_frame, text=titulo_texto, font=('Arial', 16, 'bold'),
                        bg='#ecf0f1', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Empleado
        ttk.Label(main_frame, text="Empleado:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.combo_empleado = ttk.Combobox(main_frame, width=35, font=('Arial', 10), state='readonly')
        self.combo_empleado.grid(row=1, column=1, pady=8)
        self.cargar_empleados()
        
        # Tipo de contrato
        ttk.Label(main_frame, text="Tipo de Contrato:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.combo_tipo = ttk.Combobox(main_frame, width=35, font=('Arial', 10), state='readonly')
        self.combo_tipo.grid(row=2, column=1, pady=8)
        self.cargar_tipos_contrato()
        
        # Fecha inicio
        ttk.Label(main_frame, text="Fecha Inicio:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.entry_fecha_inicio = ttk.Entry(main_frame, width=35, font=('Arial', 10))
        self.entry_fecha_inicio.grid(row=3, column=1, pady=8)
        self.entry_fecha_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Fecha fin
        ttk.Label(main_frame, text="Fecha Fin:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=8)
        self.entry_fecha_fin = ttk.Entry(main_frame, width=35, font=('Arial', 10))
        self.entry_fecha_fin.grid(row=4, column=1, pady=8)
        
        # Salario base
        ttk.Label(main_frame, text="Salario Base:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=8)
        self.entry_salario = ttk.Entry(main_frame, width=35, font=('Arial', 10))
        self.entry_salario.grid(row=5, column=1, pady=8)
        
        # Subsidio transporte
        ttk.Label(main_frame, text="Subsidio Transporte:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=8)
        self.entry_subsidio = ttk.Entry(main_frame, width=35, font=('Arial', 10))
        self.entry_subsidio.grid(row=6, column=1, pady=8)
        self.entry_subsidio.insert(0, "140606")  # Valor 2024
        
        # Estado (solo para edición)
        if self.is_edit:
            ttk.Label(main_frame, text="Estado:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=8)
            self.combo_estado = ttk.Combobox(main_frame, values=["borrador", "activo", "vencido", "terminado"], 
                                           width=32, font=('Arial', 10))
            self.combo_estado.grid(row=7, column=1, pady=8)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_row = 8 if self.is_edit else 7
        btn_frame.grid(row=btn_row, column=0, columnspan=2, pady=25)
        
        texto_btn = "💾 Actualizar" if self.is_edit else "💾 Crear Contrato"
        save_btn = tk.Button(btn_frame, text=texto_btn, command=self.guardar_contrato,
                           bg="#27ae60", fg="white", font=('Arial', 10, 'bold'),
                           relief='flat', padx=20, pady=8, cursor='hand2')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(btn_frame, text="❌ Cerrar", command=self.window.destroy,
                            bg="#e74c3c", fg="white", font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8, cursor='hand2')
        close_btn.pack(side=tk.LEFT, padx=5)
    
    def cargar_empleados(self):
        """Cargar empleados activos en combobox"""
        empleados = self.db.query(Empleado).filter(Empleado.estado == True).all()
        empleados_values = [f"{emp.nombre_completo} - {emp.cedula}" for emp in empleados]
        self.combo_empleado['values'] = empleados_values
        
        # Guardar referencia para obtener ID después
        self.empleados_dict = {f"{emp.nombre_completo} - {emp.cedula}": emp.id for emp in empleados}
    
    def cargar_tipos_contrato(self):
        """Cargar tipos de contrato"""
        tipos = self.db.query(TipoContrato).all()
        tipos_values = [tipo.nombre for tipo in tipos]
        self.combo_tipo['values'] = tipos_values
        
        # Guardar referencia
        self.tipos_dict = {tipo.nombre: tipo.id for tipo in tipos}
    
    def cargar_datos_contrato(self):
        """Cargar datos del contrato para edición"""
        if not self.contrato:
            return
        
        # Seleccionar empleado
        empleado_text = f"{self.contrato.empleado.nombre_completo} - {self.contrato.empleado.cedula}"
        self.combo_empleado.set(empleado_text)
        
        # Seleccionar tipo
        self.combo_tipo.set(self.contrato.tipo_contrato or "")
        
        # Fechas
        if self.contrato.fecha_inicio:
            self.entry_fecha_inicio.delete(0, tk.END)
            self.entry_fecha_inicio.insert(0, self.contrato.fecha_inicio.strftime("%d/%m/%Y"))
        
        if self.contrato.fecha_fin:
            self.entry_fecha_fin.delete(0, tk.END)
            self.entry_fecha_fin.insert(0, self.contrato.fecha_fin.strftime("%d/%m/%Y"))
        
        # Salarios
        self.entry_salario.delete(0, tk.END)
        self.entry_salario.insert(0, str(self.contrato.salario_base or ""))
        
        self.entry_subsidio.delete(0, tk.END)
        self.entry_subsidio.insert(0, str(self.contrato.subsidio_transporte or "140606"))
        
        # Estado
        if hasattr(self, 'combo_estado'):
            self.combo_estado.set(self.contrato.estado)
    
    def guardar_contrato(self):
        """Guardar o actualizar contrato"""
        try:
            # Validaciones básicas
            if not self.combo_empleado.get():
                messagebox.showerror("Error", "Debe seleccionar un empleado")
                return
            
            if not self.combo_tipo.get():
                messagebox.showerror("Error", "Debe seleccionar un tipo de contrato")
                return
            
            # Obtener empleado_id
            empleado_id = self.empleados_dict.get(self.combo_empleado.get())
            if not empleado_id:
                messagebox.showerror("Error", "Empleado no válido")
                return
            
            # Obtener tipo_contrato_id
            tipo_id = self.tipos_dict.get(self.combo_tipo.get())
            
            # Validar y convertir fechas
            try:
                fecha_inicio = datetime.strptime(self.entry_fecha_inicio.get(), "%d/%m/%Y").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inicio inválido (DD/MM/YYYY)")
                return
            
            fecha_fin = None
            if self.entry_fecha_fin.get().strip():
                try:
                    fecha_fin = datetime.strptime(self.entry_fecha_fin.get(), "%d/%m/%Y").date()
                except ValueError:
                    messagebox.showerror("Error", "Formato de fecha fin inválido (DD/MM/YYYY)")
                    return
            
            # Validar salarios
            try:
                salario_base = int(self.entry_salario.get()) if self.entry_salario.get().strip() else 0
                subsidio = int(self.entry_subsidio.get()) if self.entry_subsidio.get().strip() else 0
            except ValueError:
                messagebox.showerror("Error", "Los salarios deben ser números")
                return
            
            if self.is_edit:
                # Actualizar contrato existente
                self.contrato.empleado_id = empleado_id
                self.contrato.tipo_contrato_id = tipo_id
                self.contrato.tipo_contrato = self.combo_tipo.get()
                self.contrato.fecha_inicio = fecha_inicio
                self.contrato.fecha_fin = fecha_fin
                self.contrato.salario_base = salario_base
                self.contrato.subsidio_transporte = subsidio
                
                if hasattr(self, 'combo_estado'):
                    self.contrato.estado = self.combo_estado.get()
                
                mensaje = "Contrato actualizado exitosamente"
            else:
                # Crear nuevo contrato
                contrato = Contrato(
                    empleado_id=empleado_id,
                    tipo_contrato_id=tipo_id,
                    tipo_contrato=self.combo_tipo.get(),
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    salario_base=salario_base,
                    subsidio_transporte=subsidio,
                    estado='borrador'
                )
                
                # Generar número de contrato
                self.generar_numero_contrato(contrato)
                
                self.db.add(contrato)
                mensaje = "Contrato creado exitosamente"
            
            self.db.commit()
            print(mensaje)
            
            # Actualizar vista principal
            self.contratos_window.cargar_contratos()
            
            if not self.is_edit:
                # Limpiar formulario para nuevo contrato
                self.limpiar_formulario()
            else:
                self.window.destroy()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error al guardar contrato: {e}")
            messagebox.showerror("Error", f"Error al guardar contrato: {e}")
    
    def generar_numero_contrato(self, contrato):
        """Generar número único de contrato"""
        año = datetime.now().year
        
        # Contar contratos del año
        count = self.db.query(Contrato).filter(
            Contrato.numero_contrato.like(f'CT-{año}-%')
        ).count()
        
        contrato.numero_contrato = f"CT-{año}-{count + 1:03d}"
    
    def limpiar_formulario(self):
        """Limpiar formulario después de guardar"""
        self.combo_empleado.set('')
        self.combo_tipo.set('')
        self.entry_fecha_inicio.delete(0, tk.END)
        self.entry_fecha_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.entry_fecha_fin.delete(0, tk.END)
        self.entry_salario.delete(0, tk.END)
        self.entry_subsidio.delete(0, tk.END)
        self.entry_subsidio.insert(0, "140606")


class DetallesContratoWindow:
    def __init__(self, parent, contrato):
        self.parent = parent
        self.contrato = contrato
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title(f"👁️ Detalles - {contrato.numero_contrato}")
        self.window.geometry("500x400")
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title = tk.Label(main_frame, text=f"📄 {self.contrato.numero_contrato}", 
                        font=('Arial', 16, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Información del contrato
        info_items = [
            ("👤 Empleado:", self.contrato.empleado.nombre_completo),
            ("📋 Tipo:", self.contrato.tipo_contrato or "No definido"),
            ("📅 Fecha Inicio:", self.contrato.fecha_inicio.strftime("%d/%m/%Y") if self.contrato.fecha_inicio else "No definida"),
            ("📅 Fecha Fin:", self.contrato.fecha_fin.strftime("%d/%m/%Y") if self.contrato.fecha_fin else "No definida"),
            ("💰 Salario Base:", f"${self.contrato.salario_base:,}" if self.contrato.salario_base else "No definido"),
            ("🚌 Subsidio Trans.:", f"${self.contrato.subsidio_transporte:,}" if self.contrato.subsidio_transporte else "No definido"),
            ("📊 Estado:", self.contrato.estado.title()),
        ]
        
        for i, (label_text, value_text) in enumerate(info_items, 1):
            # Label
            label = tk.Label(main_frame, text=label_text, font=('Arial', 11, 'bold'),
                           bg='#ecf0f1', fg='#2c3e50', anchor='w')
            label.grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 20))
            
            # Value
            value = tk.Label(main_frame, text=value_text, font=('Arial', 11),
                           bg='#ecf0f1', fg='#34495e', anchor='w')
            value.grid(row=i, column=1, sticky=tk.W, pady=5)
        
        # Botón cerrar
        close_btn = tk.Button(main_frame, text="❌ Cerrar", command=self.window.destroy,
                            bg="#e74c3c", fg="white", font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8, cursor='hand2')
        close_btn.grid(row=len(info_items) + 2, column=0, columnspan=2, pady=20)