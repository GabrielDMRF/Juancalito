import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Agregar path para importar modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import get_db, Empleado

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.db = get_db()
        self.configurar_estilos()  # AGREGAR ESTA LÍNEA
        self.setup_main_window()
        self.create_widgets()
    
    def configurar_estilos(self):  # MOVER ESTA FUNCIÓN AQUÍ
        """Configurar estilos visuales mejorados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para el TreeView
        style.configure('Empleados.Treeview',
                       font=('Arial', 9),
                       rowheight=25)
        
        style.configure('Empleados.Treeview.Heading',
                       font=('Arial', 9, 'bold'),
                       background='#4CAF50',
                       foreground='white')
        
        style.map('Empleados.Treeview',
                 background=[('selected', '#2196F3')])
    
    def setup_main_window(self):
        self.root.title("Sistema de Gestión de Personal - V1.1")
        self.root.geometry("1100x700")
        self.root.configure(bg='#f0f0f0')
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título con estilo
        title = tk.Label(main_frame, text="🏢 Sistema de Gestión de Personal", 
                        font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=4, pady=(0, 25))
        
        # BOTONES MEJORADOS - REEMPLAZAR LA SECCIÓN ORIGINAL
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(0, 20))
        
        buttons_info = [
            ("➕ Nuevo Empleado", self.nuevo_empleado, "#27ae60"),
            ("✏️ Editar Empleado", self.editar_empleado, "#3498db"),
            ("📄 Contratos", self.abrir_contratos, "#8e44ad"), 
            ("📦 Inventarios", self.abrir_inventarios, "#1abc9c"),
            ("❌ Inactivar", self.inactivar_empleado, "#e67e22"),
            ("📊 Reportes", self.abrir_reportes, "#9b59b6")
        ]
        
        for i, (text, command, color) in enumerate(buttons_info):
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', padx=20, pady=10, cursor='hand2',
                           bd=0, activebackground=self.darker_color(color),
                           width=16)
            btn.pack(side=tk.LEFT, padx=8)
            
            # Efecto hover
            def make_hover(btn, color):
                def on_enter(e):
                    btn.config(bg=self.darker_color(color))
                def on_leave(e):
                    btn.config(bg=color)
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
            
            make_hover(btn, color)
        
        # Frame de búsqueda y filtros
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Búsqueda y Filtros", padding="15")
        search_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Búsqueda por texto
        ttk.Label(search_frame, text="Buscar:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25, font=('Arial', 10))
        search_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Filtro por área
        ttk.Label(search_frame, text="Área:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.filter_area = tk.StringVar()
        self.filter_area.trace('w', self.on_search_change)
        area_combo = ttk.Combobox(search_frame, textvariable=self.filter_area, 
                                 values=["Todas", "planta", "postcosecha"], width=15)
        area_combo.set("Todas")
        area_combo.grid(row=0, column=3, padx=(0, 20))
        
        # Filtro por estado
        ttk.Label(search_frame, text="Estado:", font=('Arial', 10, 'bold')).grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.filter_estado = tk.StringVar()
        self.filter_estado.trace('w', self.on_search_change)
        estado_combo = ttk.Combobox(search_frame, textvariable=self.filter_estado, 
                                   values=["Activos", "Inactivos", "Todos"], width=15)
        estado_combo.set("Activos")
        estado_combo.grid(row=0, column=5, padx=(0, 10))
        
        # Botón limpiar filtros
        clear_btn = tk.Button(search_frame, text="🗑️ Limpiar", command=self.limpiar_filtros,
                             bg="#95a5a6", fg="white", font=('Arial', 9, 'bold'),
                             relief='flat', padx=10, pady=5, cursor='hand2')
        clear_btn.grid(row=0, column=6)
        
        # Lista de empleados
        empleados_frame = ttk.LabelFrame(main_frame, text="👥 Lista de Empleados", padding="15")
        empleados_frame.grid(row=3, column=0, columnspan=4, pady=(15, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview para mostrar empleados CON ESTILO
        columns = ('ID', 'Nombre', 'Cedula', 'Telefono', 'Area', 'Cargo', 'Salario', 'Estado')
        self.tree = ttk.Treeview(empleados_frame, columns=columns, show='headings', 
                                height=12, style='Empleados.Treeview')
        
        # Configurar columnas
        column_widths = {'ID': 50, 'Nombre': 150, 'Cedula': 100, 'Telefono': 100, 
                        'Area': 100, 'Cargo': 120, 'Salario': 100, 'Estado': 80}
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(empleados_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(empleados_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid para tree y scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Doble click para editar
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Cargar datos
        self.cargar_empleados()
        
        # Crear barra de estado
        self.create_status_bar()
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        empleados_frame.columnconfigure(0, weight=1)
        empleados_frame.rowconfigure(0, weight=1)
    
    def darker_color(self, hex_color):
        """Hacer un color más oscuro para hover"""
        colors = {
            "#27ae60": "#229954",
            "#3498db": "#2980b9", 
            "#e67e22": "#d35400",
            "#8e44ad": "#7b1fa2",
            "#9b59b6": "#8e44ad",
            "#95a5a6": "#7f8c8d"
        }
        return colors.get(hex_color, hex_color)

    def create_status_bar(self):
        """Crear barra de estado en la parte inferior"""
        self.status_bar = tk.Frame(self.root, bg='#34495e', height=30)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.status_label = tk.Label(self.status_bar, text="Sistema listo", 
                                    bg='#34495e', fg='white', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Mostrar información actualizada
        self.update_status()

    def update_status(self):
        """Actualizar barra de estado"""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Contar empleados
            total_empleados = self.db.query(Empleado).count()
            activos = self.db.query(Empleado).filter(Empleado.estado == True).count()
            inactivos = total_empleados - activos
            
            # Contar elementos mostrados en la tabla
            items_mostrados = len(self.tree.get_children())
            
            status_text = f"📊 Total: {total_empleados} | ✅ Activos: {activos} | ❌ Inactivos: {inactivos} | 👁️ Mostrando: {items_mostrados} | 🕐 {current_time}"
            self.status_label.config(text=status_text)
            
            self.root.after(1000, self.update_status)
        except:
            self.status_label.config(text="Sistema activo")
            self.root.after(1000, self.update_status)
    
    # RESTO DE FUNCIONES IGUAL QUE ANTES...
    def on_search_change(self, *args):
        """Llamada cuando cambian los filtros de búsqueda"""
        self.cargar_empleados()
    
    def limpiar_filtros(self):
        """Limpiar todos los filtros"""
        self.search_var.set("")
        self.filter_area.set("Todas")
        self.filter_estado.set("Activos")
        
    def cargar_empleados(self):
        """Cargar empleados en el TreeView con filtros aplicados"""
        try:
            # Limpiar datos existentes
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Construir query base
            query = self.db.query(Empleado)
            
            # Aplicar filtro de estado
            estado_filtro = self.filter_estado.get()
            if estado_filtro == "Activos":
                query = query.filter(Empleado.estado == True)
            elif estado_filtro == "Inactivos":
                query = query.filter(Empleado.estado == False)
            # "Todos" no aplica filtro
            
            # Aplicar filtro de área
            area_filtro = self.filter_area.get()
            if area_filtro and area_filtro != "Todas":
                query = query.filter(Empleado.area_trabajo == area_filtro)
            
            # Aplicar búsqueda por texto
            texto_busqueda = self.search_var.get().strip().lower()
            if texto_busqueda:
                query = query.filter(
                    (Empleado.nombre_completo.ilike(f'%{texto_busqueda}%')) |
                    (Empleado.cedula.ilike(f'%{texto_busqueda}%')) |
                    (Empleado.cargo.ilike(f'%{texto_busqueda}%'))
                )
            
            # Ejecutar query
            empleados = query.all()
            
            # Cargar en TreeView
            for emp in empleados:
                estado_texto = "✅ Activo" if emp.estado else "❌ Inactivo"
                salario_texto = f"${emp.salario_base:,}" if emp.salario_base else "No definido"
                
                self.tree.insert('', 'end', values=(
                    emp.id,
                    emp.nombre_completo,
                    emp.cedula,
                    emp.telefono or "No definido",
                    emp.area_trabajo or "No definida",
                    emp.cargo or "No definido",
                    salario_texto,
                    estado_texto
                ))
            
            total = len(empleados)
            print(f"Se cargaron {total} empleados")
            
        except Exception as e:
            print(f"Error al cargar empleados: {e}")
    
    def sort_column(self, col):
        """Ordenar TreeView por columna"""
        try:
            data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
            data.sort()
            
            for index, (val, child) in enumerate(data):
                self.tree.move(child, '', index)
        except:
            pass
    
    def on_double_click(self, event):
        """Manejar doble click en TreeView"""
        self.editar_empleado()
    
    def get_selected_empleado(self):
        """Obtener empleado seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un empleado")
            return None
        
        item = self.tree.item(selection[0])
        empleado_id = item['values'][0]
        return self.db.query(Empleado).filter(Empleado.id == empleado_id).first()
    
    def nuevo_empleado(self):
        """Abrir ventana para nuevo empleado"""
        EmpleadosWindow(self.root, self, modo="nuevo")
    
    def editar_empleado(self):
        """Abrir ventana para editar empleado"""
        empleado = self.get_selected_empleado()
        if empleado:
            EmpleadosWindow(self.root, self, modo="editar", empleado=empleado)
    
    def inactivar_empleado(self):
        """Inactivar/activar empleado seleccionado"""
        empleado = self.get_selected_empleado()
        if not empleado:
            return
        
        accion = "activar" if not empleado.estado else "inactivar"
        if messagebox.askyesno("Confirmar", 
                              f"¿Estás seguro que deseas {accion} a {empleado.nombre_completo}?"):
            empleado.estado = not empleado.estado
            self.db.commit()
            self.cargar_empleados()
            print(f"Empleado {empleado.nombre_completo} {'activado' if empleado.estado else 'inactivado'}")
    
    def abrir_reportes(self):
        print("Módulo de reportes - Próximamente")


    def abrir_contratos(self):
        """Abrir ventana de gestión de contratos"""
        try:
            from views.contratos_view import ContratosWindow
            ContratosWindow(self.root, self)
        except ImportError:
            messagebox.showerror("Error", "Módulo de contratos no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir contratos: {e}")
    
    def abrir_inventarios(self):
        """Abrir ventana de gestión de inventarios"""
        try:
            # Importar la versión moderna
            from views.inventario_view import ModernInventarioWindow
            ModernInventarioWindow(self.root, self)
        except ImportError as e:
            print(f"Error de importación: {e}")
            messagebox.showerror("Error", f"Módulo de inventarios no encontrado: {e}")
        except Exception as e:
            print(f"Error general: {e}")
            messagebox.showerror("Error", f"Error al abrir inventarios: {e}")

