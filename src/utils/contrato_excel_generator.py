#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Generación de Contratos en Excel
Genera contratos personalizados en Excel y los guarda en carpetas por empleado
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import shutil
from utils.contrato_excel_generator import abrir_generador_contratos_excel

# Agregar path para importar modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.database import get_db, Empleado, Contrato, TipoContrato

# Intentar importar openpyxl para Excel
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

class ContratoExcelGenerator:
    """Generador de contratos en Excel con carpetas personalizadas"""
    
    def __init__(self):
        self.db = get_db()
        self.base_dir = Path("empleados_data")
        self.templates_dir = Path("templates_contratos")
        self.setup_directories()
    
    def setup_directories(self):
        """Crear directorios necesarios"""
        try:
            # Directorio base para empleados
            self.base_dir.mkdir(exist_ok=True)
            
            # Directorio para templates
            self.templates_dir.mkdir(exist_ok=True)
            
            # Crear template por defecto si no existe
            self.create_default_template()
            
            print(f"✅ Directorios configurados en: {self.base_dir}")
            
        except Exception as e:
            print(f"❌ Error configurando directorios: {e}")
    
    def create_default_template(self):
        """Crear template por defecto de contrato"""
        if not OPENPYXL_AVAILABLE:
            print("⚠️ openpyxl no disponible - no se puede crear template Excel")
            return
            
        template_path = self.templates_dir / "template_contrato_default.xlsx"
        
        if template_path.exists():
            return
        
        try:
            # Crear nuevo workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Contrato de Trabajo"
            
            # Estilos
            title_font = Font(name='Arial', size=16, bold=True)
            header_font = Font(name='Arial', size=12, bold=True)
            normal_font = Font(name='Arial', size=11)
            
            # Encabezado de la empresa
            ws['A1'] = "CONTRATO DE TRABAJO"
            ws['A1'].font = title_font
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:H1')
            
            ws['A3'] = "EMPRESA AGRÍCOLA S.A.S"
            ws['A3'].font = header_font
            ws['A3'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A3:H3')
            
            # Información del contrato
            row = 6
            campos_contrato = [
                ("Número de Contrato:", "{{NUMERO_CONTRATO}}"),
                ("Fecha de Elaboración:", "{{FECHA_ELABORACION}}"),
                ("", ""),
                ("DATOS DEL EMPLEADO", ""),
                ("Nombre Completo:", "{{NOMBRE_EMPLEADO}}"),
                ("Cédula de Ciudadanía:", "{{CEDULA_EMPLEADO}}"),
                ("Teléfono:", "{{TELEFONO_EMPLEADO}}"),
                ("Email:", "{{EMAIL_EMPLEADO}}"),
                ("Dirección:", "{{DIRECCION_EMPLEADO}}"),
                ("", ""),
                ("DATOS DEL CONTRATO", ""),
                ("Tipo de Contrato:", "{{TIPO_CONTRATO}}"),
                ("Fecha de Inicio:", "{{FECHA_INICIO}}"),
                ("Fecha de Finalización:", "{{FECHA_FIN}}"),
                ("Área de Trabajo:", "{{AREA_TRABAJO}}"),
                ("Cargo:", "{{CARGO_EMPLEADO}}"),
                ("", ""),
                ("DATOS SALARIALES", ""),
                ("Salario Base:", "{{SALARIO_BASE}}"),
                ("Subsidio de Transporte:", "{{SUBSIDIO_TRANSPORTE}}"),
                ("Bonificaciones:", "{{BONIFICACIONES}}"),
                ("Total Devengado:", "{{TOTAL_DEVENGADO}}"),
            ]
            
            for campo, valor in campos_contrato:
                if campo and not campo.startswith("DATOS"):
                    ws[f'A{row}'] = campo
                    ws[f'A{row}'].font = normal_font
                    ws[f'D{row}'] = valor
                    ws[f'D{row}'].font = normal_font
                elif campo.startswith("DATOS"):
                    ws[f'A{row}'] = campo
                    ws[f'A{row}'].font = header_font
                    ws.merge_cells(f'A{row}:H{row}')
                
                row += 1
            
            # Cláusulas del contrato
            row += 2
            ws[f'A{row}'] = "CLÁUSULAS DEL CONTRATO"
            ws[f'A{row}'].font = header_font
            ws.merge_cells(f'A{row}:H{row}')
            
            row += 2
            clausulas = [
                "PRIMERA: El presente contrato se celebra por el término y las condiciones establecidas.",
                "SEGUNDA: El empleado se compromete a cumplir con las funciones asignadas.",
                "TERCERA: La jornada laboral será de acuerdo a la legislación vigente.",
                "CUARTA: El salario se pagará mensualmente según lo estipulado.",
                "QUINTA: Las partes se comprometen a cumplir con las normas de seguridad."
            ]
            
            for clausula in clausulas:
                ws[f'A{row}'] = clausula
                ws[f'A{row}'].font = normal_font
                ws[f'A{row}'].alignment = Alignment(wrap_text=True)
                ws.merge_cells(f'A{row}:H{row}')
                ws.row_dimensions[row].height = 40
                row += 2
            
            # Firmas
            row += 3
            ws[f'A{row}'] = "_________________________"
            ws[f'F{row}'] = "_________________________"
            row += 1
            ws[f'A{row}'] = "EMPLEADOR"
            ws[f'F{row}'] = "EMPLEADO"
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            ws[f'F{row}'].alignment = Alignment(horizontal='center')
            
            # Ajustar columnas
            for col in range(1, 9):
                ws.column_dimensions[get_column_letter(col)].width = 15
            
            # Guardar template
            wb.save(template_path)
            print(f"✅ Template de contrato creado: {template_path}")
            
        except Exception as e:
            print(f"❌ Error creando template: {e}")
    
    def create_employee_folder(self, empleado):
        """Crear carpeta personalizada para empleado"""
        try:
            # Crear nombre de carpeta seguro
            nombre_seguro = self.safe_filename(empleado.nombre_completo)
            cedula_segura = self.safe_filename(empleado.cedula)
            
            folder_name = f"{nombre_seguro}_{cedula_segura}"
            employee_folder = self.base_dir / folder_name
            
            # Crear carpeta si no existe
            employee_folder.mkdir(exist_ok=True)
            
            # Crear subcarpetas
            subcarpetas = ["contratos", "documentos", "nomina", "historiales"]
            for subcarpeta in subcarpetas:
                (employee_folder / subcarpeta).mkdir(exist_ok=True)
            
            return employee_folder
            
        except Exception as e:
            print(f"Error creando carpeta para empleado: {e}")
            return None
    
    def safe_filename(self, filename):
        """Crear nombre de archivo seguro"""
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remover espacios extra y caracteres especiales
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_')
        
        return filename[:50]  # Limitar longitud
    
    def generate_contract_excel(self, contrato_id, template_path=None):
        """Generar contrato en Excel para un contrato específico"""
        if not OPENPYXL_AVAILABLE:
            raise Exception("openpyxl no está instalado. Instalar con: pip install openpyxl")
        
        try:
            # Obtener datos del contrato
            contrato = self.db.query(Contrato).filter(Contrato.id == contrato_id).first()
            if not contrato:
                raise Exception("Contrato no encontrado")
            
            empleado = contrato.empleado
            if not empleado:
                raise Exception("Empleado no encontrado")
            
            # Crear carpeta del empleado
            employee_folder = self.create_employee_folder(empleado)
            if not employee_folder:
                raise Exception("No se pudo crear la carpeta del empleado")
            
            # Usar template por defecto si no se especifica
            if not template_path:
                template_path = self.templates_dir / "template_contrato_default.xlsx"
            
            if not template_path.exists():
                raise Exception("Template de contrato no encontrado")
            
            # Cargar template
            wb = openpyxl.load_workbook(template_path)
            ws = wb.active
            
            # Preparar datos para reemplazar
            data_replacements = self.prepare_contract_data(contrato, empleado)
            
            # Reemplazar placeholders en todas las celdas
            self.replace_placeholders_in_worksheet(ws, data_replacements)
            
            # Generar nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            contract_filename = f"contrato_{empleado.cedula}_{timestamp}.xlsx"
            contract_path = employee_folder / "contratos" / contract_filename
            
            # Guardar contrato generado
            wb.save(contract_path)
            
            # Actualizar ruta en base de datos
            contrato.archivo_contrato_word = str(contract_path)
            self.db.commit()
            
            return {
                'success': True,
                'file_path': str(contract_path),
                'employee_folder': str(employee_folder),
                'message': f'Contrato generado exitosamente para {empleado.nombre_completo}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error generando contrato: {e}'
            }
    
    def prepare_contract_data(self, contrato, empleado):
        """Preparar datos del contrato para reemplazar placeholders"""
        try:
            # Calcular valores
            salario_base = contrato.salario_base or 0
            subsidio_transporte = contrato.subsidio_transporte or 0
            bonificaciones = contrato.bonificaciones or 0
            total_devengado = salario_base + subsidio_transporte + bonificaciones
            
            # Formatear fechas
            fecha_elaboracion = datetime.now().strftime("%d de %B de %Y")
            fecha_inicio = contrato.fecha_inicio.strftime("%d de %B de %Y") if contrato.fecha_inicio else "No definida"
            fecha_fin = contrato.fecha_fin.strftime("%d de %B de %Y") if contrato.fecha_fin else "Indefinida"
            
            # Preparar datos
            data = {
                '{{NUMERO_CONTRATO}}': contrato.numero_contrato or "SIN-NÚMERO",
                '{{FECHA_ELABORACION}}': fecha_elaboracion,
                '{{NOMBRE_EMPLEADO}}': empleado.nombre_completo or "",
                '{{CEDULA_EMPLEADO}}': empleado.cedula or "",
                '{{TELEFONO_EMPLEADO}}': empleado.telefono or "No definido",
                '{{EMAIL_EMPLEADO}}': empleado.email or "No definido",
                '{{DIRECCION_EMPLEADO}}': empleado.direccion or "No definida",
                '{{TIPO_CONTRATO}}': contrato.tipo_contrato or "No definido",
                '{{FECHA_INICIO}}': fecha_inicio,
                '{{FECHA_FIN}}': fecha_fin,
                '{{AREA_TRABAJO}}': empleado.area_trabajo or "No definida",
                '{{CARGO_EMPLEADO}}': empleado.cargo or "No definido",
                '{{SALARIO_BASE}}': f"${salario_base:,}",
                '{{SUBSIDIO_TRANSPORTE}}': f"${subsidio_transporte:,}",
                '{{BONIFICACIONES}}': f"${bonificaciones:,}",
                '{{TOTAL_DEVENGADO}}': f"${total_devengado:,}",
            }
            
            return data
            
        except Exception as e:
            print(f"Error preparando datos del contrato: {e}")
            return {}
    
    def replace_placeholders_in_worksheet(self, worksheet, data_replacements):
        """Reemplazar placeholders en toda la hoja de trabajo"""
        try:
            for row in worksheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        for placeholder, replacement in data_replacements.items():
                            if placeholder in cell.value:
                                cell.value = cell.value.replace(placeholder, str(replacement))
        
        except Exception as e:
            print(f"Error reemplazando placeholders: {e}")
    
    def get_employee_contracts_folder(self, empleado_id):
        """Obtener ruta de la carpeta de contratos de un empleado"""
        try:
            empleado = self.db.query(Empleado).filter(Empleado.id == empleado_id).first()
            if not empleado:
                return None
            
            nombre_seguro = self.safe_filename(empleado.nombre_completo)
            cedula_segura = self.safe_filename(empleado.cedula)
            folder_name = f"{nombre_seguro}_{cedula_segura}"
            
            employee_folder = self.base_dir / folder_name / "contratos"
            return employee_folder if employee_folder.exists() else None
            
        except Exception as e:
            print(f"Error obteniendo carpeta de contratos: {e}")
            return None
    
    def list_employee_contracts(self, empleado_id):
        """Listar contratos existentes de un empleado"""
        try:
            contracts_folder = self.get_employee_contracts_folder(empleado_id)
            if not contracts_folder:
                return []
            
            contracts = []
            for file_path in contracts_folder.glob("*.xlsx"):
                stat = file_path.stat()
                contracts.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
            
            return sorted(contracts, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            print(f"Error listando contratos: {e}")
            return []


class ContratoExcelWindow:
    """Ventana para generar contratos en Excel"""
    
    def __init__(self, parent, main_window, contrato=None):
        self.parent = parent
        self.main_window = main_window
        self.contrato = contrato
        self.generator = ContratoExcelGenerator()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("📄 Generador de Contratos Excel")
        self.window.geometry("600x500")
        self.window.configure(bg='#f8f9fa')
        
        self.center_window()
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_interface()
        
        # Si se pasó un contrato, cargarlo
        if contrato:
            self.load_contract_data()
    
    def center_window(self):
        """Centrar ventana"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#2c3e50', height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#2c3e50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(header_content, text="📄 Generador de Contratos Excel",
                              font=('Segoe UI', 18, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT)
        
        # Contenido principal
        content = tk.Frame(self.window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Información del contrato
        self.create_contract_info_section(content)
        
        # Opciones de generación
        self.create_generation_options(content)
        
        # Sección de archivos existentes
        self.create_existing_files_section(content)
        
        # Botones de acción
        self.create_action_buttons(content)
    
    def create_contract_info_section(self, parent):
        """Crear sección de información del contrato"""
        info_frame = tk.LabelFrame(parent, text="📋 Información del Contrato",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='white', fg='#2c3e50', padx=15, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Selección de contrato
        tk.Label(info_frame, text="Seleccionar Contrato:",
                font=('Segoe UI', 10, 'bold'),
                bg='white', fg='#2c3e50').grid(row=0, column=0, sticky='w', pady=5)
        
        self.contract_var = tk.StringVar()
        self.contract_combo = ttk.Combobox(info_frame, textvariable=self.contract_var,
                                          width=50, font=('Segoe UI', 10),
                                          state='readonly')
        self.contract_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky='ew')
        self.contract_combo.bind('<<ComboboxSelected>>', self.on_contract_selected)
        
        # Información del empleado
        self.info_labels = {}
        info_fields = [
            ("Empleado:", "empleado"),
            ("Cédula:", "cedula"),
            ("Tipo Contrato:", "tipo"),
            ("Estado:", "estado")
        ]
        
        for i, (label_text, field_key) in enumerate(info_fields, 1):
            tk.Label(info_frame, text=label_text,
                    font=('Segoe UI', 9, 'bold'),
                    bg='white', fg='#7f8c8d').grid(row=i, column=0, sticky='w', pady=3)
            
            info_label = tk.Label(info_frame, text="--",
                                 font=('Segoe UI', 9),
                                 bg='white', fg='#2c3e50')
            info_label.grid(row=i, column=1, sticky='w', pady=3, padx=(10, 0))
            self.info_labels[field_key] = info_label
        
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Cargar contratos
        self.load_contracts()
    
    def create_generation_options(self, parent):
        """Crear opciones de generación"""
        options_frame = tk.LabelFrame(parent, text="⚙️ Opciones de Generación",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='white', fg='#2c3e50', padx=15, pady=10)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Template personalizado
        template_frame = tk.Frame(options_frame, bg='white')
        template_frame.pack(fill=tk.X, pady=5)
        
        self.use_custom_template = tk.BooleanVar()
        custom_check = tk.Checkbutton(template_frame, 
                                     text="Usar template personalizado",
                                     variable=self.use_custom_template,
                                     font=('Segoe UI', 10),
                                     bg='white', fg='#2c3e50',
                                     command=self.toggle_custom_template)
        custom_check.pack(side=tk.LEFT)
        
        # Ruta del template
        self.template_frame = tk.Frame(options_frame, bg='white')
        self.template_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.template_frame, text="Template:",
                font=('Segoe UI', 9),
                bg='white', fg='#7f8c8d').pack(side=tk.LEFT)
        
        self.template_path_var = tk.StringVar()
        self.template_entry = tk.Entry(self.template_frame, 
                                      textvariable=self.template_path_var,
                                      width=40, font=('Segoe UI', 9),
                                      state='disabled')
        self.template_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        self.browse_btn = tk.Button(self.template_frame, text="Buscar",
                                   command=self.browse_template,
                                   bg='#3498db', fg='white',
                                   font=('Segoe UI', 9),
                                   relief='flat', padx=15, state='disabled')
        self.browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
    
    def create_existing_files_section(self, parent):
        """Crear sección de archivos existentes"""
        files_frame = tk.LabelFrame(parent, text="📁 Contratos Generados",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='white', fg='#2c3e50', padx=15, pady=10)
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Lista de archivos
        columns = ('Archivo', 'Fecha', 'Tamaño')
        self.files_tree = ttk.Treeview(files_frame, columns=columns, 
                                      show='headings', height=6)
        
        # Configurar columnas
        self.files_tree.heading('Archivo', text='Archivo')
        self.files_tree.heading('Fecha', text='Fecha Modificación')
        self.files_tree.heading('Tamaño', text='Tamaño')
        
        self.files_tree.column('Archivo', width=300)
        self.files_tree.column('Fecha', width=150)
        self.files_tree.column('Tamaño', width=80)
        
        # Scrollbar
        files_scroll = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, 
                                    command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scroll.set)
        
        # Grid
        self.files_tree.grid(row=0, column=0, sticky='nsew')
        files_scroll.grid(row=0, column=1, sticky='ns')
        
        files_frame.grid_rowconfigure(0, weight=1)
        files_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.files_tree.bind('<Double-1>', self.open_selected_file)
    
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        buttons_frame = tk.Frame(parent, bg='white')
        buttons_frame.pack(fill=tk.X)
        
        # Botón generar
        generate_btn = tk.Button(buttons_frame, text="📄 Generar Contrato Excel",
                               command=self.generate_contract,
                               bg='#27ae60', fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               relief='flat', bd=0, padx=20, pady=10,
                               cursor='hand2')
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón abrir carpeta
        folder_btn = tk.Button(buttons_frame, text="📁 Abrir Carpeta",
                              command=self.open_employee_folder,
                              bg='#3498db', fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=15, pady=10,
                              cursor='hand2')
        folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón refresh
        refresh_btn = tk.Button(buttons_frame, text="🔄 Actualizar",
                              command=self.refresh_files_list,
                              bg='#f39c12', fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=15, pady=10,
                              cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón cerrar
        close_btn = tk.Button(buttons_frame, text="❌ Cerrar",
                            command=self.window.destroy,
                            bg='#e74c3c', fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat', bd=0, padx=15, pady=10,
                            cursor='hand2')
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def load_contracts(self):
        """Cargar contratos disponibles"""
        try:
            db = get_db()
            contratos = db.query(Contrato).join(Empleado).all()
            
            contract_options = []
            self.contracts_dict = {}
            
            for contrato in contratos:
                display_text = f"{contrato.numero_contrato or 'SIN-NUM'} - {contrato.empleado.nombre_completo}"
                contract_options.append(display_text)
                self.contracts_dict[display_text] = contrato
            
            self.contract_combo['values'] = contract_options
            
            # Si se pasó un contrato específico, seleccionarlo
            if self.contrato:
                for display_text, contract_obj in self.contracts_dict.items():
                    if contract_obj.id == self.contrato.id:
                        self.contract_combo.set(display_text)
                        self.on_contract_selected()
                        break
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando contratos: {e}")
    
    def load_contract_data(self):
        """Cargar datos del contrato seleccionado"""
        if self.contrato:
            display_text = f"{self.contrato.numero_contrato or 'SIN-NUM'} - {self.contrato.empleado.nombre_completo}"
            self.contract_combo.set(display_text)
            self.on_contract_selected()
    
    def on_contract_selected(self, event=None):
        """Manejar selección de contrato"""
        selected = self.contract_var.get()
        if selected in self.contracts_dict:
            contrato = self.contracts_dict[selected]
            empleado = contrato.empleado
            
            # Actualizar información
            self.info_labels['empleado'].config(text=empleado.nombre_completo)
            self.info_labels['cedula'].config(text=empleado.cedula)
            self.info_labels['tipo'].config(text=contrato.tipo_contrato or "No definido")
            self.info_labels['estado'].config(text=contrato.estado or "borrador")
            
            # Actualizar lista de archivos
            self.refresh_files_list()
    
    def toggle_custom_template(self):
        """Alternar uso de template personalizado"""
        if self.use_custom_template.get():
            self.template_entry.config(state='normal')
            self.browse_btn.config(state='normal')
        else:
            self.template_entry.config(state='disabled')
            self.browse_btn.config(state='disabled')
            self.template_path_var.set("")
    
    def browse_template(self):
        """Buscar template personalizado"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Template de Contrato",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.template_path_var.set(file_path)
    
    def refresh_files_list(self):
        """Actualizar lista de archivos existentes"""
        try:
            # Limpiar lista actual
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            # Obtener contrato seleccionado
            selected = self.contract_var.get()
            if not selected or selected not in self.contracts_dict:
                return
            
            contrato = self.contracts_dict[selected]
            empleado = contrato.empleado
            
            # Obtener archivos existentes
            contracts = self.generator.list_employee_contracts(empleado.id)
            
            for contract_file in contracts:
                # Formatear tamaño
                size_kb = contract_file['size'] / 1024
                size_text = f"{size_kb:.1f} KB"
                
                # Formatear fecha
                date_text = contract_file['modified'].strftime("%d/%m/%Y %H:%M")
                
                self.files_tree.insert('', tk.END, values=(
                    contract_file['filename'],
                    date_text,
                    size_text
                ))
            
        except Exception as e:
            print(f"Error actualizando lista de archivos: {e}")
    
    def generate_contract(self):
        """Generar contrato en Excel"""
        try:
            if not OPENPYXL_AVAILABLE:
                messagebox.showerror("Error", 
                    "La librería openpyxl no está instalada.\n\n" +
                    "Para instalar ejecute: pip install openpyxl")
                return
            
            # Validar selección
            selected = self.contract_var.get()
            if not selected or selected not in self.contracts_dict:
                messagebox.showwarning("Advertencia", "Seleccione un contrato")
                return
            
            contrato = self.contracts_dict[selected]
            
            # Obtener template
            template_path = None
            if self.use_custom_template.get() and self.template_path_var.get():
                template_path = Path(self.template_path_var.get())
                if not template_path.exists():
                    messagebox.showerror("Error", "El template seleccionado no existe")
                    return
            
            # Mostrar progreso
            progress_window = self.show_progress_window()
            
            # Generar contrato
            self.window.update()
            result = self.generator.generate_contract_excel(contrato.id, template_path)
            
            # Cerrar ventana de progreso
            progress_window.destroy()
            
            if result['success']:
                # Actualizar lista de archivos
                self.refresh_files_list()
                
                # Mostrar resultado exitoso
                if messagebox.askyesno("Éxito", 
                    f"Contrato generado exitosamente:\n\n" +
                    f"Empleado: {contrato.empleado.nombre_completo}\n" +
                    f"Archivo: {Path(result['file_path']).name}\n\n" +
                    "¿Desea abrir el archivo?"):
                    self.open_file(result['file_path'])
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando contrato: {e}")
    
    def show_progress_window(self):
        """Mostrar ventana de progreso"""
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Generando Contrato")
        progress_window.geometry("300x100")
        progress_window.configure(bg='white')
        progress_window.resizable(False, False)
        
        # Centrar ventana
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (100 // 2)
        progress_window.geometry(f"300x100+{x}+{y}")
        
        # Contenido
        tk.Label(progress_window, text="Generando contrato Excel...",
                font=('Segoe UI', 12),
                bg='white', fg='#2c3e50').pack(expand=True)
        
        # Barra de progreso
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        progress_window.update()
        
        return progress_window
    
    def open_selected_file(self, event=None):
        """Abrir archivo seleccionado"""
        selection = self.files_tree.selection()
        if not selection:
            return
        
        item = self.files_tree.item(selection[0])
        filename = item['values'][0]
        
        # Obtener ruta completa
        selected = self.contract_var.get()
        if selected in self.contracts_dict:
            contrato = self.contracts_dict[selected]
            contracts_folder = self.generator.get_employee_contracts_folder(contrato.empleado.id)
            if contracts_folder:
                file_path = contracts_folder / filename
                if file_path.exists():
                    self.open_file(str(file_path))
    
    def open_file(self, file_path):
        """Abrir archivo con aplicación por defecto"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['start', file_path], shell=True, check=True)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', file_path], check=True)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
    
    def open_employee_folder(self):
        """Abrir carpeta del empleado"""
        try:
            selected = self.contract_var.get()
            if not selected or selected not in self.contracts_dict:
                messagebox.showwarning("Advertencia", "Seleccione un contrato")
                return
            
            contrato = self.contracts_dict[selected]
            employee_folder = self.generator.create_employee_folder(contrato.empleado)
            
            if employee_folder and employee_folder.exists():
                import subprocess
                import platform
                
                system = platform.system()
                if system == 'Windows':
                    subprocess.run(['explorer', str(employee_folder)], check=True)
                elif system == 'Darwin':  # macOS
                    subprocess.run(['open', str(employee_folder)], check=True)
                else:  # Linux
                    subprocess.run(['xdg-open', str(employee_folder)], check=True)
            else:
                messagebox.showerror("Error", "No se pudo acceder a la carpeta del empleado")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo carpeta: {e}")


# ============= INTEGRACIÓN CON EL SISTEMA EXISTENTE =============

def integrar_generador_contratos():
    """Función para integrar el generador en contratos_view.py"""
    
    # Esta función se debe agregar a la clase ContratosWindow en contratos_view.py
    def generar_contrato_excel(self):
        """Generar contrato en Excel - Nueva funcionalidad"""
        contrato = self.get_selected_contrato()
        if contrato:
            ContratoExcelWindow(self.window, self, contrato)
    
    # Código para agregar botón en contratos_view.py
    boton_excel_code = '''
    # Agregar este botón en el create_widgets de ContratosWindow
    excel_btn = tk.Button(btn_frame, text="📄 Generar Excel", 
                         command=self.generar_contrato_excel,
                         bg="#27ae60", fg='white', font=('Arial', 10, 'bold'),
                         relief='flat', padx=15, pady=8, cursor='hand2')
    excel_btn.pack(side=tk.LEFT, padx=8)
    '''
    
    return boton_excel_code


# ============= UTILIDADES ADICIONALES =============

class ContractTemplateManager:
    """Gestor de templates de contratos"""
    
    def __init__(self):
        self.templates_dir = Path("templates_contratos")
        self.templates_dir.mkdir(exist_ok=True)
    
    def create_advanced_template(self):
        """Crear template avanzado con más opciones"""
        if not OPENPYXL_AVAILABLE:
            return
        
        template_path = self.templates_dir / "template_contrato_avanzado.xlsx"
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Contrato Laboral"
            
            # Configuración avanzada con colores y estilos
            # ... (código para template avanzado)
            
            wb.save(template_path)
            print(f"Template avanzado creado: {template_path}")
            
        except Exception as e:
            print(f"Error creando template avanzado: {e}")
    
    def validate_template(self, template_path):
        """Validar que el template tenga los placeholders necesarios"""
        if not OPENPYXL_AVAILABLE:
            return False, "openpyxl no disponible"
        
        try:
            wb = openpyxl.load_workbook(template_path)
            ws = wb.active
            
            required_placeholders = [
                '{{NOMBRE_EMPLEADO}}', '{{CEDULA_EMPLEADO}}', 
                '{{NUMERO_CONTRATO}}', '{{FECHA_INICIO}}'
            ]
            
            found_placeholders = []
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        for placeholder in required_placeholders:
                            if placeholder in cell.value and placeholder not in found_placeholders:
                                found_placeholders.append(placeholder)
            
            missing = [p for p in required_placeholders if p not in found_placeholders]
            
            if missing:
                return False, f"Faltan placeholders: {', '.join(missing)}"
            
            return True, "Template válido"
            
        except Exception as e:
            return False, f"Error validando template: {e}"


# ============= FUNCIÓN PRINCIPAL PARA INTEGRAR =============

def abrir_generador_contratos_excel(parent, main_window, contrato=None):
    """Función principal para abrir el generador de contratos Excel"""
    try:
        ContratoExcelWindow(parent, main_window, contrato)
    except Exception as e:
        messagebox.showerror("Error", f"Error abriendo generador de contratos: {e}")


# ============= INSTRUCCIONES DE INTEGRACIÓN =============

integration_instructions = """
INSTRUCCIONES PARA INTEGRAR EL GENERADOR DE CONTRATOS EXCEL:

1. INSTALAR DEPENDENCIAS:
   pip install openpyxl

2. AGREGAR IMPORTACIÓN en contratos_view.py:
   from utils.contrato_excel_generator import abrir_generador_contratos_excel

3. AGREGAR MÉTODO en la clase ContratosWindow:
   def generar_contrato_excel(self):
       contrato = self.get_selected_contrato()
       if contrato:
           abrir_generador_contratos_excel(self.window, self, contrato)

4. AGREGAR BOTÓN en create_widgets() de ContratosWindow:
   excel_btn = tk.Button(btn_frame, text="📄 Excel", 
                        command=self.generar_contrato_excel,
                        bg="#27ae60", fg='white', font=('Arial', 10, 'bold'),
                        relief='flat', padx=15, pady=8, cursor='hand2')
   excel_btn.pack(side=tk.LEFT, padx=8)

5. ESTRUCTURA DE CARPETAS CREADA:
   empleados_data/
   ├── NombreEmpleado_Cedula/
   │   ├── contratos/          # Contratos Excel generados
   │   ├── documentos/         # Otros documentos
   │   ├── nomina/             # Archivos de nómina
   │   └── historiales/        # Historiales laborales
   
6. CARACTERÍSTICAS:
   ✅ Genera contratos Excel personalizados
   ✅ Crea carpetas automáticas por empleado
   ✅ Template personalizable con placeholders
   ✅ Lista archivos generados anteriormente
   ✅ Abre archivos y carpetas automáticamente
   ✅ Integración completa con sistema existente

7. PLACEHOLDERS DISPONIBLES:
   {{NOMBRE_EMPLEADO}}, {{CEDULA_EMPLEADO}}, {{NUMERO_CONTRATO}}
   {{FECHA_ELABORACION}}, {{FECHA_INICIO}}, {{FECHA_FIN}}
   {{TIPO_CONTRATO}}, {{AREA_TRABAJO}}, {{CARGO_EMPLEADO}}
   {{SALARIO_BASE}}, {{SUBSIDIO_TRANSPORTE}}, {{BONIFICACIONES}}
   {{TOTAL_DEVENGADO}}, {{TELEFONO_EMPLEADO}}, {{EMAIL_EMPLEADO}}
"""

print(integration_instructions)