#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración del Sistema de Gestión de Personal e Inventarios
Archivo central de configuraciones y constantes del sistema
"""

import os
from pathlib import Path
from datetime import datetime

# ===================== INFORMACIÓN DEL SISTEMA =====================

SYSTEM_INFO = {
    'name': 'Sistema de Gestión de Personal e Inventarios',
    'version': '2.0.0',
    'description': 'Sistema integrado para gestión de personal, químicos, almacén y poscosecha',
    'author': 'Desarrollador del Sistema',
    'created': '2024',
    'last_update': datetime.now().strftime('%Y-%m-%d')
}

# ===================== CONFIGURACIÓN DE DIRECTORIOS =====================

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Directorios principales
DIRECTORIES = {
    'database': BASE_DIR / 'database',
    'src': BASE_DIR / 'src',
    'views': BASE_DIR / 'src' / 'views',
    'models': BASE_DIR / 'src' / 'models',
    'reports': BASE_DIR / 'reports',
    'backups': BASE_DIR / 'backups',
    'temp': BASE_DIR / 'temp',
    'logs': BASE_DIR / 'logs',
    'empleados_data': BASE_DIR / 'empleados_data',
    'inventario_quimicos_sistema': BASE_DIR / 'inventario_quimicos_sistema',
}

# Crear directorios si no existen
def create_directories():
    """Crear todos los directorios necesarios"""
    for name, path in DIRECTORIES.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directorio {name}: {path}")
        except Exception as e:
            print(f"❌ Error creando directorio {name}: {e}")

# ===================== CONFIGURACIÓN DE BASE DE DATOS =====================

# Configuración de bases de datos
DATABASE_CONFIG = {
    'personal': {
        'path': DIRECTORIES['database'] / 'gestion_personal.db',
        'description': 'Base de datos de gestión de personal y contratos'
    },
    'quimicos': {
        'path': DIRECTORIES['database'] / 'inventario_quimicos_avanzado.db',
        'description': 'Base de datos de inventario de químicos agrícolas'
    },
    'almacen': {
        'path': DIRECTORIES['database'] / 'inventario_almacen.db',
        'description': 'Base de datos de inventario de almacén general'
    },
    'poscosecha': {
        'path': DIRECTORIES['database'] / 'inventario_poscosecha.db',
        'description': 'Base de datos de inventario de poscosecha'
    }
}

# Configuración SQLAlchemy
SQLALCHEMY_CONFIG = {
    'echo': False,  # True para debug SQL
    'pool_timeout': 20,
    'pool_recycle': -1,
    'pool_pre_ping': True
}

# ===================== CONFIGURACIÓN DE LA INTERFAZ =====================

# Tema de colores del sistema
COLOR_THEME = {
    # Colores principales
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#3498db',
    
    # Colores de estado
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    
    # Colores de sistema
    'background': '#f8f9fa',
    'surface': '#ffffff',
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
    'border': '#dee2e6',
    
    # Colores específicos de módulos
    'personal': '#8e44ad',      # Púrpura para personal
    'quimicos': '#27ae60',      # Verde para químicos
    'almacen': '#3498db',       # Azul para almacén
    'poscosecha': '#16a085',    # Verde oscuro para poscosecha
    'contratos': '#e67e22',     # Naranja para contratos
}

# Configuración de fuentes
FONT_CONFIG = {
    'family': 'Segoe UI',
    'size': {
        'small': 8,
        'normal': 10,
        'medium': 12,
        'large': 14,
        'title': 16,
        'header': 20
    },
    'weight': {
        'normal': 'normal',
        'bold': 'bold'
    }
}

# Configuración de ventanas
WINDOW_CONFIG = {
    'main': {
        'width': 1100,
        'height': 700,
        'min_width': 900,
        'min_height': 600,
        'resizable': True
    },
    'inventario': {
        'width': 1300,
        'height': 800,
        'min_width': 1200,
        'min_height': 700,
        'resizable': True
    },
    'contratos': {
        'width': 1000,
        'height': 700,
        'min_width': 800,
        'min_height': 600,
        'resizable': True
    }
}

# ===================== CONFIGURACIÓN DE INVENTARIOS =====================

# Configuración específica de químicos
QUIMICOS_CONFIG = {
    'clases': [
        'ACARICIDA', 'FUNGICIDA', 'INSECTICIDA', 'HERBICIDA',
        'FERTILIZANTE', 'REGULADOR', 'ADHERENTE', 'OTRO'
    ],
    'unidades': ['C.C', 'ML', 'LT', 'GR', 'KG', 'UND', 'GAL'],
    'niveles_peligrosidad': ['BAJO', 'MEDIO', 'ALTO'],
    'ubicaciones_default': ['A-01', 'A-02', 'A-03', 'A-04', 'A-05'],
    'backup_interval': 24,  # horas
    'alert_days': {
        'stock': 7,
        'vencimiento': 30
    }
}

# Configuración específica de almacén
ALMACEN_CONFIG = {
    'categorias': ['HERRAMIENTAS', 'REPUESTOS', 'LUBRICANTES', 'MATERIALES', 'OTRO'],
    'unidades': ['UND', 'KG', 'LT', 'MT', 'M2', 'GALONES'],
    'ubicaciones': ['A-01', 'A-02', 'A-03', 'B-01', 'B-02', 'C-01'],
    'stock_alert_percentage': 20  # % del stock mínimo para alertar
}

# Configuración específica de poscosecha
POSCOSECHA_CONFIG = {
    'categorias': ['EMBALAJE', 'QUIMICO', 'ETIQUETA', 'HERRAMIENTA', 'GENERAL'],
    'tipos_producto': ['EMPAQUE', 'TRATAMIENTO', 'IDENTIFICACION', 'LIMPIEZA', 'GENERAL'],
    'unidades': ['UND', 'KG', 'LT', 'ML', 'GR', 'MT', 'M2'],
    'ubicaciones': ['PC-01', 'PC-02', 'PC-03', 'PC-04', 'PC-05']
}

# ===================== CONFIGURACIÓN DE PERSONAL =====================

# Configuración de empleados
EMPLEADOS_CONFIG = {
    'areas_trabajo': ['planta', 'postcosecha', 'administracion', 'campo'],
    'cargos_default': [
        'operario', 'supervisor', 'coordinador', 'jefe', 'gerente',
        'tecnico', 'auxiliar', 'analista', 'administrador'
    ],
    'salario_minimo': 1300000,  # Salario mínimo 2024 Colombia
    'subsidio_transporte': 140606  # Subsidio transporte 2024
}

# Configuración de contratos
CONTRATOS_CONFIG = {
    'tipos': {
        'temporal': {
            'nombre': 'Temporal',
            'dias_default': 90,
            'renovable': True
        },
        'permanente': {
            'nombre': 'Indefinido',
            'dias_default': None,
            'renovable': False
        },
        'temporada': {
            'nombre': 'Por temporada',
            'dias_default': 120,
            'renovable': True
        },
        'prestacion_servicios': {
            'nombre': 'Prestación de servicios',
            'dias_default': 180,
            'renovable': True
        }
    },
    'estados': ['borrador', 'activo', 'vencido', 'terminado', 'suspendido']
}

# ===================== CONFIGURACIÓN DE REPORTES =====================

# Configuración de reportes
REPORTS_CONFIG = {
    'formats': ['PDF', 'Excel', 'CSV'],
    'templates_dir': DIRECTORIES['reports'] / 'templates',
    'output_dir': DIRECTORIES['reports'] / 'generated',
    'default_format': 'PDF',
    'include_charts': True,
    'auto_open': True
}

# Tipos de reportes disponibles
REPORT_TYPES = {
    'personal': [
        'listado_empleados', 'contratos_activos', 'contratos_vencidos',
        'nomina_mensual', 'empleados_por_area'
    ],
    'inventarios': [
        'inventario_general', 'productos_criticos', 'valorización',
        'movimientos_periodo', 'alertas_vencimiento'
    ],
    'quimicos': [
        'inventario_quimicos', 'quimicos_alto_riesgo', 'consumo_mensual',
        'proveedores_quimicos', 'alertas_seguridad'
    ],
    'almacen': [
        'inventario_almacen', 'productos_bajo_stock', 'movimientos_almacen',
        'ubicaciones_almacen', 'proveedores_almacen'
    ],
    'poscosecha': [
        'inventario_poscosecha', 'productos_empaque', 'tratamientos_aplicados',
        'control_calidad', 'productos_vencidos'
    ]
}

# ===================== CONFIGURACIÓN DE BACKUPS =====================

# Configuración de backups
BACKUP_CONFIG = {
    'auto_backup': True,
    'backup_interval': 24,  # horas
    'max_backups': 30,  # máximo número de backups a mantener
    'backup_on_close': True,
    'compression': True,
    'include_logs': False,
    'backup_databases': True,
    'backup_files': True
}

# Archivos a incluir en backup
BACKUP_INCLUDE = [
    'database/*.db',
    'empleados_data/**/*',
    'src/config.py',
    'requirements.txt'
]

# Archivos a excluir del backup
BACKUP_EXCLUDE = [
    '**/__pycache__/**',
    '**/*.pyc',
    'temp/**/*',
    'logs/*.log',
    '.git/**/*'
]

# ===================== CONFIGURACIÓN DE LOGGING =====================

# Configuración de logs
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Archivos de log por módulo
LOG_FILES = {
    'main': DIRECTORIES['logs'] / 'main.log',
    'personal': DIRECTORIES['logs'] / 'personal.log',
    'inventarios': DIRECTORIES['logs'] / 'inventarios.log',
    'contratos': DIRECTORIES['logs'] / 'contratos.log',
    'database': DIRECTORIES['logs'] / 'database.log',
    'errors': DIRECTORIES['logs'] / 'errors.log'
}

# ===================== CONFIGURACIÓN DE IMPORTACIÓN =====================

# Configuración para importar datos desde Excel
IMPORT_CONFIG = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': ['.xlsx', '.xls', '.csv'],
    'temp_dir': DIRECTORIES['temp'],
    'backup_before_import': True,
    'validate_data': True,
    'skip_duplicates': True
}

# Configuración de mapeo de columnas para importación
COLUMN_MAPPING = {
    'empleados': {
        'nombre': ['nombre', 'nombre_completo', 'empleado', 'full_name'],
        'cedula': ['cedula', 'cc', 'documento', 'id'],
        'telefono': ['telefono', 'tel', 'celular', 'phone'],
        'area': ['area', 'area_trabajo', 'department', 'seccion']
    },
    'quimicos': {
        'codigo': ['codigo', 'code', 'ref', 'referencia'],
        'nombre': ['nombre', 'producto', 'name', 'descripcion'],
        'clase': ['clase', 'tipo', 'categoria', 'class'],
        'saldo': ['saldo', 'stock', 'cantidad', 'existencias']
    }
}

# ===================== CONFIGURACIÓN DE VALIDACIONES =====================

# Reglas de validación
VALIDATION_RULES = {
    'empleados': {
        'cedula': {
            'required': True,
            'unique': True,
            'min_length': 6,
            'max_length': 12,
            'numeric': True
        },
        'nombre': {
            'required': True,
            'min_length': 3,
            'max_length': 100
        },
        'telefono': {
            'required': False,
            'min_length': 7,
            'max_length': 15,
            'numeric': True
        },
        'email': {
            'required': False,
            'format': 'email'
        }
    },
    'productos': {
        'codigo': {
            'required': True,
            'unique': True,
            'max_length': 20
        },
        'nombre': {
            'required': True,
            'min_length': 3,
            'max_length': 200
        },
        'valor_unitario': {
            'required': True,
            'numeric': True,
            'min_value': 0
        }
    }
}

# ===================== FUNCIONES AUXILIARES =====================

def get_database_url(db_name):
    """Obtener URL de conexión para una base de datos específica"""
    if db_name in DATABASE_CONFIG:
        return f"sqlite:///{DATABASE_CONFIG[db_name]['path']}"
    return None

def get_color(color_name, default='#000000'):
    """Obtener color del tema"""
    return COLOR_THEME.get(color_name, default)

def get_font(size='normal', weight='normal'):
    """Obtener configuración de fuente"""
    font_size = FONT_CONFIG['size'].get(size, 10)
    font_weight = FONT_CONFIG['weight'].get(weight, 'normal')
    return (FONT_CONFIG['family'], font_size, font_weight)

def initialize_system():
    """Inicializar el sistema creando directorios y configuraciones"""
    print("🚀 Inicializando sistema...")
    
    # Crear directorios
    create_directories()
    
    # Verificar dependencias
    check_dependencies()
    
    print("✅ Sistema inicializado correctamente")

def check_dependencies():
    """Verificar dependencias del sistema"""
    required_packages = [
        'tkinter', 'sqlite3', 'datetime', 'pathlib', 'os', 'sys'
    ]
    
    optional_packages = {
        'openpyxl': 'Para funcionalidades de Excel',
        'reportlab': 'Para generación de PDFs',
        'pillow': 'Para manejo de imágenes',
        'matplotlib': 'Para gráficos y estadísticas'
    }
    
    print("📦 Verificando dependencias...")
    
    # Verificar paquetes requeridos
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - REQUERIDO")
    
    # Verificar paquetes opcionales
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"⚠️  {package} - {description} (Opcional)")

def get_system_info():
    """Obtener información del sistema"""
    return {
        **SYSTEM_INFO,
        'directories': {name: str(path) for name, path in DIRECTORIES.items()},
        'databases': len(DATABASE_CONFIG),
        'modules': ['Personal', 'Contratos', 'Químicos', 'Almacén', 'Poscosecha']
    }

# ===================== CONFIGURACIÓN DE DESARROLLO =====================

# Configuración para modo desarrollo
DEBUG_CONFIG = {
    'enabled': False,  # Cambiar a True para modo desarrollo
    'show_sql': False,
    'auto_reload': False,
    'test_data': True,
    'skip_validations': False
}

# Datos de prueba para desarrollo
TEST_DATA = {
    'empleados': [
        {
            'nombre_completo': 'Juan Pérez García',
            'cedula': '12345678',
            'telefono': '3001234567',
            'email': 'juan.perez@empresa.com',
            'area_trabajo': 'planta',
            'cargo': 'operario',
            'salario_base': 1300000
        },
        {
            'nombre_completo': 'María González López',
            'cedula': '87654321',
            'telefono': '3009876543',
            'email': 'maria.gonzalez@empresa.com',
            'area_trabajo': 'postcosecha',
            'cargo': 'supervisor',
            'salario_base': 1800000
        }
    ]
}

# ===================== FUNCIÓN PRINCIPAL =====================

if __name__ == "__main__":
    # Ejecutar inicialización si se ejecuta directamente
    initialize_system()
    
    # Mostrar información del sistema
    info = get_system_info()
    print("\n📋 INFORMACIÓN DEL SISTEMA:")
    print(f"Nombre: {info['name']}")
    print(f"Versión: {info['version']}")
    print(f"Módulos: {', '.join(info['modules'])}")
    print(f"Bases de datos: {info['databases']}")
    print(f"Última actualización: {info['last_update']}")