# CLASE EmpleadosWindow SIGUE IGUAL...
class EmpleadosWindow:
    def __init__(self, parent, main_window, modo="nuevo", empleado=None):
        self.parent = parent
        self.main_window = main_window
        self.db = get_db()
        self.modo = modo
        self.empleado = empleado
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        titulo = "Editar Empleado" if modo == "editar" else "Nuevo Empleado"
        self.window.title(titulo)
        self.window.geometry("500x450")
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
        
        # Si es edición, cargar datos
        if modo == "editar" and empleado:
            self.cargar_datos_empleado()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título con emoji
        titulo_texto = "✏️ Editar Empleado" if self.modo == "editar" else "➕ Registrar Nuevo Empleado"
        title_label = tk.Label(main_frame, text=titulo_texto, font=('Arial', 16, 'bold'),
                              bg='#ecf0f1', fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos con mejor estilo
        campos = [
            ("Nombre Completo:", "entry_nombre"),
            ("Cedula:", "entry_cedula"),
            ("Telefono:", "entry_telefono"),
            ("Email:", "entry_email"),
            ("Direccion:", "entry_direccion"),
            ("Cargo:", "entry_cargo"),
            ("Salario Base:", "entry_salario")
        ]
        
        for i, (label_text, entry_name) in enumerate(campos, 1):
            label = ttk.Label(main_frame, text=label_text, font=('Arial', 10, 'bold'))
            label.grid(row=i, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            
            entry = ttk.Entry(main_frame, width=30, font=('Arial', 10))
            entry.grid(row=i, column=1, pady=8)
            setattr(self, entry_name, entry)
        
        # Área como combobox
        ttk.Label(main_frame, text="Area:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        self.combo_area = ttk.Combobox(main_frame, values=["planta", "postcosecha"], width=27, font=('Arial', 10))
        self.combo_area.grid(row=8, column=1, pady=8)
        
        # Estado (solo para edición)
        if self.modo == "editar":
            ttk.Label(main_frame, text="Estado:", font=('Arial', 10, 'bold')).grid(row=9, column=0, sticky=tk.W, pady=8, padx=(0, 10))
            self.combo_estado = ttk.Combobox(main_frame, values=["Activo", "Inactivo"], width=27, font=('Arial', 10))
            self.combo_estado.grid(row=9, column=1, pady=8)
        
        # Botones con colores
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_row = 10 if self.modo == "editar" else 9
        btn_frame.grid(row=btn_row, column=0, columnspan=2, pady=25)
        
        # Botón principal
        texto_boton = "💾 Actualizar" if self.modo == "editar" else "💾 Guardar"
        save_btn = tk.Button(btn_frame, text=texto_boton, command=self.guardar_empleado,
                           bg="#27ae60", fg="white", font=('Arial', 10, 'bold'),
                           relief='flat', padx=20, pady=8, cursor='hand2')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón limpiar
        clear_btn = tk.Button(btn_frame, text="🗑️ Limpiar", command=self.limpiar_campos,
                            bg="#f39c12", fg="white", font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8, cursor='hand2')
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón cerrar
        close_btn = tk.Button(btn_frame, text="❌ Cerrar", command=self.window.destroy,
                            bg="#e74c3c", fg="white", font=('Arial', 10, 'bold'),
                            relief='flat', padx=20, pady=8, cursor='hand2')
        close_btn.pack(side=tk.LEFT, padx=5)
    
    # RESTO DE FUNCIONES IGUAL...
    def cargar_datos_empleado(self):
        """Cargar datos del empleado en el formulario"""
        if not self.empleado:
            return
        
        self.entry_nombre.insert(0, self.empleado.nombre_completo or "")
        self.entry_cedula.insert(0, self.empleado.cedula or "")
        self.entry_telefono.insert(0, self.empleado.telefono or "")
        self.entry_email.insert(0, self.empleado.email or "")
        self.entry_direccion.insert(0, self.empleado.direccion or "")
        self.combo_area.set(self.empleado.area_trabajo or "")
        self.entry_cargo.insert(0, self.empleado.cargo or "")
        self.entry_salario.insert(0, str(self.empleado.salario_base or ""))
        
        if hasattr(self, 'combo_estado'):
            self.combo_estado.set("Activo" if self.empleado.estado else "Inactivo")
    
    def guardar_empleado(self):
        try:
            # Validar campos obligatorios
            if not self.entry_nombre.get().strip():
                messagebox.showerror("Error", "El nombre es obligatorio")
                self.entry_nombre.focus()
                return
            
            if not self.entry_cedula.get().strip():
                messagebox.showerror("Error", "La cedula es obligatoria")
                self.entry_cedula.focus()
                return
            
            # Validar cédula única (solo para nuevos o si cambió)
            cedula_nueva = self.entry_cedula.get().strip()
            if self.modo == "nuevo" or (self.empleado and self.empleado.cedula != cedula_nueva):
                cedula_existente = self.db.query(Empleado).filter(Empleado.cedula == cedula_nueva).first()
                if cedula_existente:
                    messagebox.showerror("Error", "Ya existe un empleado con esa cedula")
                    self.entry_cedula.focus()
                    return
            
            # Validar salario
            salario = 0
            if self.entry_salario.get().strip():
                try:
                    salario = int(self.entry_salario.get().strip())
                except ValueError:
                    messagebox.showerror("Error", "El salario debe ser un numero")
                    self.entry_salario.focus()
                    return
            
            if self.modo == "nuevo":
                # Crear nuevo empleado
                empleado = Empleado(
                    nombre_completo=self.entry_nombre.get().strip(),
                    cedula=cedula_nueva,
                    telefono=self.entry_telefono.get().strip(),
                    email=self.entry_email.get().strip(),
                    direccion=self.entry_direccion.get().strip(),
                    area_trabajo=self.combo_area.get(),
                    cargo=self.entry_cargo.get().strip(),
                    salario_base=salario
                )
                self.db.add(empleado)
                mensaje = "Empleado creado exitosamente"
            else:
                # Actualizar empleado existente
                self.empleado.nombre_completo = self.entry_nombre.get().strip()
                self.empleado.cedula = cedula_nueva
                self.empleado.telefono = self.entry_telefono.get().strip()
                self.empleado.email = self.entry_email.get().strip()
                self.empleado.direccion = self.entry_direccion.get().strip()
                self.empleado.area_trabajo = self.combo_area.get()
                self.empleado.cargo = self.entry_cargo.get().strip()
                self.empleado.salario_base = salario
                
                if hasattr(self, 'combo_estado'):
                    self.empleado.estado = self.combo_estado.get() == "Activo"
                
                mensaje = "Empleado actualizado exitosamente"
            
            self.db.commit()
            print(mensaje)
            
            # Actualizar ventana principal
            self.main_window.cargar_empleados()
            
            # Limpiar campos o cerrar
            if self.modo == "nuevo":
                self.limpiar_campos()
            else:
                self.window.destroy()
            
        except Exception as e:
            print(f"Error al guardar: {e}")
            messagebox.showerror("Error", f"Error al guardar empleado: {e}")
    
    def limpiar_campos(self):
        """Limpiar todos los campos del formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_cedula.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_direccion.delete(0, tk.END)
        self.combo_area.set('')
        self.entry_cargo.delete(0, tk.END)
        self.entry_salario.delete(0, tk.END)
       
        
        if hasattr(self, 'combo_estado'):
            self.combo_estado.set('Activo')