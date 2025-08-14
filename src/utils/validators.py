import re
import os
from datetime import datetime, date
from typing import Tuple, Optional, List
import mimetypes
from sqlalchemy.orm import Session
from models.database import Empleado

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass

class DataValidator:
    """Clase para validación de datos del sistema de gestión de personal"""
    
    @staticmethod
    def validar_cedula_colombiana(cedula: str) -> Tuple[bool, str]:
        """
        Validar formato de cédula colombiana
        Retorna: (es_valida, mensaje_error)
        """
        # Limpiar espacios y caracteres especiales
        cedula_limpia = re.sub(r'[^\d]', '', cedula)
        
        # Verificar longitud
        if len(cedula_limpia) < 8 or len(cedula_limpia) > 12:
            return False, "La cédula debe tener entre 8 y 12 dígitos"
        
        # Verificar que sean solo números
        if not cedula_limpia.isdigit():
            return False, "La cédula debe contener solo números"
        
        # Validación específica para cédulas colombianas (algoritmo de verificación)
        # Solo validar algoritmo para cédulas de 10 dígitos que parezcan válidas
        # NOTA: Se ha deshabilitado la validación estricta del algoritmo para permitir
        # cédulas que pueden ser válidas en la práctica pero no pasan el algoritmo
        if len(cedula_limpia) == 10 and cedula_limpia.isdigit():
            # Comentado: Algoritmo de validación estricto
            # if not DataValidator._validar_algoritmo_cedula(cedula_limpia):
            #     return False, "Cédula inválida según algoritmo de verificación"
            pass
        
        return True, ""
    
    @staticmethod
    def _validar_algoritmo_cedula(cedula: str) -> bool:
        """
        Algoritmo de validación de cédula colombiana
        Basado en el algoritmo oficial de la DIAN
        """
        if len(cedula) != 10:
            return False
        
        # Multiplicadores para el algoritmo
        multiplicadores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43]
        
        # Calcular suma ponderada
        suma = 0
        for i in range(9):
            suma += int(cedula[i]) * multiplicadores[i]
        
        # Calcular dígito de verificación
        residuo = suma % 11
        if residuo == 0:
            digito_verificador = 0
        else:
            digito_verificador = 11 - residuo
        
        # Comparar con el último dígito
        return int(cedula[9]) == digito_verificador
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """
        Validar formato de email
        Retorna: (es_valido, mensaje_error)
        """
        if not email.strip():
            return True, ""  # Email es opcional
        
        # Patrón regex para validar email
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(patron_email, email.strip()):
            return False, "Formato de email inválido"
        
        # Validaciones adicionales
        if len(email) > 50:
            return False, "El email no puede exceder 50 caracteres"
        
        if email.count('@') != 1:
            return False, "El email debe contener exactamente un símbolo @"
        
        return True, ""
    
    @staticmethod
    def validar_telefono(telefono: str) -> Tuple[bool, str]:
        """
        Validar formato de teléfono colombiano
        Retorna: (es_valido, mensaje_error)
        """
        if not telefono.strip():
            return True, ""  # Teléfono es opcional
        
        # Limpiar espacios y caracteres especiales
        telefono_limpio = re.sub(r'[^\d]', '', telefono)
        
        # Verificar longitud
        if len(telefono_limpio) < 7 or len(telefono_limpio) > 10:
            return False, "El teléfono debe tener entre 7 y 10 dígitos"
        
        # Verificar que sean solo números
        if not telefono_limpio.isdigit():
            return False, "El teléfono debe contener solo números"
        
        # Validar códigos de área colombianos
        codigos_area = ['300', '301', '302', '303', '304', '305', '306', '307', '308', '309',
                       '310', '311', '312', '313', '314', '315', '316', '317', '318', '319',
                       '320', '321', '322', '323', '324', '325', '326', '327', '328', '329',
                       '330', '331', '332', '333', '334', '335', '336', '337', '338', '339',
                       '340', '341', '342', '343', '344', '345', '346', '347', '348', '349',
                       '350', '351', '352', '353', '354', '355', '356', '357', '358', '359',
                       '360', '361', '362', '363', '364', '365', '366', '367', '368', '369',
                       '370', '371', '372', '373', '374', '375', '376', '377', '378', '379',
                       '380', '381', '382', '383', '384', '385', '386', '387', '388', '389',
                       '390', '391', '392', '393', '394', '395', '396', '397', '398', '399']
        
        if len(telefono_limpio) == 10:
            codigo_area = telefono_limpio[:3]
            if codigo_area not in codigos_area:
                return False, "Código de área inválido para Colombia"
        
        return True, ""
    
    @staticmethod
    def validar_nombre(nombre: str) -> Tuple[bool, str]:
        """
        Validar formato de nombre completo
        Retorna: (es_valido, mensaje_error)
        """
        if not nombre.strip():
            return False, "El nombre es obligatorio"
        
        # Verificar longitud mínima y máxima
        if len(nombre.strip()) < 3:
            return False, "El nombre debe tener al menos 3 caracteres"
        
        if len(nombre.strip()) > 100:
            return False, "El nombre no puede exceder 100 caracteres"
        
        # Verificar que contenga solo letras, espacios y caracteres especiales válidos
        patron_nombre = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        if not re.match(patron_nombre, nombre.strip()):
            return False, "El nombre solo puede contener letras y espacios"
        
        # Verificar que tenga al menos dos palabras (nombre y apellido)
        palabras = nombre.strip().split()
        if len(palabras) < 2:
            return False, "Debe ingresar nombre y apellido"
        
        return True, ""
    
    @staticmethod
    def validar_salario(salario: str) -> Tuple[bool, str]:
        """
        Validar formato de salario
        Retorna: (es_valido, mensaje_error)
        """
        if not salario.strip():
            return True, ""  # Salario es opcional
        
        try:
            valor = int(salario.strip())
            if valor < 0:
                return False, "El salario no puede ser negativo"
            if valor > 999999999:
                return False, "El salario es demasiado alto"
            return True, ""
        except ValueError:
            return False, "El salario debe ser un número entero"
    
    @staticmethod
    def validar_fecha_nacimiento(fecha: date) -> Tuple[bool, str]:
        """
        Validar fecha de nacimiento
        Retorna: (es_valida, mensaje_error)
        """
        if not fecha:
            return True, ""  # Fecha es opcional
        
        hoy = date.today()
        
        # Verificar que no sea fecha futura
        if fecha > hoy:
            return False, "La fecha de nacimiento no puede ser futura"
        
        # Verificar edad mínima (18 años)
        edad_minima = date(hoy.year - 18, hoy.month, hoy.day)
        if fecha > edad_minima:
            return False, "El empleado debe ser mayor de 18 años"
        
        # Verificar edad máxima (100 años)
        edad_maxima = date(hoy.year - 100, hoy.month, hoy.day)
        if fecha < edad_maxima:
            return False, "La fecha de nacimiento parece incorrecta"
        
        return True, ""
    
    @staticmethod
    def verificar_duplicado_cedula(db: Session, cedula: str, empleado_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Verificar si ya existe un empleado con la misma cédula
        Retorna: (es_duplicado, mensaje_error)
        """
        # Buscar empleado con la misma cédula
        query = db.query(Empleado).filter(Empleado.cedula == cedula)
        
        # Si estamos editando, excluir el empleado actual
        if empleado_id:
            query = query.filter(Empleado.id != empleado_id)
        
        empleado_existente = query.first()
        
        if empleado_existente:
            return True, f"Ya existe un empleado con la cédula {cedula}"
        
        return False, ""
    
    @staticmethod
    def validar_archivo(ruta_archivo: str, tipos_permitidos: List[str] = None) -> Tuple[bool, str]:
        """
        Validar archivo subido
        Retorna: (es_valido, mensaje_error)
        """
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            return False, "El archivo no existe"
        
        # Verificar tamaño del archivo (máximo 10MB)
        tamaño = os.path.getsize(ruta_archivo)
        if tamaño > 10 * 1024 * 1024:  # 10MB
            return False, "El archivo es demasiado grande (máximo 10MB)"
        
        # Verificar tipo de archivo
        if tipos_permitidos:
            mime_type, _ = mimetypes.guess_type(ruta_archivo)
            extension = os.path.splitext(ruta_archivo)[1].lower()
            
            tipos_validos = []
            for tipo in tipos_permitidos:
                if tipo.startswith('.'):
                    tipos_validos.append(tipo.lower())
                else:
                    tipos_validos.extend(mimetypes.guess_all_extensions(tipo))
            
            if extension not in tipos_validos:
                return False, f"Tipo de archivo no permitido. Tipos válidos: {', '.join(tipos_permitidos)}"
        
        return True, ""
    
    @staticmethod
    def validar_empleado_completo(db: Session, datos: dict, empleado_id: Optional[int] = None) -> Tuple[bool, List[str]]:
        """
        Validar todos los datos de un empleado
        Retorna: (es_valido, lista_errores)
        """
        errores = []
        
        # Validar nombre
        es_valido, mensaje = DataValidator.validar_nombre(datos.get('nombre_completo', ''))
        if not es_valido:
            errores.append(f"Nombre: {mensaje}")
        
        # Validar cédula
        cedula = datos.get('cedula', '')
        es_valido, mensaje = DataValidator.validar_cedula_colombiana(cedula)
        if not es_valido:
            errores.append(f"Cédula: {mensaje}")
        else:
            # Verificar duplicado solo si la cédula es válida
            es_duplicado, mensaje = DataValidator.verificar_duplicado_cedula(db, cedula, empleado_id)
            if es_duplicado:
                errores.append(f"Cédula: {mensaje}")
        
        # Validar teléfono
        es_valido, mensaje = DataValidator.validar_telefono(datos.get('telefono', ''))
        if not es_valido:
            errores.append(f"Teléfono: {mensaje}")
        
        # Validar email
        es_valido, mensaje = DataValidator.validar_email(datos.get('email', ''))
        if not es_valido:
            errores.append(f"Email: {mensaje}")
        
        # Validar salario
        es_valido, mensaje = DataValidator.validar_salario(str(datos.get('salario_base', '')))
        if not es_valido:
            errores.append(f"Salario: {mensaje}")
        
        # Validar fecha de nacimiento
        fecha_nac = datos.get('fecha_nacimiento')
        if fecha_nac:
            es_valido, mensaje = DataValidator.validar_fecha_nacimiento(fecha_nac)
            if not es_valido:
                errores.append(f"Fecha de nacimiento: {mensaje}")
        
        return len(errores) == 0, errores

# Funciones de conveniencia para uso directo
def validar_cedula(cedula: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar cédula"""
    return DataValidator.validar_cedula_colombiana(cedula)

def validar_email_simple(email: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar email"""
    return DataValidator.validar_email(email)

def validar_telefono_simple(telefono: str) -> Tuple[bool, str]:
    """Función de conveniencia para validar teléfono"""
    return DataValidator.validar_telefono(telefono)

def verificar_duplicado_simple(db: Session, cedula: str, empleado_id: Optional[int] = None) -> Tuple[bool, str]:
    """Función de conveniencia para verificar duplicados"""
    return DataValidator.verificar_duplicado_cedula(db, cedula, empleado_id) 