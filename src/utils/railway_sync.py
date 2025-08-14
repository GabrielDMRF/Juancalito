import requests
import json
import sqlite3
from datetime import datetime, date
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class RailwaySync:
    def __init__(self, railway_url="https://juancalito-production.up.railway.app", local_db_path="empleados.db"):
        self.railway_url = railway_url
        self.local_db_path = local_db_path
        
    def sync_empleados_to_railway(self):
        """Sincronizar empleados de la app local a Railway"""
        try:
            # Obtener empleados de la base de datos local
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cedula, nombre_completo, telefono, email, direccion, 
                       fecha_ingreso, area_trabajo, cargo, salario_base, estado
                FROM empleados
            """)
            
            empleados = cursor.fetchall()
            conn.close()
            
            if not empleados:
                logger.info("No hay empleados para sincronizar")
                return True
            
            # Enviar cada empleado a Railway
            success_count = 0
            for empleado in empleados:
                empleado_data = {
                    'cedula': empleado[0],
                    'nombre_completo': empleado[1],
                    'telefono': empleado[2] or '',
                    'email': empleado[3] or '',
                    'direccion': empleado[4] or '',
                    'fecha_ingreso': empleado[5] or '',
                    'area_trabajo': empleado[6] or '',
                    'cargo': empleado[7] or '',
                    'salario_base': empleado[8] or 0,
                    'estado': empleado[9] or 1
                }
                
                if self._send_empleado_to_railway(empleado_data):
                    success_count += 1
                else:
                    logger.error(f"Error enviando empleado {empleado[0]} a Railway")
                
            logger.info(f"Sincronizados {success_count}/{len(empleados)} empleados a Railway")
            return success_count == len(empleados)
            
        except Exception as e:
            logger.error(f"Error sincronizando empleados: {e}")
            return False
    
    def sync_asistencias_to_railway(self):
        """Sincronizar asistencias de la app local a Railway"""
        try:
            # Obtener asistencias de la base de datos local
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.fecha, a.hora_entrada, a.hora_salida, a.tipo_registro,
                       a.token_qr, a.ip_registro, a.dispositivo,
                       e.cedula, e.nombre_completo
                FROM asistencias a
                JOIN empleados e ON a.empleado_id = e.id
            """)
            
            asistencias = cursor.fetchall()
            conn.close()
            
            # Enviar cada asistencia a Railway
            for asistencia in asistencias:
                self._send_asistencia_to_railway({
                    'fecha': asistencia[0],
                    'hora_entrada': asistencia[1],
                    'hora_salida': asistencia[2],
                    'tipo_registro': asistencia[3],
                    'token_qr': asistencia[4],
                    'ip_registro': asistencia[5],
                    'dispositivo': asistencia[6],
                    'cedula_empleado': asistencia[7],
                    'nombre_empleado': asistencia[8]
                })
                
            logger.info(f"Sincronizadas {len(asistencias)} asistencias a Railway")
            return True
            
        except Exception as e:
            logger.error(f"Error sincronizando asistencias: {e}")
            return False
    
    def sync_from_railway(self):
        """Sincronizar datos desde Railway a la app local"""
        try:
            # Obtener solo asistencias recientes (más eficiente)
            response = requests.get(f"{self.railway_url}/sync_recent_asistencias", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Sincronizar asistencias
                if 'asistencias' in data:
                    self._sync_asistencias_from_railway(data['asistencias'])
                    logger.info(f"Sincronizadas {len(data['asistencias'])} asistencias desde Railway")
                    
                return True
            else:
                logger.error(f"Error obteniendo datos de Railway: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Timeout sincronizando desde Railway")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión con Railway")
            return False
        except Exception as e:
            logger.error(f"Error sincronizando desde Railway: {e}")
            return False
    
    def _send_empleado_to_railway(self, empleado_data):
        """Enviar un empleado específico a Railway"""
        try:
            response = requests.post(
                f"{self.railway_url}/sync_empleado",
                json=empleado_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Error HTTP {response.status_code}: {response.text}")
                # Si es error 500, intentar de nuevo después de un delay
                if response.status_code == 500:
                    import time
                    time.sleep(2)
                    response = requests.post(
                        f"{self.railway_url}/sync_empleado",
                        json=empleado_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return True
                return False
                
            return True
            
        except requests.exceptions.Timeout:
            logger.error("Timeout enviando empleado a Railway")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión con Railway")
            return False
        except Exception as e:
            logger.error(f"Error enviando empleado a Railway: {e}")
            return False
    
    def _send_asistencia_to_railway(self, asistencia_data):
        """Enviar una asistencia específica a Railway"""
        try:
            response = requests.post(
                f"{self.railway_url}/sync_asistencia",
                json=asistencia_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error enviando asistencia a Railway: {e}")
            return False
    
    def _sync_empleados_from_railway(self, empleados_data):
        """Sincronizar empleados desde Railway a la base local"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            for empleado in empleados_data:
                cursor.execute("""
                    INSERT OR REPLACE INTO empleados 
                    (cedula, nombre_completo, telefono, email, direccion, 
                     fecha_ingreso, area_trabajo, cargo, salario_base, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    empleado['cedula'], empleado['nombre_completo'],
                    empleado.get('telefono'), empleado.get('email'),
                    empleado.get('direccion'), empleado.get('fecha_ingreso'),
                    empleado.get('area_trabajo'), empleado.get('cargo'),
                    empleado.get('salario_base'), empleado.get('estado', 1)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error sincronizando empleados desde Railway: {e}")
    
    def _sync_asistencias_from_railway(self, asistencias_data):
        """Sincronizar asistencias desde Railway a la base local"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            sync_count = 0
            for asistencia in asistencias_data:
                try:
                    # Primero obtener el empleado_id
                    cursor.execute("SELECT id FROM empleados WHERE cedula = ?", (asistencia['cedula_empleado'],))
                    empleado_result = cursor.fetchone()
                    
                    if empleado_result:
                        empleado_id = empleado_result[0]
                        
                        # Verificar si ya existe esta asistencia
                        cursor.execute("""
                            SELECT id FROM asistencias 
                            WHERE empleado_id = ? AND fecha = ? AND token_qr = ?
                        """, (empleado_id, asistencia['fecha'], asistencia.get('token_qr')))
                        
                        existing = cursor.fetchone()
                        
                        if not existing:
                            # Insertar nueva asistencia
                            cursor.execute("""
                                INSERT INTO asistencias 
                                (empleado_id, fecha, hora_entrada, hora_salida, 
                                 tipo_registro, token_qr, ip_registro, dispositivo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                empleado_id, asistencia['fecha'], asistencia.get('hora_entrada'),
                                asistencia.get('hora_salida'), asistencia.get('tipo_registro'),
                                asistencia.get('token_qr'), asistencia.get('ip_registro'),
                                asistencia.get('dispositivo')
                            ))
                            sync_count += 1
                        else:
                            # Actualizar asistencia existente
                            cursor.execute("""
                                UPDATE asistencias 
                                SET hora_entrada = ?, hora_salida = ?, tipo_registro = ?,
                                    ip_registro = ?, dispositivo = ?
                                WHERE id = ?
                            """, (
                                asistencia.get('hora_entrada'), asistencia.get('hora_salida'),
                                asistencia.get('tipo_registro'), asistencia.get('ip_registro'),
                                asistencia.get('dispositivo'), existing[0]
                            ))
                            sync_count += 1
                    else:
                        logger.warning(f"Empleado no encontrado: {asistencia['cedula_empleado']}")
                        
                except Exception as e:
                    logger.error(f"Error procesando asistencia individual: {e}")
                    continue
            
            conn.commit()
            conn.close()
            logger.info(f"Sincronizadas {sync_count} asistencias desde Railway")
            
        except Exception as e:
            logger.error(f"Error sincronizando asistencias desde Railway: {e}")
    
    def get_railway_status(self):
        """Verificar el estado de Railway"""
        try:
            response = requests.get(f"{self.railway_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
