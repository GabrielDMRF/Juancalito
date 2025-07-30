#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRACIÓN DE AUTO-GENERACIÓN DE EXCEL EN EL SISTEMA EXISTENTE
Modificaciones mínimas para agregar funcionalidad de Excel automático
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime
from pathlib import Path

# Importaciones para Excel (opcional)
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# ================= GESTOR DE EXCEL PARA EMPLEADOS =================

class AutoExcelEmployeeManager:
    """Gestor de auto-generación de Excel para empleados"""
    
    def __init__(self):
        self.base_dir = Path("empleados_data")
        self.templates_dir = Path("templates_empleados")
        self.setup_directories()
    
    def setup_directories(self):
        """Configurar directorios necesarios"""
        try:
            self.base_dir.mkdir(exist_ok=True)
            self.templates_dir.mkdir(exist_ok=True)
            self.create_employee_template()
            print(f"✅ Sistema auto-Excel configurado en: {self.base_dir}")
        except Exception as e:
            print(f"❌ Error configurando sistema: {e}")
    
    def create_employee_template(self):
        """Crear template básico para empleados"""
        if not OPENPYXL_AVAILABLE:
            print("⚠️ openpyxl no disponible - no se puede crear template Excel")
            return
            
        template_path = self.templates_dir / "template_empleado_auto.xlsx"
        
        if template_path.exists():
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Información Empleado"
            
            # Estilos
            title_font = Font(name='Arial', size=16, bold=True)
            header_font = Font(name='Arial', size=12, bold=True)
            normal_font = Font(name='Arial', size=11)
            
            # TÍTULO PRINCIPAL
            ws['A1'] = "INFORMACIÓN DE EMPLEADO"
            ws['A1'].font = title_font
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:F1')
            ws.row_dimensions[1].height = 35
            
            # DATOS BÁSICOS
            ws['A3'] = "EMPRESA: FLORES JUNCALITO S.A.S"
            ws['A3'].font = header_font
            ws['A3'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A3:F3')
            
            # Información del empleado
            row = 5
            employee_info = [
                ["DATOS PERSONALES", "", "", ""],
                ["Nombre Completo:", "{{NOMBRE_EMPLEADO}}", "Cédula:", "{{CEDULA_EMPLEADO}}"],
                ["Teléfono:", "{{TELEFONO_EMPLEADO}}", "Email:", "{{EMAIL_EMPLEADO}}"],
                ["Dirección:", "{{DIRECCION_EMPLEADO}}", "Fecha Registro:", "{{FECHA_REGISTRO}}"],
                ["", "", "", ""],
                ["DATOS LABORALES", "", "", ""],
                ["Área de Trabajo:", "{{AREA_TRABAJO}}", "Cargo:", "{{CARGO_EMPLEADO}}"],
                ["Salario Base:", "{{SALARIO_BASE}}", "Estado:", "{{ESTADO_EMPLEADO}}"],
                ["Fecha Ingreso:", "{{FECHA_INGRESO}}", "Carpeta Personal:", "{{CARPETA_PERSONAL}}"],
                ["", "", "", ""],
                ["INFORMACIÓN ADICIONAL", "", "", ""],
                ["ID Sistema:", "{{ID_EMPLEADO}}", "Fecha Creación:", "{{FECHA_CREACION}}"],
                ["Observaciones:", "{{OBSERVACIONES}}", "", ""]
            ]
            
            # Crear tabla con bordes
            thin_border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin')
            )
            
            for fila_data in employee_info:
                for col, valor in enumerate(fila_data, 1):
                    if col <= 4:
                        cell = ws.cell(row=row, column=col, value=valor)
                        cell.border = thin_border
                        cell.alignment = Alignment(vertical='center', wrap_text=True)
                        
                        if valor in ["DATOS PERSONALES", "DATOS LABORALES", "INFORMACIÓN ADICIONAL"]:
                            # Headers de sección
                            cell.font = Font(name='Arial', size=12, bold=True, color="FFFFFF")
                            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                            ws.merge_cells(f'{get_column_letter(col)}{row}:{get_column_letter(col+3)}{row}')
                        elif col in [1, 3] and valor.endswith(":"):
                            # Labels de campos
                            cell.font = Font(name='Arial', size=10, bold=True)
                            cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
                        else:
                            # Valores
                            cell.font = Font(name='Arial', size=10)
                
                ws.row_dimensions[row].height = 25
                row += 1
            
            # Configurar anchos
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 25
            
            # Notas adicionales
            row += 2
            ws[f'A{row}'] = "NOTAS IMPORTANTES:"
            ws[f'A{row}'].font = header_font
            ws.merge_cells(f'A{row}:F{row}')
            row += 1
            
            notes = [
                "• Este archivo se genera automáticamente al registrar el empleado",
                "• Los datos se sincronizan con la base de datos del sistema",
                "• Mantener actualizada la información de contacto",
                "• Para modificaciones contactar al área de Recursos Humanos"
            ]
            
            for note in notes:
                ws[f'A{row}'] = note
                ws[f'A{row}'].font = normal_font
                ws.merge_cells(f'A{row}:F{row}')
                row += 1
            
            # Footer
            row += 2
            ws[f'A{row}'] = f"Generado automáticamente por Sistema de Gestión Personal"
            ws[f'A{row}'].font = Font(name='Arial', size=9, italic=True)
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            ws.merge_cells(f'A{row}:F{row}')
            
            wb.save(template_path)
            print(f"✅ Template de empleado creado: {template_path}")
            
        except Exception as e:
            print(f"❌ Error creando template: {e}")
    
    def create_employee_folder(self, empleado):
        """Crear carpeta personalizada para empleado"""
        try:
            nombre_seguro = self.safe_filename(empleado.nombre_completo)
            cedula_segura = self.safe_filename(empleado.cedula)
            
            folder_name = f"{nombre_seguro}_{cedula_segura}"
            employee_folder = self.base_dir / folder_name
            
            employee_folder.mkdir(exist_ok=True)
            
            # Crear subcarpetas
            subcarpetas = ["contratos", "documentos", "nomina", "historiales", "informacion_personal"]
            for subcarpeta in subcarpetas:
                (employee_folder / subcarpeta).mkdir(exist_ok=True)
            
            return employee_folder
            
        except Exception as e:
            print(f"Error creando carpeta para empleado: {e}")
            return None
    
    def safe_filename(self, filename):
        """Crear nombre de archivo seguro"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_')
        
        return filename[:50]
    
    def auto_generate_employee_excel(self, empleado):
        """Generar automáticamente Excel al crear empleado"""
        if not OPENPYXL_AVAILABLE:
            return {
                'success': False,
                'error': 'openpyxl no instalado',
                'message': 'Para generar Excel automáticamente, instale: pip install openpyxl'
            }
        
        try:
            # Crear carpeta del empleado
            employee_folder = self.create_employee_folder(empleado)
            if not employee_folder:
                raise Exception("No se pudo crear la carpeta del empleado")
            
            # Usar template
            template_path = self.templates_dir / "template_empleado_auto.xlsx"
            if not template_path.exists():
                self.create_employee_template()
            
            # Cargar template
            wb = openpyxl.load_workbook(template_path)
            ws = wb.active
            
            # Preparar datos para reemplazar
            data_replacements = self.prepare_employee_data(empleado, employee_folder)
            
            # Reemplazar placeholders
            self.replace_placeholders_in_worksheet(ws, data_replacements)
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"info_empleado_{empleado.cedula}_{timestamp}.xlsx"
            excel_path = employee_folder / "informacion_personal" / excel_filename
            
            # Guardar Excel generado
            wb.save(excel_path)
            
            return {
                'success': True,
                'file_path': str(excel_path),
                'employee_folder': str(employee_folder),
                'message': f'Excel generado automáticamente para {empleado.nombre_completo}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error generando Excel: {e}'
            }
    
    def prepare_employee_data(self, empleado, employee_folder):
        """Preparar datos del empleado para el Excel"""
        try:
            # Formatear fechas
            fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fecha_ingreso = empleado.fecha_ingreso.strftime("%d/%m/%Y") if empleado.fecha_ingreso else "No definida"
            fecha_creacion = empleado.fecha_creacion.strftime("%d/%m/%Y %H:%M:%S") if hasattr(empleado, 'fecha_creacion') and empleado.fecha_creacion else fecha_registro
            
            # Formatear salario
            salario_formateado = f"${empleado.salario_base:,}" if empleado.salario_base else "No definido"
            
            # Estado
            estado_texto = "ACTIVO" if empleado.estado else "INACTIVO"
            
            # Preparar datos
            data = {
                '{{NOMBRE_EMPLEADO}}': empleado.nombre_completo or "",
                '{{CEDULA_EMPLEADO}}': empleado.cedula or "",
                '{{TELEFONO_EMPLEADO}}': empleado.telefono or "No definido",
                '{{EMAIL_EMPLEADO}}': empleado.email or "No definido",
                '{{DIRECCION_EMPLEADO}}': empleado.direccion or "No definida",
                '{{FECHA_REGISTRO}}': fecha_registro,
                '{{AREA_TRABAJO}}': empleado.area_trabajo or "No definida",
                '{{CARGO_EMPLEADO}}': empleado.cargo or "No definido",
                '{{SALARIO_BASE}}': salario_formateado,
                '{{ESTADO_EMPLEADO}}': estado_texto,
                '{{FECHA_INGRESO}}': fecha_ingreso,
                '{{CARPETA_PERSONAL}}': str(employee_folder),
                '{{ID_EMPLEADO}}': str(empleado.id) if hasattr(empleado, 'id') else "Pendiente",
                '{{FECHA_CREACION}}': fecha_creacion,
                '{{OBSERVACIONES}}': "Empleado registrado en el sistema"
            }
            
            return data
            
        except Exception as e:
            print(f"Error preparando datos del empleado: {e}")
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


# ================= MODIFICACIÓN DE LA CLASE EmpleadosWindow =================

# CÓDIGO PARA INTEGRAR EN src/views/main_window.py
# Modificar la clase EmpleadosWindow existente agregando estas funciones:

def integrar_auto_excel_en_empleados_window():
    """
    INTEGRACIÓN: Agregar estas modificaciones a la clase EmpleadosWindow existente
    """
    
    # 1. EN EL __init__ DE EmpleadosWindow, AGREGAR:
    init_code = """
    # En EmpleadosWindow.__init__, agregar después de las líneas existentes:
    
    # Inicializar gestor de auto-Excel
    self.auto_excel_manager = AutoExcelEmployeeManager()
    """
    
    # 2. EN create_widgets(), AGREGAR SECCIÓN DE EXCEL:
    create_widgets_addition = """
    # En EmpleadosWindow.create_widgets(), agregar después del área de trabajo:
    
    # NUEVA SECCIÓN: Opciones de Excel Automático
    excel_frame = tk.LabelFrame(main_frame, text="📊 Generación Automática Excel", 
                               font=('Arial', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50')
    excel_row = 10 if self.modo == "editar" else 9
    excel_frame.grid(row=excel_row, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))
    
    # Checkbox para generar Excel automáticamente
    self.auto_excel_var = tk.BooleanVar()
    self.auto_excel_var.set(True)  # Por defecto activado
    
    auto_excel_check = tk.Checkbutton(excel_frame, 
                                     text="Generar Excel automáticamente al guardar",
                                     variable=self.auto_excel_var,
                                     font=('Arial', 10),
                                     bg='#ecf0f1', fg='#2c3e50')
    auto_excel_check.pack(anchor='w', padx=10, pady=5)
    
    # Información sobre el Excel
    info_label = tk.Label(excel_frame, 
                         text="✓ Crea carpeta personal del empleado\\n✓ Genera Excel con información completa\\n✓ Organiza documentos automáticamente",
                         font=('Arial', 9), 
                         bg='#ecf0f1', fg='#7f8c8d',
                         justify=tk.LEFT)
    info_label.pack(anchor='w', padx=10, pady=(0, 10))
    
    # Actualizar texto del botón guardar
    texto_boton = "Actualizar" if self.modo == "editar" else "Guardar y Generar Excel"
    """
    
    # 3. REEMPLAZAR EL MÉTODO guardar_empleado() COMPLETO:
    nuevo_guardar_empleado = """
def guardar_empleado_con_excel(self):
    \"\"\"Guardar empleado y generar Excel automáticamente\"\"\"
    try:
        # Validar campos obligatorios
        if not self.entry_nombre.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            self.entry_nombre.focus()
            return
        
        if not self.entry_cedula.get().strip():
            messagebox.showerror("Error", "La cédula es obligatoria")
            self.entry_cedula.focus()
            return
        
        # Validar cédula única
        cedula_nueva = self.entry_cedula.get().strip()
        if self.modo == "nuevo" or (self.empleado and self.empleado.cedula != cedula_nueva):
            cedula_existente = self.db.query(Empleado).filter(Empleado.cedula == cedula_nueva).first()
            if cedula_existente:
                messagebox.showerror("Error", "Ya existe un empleado con esa cédula")
                self.entry_cedula.focus()
                return
        
        # Validar salario
        salario = 0
        if self.entry_salario.get().strip():
            try:
                salario = int(self.entry_salario.get().strip())
            except ValueError:
                messagebox.showerror("Error", "El salario debe ser un número")
                self.entry_salario.focus()
                return
        
        empleado_saved = None
        
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
            self.db.commit()  # Commit para obtener el ID
            empleado_saved = empleado
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
            
            self.db.commit()
            empleado_saved = self.empleado
            mensaje = "Empleado actualizado exitosamente"
        
        print(mensaje)
        
        # GENERAR EXCEL AUTOMÁTICAMENTE si está activado
        excel_result = None
        if self.auto_excel_var.get() and empleado_saved:
            try:
                # Mostrar ventana de progreso
                progress_window = self.show_progress_window()
                
                # Generar Excel automáticamente
                excel_result = self.auto_excel_manager.auto_generate_employee_excel(empleado_saved)
                
                # Cerrar ventana de progreso
                progress_window.destroy()
                
            except Exception as e:
                print(f"Error generando Excel automático: {e}")
                excel_result = {'success': False, 'error': str(e)}
        
        # Actualizar ventana principal
        self.main_window.cargar_empleados()
        
        # Mostrar resultado
        if excel_result and excel_result['success']:
            # Éxito con Excel
            if messagebox.askyesno("¡Empleado Registrado Exitosamente!", 
                f"✅ {mensaje}\\n\\n" +
                f"📊 Excel generado automáticamente\\n" +
                f"📁 Carpeta personal creada\\n" +
                f"📋 Información organizada\\n\\n" +
                "¿Desea abrir la carpeta del empleado?"):
                self.open_employee_folder(excel_result['employee_folder'])
            
        elif excel_result and not excel_result['success']:
            # Error con Excel pero empleado guardado
            messagebox.showwarning("Empleado Guardado - Excel no Generado", 
                f"✅ {mensaje}\\n\\n" +
                f"⚠️ No se pudo generar Excel automático:\\n{excel_result['message']}\\n\\n" +
                "El empleado se guardó correctamente en la base de datos.")
        else:
            # Solo empleado guardado
            messagebox.showinfo("Éxito", mensaje)
        
        # Limpiar campos o cerrar
        if self.modo == "nuevo":
            self.limpiar_campos()
        else:
            self.window.destroy()
        
    except Exception as e:
        self.db.rollback()
        print(f"Error al guardar: {e}")
        messagebox.showerror("Error", f"Error al guardar empleado: {e}")

def show_progress_window(self):
    \"\"\"Mostrar ventana de progreso para generación Excel\"\"\"
    progress_window = tk.Toplevel(self.window)
    progress_window.title("Generando Excel")
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
    tk.Label(progress_window, text="📊 Generando Excel automático...",
            font=('Segoe UI', 12),
            bg='white', fg='#2c3e50').pack(expand=True)
    
    # Barra de progreso
    progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
    progress_bar.pack(fill=tk.X, padx=20, pady=10)
    progress_bar.start()
    
    progress_window.update()
    
    return progress_window

def open_employee_folder(self, folder_path):
    \"\"\"Abrir carpeta del empleado\"\"\"
    try:
        import subprocess
        import platform
        
        system = platform.system()
        if system == 'Windows':
            subprocess.run(['explorer', folder_path], check=True)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', folder_path], check=True)
            
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")
    """
    
    return {
        'init_code': init_code,
        'create_widgets_addition': create_widgets_addition,
        'nuevo_guardar_empleado': nuevo_guardar_empleado
    }


# ================= INSTRUCCIONES DE IMPLEMENTACIÓN =================

def mostrar_instrucciones_implementacion():
    """Instrucciones paso a paso para implementar"""
    
    instrucciones = """
╔═══════════════════════════════════════════════════════════════╗
║                    INSTRUCCIONES DE IMPLEMENTACIÓN           ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ 1. INSTALAR DEPENDENCIA (si no está instalada):             ║
║    pip install openpyxl                                       ║
║                                                               ║
║ 2. AGREGAR AL INICIO del archivo main_window.py:            ║
║    - Copiar toda la clase AutoExcelEmployeeManager           ║
║    - Agregar después de las importaciones                     ║
║                                                               ║
║ 3. MODIFICAR EmpleadosWindow.__init__():                     ║
║    - Agregar: self.auto_excel_manager = AutoExcelEmployeeManager() ║
║                                                               ║
║ 4. MODIFICAR EmpleadosWindow.create_widgets():               ║
║    - Agregar la sección de Excel después del área de trabajo  ║
║    - Cambiar el texto del botón a "Guardar y Generar Excel"  ║
║                                                               ║
║ 5. REEMPLAZAR EmpleadosWindow.guardar_empleado():            ║
║    - Cambiar nombre a: guardar_empleado_con_excel()          ║
║    - Usar el código del método nuevo_guardar_empleado        ║
║                                                               ║
║ 6. AGREGAR MÉTODOS AUXILIARES:                               ║
║    - show_progress_window()                                   ║
║    - open_employee_folder()                                   ║
║                                                               ║
║ 7. ACTUALIZAR EL BOTÓN:                                      ║
║    - Cambiar command=self.guardar_empleado por              ║
║    - command=self.guardar_empleado_con_excel                 ║
║                                                               ║
║ ✅ RESULTADO:                                                ║
║    Al registrar un empleado nuevo:                           ║
║    • Se guarda en la base de datos                           ║
║    • Se crea carpeta personal automática                     ║
║    • Se genera Excel con información completa                ║
║    • Se organizan subcarpetas (contratos, documentos, etc.)  ║
║    • Opción de abrir carpeta automáticamente                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    
    return instrucciones


# ================= EJEMPLO DE INTEGRACIÓN COMPLETA =================

def ejemplo_integracion_completa():
    """Ejemplo de cómo quedaría la integración completa"""
    
    codigo_ejemplo = '''
# EN src/views/main_window.py - DESPUÉS DE LAS IMPORTACIONES:

# Agregar la clase AutoExcelEmployeeManager completa aquí

# MODIFICAR la clase EmpleadosWindow:

class EmpleadosWindow:
    def __init__(self, parent, main_window, modo="nuevo", empleado=None):
        self.parent = parent
        self.main_window = main_window
        self.db = get_db()
        self.modo = modo
        self.empleado = empleado
        
        # NUEVO: Inicializar gestor de auto-Excel
        self.auto_excel_manager = AutoExcelEmployeeManager()
        
        # Resto del código existente...
        self.window = tk.Toplevel(parent)
        titulo = "Editar Empleado" if modo == "editar" else "Nuevo Empleado"
        self.window.title(titulo)
        self.window.geometry("500x500")  # Aumentar altura
        self.window.configure(bg='#ecf0f1')
        self.create_widgets()
        
        if modo == "editar" and empleado:
            self.cargar_datos_empleado()
    
    def create_widgets(self):
        # Todo el código existente hasta la sección de área de trabajo...
        
        # NUEVO: Agregar después del área de trabajo
        excel_frame = tk.LabelFrame(main_frame, text="📊 Generación Automática Excel", 
                                   font=('Arial', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50')
        excel_row = 10 if self.modo == "editar" else 9
        excel_frame.grid(row=excel_row, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))
        
        self.auto_excel_var = tk.BooleanVar()
        self.auto_excel_var.set(True)
        
        auto_excel_check = tk.Checkbutton(excel_frame, 
                                         text="Generar Excel automáticamente al guardar",
                                         variable=self.auto_excel_var,
                                         font=('Arial', 10),
                                         bg='#ecf0f1', fg='#2c3e50')
        auto_excel_check.pack(anchor='w', padx=10, pady=5)
        
        # Resto de botones...
        texto_boton = "Actualizar" if self.modo == "editar" else "Guardar y Generar Excel"
        save_btn = tk.Button(btn_frame, text=texto_boton, 
                           command=self.guardar_empleado_con_excel,  # CAMBIADO
                           bg="#27ae60", fg="white", font=('Arial', 10, 'bold'),
                           relief='flat', padx=20, pady=8, cursor='hand2')
    
    # REEMPLAZAR el método guardar_empleado por guardar_empleado_con_excel
    # Usar el código completo del método nuevo_guardar_empleado mostrado arriba
    '''
    
    return codigo_ejemplo


# ================= TESTING Y VERIFICACIÓN =================

def test_auto_excel_functionality():
    """Función para probar la funcionalidad de Excel"""
    try:
        print("🧪 Probando funcionalidad de auto-Excel...")
        
        # Crear instancia del gestor
        manager = AutoExcelEmployeeManager()
        
        # Verificar que se crearon los directorios
        if manager.base_dir.exists() and manager.templates_dir.exists():
            print("✅ Directorios creados correctamente")
        else:
            print("❌ Error en creación de directorios")
            return False
        
        # Verificar template
        template_path = manager.templates_dir / "template_empleado_auto.xlsx"
        if template_path.exists():
            print("✅ Template de Excel creado")
        else:
            print("⚠️ Template no creado (verificar openpyxl)")
        
        print("✅ Sistema de auto-Excel configurado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False


# ================= CÓDIGO COMPLETO PARA COPY-PASTE =================

def get_complete_integration_code():
    """Código completo listo para integrar en main_window.py"""
    
    return '''
# ===== AGREGAR DESPUÉS DE LAS IMPORTACIONES EN main_window.py =====

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import sqlite3
from datetime import datetime, date
import csv
import sys, os
from pathlib import Path

# Importaciones para Excel (AGREGAR ESTAS)
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# ===== AGREGAR ESTA CLASE COMPLETA =====

class AutoExcelEmployeeManager:
    """Gestor de auto-generación de Excel para empleados"""
    
    def __init__(self):
        self.base_dir = Path("empleados_data")
        self.templates_dir = Path("templates_empleados")
        self.setup_directories()
    
    def setup_directories(self):
        """Configurar directorios necesarios"""
        try:
            self.base_dir.mkdir(exist_ok=True)
            self.templates_dir.mkdir(exist_ok=True)
            self.create_employee_template()
            print(f"✅ Sistema auto-Excel configurado en: {self.base_dir}")
        except Exception as e:
            print(f"❌ Error configurando sistema: {e}")
    
    def create_employee_template(self):
        """Crear template básico para empleados"""
        if not OPENPYXL_AVAILABLE:
            print("⚠️ openpyxl no disponible - no se puede crear template Excel")
            return
            
        template_path = self.templates_dir / "template_empleado_auto.xlsx"
        
        if template_path.exists():
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Información Empleado"
            
            # Estilos
            title_font = Font(name='Arial', size=16, bold=True)
            header_font = Font(name='Arial', size=12, bold=True)
            thin_border = Border(
                left=Side(style='thin'), right=Side(style='thin'),
                top=Side(style='thin'), bottom=Side(style='thin')
            )
            
            # TÍTULO PRINCIPAL
            ws['A1'] = "INFORMACIÓN DE EMPLEADO"
            ws['A1'].font = title_font
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:F1')
            
            # EMPRESA
            ws['A3'] = "EMPRESA: FLORES JUNCALITO S.A.S"
            ws['A3'].font = header_font
            ws['A3'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A3:F3')
            
            # Información del empleado
            row = 5
            employee_info = [
                ["DATOS PERSONALES", "", "", ""],
                ["Nombre Completo:", "{{NOMBRE_EMPLEADO}}", "Cédula:", "{{CEDULA_EMPLEADO}}"],
                ["Teléfono:", "{{TELEFONO_EMPLEADO}}", "Email:", "{{EMAIL_EMPLEADO}}"],
                ["Dirección:", "{{DIRECCION_EMPLEADO}}", "Fecha Registro:", "{{FECHA_REGISTRO}}"],
                ["", "", "", ""],
                ["DATOS LABORALES", "", "", ""],
                ["Área de Trabajo:", "{{AREA_TRABAJO}}", "Cargo:", "{{CARGO_EMPLEADO}}"],
                ["Salario Base:", "{{SALARIO_BASE}}", "Estado:", "{{ESTADO_EMPLEADO}}"],
                ["Fecha Ingreso:", "{{FECHA_INGRESO}}", "Carpeta Personal:", "{{CARPETA_PERSONAL}}"],
                ["", "", "", ""],
                ["INFORMACIÓN ADICIONAL", "", "", ""],
                ["ID Sistema:", "{{ID_EMPLEADO}}", "Fecha Creación:", "{{FECHA_CREACION}}"],
                ["Observaciones:", "{{OBSERVACIONES}}", "", ""]
            ]
            
            for fila_data in employee_info:
                for col, valor in enumerate(fila_data, 1):
                    if col <= 4:
                        cell = ws.cell(row=row, column=col, value=valor)
                        cell.border = thin_border
                        cell.alignment = Alignment(vertical='center', wrap_text=True)
                        
                        if valor in ["DATOS PERSONALES", "DATOS LABORALES", "INFORMACIÓN ADICIONAL"]:
                            cell.font = Font(name='Arial', size=12, bold=True, color="FFFFFF")
                            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                            ws.merge_cells(f'{get_column_letter(col)}{row}:{get_column_letter(col+3)}{row}')
                        elif col in [1, 3] and valor.endswith(":"):
                            cell.font = Font(name='Arial', size=10, bold=True)
                            cell.fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
                        else:
                            cell.font = Font(name='Arial', size=10)
                
                ws.row_dimensions[row].height = 25
                row += 1
            
            # Configurar anchos
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 25
            
            wb.save(template_path)
            print(f"✅ Template de empleado creado")
            
        except Exception as e:
            print(f"❌ Error creando template: {e}")
    
    def create_employee_folder(self, empleado):
        """Crear carpeta personalizada para empleado"""
        try:
            nombre_seguro = self.safe_filename(empleado.nombre_completo)
            cedula_segura = self.safe_filename(empleado.cedula)
            
            folder_name = f"{nombre_seguro}_{cedula_segura}"
            employee_folder = self.base_dir / folder_name
            
            employee_folder.mkdir(exist_ok=True)
            
            # Crear subcarpetas
            subcarpetas = ["contratos", "documentos", "nomina", "historiales", "informacion_personal"]
            for subcarpeta in subcarpetas:
                (employee_folder / subcarpeta).mkdir(exist_ok=True)
            
            return employee_folder
            
        except Exception as e:
            print(f"Error creando carpeta: {e}")
            return None
    
    def safe_filename(self, filename):
        """Crear nombre de archivo seguro"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        filename = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = filename.replace(' ', '_')
        
        return filename[:50]
    
    def auto_generate_employee_excel(self, empleado):
        """Generar automáticamente Excel al crear empleado"""
        if not OPENPYXL_AVAILABLE:
            return {
                'success': False,
                'error': 'openpyxl no instalado',
                'message': 'Para generar Excel automáticamente, instale: pip install openpyxl'
            }
        
        try:
            # Crear carpeta del empleado
            employee_folder = self.create_employee_folder(empleado)
            if not employee_folder:
                raise Exception("No se pudo crear la carpeta del empleado")
            
            # Usar template
            template_path = self.templates_dir / "template_empleado_auto.xlsx"
            if not template_path.exists():
                self.create_employee_template()
            
            # Cargar template
            wb = openpyxl.load_workbook(template_path)
            ws = wb.active
            
            # Preparar datos
            data_replacements = self.prepare_employee_data(empleado, employee_folder)
            
            # Reemplazar placeholders
            self.replace_placeholders_in_worksheet(ws, data_replacements)
            
            # Generar archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"info_empleado_{empleado.cedula}_{timestamp}.xlsx"
            excel_path = employee_folder / "informacion_personal" / excel_filename
            
            # Guardar Excel
            wb.save(excel_path)
            
            return {
                'success': True,
                'file_path': str(excel_path),
                'employee_folder': str(employee_folder),
                'message': f'Excel generado para {empleado.nombre_completo}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error generando Excel: {e}'
            }
    
    def prepare_employee_data(self, empleado, employee_folder):
        """Preparar datos del empleado para el Excel"""
        try:
            fecha_registro = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fecha_ingreso = empleado.fecha_ingreso.strftime("%d/%m/%Y") if hasattr(empleado, 'fecha_ingreso') and empleado.fecha_ingreso else "No definida"
            salario_formateado = f"${empleado.salario_base:,}" if empleado.salario_base else "No definido"
            estado_texto = "ACTIVO" if empleado.estado else "INACTIVO"
            
            return {
                '{{NOMBRE_EMPLEADO}}': empleado.nombre_completo or "",
                '{{CEDULA_EMPLEADO}}': empleado.cedula or "",
                '{{TELEFONO_EMPLEADO}}': empleado.telefono or "No definido",
                '{{EMAIL_EMPLEADO}}': empleado.email or "No definido",
                '{{DIRECCION_EMPLEADO}}': empleado.direccion or "No definida",
                '{{FECHA_REGISTRO}}': fecha_registro,
                '{{AREA_TRABAJO}}': empleado.area_trabajo or "No definida",
                '{{CARGO_EMPLEADO}}': empleado.cargo or "No definido",
                '{{SALARIO_BASE}}': salario_formateado,
                '{{ESTADO_EMPLEADO}}': estado_texto,
                '{{FECHA_INGRESO}}': fecha_ingreso,
                '{{CARPETA_PERSONAL}}': str(employee_folder),
                '{{ID_EMPLEADO}}': str(empleado.id) if hasattr(empleado, 'id') else "Generando...",
                '{{FECHA_CREACION}}': fecha_registro,
                '{{OBSERVACIONES}}': "Empleado registrado automáticamente"
            }
            
        except Exception as e:
            print(f"Error preparando datos: {e}")
            return {}
    
    def replace_placeholders_in_worksheet(self, worksheet, data_replacements):
        """Reemplazar placeholders en la hoja"""
        try:
            for row in worksheet.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        for placeholder, replacement in data_replacements.items():
                            if placeholder in cell.value:
                                cell.value = cell.value.replace(placeholder, str(replacement))
        except Exception as e:
            print(f"Error reemplazando placeholders: {e}")

# ===== MODIFICAR LA CLASE EmpleadosWindow EXISTENTE =====

# En EmpleadosWindow.__init__, AGREGAR esta línea después de self.empleado = empleado:
# self.auto_excel_manager = AutoExcelEmployeeManager()

# En EmpleadosWindow.create_widgets(), AGREGAR después del combo_area:

"""
# SECCIÓN DE EXCEL AUTOMÁTICO - AGREGAR ESTO
excel_frame = tk.LabelFrame(main_frame, text="📊 Generación Automática Excel", 
                           font=('Arial', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50')
excel_row = 10 if self.modo == "editar" else 9
excel_frame.grid(row=excel_row, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))

self.auto_excel_var = tk.BooleanVar()
self.auto_excel_var.set(True)  # Por defecto activado

auto_excel_check = tk.Checkbutton(excel_frame, 
                                 text="Generar Excel automáticamente al guardar",
                                 variable=self.auto_excel_var,
                                 font=('Arial', 10),
                                 bg='#ecf0f1', fg='#2c3e50')
auto_excel_check.pack(anchor='w', padx=10, pady=5)

info_label = tk.Label(excel_frame, 
                     text="✓ Crea carpeta personal del empleado\\n✓ Genera Excel con información completa\\n✓ Organiza documentos automáticamente",
                     font=('Arial', 9), 
                     bg='#ecf0f1', fg='#7f8c8d',
                     justify=tk.LEFT)
info_label.pack(anchor='w', padx=10, pady=(0, 10))
"""

# CAMBIAR EL TEXTO DEL BOTÓN:
# texto_boton = "Actualizar" if self.modo == "editar" else "Guardar y Generar Excel"

# CAMBIAR EL COMMAND DEL BOTÓN:
# command=self.guardar_empleado_con_excel

# REEMPLAZAR COMPLETAMENTE el método guardar_empleado por este:
'''

def guardar_empleado_con_excel(self):
    """Guardar empleado y generar Excel automáticamente"""
    try:
        # Validaciones existentes
        if not self.entry_nombre.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            self.entry_nombre.focus()
            return
        
        if not self.entry_cedula.get().strip():
            messagebox.showerror("Error", "La cédula es obligatoria")
            self.entry_cedula.focus()
            return
        
        # Validar cédula única
        cedula_nueva = self.entry_cedula.get().strip()
        if self.modo == "nuevo" or (self.empleado and self.empleado.cedula != cedula_nueva):
            cedula_existente = self.db.query(Empleado).filter(Empleado.cedula == cedula_nueva).first()
            if cedula_existente:
                messagebox.showerror("Error", "Ya existe un empleado con esa cédula")
                self.entry_cedula.focus()
                return
        
        # Validar salario
        salario = 0
        if self.entry_salario.get().strip():
            try:
                salario = int(self.entry_salario.get().strip())
            except ValueError:
                messagebox.showerror("Error", "El salario debe ser un número")
                self.entry_salario.focus()
                return
        
        empleado_saved = None
        
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
            self.db.commit()  # Commit para obtener ID
            empleado_saved = empleado
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
            
            self.db.commit()
            empleado_saved = self.empleado
            mensaje = "Empleado actualizado exitosamente"
        
        # GENERAR EXCEL AUTOMÁTICAMENTE
        excel_result = None
        if hasattr(self, 'auto_excel_var') and self.auto_excel_var.get() and empleado_saved:
            try:
                # Mostrar progreso
                progress_window = self.show_progress_window()
                
                # Generar Excel
                excel_result = self.auto_excel_manager.auto_generate_employee_excel(empleado_saved)
                
                # Cerrar progreso
                progress_window.destroy()
                
            except Exception as e:
                excel_result = {'success': False, 'error': str(e)}
        
        # Actualizar interfaz
        self.main_window.cargar_empleados()
        
        # Mostrar resultado
        if excel_result and excel_result['success']:
            if messagebox.askyesno("¡Empleado Registrado!", 
                f"✅ {mensaje}\\n\\n" +
                f"📊 Excel generado automáticamente\\n" +
                f"📁 Carpeta personal creada\\n\\n" +
                "¿Abrir carpeta del empleado?"):
                self.open_employee_folder(excel_result['employee_folder'])
        elif excel_result and not excel_result['success']:
            messagebox.showwarning("Empleado Guardado", 
                f"✅ {mensaje}\\n\\n⚠️ Excel no generado: {excel_result['message']}")
        else:
            messagebox.showinfo("Éxito", mensaje)
        
        # Limpiar o cerrar
        if self.modo == "nuevo":
            self.limpiar_campos()
        else:
            self.window.destroy()
        
    except Exception as e:
        self.db.rollback()
        messagebox.showerror("Error", f"Error: {e}")

def show_progress_window(self):
    """Ventana de progreso"""
    progress_window = tk.Toplevel(self.window)
    progress_window.title("Generando Excel")
    progress_window.geometry("300x100")
    progress_window.configure(bg='white')
    progress_window.resizable(False, False)
    progress_window.transient(self.window)
    progress_window.grab_set()
    
    x = (progress_window.winfo_screenwidth() // 2) - 150
    y = (progress_window.winfo_screenheight() // 2) - 50
    progress_window.geometry(f"300x100+{x}+{y}")
    
    tk.Label(progress_window, text="📊 Generando Excel...",
            font=('Arial', 12), bg='white').pack(expand=True)
    
    progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
    progress_bar.pack(fill=tk.X, padx=20, pady=10)
    progress_bar.start()
    progress_window.update()
    
    return progress_window

def open_employee_folder(self, folder_path):
    """Abrir carpeta del empleado"""
    try:
        import subprocess
        import platform
        
        system = platform.system()
        if system == 'Windows':
            subprocess.run(['explorer', folder_path])
        elif system == 'Darwin':
            subprocess.run(['open', folder_path])
        else:
            subprocess.run(['xdg-open', folder_path])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir: {e}")

# ===== AGREGAR ESTOS MÉTODOS A LA CLASE EmpleadosWindow =====
''


# ================= RESUMEN DE CAMBIOS NECESARIOS =================

def resumen_cambios():
    """Resumen de todos los cambios necesarios"""
    
    return
# ================= VALIDACIÓN FINAL =================

def validar_integracion():
    """Validar que la integración sea correcta"""
    print("🔍 Validando integración...")
    
    checks = [
        ("Importación openpyxl", OPENPYXL_AVAILABLE),
        ("Clase AutoExcelEmployeeManager", 'AutoExcelEmployeeManager' in globals()),
        ("Directorio empleados_data", Path("empleados_data").exists()),
        ("Template directory", Path("templates_empleados").exists())
    ]
    
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {check_name}")
    
    return all(check[1] for check in checks)


if __name__ == "__main__":
    print("🔧 Sistema de Auto-Generación de Excel para Empleados")
    print("=" * 60)
    print(resumen_cambios())
    
    if validar_integracion():
        print("\n✅ Sistema listo para integración")
    else:
        print("\n⚠️ Verificar dependencias antes de integrar")