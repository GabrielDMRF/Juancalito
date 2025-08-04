import sqlite3
import os
# Línea 3, cambiar:
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Empleado(Base):
    __tablename__ = 'empleados'
    
    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(15))
    email = Column(String(50))
    direccion = Column(String(200))
    fecha_ingreso = Column(Date)
    area_trabajo = Column(String(50))  # planta/postcosecha
    cargo = Column(String(50))
    salario_base = Column(Integer)
    estado = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    carpeta_personal = Column(String(300))
    
    # Campos adicionales para el contrato
    lugar_nacimiento = Column(String(100))
    fecha_nacimiento = Column(Date)
    nacionalidad = Column(String(50), default="COLOMBIANA")  
    
    # Relaciones
    contratos = relationship("Contrato", back_populates="empleado")
    documentos = relationship("DocumentoEmpleado", back_populates="empleado")  

class Contrato(Base):
    __tablename__ = 'contratos'
    
    id = Column(Integer, primary_key=True)
    numero_contrato = Column(String(20), unique=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'))
    tipo_contrato_id = Column(Integer, ForeignKey('tipos_contrato.id'))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    salario_contrato = Column(Integer)
    archivo_path = Column(String(255))
    estado = Column(String(20), default='borrador')  # 🆕 CAMBIADO Boolean a String
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # 🆕 NUEVOS CAMPOS:
    salario_base = Column(Integer)
    subsidio_transporte = Column(Integer, default=0)
    bonificaciones = Column(Integer, default=0)
    archivo_contrato_word = Column(String(400))
    
    # Relaciones
    empleado = relationship("Empleado", back_populates="contratos")
    tipo_contrato_rel = relationship("TipoContrato", back_populates="contratos")  # 🆕 NUEVA LÍNEA
    documentos = relationship("DocumentoEmpleado", back_populates="contrato")  # 🆕 NUEVA LÍNEA

class TipoContrato(Base):
    __tablename__ = 'tipos_contrato'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200))
    dias_vigencia_default = Column(Integer)
    
    contratos = relationship("Contrato", back_populates="tipo_contrato_rel") 

class DocumentoEmpleado(Base):
    __tablename__ = 'documentos_empleado'
    
    id = Column(Integer, primary_key=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=False)
    contrato_id = Column(Integer, ForeignKey('contratos.id'), nullable=True)
    
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    tipo_documento = Column(String(50))
    categoria = Column(String(50))
    
    tamaño_archivo = Column(Integer)
    extension = Column(String(10))
    fecha_subida = Column(DateTime, default=datetime.now)
    descripcion = Column(String(200))
    
    empleado = relationship("Empleado", back_populates="documentos")
    contrato = relationship("Contrato", back_populates="documentos")




# Configuración de la base de datos
def get_database_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_dir = os.path.join(base_dir, 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    return os.path.join(db_dir, 'gestion_personal.db')

DATABASE_URL = f"sqlite:///{get_database_path()}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        crear_tipos_contrato_default()  # 🆕 NUEVA LÍNEA
        crear_directorios_base()  # 🆕 NUEVA LÍNEA
        print("[OK] Tablas y directorios creados exitosamente")
        return True
    except Exception as e:
        print(f"[ERROR] Error creando tablas: {e}")
        return False

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

# Función de prueba
def test_database():
    try:
        print("Iniciando prueba de base de datos...")
        
        # Crear tablas
        if not create_tables():
            return False
            
        db = get_db()
        
        # Verificar si ya existe el empleado de prueba
        empleado_existente = db.query(Empleado).filter(Empleado.cedula == "12345678").first()
        
        if not empleado_existente:
            # Crear empleado de prueba
            empleado_prueba = Empleado(
                nombre_completo="Juan Perez",
                cedula="12345678",
                telefono="3001234567",
                area_trabajo="planta",
                cargo="operario",
                salario_base=1300000
            )
            
            db.add(empleado_prueba)
            db.commit()
            print("[OK] Empleado de prueba creado")
        else:
            print("[INFO] Empleado de prueba ya existe")
        
        # Verificar que se guardó
        empleados = db.query(Empleado).all()
        print(f"[OK] Base de datos funcionando - {len(empleados)} empleados registrados")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en base de datos: {e}")
        return False
    
def crear_tipos_contrato_default():
    """Crear tipos de contrato por defecto"""
    tipos = [
        {"nombre": "temporal", "descripcion": "Contrato temporal", "dias_vigencia_default": 90},
        {"nombre": "permanente", "descripcion": "Contrato indefinido", "dias_vigencia_default": None},
        {"nombre": "temporada", "descripcion": "Contrato por temporada", "dias_vigencia_default": 120}
    ]
    
    db = SessionLocal()
    for tipo_data in tipos:
        existente = db.query(TipoContrato).filter(TipoContrato.nombre == tipo_data["nombre"]).first()
        if not existente:
            tipo = TipoContrato(**tipo_data)
            db.add(tipo)
    
    db.commit()
    db.close()

def crear_directorios_base():
    """Crear directorios necesarios"""
    directorios = ["empleados_data", "temp"]
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    for directorio in directorios:
        ruta = os.path.join(base_dir, directorio)
        os.makedirs(ruta, exist_ok=True)    


if __name__ == "__main__":
    test_database()