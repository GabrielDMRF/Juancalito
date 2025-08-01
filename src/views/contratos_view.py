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
        # Crear ventana de Contratos
        self.window = tk.Toplevel(parent)
        self.window.title("🔖 Gestión de Contratos")
        self.window.geometry("1000x700")
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
        # Cargar datos iniciales de contratos
        self.cargar_contratos()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Título
        title = tk.Label(main_frame, text="📋 Gestión de Contratos", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        title.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        # Botones principales
        btn_frame = tk.Frame(main_frame, bg='#ecf0f1')
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(0, 20))
        buttons_info = [
            ("➕ Nuevo Contrato", self.nuevo_contrato, "#27ae60"),
            ("✏️ Editar Contrato", self.editar_contrato, "#3498db"),
            ("👁️ Ver Detalles", self.ver_contrato, "#f39c12"),
            ("📄 Generar Excel", self.generar_contrato_excel, "#16a085"),
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
        columns = ('ID', 'Número', 'Empleado', 'Tipo', 'Inicio', 'Fin', 'Salario', 'Estado')
        self.tree = ttk.Treeview(contratos_frame, columns=columns, show='headings', height=15)
        column_widths = {'ID': 50, 'Número': 120, 'Empleado': 180, 'Tipo': 100,
                         'Inicio': 100, 'Fin': 100, 'Salario': 120, 'Estado': 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        v_scrollbar = ttk.Scrollbar(contratos_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        # Doble click para ver detalles de contrato
        self.tree.bind('<Double-1>', lambda e: self.ver_contrato())
        # Configurar expandibilidad
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        contratos_frame.columnconfigure(0, weight=1)
        contratos_frame.rowconfigure(0, weight=1)
    
    def cargar_contratos(self):
        """Cargar todos los contratos en el TreeView"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            contratos = self.db.query(Contrato).join(Empleado).all()
            for contrato in contratos:
                fecha_inicio = contrato.fecha_inicio.strftime("%d/%m/%Y") if contrato.fecha_inicio else "No definida"
                fecha_fin = contrato.fecha_fin.strftime("%d/%m/%Y") if contrato.fecha_fin else "No definida"
                salario = f"${contrato.salario_base:,}" if contrato.salario_base else "No definido"
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
            print(f"Se cargaron {len(contratos)} contratos")
        except Exception as e:
            print(f"Error al cargar contratos: {e}")
            messagebox.showerror("Error", f"Error al cargar contratos: {e}")
    
    def get_selected_contrato(self):
        """Obtener el contrato seleccionado en el TreeView"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor selecciona un contrato")
            return None
        contrato_id = self.tree.item(selection[0])['values'][0]
        return self.db.query(Contrato).filter(Contrato.id == contrato_id).first()
    
    def nuevo_contrato(self):
        """Abrir ventana para crear un nuevo contrato"""
        NuevoContratoWindow(self.window, self)
    
    def editar_contrato(self):
        """Abrir ventana para editar el contrato seleccionado"""
        contrato = self.get_selected_contrato()
        if contrato:
            NuevoContratoWindow(self.window, self, contrato=contrato)
    
    def ver_contrato(self):
        """Abrir ventana de detalles del contrato seleccionado"""
        contrato = self.get_selected_contrato()
        if contrato:
            DetallesContratoWindow(self.window, contrato)
    
    def generar_contrato_excel(self):
        """Generar el contrato profesional en formato Excel para el contrato seleccionado"""
        contrato = self.get_selected_contrato()
        if contrato:
            try:
                from utils.contrato_excel_generator import abrir_generador_contratos_profesional_excel
                abrir_generador_contratos_profesional_excel(self.window, self, contrato)
            except ImportError:
                messagebox.showinfo(
                    "Generar Excel",
                    "Falta la librería 'openpyxl'. Instálala con:\n\npip install openpyxl"
                )

# ... (Clases NuevoContratoWindow, DetallesContratoWindow permanecen sin cambios) ...
# OMITIDAS POR BREVIDAD, ya que la pregunta se enfoca en la generación de Excel.
