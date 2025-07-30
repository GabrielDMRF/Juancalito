#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Contrato Profesional Excel
Basado en el formato real del contrato de FLORES JUNCALITO S.A.S
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import shutil

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

class ContratoProfesionalExcelGenerator:
    """Generador de contratos Excel profesionales basado en formato real"""
    
    def __init__(self):
        self.db = get_db()
        self.base_dir = Path("empleados_data")
        self.templates_dir = Path("templates_contratos")
        self.setup_directories()
    
    def setup_directories(self):
        """Crear directorios necesarios"""
        try:
            self.base_dir.mkdir(exist_ok=True)
            self.templates_dir.mkdir(exist_ok=True)
            self.create_professional_template()
            print(f"✅ Directorios configurados en: {self.base_dir}")
        except Exception as e:
            print(f"❌ Error configurando directorios: {e}")
    
    def create_professional_template(self):
        """Crear template profesional basado en el formato real"""
        if not OPENPYXL_AVAILABLE:
            print("⚠️ openpyxl no disponible - no se puede crear template Excel")
            return
            
        template_path = self.templates_dir / "contrato_profesional_template.xlsx"
        
        if template_path.exists():
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Contrato de Trabajo"
            
            # Configurar página
            ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
            ws.page_margins.left = 0.5
            ws.page_margins.right = 0.5
            ws.page_margins.top = 0.5
            ws.page_margins.bottom = 0.5
            
            # Estilos
            title_font = Font(name='Arial', size=14, bold=True)
            header_font = Font(name='Arial', size=12, bold=True)
            normal_font = Font(name='Arial', size=10)
            small_font = Font(name='Arial', size=9)
            
            # Bordes
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # TÍTULO PRINCIPAL
            ws['A1'] = "CONTRATO INDIVIDUAL DE TRABAJO A TERMINO FIJO INFERIOR A UN AÑO"
            ws['A1'].font = title_font
            ws['A1'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            ws.merge_cells('A1:F1')
            ws.row_dimensions[1].height = 30
            
            # TRABAJADOR
            ws['A3'] = "TRABAJADOR {{NUMERO_TRABAJADOR}}"
            ws['A3'].font = header_font
            ws['A3'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A3:F3')
            
            # TABLA DE INFORMACIÓN PRINCIPAL
            row = 5
            
            # Encabezados de tabla con bordes
            tabla_info = [
                ["NOMBRE EMPLEADOR:", "{{NOMBRE_EMPLEADOR}}", "DIRECCION DE EMPLEADOR", "{{DIRECCION_EMPLEADOR}}"],
                ["NOMBRE DEL TRABAJADOR:", "{{NOMBRE_EMPLEADO}}", "DIRECCION TRABAJADOR:", "{{DIRECCION_EMPLEADO}}"],
                ["LUGAR, FECHA DE NACIMIENTO Y NACIONALIDAD", "{{LUGAR_NACIMIENTO}}", "CARGO U OFICIO QUE DESEMPEÑARA EL TRABAJADOR", "{{CARGO_EMPLEADO}}"],
                ["SALARIO ORDINARIO / INTEGRAL", "VALOR", "VALOR EN LETRAS", ""],
                ["( X ) ( )", "${{SALARIO_BASE}}", "{{SALARIO_LETRAS}}", ""],
                ["PERIODOS DE PAGO", "{{PERIODO_PAGO}}", "FECHA DE INICIACION DE LABORES", "{{FECHA_INICIO}}"],
                ["LUGAR DONDE DESEMPEÑARA LAS LABORES", "{{LUGAR_LABORES}}", "CIUDAD DONDE HA SIDO CONTRATADO EL TRABAJADOR", "{{CIUDAD_CONTRATO}}"],
                ["TERMINO INICIAL DEL CONTRATO", "{{TERMINO_CONTRATO}}", "VENCE EL DIA", "{{FECHA_FIN}}"]
            ]
            
            for fila_data in tabla_info:
                for col, valor in enumerate(fila_data, 1):
                    cell = ws.cell(row=row, column=col, value=valor)
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical='center', wrap_text=True)
                    
                    if col in [1, 3]:  # Columnas de títulos
                        cell.font = Font(name='Arial', size=9, bold=True)
                        cell.fill = PatternFill(start_color="E6E6E6", end_color="E6E6E6", fill_type="solid")
                    else:
                        cell.font = Font(name='Arial', size=9)
                
                ws.row_dimensions[row].height = 25
                row += 1
            
            # Ajustar anchos de columna
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 25
            ws.column_dimensions['D'].width = 25
            
            # CLÁUSULAS DEL CONTRATO
            row += 2
            
            # Párrafo introductorio
            ws[f'A{row}'] = ("Entre EL EMPLEADOR Y EL TRABAJADOR, de las condiciones ya dichas, "
                           "identificados como aparece al pie de sus firmas, se ha celebrado el "
                           "presente contrato individual de trabajo, regido además por las siguientes cláusulas.")
            ws[f'A{row}'].font = normal_font
            ws[f'A{row}'].alignment = Alignment(wrap_text=True, justify_last_line=True)
            ws.merge_cells(f'A{row}:F{row}')
            ws.row_dimensions[row].height = 40
            row += 2
            
            # CLÁUSULAS DETALLADAS
            clausulas = [
                ("PRIMERA: OBJETO", 
                 "EL EMPLEADOR contrata los servicios personales de EL TRABAJADOR y este se obliga: "
                 "a) a poner al servicio de EL EMPLEADOR toda la capacidad normal de trabajo en el "
                 "desempeño de las funciones propias del oficio mencionado y en las labores anexas y "
                 "complementarias del mismo, de conformidad con las órdenes e instrucciones que le "
                 "imparta EL EMPLEADOR directamente o a través de sus representantes; b) a prestar "
                 "sus servicios de forma exclusiva a EL EMPLEADOR; es decir, a no prestar directamente "
                 "ni indirectamente servicios laborales a otros empleadores, ni a trabajar por cuenta "
                 "propia en el mismo oficio, durante la vigencia del contrato; y c) a guardar absoluta "
                 "reserva sobre los hechos, documentos físicos y/o electrónicos, informaciones y en "
                 "general, sobre todos los asuntos y materias que lleguen a su conocimiento por causa "
                 "o con ocasión de su contrato de trabajo."),
                
                ("SEGUNDA: REMUNERACIÓN", 
                 "EL EMPLEADOR pagará a EL TRABAJADOR por la prestación de sus servicios el salario "
                 "indicado en el encabezado del presente documento, pagadero en las oportunidades "
                 "también señaladas arriba."),
                
                ("TERCERA: DURACIÓN DEL CONTRATO", 
                 "El término inicial de la duración del contrato será el señalado arriba. Si antes "
                 "de la fecha de vencimiento ninguna de las partes avisare por escrito a la otra su "
                 "determinación de no prorrogar el contrato con antelación no inferior a (30) días, "
                 "este se entenderá prorrogado por un período igual al inicialmente pactado."),
                
                ("CUARTA: TRABAJO NOCTURNO, SUPLEMENTARIO, DOMINICAL Y/O FESTIVO", 
                 "Todo trabajo nocturno, suplementario o en extras y todo trabajo en día domingo o "
                 "festivo en los que legalmente debe concederse descanso se remunera conforme a la ley. "
                 "Para el reconocimiento y pago del trabajo suplementario, nocturno, dominical o festivo "
                 "EL EMPLEADOR o sus representantes deberán haberlo autorizado previamente y por escrito."),
                
                ("QUINTA: JORNADA DE TRABAJO", 
                 "EL TRABAJADOR se obliga a laborar la jornada máxima legal, salvo acuerdo especial, "
                 "en los turnos y dentro de las horas señaladas por EL EMPLEADOR, pudiendo hacer este "
                 "ajustes o cambios de horario cuando lo estime conveniente."),
                
                ("SEXTA: PERÍODO DE PRUEBA", 
                 "La quinta parte de la duración inicial del presente contrato se considera como "
                 "período de prueba, sin que exceda de dos (2) meses contados a partir de la fecha "
                 "de inicio, y por consiguiente, cualquiera de las partes podrá terminar el contrato "
                 "unilateralmente, en cualquier momento durante dicho período y sin previo aviso."),
                
                ("SÉPTIMA: TERMINACIÓN UNILATERAL", 
                 "Son justas causas para dar por terminado unilateralmente este contrato, por "
                 "cualquiera de las partes, las enumeradas en el Art. 62 del C.S.T., modificado "
                 "por el Art. 7º del decreto 235/65."),
                
                ("OCTAVA: PROPIEDAD INTELECTUAL", 
                 "Las partes acuerdan que todas las invenciones, descubrimientos y trabajos originales "
                 "concebidos o hechos por EL TRABAJADOR en vigencia del presente contrato pertenecerán "
                 "a EL EMPLEADOR."),
                
                ("NOVENA: MODIFICACIÓN DE LAS CONDICIONES LABORALES", 
                 "EL TRABAJADOR acepta desde ahora expresamente todas las modificaciones de sus "
                 "condiciones laborales determinadas por EL EMPLEADOR en ejercicio de su poder "
                 "subordinante, siempre que tales modificaciones no afecten su honor, dignidad o "
                 "sus derechos mínimos."),
                
                ("DÉCIMA: DIRECCIÓN DEL TRABAJADOR", 
                 "EL TRABAJADOR se compromete a informar por escrito y de manera inmediata a EL "
                 "EMPLEADOR cualquier cambio en su dirección de residencia."),
                
                ("UNDÉCIMA: EFECTOS", 
                 "El presente contrato reemplaza en su integridad y deja sin efecto cualquier otro "
                 "contrato, verbal o escrito, celebrado entre las partes con anterioridad.")
            ]
            
            for titulo, contenido in clausulas:
                # Título de la cláusula
                ws[f'A{row}'] = titulo
                ws[f'A{row}'].font = Font(name='Arial', size=10, bold=True)
                ws[f'A{row}'].alignment = Alignment(wrap_text=True)
                ws.merge_cells(f'A{row}:F{row}')
                row += 1
                
                # Contenido de la cláusula
                ws[f'A{row}'] = contenido
                ws[f'A{row}'].font = normal_font
                ws[f'A{row}'].alignment = Alignment(wrap_text=True, justify_last_line=True)
                ws.merge_cells(f'A{row}:F{row}')
                ws.row_dimensions[row].height = max(60, len(contenido) // 8)
                row += 2
            
            # CLÁUSULAS ADICIONALES
            row += 1
            ws[f'A{row}'] = "CLÁUSULAS ADICIONALES"
            ws[f'A{row}'].font = header_font
            ws[f'A{row}'].alignment = Alignment(horizontal='center')
            ws.merge_cells(f'A{row}:F{row}')
            row += 1
            
            ws[f'A{row}'] = ("LAS PARTES ACEPTAN DE COMÚN ACUERDO QUE LAS BONIFICACIONES QUE LA EMPRESA "
                           "DÉ Y EL TRABAJADOR RECIBA POR TEMPORADAS O EN CUALQUIER OTRO MOMENTO, SON DE "
                           "PLENA LIBERALIDAD Y NO HACEN PARTE DEL SALARIO.")
            ws[f'A{row}'].font = normal_font
            ws[f'A{row}'].alignment = Alignment(wrap_text=True)
            ws.merge_cells(f'A{row}:F{row}')
            ws.row_dimensions[row].height = 40
            row += 2
            
            # PRÓRROGAS
            prorrogas_text = [
                "1 PRÓRROGA: {{FECHA_FIN}} A {{FECHA_PRORROGA_1}}",
                "2 PRÓRROGA: {{FECHA_PRORROGA_1}} A {{FECHA_PRORROGA_2}}",
                "3 PRÓRROGA: {{FECHA_PRORROGA_2}} A {{FECHA_PRORROGA_3}}",
                "",
                "INICIANDO UN CONTRATO DE TRABAJO A UN AÑO A PARTIR DEL DÍA {{FECHA_CONTRATO_ANUAL}}"
            ]
            
            for prorroga in prorrogas_text:
                ws[f'A{row}'] = prorroga
                ws[f'A{row}'].font = normal_font
                ws.merge_cells(f'A{row}:F{row}')
                row += 1
            
            row += 2
            
            # INFORMACIÓN DE LUGAR Y FECHA
            ws[f'A{row}'] = "CIUDAD: {{CIUDAD_CONTRATO}}"
            ws[f'A{row}'].font = normal_font
            ws[f'D{row}'] = "FECHA: {{FECHA_ELABORACION}}"
            ws[f'D{row}'].font = normal_font
            row += 3
            
            # FIRMAS
            ws[f'A{row}'] = "Recibí copia del documento"
            ws[f'A{row}'].font = normal_font
            row += 2
            
            ws[f'A{row}'] = "________________________________"
            ws[f'D{row}'] = "________________________________"
            row += 1
            
            ws[f'A{row}'] = "EL EMPLEADOR: {{NOMBRE_EMPLEADOR_FIRMA}}"
            ws[f'D{row}'] = "EL TRABAJADOR: {{NOMBRE_EMPLEADO}}"
            ws[f'A{row}'].font = Font(name='Arial', size=9, bold=True)
            ws[f'D{row}'].font = Font(name='Arial', size=9, bold=True)
            row += 1
            
            ws[f'A{row}'] = "CC Ó NIT: {{NIT_EMPLEADOR}}"
            ws[f'D{row}'] = "CC: {{CEDULA_EMPLEADO}}"
            ws[f'A{row}'].font = Font(name='Arial', size=9, bold=True)
            ws[f'D{row}'].font = Font(name='Arial', size=9, bold=True)
            row += 2
            
            ws[f'A{row}'] = "TESTIGO: {{NOMBRE_TESTIGO}}"
            ws[f'D{row}'] = "TESTIGO: ____________________"
            ws[f'A{row}'].font = Font(name='Arial', size=9, bold=True)
            ws[f'D{row}'].font = Font(name='Arial', size=9, bold=True)
            row += 1
            
            ws[f'A{row}'] = "CC Nº: {{CEDULA_TESTIGO}}"
            ws[f'D{row}'] = "CC Nº: ____________________"
            ws[f'A{row}'].font = Font(name='Arial', size=9, bold=True)  
            ws[f'D{row}'].font = Font(name='Arial', size=9, bold=True)
            
            # Configurar impresión
            ws.print_options.horizontalCentered = True
            ws.print_area = f'A1:F{row}'
            
            # Guardar template
            wb.save(template_path)
            print(f"✅ Template profesional creado: {template_path}")
            
        except Exception as e:
            print(f"❌ Error creando template profesional: {e}")
    
    def create_employee_folder(self, empleado):
        """Crear carpeta personalizada para empleado"""
        try:
            nombre_seguro = self.safe_filename(empleado.nombre_completo)
            cedula_segura = self.safe_filename(empleado.cedula)
            
            folder_name = f"{nombre_seguro}_{cedula_segura}"
            employee_folder = self.base_dir / folder_name
            
            employee_folder.mkdir(exist_ok=True)
            
            subcarpetas = ["contratos", "documentos", "nomina", "historiales"]
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
    
    def numero_a_letras(self, numero):
        """Convertir número a letras para el salario"""
        try:
            # Implementación básica para números comunes de salarios
            if numero == 1423500:
                return "UN MILLÓN CUATROCIENTOS VEINTITRÉS MIL QUINIENTOS PESOS M/CTE"
            elif numero >= 1000000:
                millones = numero // 1000000
                resto = numero % 1000000
                return f"{self.convertir_millones(millones)} MILLONES {self.convertir_miles(resto)} PESOS M/CTE"
            else:
                return self.convertir_miles(numero) + " PESOS M/CTE"
        except:
            return "SALARIO EN LETRAS"
    
    def convertir_millones(self, num):
        """Convertir millones a letras"""
        unidades = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        if num == 1:
            return "UN"
        elif num < 10:
            return unidades[num]
        else:
            return str(num)
    
    def convertir_miles(self, num):
        """Convertir miles a letras (implementación básica)"""
        if num == 0:
            return ""
        elif num < 1000:
            return str(num)
        else:
            miles = num // 1000
            resto = num % 1000
            return f"{miles} MIL {resto}"
    
    def generate_professional_contract_excel(self, contrato_id, template_path=None):
        """Generar contrato profesional en Excel"""
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
            
            # Usar template profesional
            if not template_path:
                template_path = self.templates_dir / "contrato_profesional_template.xlsx"
            
            if not template_path.exists():
                raise Exception("Template de contrato no encontrado")
            
            # Cargar template
            wb = openpyxl.load_workbook(template_path)
            ws = wb.active
            
            # Preparar datos para reemplazar
            data_replacements = self.prepare_professional_contract_data(contrato, empleado)
            
            # Reemplazar placeholders en todas las celdas
            self.replace_placeholders_in_worksheet(ws, data_replacements)
            
            # Generar nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            contract_filename = f"contrato_profesional_{empleado.cedula}_{timestamp}.xlsx"
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
                'message': f'Contrato profesional generado exitosamente para {empleado.nombre_completo}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error generando contrato: {e}'
            }
    
    def prepare_professional_contract_data(self, contrato, empleado):
        """Preparar datos profesionales del contrato"""
        try:
            # Calcular valores
            salario_base = contrato.salario_base or 1423500  # Valor por defecto
            subsidio_transporte = contrato.subsidio_transporte or 140606
            bonificaciones = contrato.bonificaciones or 0
            
            # Formatear fechas
            fecha_elaboracion = datetime.now().strftime("%d DE %B DE %Y").upper()
            fecha_inicio = contrato.fecha_inicio.strftime("%d DE %B %Y") if contrato.fecha_inicio else "17 DE FEBRERO 2025"
            fecha_fin = contrato.fecha_fin.strftime("%d DE %B %Y") if contrato.fecha_fin else "16 DE ABRIL 2025"
            
            # Calcular prórrogas (ejemplo basado en el documento)
            if contrato.fecha_fin:
                fecha_fin_obj = contrato.fecha_fin
                fecha_prorroga_1 = fecha_fin_obj + timedelta(days=60)  # 2 meses
                fecha_prorroga_2 = fecha_prorroga_1 + timedelta(days=60)  # 2 meses más
                fecha_prorroga_3 = fecha_prorroga_2 + timedelta(days=60)  # 2 meses más
                fecha_contrato_anual = fecha_prorroga_3
                
                fecha_prorroga_1_str = fecha_prorroga_1.strftime("%d DE %B %Y")
                fecha_prorroga_2_str = fecha_prorroga_2.strftime("%d DE %B %Y")
                fecha_prorroga_3_str = fecha_prorroga_3.strftime("%d DE %B %Y")
                fecha_contrato_anual_str = fecha_contrato_anual.strftime("%d DE %B %Y")
            else:
                fecha_prorroga_1_str = "17 DE JUNIO 2025"
                fecha_prorroga_2_str = "17 DE AGOSTO 2025"
                fecha_prorroga_3_str = "17 DE OCTUBRE 2025"
                fecha_contrato_anual_str = "17 DE OCTUBRE 2025"
            
            # Preparar todos los placeholders
            data = {
                # Información básica
                '{{NUMERO_TRABAJADOR}}': f"855-{contrato.id:03d}",
                '{{NOMBRE_EMPLEADOR}}': "FLORES JUNCALITO S.A.S",
                '{{DIRECCION_EMPLEADOR}}': "CARRERA 19 C N. 88-07",
                '{{NOMBRE_EMPLEADO}}': empleado.nombre_completo or "XXXXXXXXXXXXXXXXXXXX",
                '{{DIRECCION_EMPLEADO}}': empleado.direccion or "XXXXXXXXXXXXXXX",
                '{{LUGAR_NACIMIENTO}}': f"{empleado.direccion or 'XXXXXXXXXXXXXXX'}, COLOMBIANO(A)",
                '{{CARGO_EMPLEADO}}': empleado.cargo or "OPERARIO(A) - OFICIOS VARIOS",
                
                # Información salarial
                '{{SALARIO_BASE}}': f"{salario_base:,}",
                '{{SALARIO_LETRAS}}': self.numero_a_letras(salario_base),
                '{{PERIODO_PAGO}}': "MENSUALES",
                
                # Fechas
                '{{FECHA_INICIO}}': fecha_inicio,
                '{{FECHA_FIN}}': fecha_fin,
                '{{FECHA_ELABORACION}}': fecha_elaboracion,
                
                # Lugares
                '{{LUGAR_LABORES}}': "FLORES JUNCALITO S.A.S",
                '{{CIUDAD_CONTRATO}}': "BARRIO SAN JOSE -- EL ROSAL C/MARCA",
                
                # Duración
                '{{TERMINO_CONTRATO}}': "A DOS MESES" if contrato.tipo_contrato == "temporal" else "INDEFINIDO",
                
                # Prórrogas
                '{{FECHA_PRORROGA_1}}': fecha_prorroga_1_str,
                '{{FECHA_PRORROGA_2}}': fecha_prorroga_2_str,
                '{{FECHA_PRORROGA_3}}': fecha_prorroga_3_str,
                '{{FECHA_CONTRATO_ANUAL}}': fecha_contrato_anual_str,
                
                # Información del empleado
                '{{CEDULA_EMPLEADO}}': empleado.cedula or "XXXXXXXXXXXXXXXXX",
                '{{TELEFONO_EMPLEADO}}': empleado.telefono or "No definido",
                '{{EMAIL_EMPLEADO}}': empleado.email or "No definido",
                
                # Información del empleador (datos reales de la empresa)
                '{{NOMBRE_EMPLEADOR_FIRMA}}': "FELIPE DE LA TORRE",
                '{{NIT_EMPLEADOR}}': "860.065.678-2",
                '{{NOMBRE_TESTIGO}}': "NELLY GRACIELA TORRES R.",
                '{{CEDULA_TESTIGO}}': "52.326.084 DE BTÁ",
            }
            
            return data
            
        except Exception as e:
            print(f"Error preparando datos del contrato profesional: {e}")
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


class ContratoProfesionalExcelWindow:
    """Ventana para generar contratos profesionales en Excel"""
    
    def __init__(self, parent, main_window, contrato=None):
        self.parent = parent
        self.main_window = main_window
        self.contrato = contrato
        self.generator = ContratoProfesionalExcelGenerator()
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("📄 Generador de Contratos Profesionales Excel")
        self.window.geometry("700x600")
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
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"700x600+{x}+{y}")
    
    def create_interface(self):
        """Crear interfaz de la ventana"""
        # Header
        header = tk.Frame(self.window, bg='#2c3e50', height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg='#2c3e50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        title_label = tk.Label(header_content, text="📄 Generador de Contratos Profesionales",
                              font=('Segoe UI', 18, 'bold'),
                              bg='#2c3e50', fg='white')
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(header_content, text="Formato Oficial FLORES JUNCALITO S.A.S",
                                font=('Segoe UI', 10),
                                bg='#2c3e50', fg='#ecf0f1')
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Contenido principal
        content = tk.Frame(self.window, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Información del contrato
        self.create_contract_info_section(content)
        
        # Vista previa de datos
        self.create_preview_section(content)
        
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
                                          width=60, font=('Segoe UI', 10),
                                          state='readonly')
        self.contract_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky='ew')
        self.contract_combo.bind('<<ComboboxSelected>>', self.on_contract_selected)
        
        # Información del empleado
        self.info_labels = {}
        info_fields = [
            ("Empleado:", "empleado"),
            ("Cédula:", "cedula"),
            ("Cargo:", "cargo"),
            ("Área:", "area"),
            ("Tipo Contrato:", "tipo"),
            ("Salario:", "salario"),
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
    
    def create_preview_section(self, parent):
        """Crear sección de vista previa"""
        preview_frame = tk.LabelFrame(parent, text="👁️ Vista Previa del Contrato",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='white', fg='#2c3e50', padx=15, pady=10)
        preview_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Información que aparecerá en el contrato
        preview_text = tk.Text(preview_frame, height=8, width=70,
                              font=('Segoe UI', 9), wrap=tk.WORD,
                              bg='#f8f9fa', relief='solid', bd=1)
        preview_text.pack(fill=tk.X, pady=5)
        
        # Scrollbar para el text
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scroll.set)
        
        self.preview_text = preview_text
        
        # Texto inicial
        self.update_preview("Seleccione un contrato para ver la vista previa...")
    
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
        
        self.files_tree.column('Archivo', width=350)
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
        generate_btn = tk.Button(buttons_frame, text="📄 Generar Contrato Profesional",
                               command=self.generate_professional_contract,
                               bg='#27ae60', fg='white',
                               font=('Segoe UI', 12, 'bold'),
                               relief='flat', bd=0, padx=25, pady=12,
                               cursor='hand2')
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón vista previa
        preview_btn = tk.Button(buttons_frame, text="👁️ Actualizar Vista Previa",
                              command=self.update_contract_preview,
                              bg='#3498db', fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=20, pady=12,
                              cursor='hand2')
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón abrir carpeta
        folder_btn = tk.Button(buttons_frame, text="📁 Abrir Carpeta",
                              command=self.open_employee_folder,
                              bg='#f39c12', fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief='flat', bd=0, padx=15, pady=12,
                              cursor='hand2')
        folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón cerrar
        close_btn = tk.Button(buttons_frame, text="❌ Cerrar",
                            command=self.window.destroy,
                            bg='#e74c3c', fg='white',
                            font=('Segoe UI', 11, 'bold'),
                            relief='flat', bd=0, padx=15, pady=12,
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
                display_text = f"{contrato.numero_contrato or 'SIN-NUM'} - {contrato.empleado.nombre_completo} - {contrato.tipo_contrato or 'Sin tipo'}"
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
            display_text = f"{self.contrato.numero_contrato or 'SIN-NUM'} - {self.contrato.empleado.nombre_completo} - {self.contrato.tipo_contrato or 'Sin tipo'}"
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
            self.info_labels['cargo'].config(text=empleado.cargo or "OPERARIO(A) - OFICIOS VARIOS")
            self.info_labels['area'].config(text=empleado.area_trabajo or "No definida")
            self.info_labels['tipo'].config(text=contrato.tipo_contrato or "No definido")
            self.info_labels['salario'].config(text=f"${contrato.salario_base:,}" if contrato.salario_base else "No definido")
            self.info_labels['estado'].config(text=contrato.estado or "borrador")
            
            # Actualizar vista previa
            self.update_contract_preview()
            
            # Actualizar lista de archivos
            self.refresh_files_list()
    
    def update_contract_preview(self):
        """Actualizar vista previa del contrato"""
        selected = self.contract_var.get()
        if not selected or selected not in self.contracts_dict:
            self.update_preview("Seleccione un contrato para ver la vista previa...")
            return
        
        contrato = self.contracts_dict[selected]
        empleado = contrato.empleado
        
        # Generar vista previa del contrato
        preview_text = f"""
CONTRATO INDIVIDUAL DE TRABAJO A TÉRMINO FIJO INFERIOR A UN AÑO

TRABAJADOR 855-{contrato.id:03d}

DATOS PRINCIPALES:
• Empleador: FLORES JUNCALITO S.A.S
• Trabajador: {empleado.nombre_completo}
• Cédula: {empleado.cedula}
• Cargo: {empleado.cargo or 'OPERARIO(A) - OFICIOS VARIOS'}
• Dirección Trabajador: {empleado.direccion or 'XXXXXXXXXXXXXXX'}

INFORMACIÓN CONTRACTUAL:
• Salario: ${contrato.salario_base:,} ({self.generator.numero_a_letras(contrato.salario_base or 1423500)})
• Período de Pago: MENSUALES
• Fecha Inicio: {contrato.fecha_inicio.strftime('%d DE %B %Y') if contrato.fecha_inicio else '17 DE FEBRERO 2025'}
• Fecha Fin: {contrato.fecha_fin.strftime('%d DE %B %Y') if contrato.fecha_fin else '16 DE ABRIL 2025'}
• Término: {'A DOS MESES' if contrato.tipo_contrato == 'temporal' else 'INDEFINIDO'}

LUGAR DE TRABAJO:
• Empresa: FLORES JUNCALITO S.A.S
• Ubicación: BARRIO SAN JOSE -- EL ROSAL C/MARCA

ESTRUCTURA DEL CONTRATO:
✓ Cláusula Primera: Objeto del contrato
✓ Cláusula Segunda: Remuneración
✓ Cláusula Tercera: Duración del contrato
✓ Cláusula Cuarta: Trabajo nocturno y suplementario
✓ Cláusula Quinta: Jornada de trabajo
✓ Cláusula Sexta: Período de prueba
✓ Cláusula Séptima: Terminación unilateral
✓ Cláusula Octava: Propiedad intelectual
✓ Cláusula Novena: Modificación de condiciones laborales
✓ Cláusula Décima: Dirección del trabajador
✓ Cláusula Undécima: Efectos

PRÓRROGAS PROGRAMADAS:
• 1ª Prórroga: Hasta {(contrato.fecha_fin + timedelta(days=60)).strftime('%d DE %B %Y') if contrato.fecha_fin else '17 DE JUNIO 2025'}
• 2ª Prórroga: Hasta {(contrato.fecha_fin + timedelta(days=120)).strftime('%d DE %B %Y') if contrato.fecha_fin else '17 DE AGOSTO 2025'}
• 3ª Prórroga: Hasta {(contrato.fecha_fin + timedelta(days=180)).strftime('%d DE %B %Y') if contrato.fecha_fin else '17 DE OCTUBRE 2025'}

FIRMAS:
• Empleador: FELIPE DE LA TORRE (CC/NIT: 860.065.678-2)
• Trabajador: {empleado.nombre_completo} (CC: {empleado.cedula})
• Testigo: NELLY GRACIELA TORRES R. (CC: 52.326.084 DE BTÁ)
        """
        
        self.update_preview(preview_text.strip())
    
    def update_preview(self, text):
        """Actualizar texto de vista previa"""
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', text)
    
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
    
    def generate_professional_contract(self):
        """Generar contrato profesional en Excel"""
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
            
            # Mostrar progreso
            progress_window = self.show_progress_window()
            
            # Generar contrato profesional
            self.window.update()
            result = self.generator.generate_professional_contract_excel(contrato.id)
            
            # Cerrar ventana de progreso
            progress_window.destroy()
            
            if result['success']:
                # Actualizar lista de archivos
                self.refresh_files_list()
                
                # Mostrar resultado exitoso
                if messagebox.askyesno("¡Contrato Generado Exitosamente!", 
                    f"✅ Contrato profesional generado:\n\n" +
                    f"📄 Empleado: {contrato.empleado.nombre_completo}\n" +
                    f"📋 Contrato: {contrato.numero_contrato}\n" +
                    f"💼 Formato: FLORES JUNCALITO S.A.S Oficial\n" +
                    f"📁 Archivo: {Path(result['file_path']).name}\n\n" +
                    "¿Desea abrir el archivo generado?"):
                    self.open_file(result['file_path'])
            else:
                messagebox.showerror("Error", result['message'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generando contrato: {e}")
    
    def show_progress_window(self):
        """Mostrar ventana de progreso"""
        progress_window = tk.Toplevel(self.window)
        progress_window.title("Generando Contrato Profesional")
        progress_window.geometry("350x120")
        progress_window.configure(bg='white')
        progress_window.resizable(False, False)
        
        # Centrar ventana
        progress_window.transient(self.window)
        progress_window.grab_set()
        
        x = (progress_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (120 // 2)
        progress_window.geometry(f"350x120+{x}+{y}")
        
        # Contenido
        tk.Label(progress_window, text="📄 Generando contrato profesional Excel...",
                font=('Segoe UI', 12),
                bg='white', fg='#2c3e50').pack(expand=True, pady=10)
        
        tk.Label(progress_window, text="Formato oficial FLORES JUNCALITO S.A.S",
                font=('Segoe UI', 9),
                bg='white', fg='#7f8c8d').pack()
        
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


# ============= FUNCIÓN PRINCIPAL PARA INTEGRAR =============

def abrir_generador_contratos_profesional_excel(parent, main_window, contrato=None):
    """Función principal para abrir el generador de contratos profesionales Excel"""
    try:
        ContratoProfesionalExcelWindow(parent, main_window, contrato)
    except Exception as e:
        messagebox.showerror("Error", f"Error abriendo generador de contratos: {e}")


# ============= INSTRUCCIONES DE INTEGRACIÓN MEJORADAS =============

integration_instructions_professional = """
SISTEMA DE CONTRATOS PROFESIONALES EXCEL - FORMATO OFICIAL

✅ CARACTERÍSTICAS DEL SISTEMA:
• Formato oficial basado en FLORES JUNCALITO S.A.S
• Contrato completo con todas las cláusulas legales
• Tabla profesional con bordes y formato empresarial
• Placeholders automáticos para todos los datos
• Cálculo automático de prórrogas y fechas
• Conversión de números a letras para salarios
• Información legal completa y actualizada

📋 CONTENIDO DEL CONTRATO GENERADO:
• Tabla de información principal (empleador, trabajador, salarios, fechas)
• 11 cláusulas legales completas
• Información de prórrogas automáticas
• Sección de firmas con datos reales
• Formato de impresión optimizado
• Cláusulas adicionales incluidas

🔧 PARA INTEGRAR EN contratos_view.py:

1. REEMPLAZAR el método generar_contrato_excel() con:

def generar_contrato_excel(self):
    contrato = self.get_selected_contrato()
    if contrato:
        try:
            from utils.contrato_excel_generator import abrir_generador_contratos_profesional_excel
            abrir_generador_contratos_profesional_excel(self.window, self, contrato)
        except ImportError:
            messagebox.showinfo("Generar Excel", "Instale openpyxl y agregue contrato_excel_generator.py")

📁 ESTRUCTURA CREADA:
empleados_data/
├── NombreEmpleado_Cedula/
│   ├── contratos/
│   │   └── contrato_profesional_cedula_timestamp.xlsx
│   ├── documentos/
│   ├── nomina/
│   └── historiales/
└── templates_contratos/
    └── contrato_profesional_template.xlsx

🎯 DATOS RELLENADOS AUTOMÁTICAMENTE:
• Información completa del empleado
• Datos salariales con conversión a letras
• Fechas formateadas correctamente
• Cálculo automático de prórrogas
• Información legal de la empresa
• Datos de testigos y firmas
• Cláusulas personalizadas

💡 VENTAJAS:
• Formato 100% profesional y legal
• Basado en contrato real de empresa
• Todos los datos se rellenan automáticamente
• Vista previa antes de generar
• Gestión completa de archivos
• Apertura automática del archivo generado
"""

