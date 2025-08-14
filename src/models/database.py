import os
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
import requests
import json

# Configuración de base de datos local
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'empleados.db')
LOCAL_ENGINE = create_engine(f'sqlite:///{DB_PATH}')
LOCAL_SESSION = sessionmaker(bind=LOCAL_ENGINE)

Base = declarative_base()

# Configuración de base de datos centralizada en Railway
RAILWAY_DB_URL = "https://juancalito-production.up.railway.app"

class Empleado(Base):
    __tablename__ = 'empleados'
    
    id = Column(Integer, primary_key=True)
    cedula = Column(String(20), unique=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(Text)
    fecha_ingreso = Column(Date)
    area_trabajo = Column(String(50))
    cargo = Column(String(50))
    salario_base = Column(Float)
    estado = Column(Boolean, default=True)
    
    contratos = relationship("Contrato", back_populates="empleado")
    asistencias = relationship("Asistencia", back_populates="empleado")

class TipoContrato(Base):
    __tablename__ = 'tipos_contrato'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text)

class Contrato(Base):
    __tablename__ = 'contratos'
    
    id = Column(Integer, primary_key=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'))
    tipo_contrato_id = Column(Integer, ForeignKey('tipos_contrato.id'))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    salario = Column(Float, nullable=False)
    estado = Column(String(20), default='activo')
    
    empleado = relationship("Empleado", back_populates="contratos")
    tipo_contrato = relationship("TipoContrato")

class Asistencia(Base):
    __tablename__ = 'asistencias'
    
    id = Column(Integer, primary_key=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'))
    fecha = Column(Date, nullable=False)
    hora_entrada = Column(DateTime)
    hora_salida = Column(DateTime)
    tipo_registro = Column(String(20), default='entrada')
    token_qr = Column(String(100))
    ip_registro = Column(String(45))
    dispositivo = Column(Text)
    
    empleado = relationship("Empleado", back_populates="asistencias")

class TokenQR(Base):
    __tablename__ = 'tokens_qr'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(100), unique=True, nullable=False)
    fecha_generacion = Column(Date, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True)

class RailwayDatabase:
    """Clase para manejar operaciones con la base de datos de Railway"""
    
    def __init__(self):
        self.base_url = RAILWAY_DB_URL
        self.session = None
    
    def get_empleados(self):
        """Obtener todos los empleados desde Railway"""
        try:
            response = requests.get(f"{self.base_url}/api/empleados", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error obteniendo empleados: {e}")
            return []
    
    def get_asistencias(self, fecha_inicio=None, fecha_fin=None):
        """Obtener asistencias desde Railway"""
        try:
            params = {}
            if fecha_inicio:
                params['fecha_inicio'] = fecha_inicio
            if fecha_fin:
                params['fecha_fin'] = fecha_fin
                
            response = requests.get(f"{self.base_url}/api/asistencias", params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error obteniendo asistencias: {e}")
            return []
    
    def add_empleado(self, empleado_data):
        """Agregar empleado a Railway"""
        try:
            response = requests.post(
                f"{self.base_url}/api/empleados",
                json=empleado_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error agregando empleado: {e}")
            return False
    
    def add_asistencia(self, asistencia_data):
        """Agregar asistencia a Railway"""
        try:
            response = requests.post(
                f"{self.base_url}/api/asistencias",
                json=asistencia_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error agregando asistencia: {e}")
            return False
    
    def update_empleado(self, empleado_id, empleado_data):
        """Actualizar empleado en Railway"""
        try:
            response = requests.put(
                f"{self.base_url}/api/empleados/{empleado_id}",
                json=empleado_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error actualizando empleado: {e}")
            return False
    
    def delete_empleado(self, empleado_id):
        """Eliminar empleado de Railway"""
        try:
            response = requests.delete(f"{self.base_url}/api/empleados/{empleado_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error eliminando empleado: {e}")
            return False

# Instancia global de la base de datos de Railway
railway_db = RailwayDatabase()

# Función para obtener la sesión de Railway
def get_railway_session():
    return railway_db

# Función para obtener la base de datos (compatibilidad con código existente)
def get_db():
    """Devuelve una sesión de SQLAlchemy para la base de datos local"""
    return LOCAL_SESSION()

# Función para crear tablas (compatibilidad con código existente)
def create_tables():
    """Crear las tablas en la base de datos local"""
    Base.metadata.create_all(LOCAL_ENGINE)

# Función para obtener la ruta de la base de datos (compatibilidad con código existente)
def get_database_path():
    """Obtener la ruta de la base de datos local"""
    return DB_PATH