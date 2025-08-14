from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import os
import hashlib
from datetime import datetime, date, timedelta
import threading
import time
from pathlib import Path
import qrcode
from PIL import Image
import io
import base64
import socket

class QRServer:
    def __init__(self, db_path, port=5000):
        self.app = Flask(__name__)
        self.db_path = db_path
        self.port = port
        self.server_thread = None
        self.is_running = False
        
        # Configurar rutas
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/')
        def home():
            # Redirigir al formulario de asistencia con un token válido
            try:
                # Obtener el token del día
                fecha_actual = date.today()
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT token FROM tokens_qr 
                    WHERE fecha_generacion = ? AND activo = 1
                """, (fecha_actual,))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    token = result[0]
                    return redirect(f'/asistencia?token={token}')
                else:
                    # Si no hay token, generar uno nuevo
                    qr_data = self.generar_qr_diario()
                    return redirect(f'/asistencia?token={qr_data["token"]}')
                    
            except Exception as e:
                print(f"Error redirigiendo al formulario: {e}")
                return "Error: No se pudo acceder al formulario de asistencia", 500
        
        @self.app.route('/asistencia')
        def asistencia():
            token = request.args.get('token')
            if not token:
                return "Token no válido", 400
            
            # Verificar si el token es válido
            if not self.verificar_token(token):
                return "Token expirado o no válido", 400
            
            return self.render_formulario_asistencia(token)
        
        @self.app.route('/registrar_asistencia', methods=['POST'])
        def registrar_asistencia():
            try:
                token = request.form.get('token')
                documento = request.form.get('documento')
                nombre = request.form.get('nombre')
                tipo_registro = request.form.get('tipo_registro', 'entrada')
                
                if not all([token, documento, nombre]):
                    return jsonify({'error': 'Todos los campos son requeridos'}), 400
                
                # Verificar token
                if not self.verificar_token(token):
                    return jsonify({'error': 'Token expirado'}), 400
                
                # Registrar asistencia
                resultado = self.procesar_asistencia(token, documento, nombre, request, tipo_registro)
                
                if resultado['success']:
                    return self.render_exito(resultado['mensaje'], tipo_registro, token)
                else:
                    return self.render_error(resultado['mensaje'])
                    
            except Exception as e:
                return jsonify({'error': f'Error interno: {str(e)}'}), 500
        
        @self.app.route('/qr_diario')
        def qr_diario():
            """Endpoint para obtener el QR del día"""
            try:
                qr_data = self.generar_qr_diario()
                return jsonify(qr_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/network_info')
        def network_info_page():
            """Página con información de red y opciones de conexión"""
            return self.render_network_info()
    
    def verificar_token(self, token):
        """Verificar si el token es válido y no ha expirado"""
        try:
            # Para tokens de Railway, siempre aceptar si tienen el formato correcto
            if token and '_' in token:
                # Verificar que el token tenga el formato de fecha_hash
                parts = token.split('_')
                if len(parts) == 2:
                    fecha_str = parts[0]
                    try:
                        # Verificar que la fecha sea válida
                        fecha_token = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                        fecha_actual = date.today()
                        
                        # Aceptar tokens del día actual
                        if fecha_token == fecha_actual:
                            return True
                    except:
                        pass
            
            # Si no es un token de Railway, verificar en la base de datos local
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT activo, fecha_expiracion FROM tokens_qr 
                WHERE token = ? AND activo = 1
            """, (token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                activo, fecha_expiracion = result
                if activo and datetime.fromisoformat(fecha_expiracion) > datetime.now():
                    return True
            
            return False
        except Exception as e:
            print(f"Error verificando token: {e}")
            return False
    
    def procesar_asistencia(self, token, documento, nombre, request, tipo_registro='entrada'):
        """Procesar el registro de asistencia con tipo específico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar empleado por documento
            cursor.execute("""
                SELECT id, nombre_completo FROM empleados 
                WHERE cedula = ? AND estado = 1
            """, (documento,))
            
            empleado = cursor.fetchone()
            if not empleado:
                conn.close()
                return {'success': False, 'mensaje': 'Empleado no encontrado o inactivo'}
            
            empleado_id, nombre_db = empleado
            
            # Verificar si ya hay un registro para hoy
            hoy = date.today()
            cursor.execute("""
                SELECT id, hora_entrada, hora_salida FROM asistencias 
                WHERE empleado_id = ? AND fecha = ?
            """, (empleado_id, hoy))
            
            registro_existente = cursor.fetchone()
            ahora = datetime.now()
            
            if tipo_registro == 'entrada':
                if registro_existente and registro_existente[1]:  # Ya tiene entrada
                    return {'success': False, 'mensaje': 'Ya tienes entrada registrada para hoy'}
                
                # Registrar entrada
                if registro_existente:
                    # Actualizar entrada existente
                    cursor.execute("""
                        UPDATE asistencias 
                        SET hora_entrada = ?, tipo_registro = 'entrada'
                        WHERE id = ?
                    """, (ahora, registro_existente[0]))
                else:
                    # Crear nuevo registro
                    cursor.execute("""
                        INSERT INTO asistencias (empleado_id, fecha, hora_entrada, tipo_registro, token_qr, ip_registro, dispositivo)
                        VALUES (?, ?, ?, 'entrada', ?, ?, ?)
                    """, (empleado_id, hoy, ahora, token, request.remote_addr, request.headers.get('User-Agent', '')))
                
                mensaje = f"✅ Entrada registrada exitosamente a las {ahora.strftime('%H:%M:%S')}"
                
            elif tipo_registro == 'salida':
                if not registro_existente or not registro_existente[1]:  # No tiene entrada
                    return {'success': False, 'mensaje': 'Debes registrar entrada antes de salida'}
                
                if registro_existente[2]:  # Ya tiene salida
                    return {'success': False, 'mensaje': 'Ya tienes salida registrada para hoy'}
                
                # Registrar salida
                cursor.execute("""
                    UPDATE asistencias 
                    SET hora_salida = ?, tipo_registro = 'salida'
                    WHERE id = ?
                """, (ahora, registro_existente[0]))
                
                # Calcular horas trabajadas
                hora_entrada = datetime.fromisoformat(registro_existente[1])
                tiempo_trabajado = ahora - hora_entrada
                horas = tiempo_trabajado.total_seconds() / 3600
                
                mensaje = f"🚪 Salida registrada exitosamente a las {ahora.strftime('%H:%M:%S')}<br>⏱️ Horas trabajadas: {horas:.2f} horas"
            
            conn.commit()
            conn.close()
            
            # Sincronizar con Railway después de guardar localmente
            try:
                self._sincronizar_con_railway(empleado_id, hoy, ahora, tipo_registro, token, request)
            except Exception as e:
                print(f"Error sincronizando con Railway: {e}")
            
            return {'success': True, 'mensaje': mensaje}
            
        except Exception as e:
            print(f"Error procesando asistencia: {e}")
            return {'success': False, 'mensaje': f'Error interno: {str(e)}'}
    
    def _sincronizar_con_railway(self, empleado_id, fecha, hora, tipo_registro, token, request):
        """Sincronizar asistencia con Railway"""
        try:
            import requests
            
            # Obtener datos del empleado
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cedula, nombre_completo FROM empleados WHERE id = ?
            """, (empleado_id,))
            
            empleado = cursor.fetchone()
            conn.close()
            
            if not empleado:
                return
            
            cedula, nombre = empleado
            
            # Preparar datos para Railway
            asistencia_data = {
                'fecha': fecha.isoformat(),
                'hora_entrada': hora.isoformat() if tipo_registro == 'entrada' else None,
                'hora_salida': hora.isoformat() if tipo_registro == 'salida' else None,
                'tipo_registro': tipo_registro,
                'token_qr': token,
                'ip_registro': request.remote_addr,
                'dispositivo': request.headers.get('User-Agent', ''),
                'cedula_empleado': cedula,
                'nombre_empleado': nombre
            }
            
            # Enviar a Railway
            response = requests.post(
                'https://juancalito-production.up.railway.app/sync_asistencia',
                json=asistencia_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Asistencia sincronizada con Railway: {nombre} - {tipo_registro}")
            else:
                print(f"❌ Error sincronizando con Railway: {response.status_code}")
                
        except Exception as e:
            print(f"Error en sincronización Railway: {e}")
    
    def generar_qr_diario(self):
        """Generar QR del día con token único"""
        try:
            # Crear token único para el día
            fecha_actual = date.today()
            token_base = f"{fecha_actual.isoformat()}_{hashlib.md5(str(fecha_actual).encode()).hexdigest()[:8]}"
            
            # Verificar si ya existe un token para hoy
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT token FROM tokens_qr 
                WHERE fecha_generacion = ? AND activo = 1
            """, (fecha_actual,))
            
            existing_token = cursor.fetchone()
            
            if existing_token:
                token = existing_token[0]
            else:
                # Crear nuevo token
                token = token_base
                fecha_expiracion = datetime.combine(fecha_actual, datetime.max.time())
                
                cursor.execute("""
                    INSERT INTO tokens_qr (token, fecha_generacion, fecha_expiracion, activo)
                    VALUES (?, ?, ?, 1)
                """, (token, fecha_actual, fecha_expiracion))
                
                conn.commit()
            
            conn.close()
            
            # Obtener IP local para el QR
            ip_local = self._obtener_ip_local()
            
            # Generar URL del QR - SIEMPRE usar Railway para que funcione desde cualquier lugar
            url = f"https://juancalito-production.up.railway.app/asistencia?token={token}"
            
            # Generar imagen QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'token': token,
                'url': url,
                'qr_image': f"data:image/png;base64,{img_str}",
                'fecha': fecha_actual.isoformat(),
                'ip_local': ip_local
            }
            
        except Exception as e:
            print(f"Error generando QR: {e}")
            raise e
    
    def _obtener_ip_local(self):
        """Obtener la IP local de la computadora"""
        try:
            import socket
            # Conectar a un servidor externo para obtener la IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_local = s.getsockname()[0]
            s.close()
            return ip_local
        except Exception:
            # Si falla, usar localhost como respaldo
            return "localhost"
    
    def render_formulario_asistencia(self, token):
        """Renderizar formulario de asistencia mejorado"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Registro de Asistencia</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .info {{
                    background-color: #e8f4fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                    border-left: 4px solid #3498db;
                    text-align: center;
                }}
                .info h2 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                    font-size: 18px;
                }}
                .info p {{
                    margin: 5px 0;
                    font-size: 16px;
                    color: #34495e;
                }}
                .form-group {{
                    margin-bottom: 20px;
                }}
                label {{
                    display: block;
                    margin-bottom: 8px;
                    font-weight: bold;
                    color: #34495e;
                    font-size: 14px;
                }}
                input[type="text"] {{
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                    box-sizing: border-box;
                    transition: border-color 0.3s;
                }}
                input[type="text"]:focus {{
                    border-color: #3498db;
                    outline: none;
                    box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
                }}
                .btn-container {{
                    display: flex;
                    gap: 15px;
                    margin-top: 25px;
                }}
                .btn-entrada {{
                    flex: 1;
                    padding: 15px;
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .btn-salida {{
                    flex: 1;
                    padding: 15px;
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                }}
                .btn-entrada:hover {{
                    background-color: #229954;
                    transform: translateY(-2px);
                }}
                .btn-salida:hover {{
                    background-color: #c0392b;
                    transform: translateY(-2px);
                }}
                .loading {{
                    display: none;
                    text-align: center;
                    margin-top: 20px;
                }}
                .spinner {{
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #3498db;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 10px;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
                .error {{
                    background-color: #fadbd8;
                    color: #c0392b;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                    display: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📱 Registro de Asistencia</h1>
                
                <div class="info">
                    <h2>📅 Información del Registro</h2>
                    <p><strong>Fecha:</strong> <span id="fecha-actual">{date.today().strftime('%d/%m/%Y')}</span></p>
                    <p><strong>Hora:</strong> <span id="hora-actual"></span></p>
                    <p><strong>Token QR:</strong> <span style="font-family: monospace; font-size: 12px;">{token[:20]}...</span></p>
                </div>
                
                <form id="asistenciaForm">
                    <input type="hidden" name="token" value="{token}">
                    <input type="hidden" name="tipo_registro" id="tipo_registro" value="entrada">
                    
                    <div class="form-group">
                        <label for="documento">📄 Número de Documento:</label>
                        <input type="text" id="documento" name="documento" required 
                               placeholder="Ej: 12345678" maxlength="20">
                    </div>
                    
                    <div class="form-group">
                        <label for="nombre">👤 Nombre Completo:</label>
                        <input type="text" id="nombre" name="nombre" required 
                               placeholder="Ej: Juan Pérez González" maxlength="100">
                    </div>
                    
                    <div class="btn-container">
                        <button type="button" class="btn-entrada" onclick="registrarAsistencia('entrada')">
                            ✅ Marcar Entrada
                        </button>
                        <button type="button" class="btn-salida" onclick="registrarAsistencia('salida')">
                            🚪 Marcar Salida
                        </button>
                    </div>
                </form>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Procesando registro...</p>
                </div>
                
                <div class="error" id="error"></div>
            </div>
            
            <script>
                function actualizarHora() {{
                    const ahora = new Date();
                    const hora = ahora.toLocaleTimeString('es-ES');
                    document.getElementById('hora-actual').textContent = hora;
                }}
                
                function registrarAsistencia(tipo) {{
                    const documento = document.getElementById('documento').value.trim();
                    const nombre = document.getElementById('nombre').value.trim();
                    
                    if (!documento || !nombre) {{
                        mostrarError('Por favor complete todos los campos');
                        return;
                    }}
                    
                    // Mostrar loading
                    document.getElementById('loading').style.display = 'block';
                    document.getElementById('error').style.display = 'none';
                    
                    // Deshabilitar botones
                    document.querySelectorAll('button').forEach(btn => btn.disabled = true);
                    
                    const formData = new FormData();
                    formData.append('token', '{token}');
                    formData.append('documento', documento);
                    formData.append('nombre', nombre);
                    formData.append('tipo_registro', tipo);
                    
                    fetch('/registrar_asistencia', {{
                        method: 'POST',
                        body: formData
                    }})
                    .then(response => response.text())
                    .then(html => {{
                        document.body.innerHTML = html;
                    }})
                    .catch(error => {{
                        console.error('Error:', error);
                        mostrarError('Error de conexión. Intente nuevamente.');
                        document.getElementById('loading').style.display = 'none';
                        document.querySelectorAll('button').forEach(btn => btn.disabled = false);
                    }});
                }}
                
                function mostrarError(mensaje) {{
                    const errorDiv = document.getElementById('error');
                    errorDiv.textContent = mensaje;
                    errorDiv.style.display = 'block';
                }}
                
                // Actualizar hora cada segundo
                actualizarHora();
                setInterval(actualizarHora, 1000);
                
                // Auto-focus en el primer campo
                document.getElementById('documento').focus();
            </script>
        </body>
        </html>
        """
        return html
    
    def render_exito(self, mensaje, tipo_registro='entrada', token=None):
        """Renderizar página de éxito mejorada"""
        icono = "✅" if tipo_registro == 'entrada' else "🚪"
        color = "#27ae60" if tipo_registro == 'entrada' else "#e74c3c"
        titulo = "¡Entrada Registrada!" if tipo_registro == 'entrada' else "¡Salida Registrada!"
        
        # Obtener token si no se proporciona
        if not token:
            try:
                fecha_actual = date.today()
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT token FROM tokens_qr 
                    WHERE fecha_generacion = ? AND activo = 1
                """, (fecha_actual,))
                result = cursor.fetchone()
                conn.close()
                token = result[0] if result else ""
            except:
                token = ""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Asistencia Registrada</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .success-icon {{
                    font-size: 80px;
                    color: {color};
                    margin-bottom: 20px;
                    animation: bounce 1s ease-in-out;
                }}
                @keyframes bounce {{
                    0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
                    40% {{ transform: translateY(-10px); }}
                    60% {{ transform: translateY(-5px); }}
                }}
                h1 {{
                    color: {color};
                    margin-bottom: 25px;
                    font-size: 28px;
                }}
                .mensaje {{
                    background-color: #d5f4e6;
                    padding: 25px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    border-left: 6px solid {color};
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .info-adicional {{
                    background-color: #e8f4fd;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 25px;
                    border-left: 4px solid #3498db;
                }}
                .btn-container {{
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 25px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    transition: all 0.3s;
                }}
                .btn:hover {{
                    background-color: #2980b9;
                    transform: translateY(-2px);
                }}
                .btn-secundario {{
                    background-color: #95a5a6;
                }}
                .btn-secundario:hover {{
                    background-color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">{icono}</div>
                <h1>{titulo}</h1>
                <div class="mensaje">
                    {mensaje}
                </div>
                <div class="info-adicional">
                    <strong>📅 Fecha:</strong> {date.today().strftime('%d/%m/%Y')}<br>
                    <strong>🕐 Hora:</strong> <span id="hora-actual"></span><br>
                    <strong>📱 Dispositivo:</strong> {request.headers.get('User-Agent', 'No disponible')[:50]}...
                </div>
                <div class="btn-container">
                    <a href="/asistencia?token={token}" class="btn">🔄 Nuevo Registro</a>
                    <a href="/" class="btn btn-secundario">🏠 Volver al Inicio</a>
                    <a href="javascript:window.close()" class="btn btn-secundario">❌ Cerrar</a>
                </div>
            </div>
            
            <script>
                function actualizarHora() {{
                    const ahora = new Date();
                    const hora = ahora.toLocaleTimeString('es-ES');
                    document.getElementById('hora-actual').textContent = hora;
                }}
                
                actualizarHora();
                setInterval(actualizarHora, 1000);
                
                // Auto-cerrar después de 10 segundos
                setTimeout(() => {{
                    if (confirm('¿Deseas cerrar esta ventana?')) {{
                        window.close();
                    }}
                }}, 10000);
            </script>
        </body>
        </html>
        """
        return html
    
    def render_error(self, mensaje):
        """Renderizar página de error"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error en Registro</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 500px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .error-icon {{
                    font-size: 60px;
                    color: #e74c3c;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #e74c3c;
                    margin-bottom: 20px;
                }}
                .mensaje {{
                    background-color: #fadbd8;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 4px solid #e74c3c;
                }}
                .volver {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1>Error en el Registro</h1>
                <div class="mensaje">
                    {mensaje}
                </div>
                <div class="btn-container">
                    <a href="/" class="volver">🔄 Volver al Inicio</a>
                    <a href="javascript:window.close()" class="volver" style="margin-left: 10px;">❌ Cerrar</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def start_server(self):
        """Iniciar servidor en un hilo separado"""
        if not self.is_running:
            # Verificar si el puerto está disponible
            if self._puerto_disponible():
                self.is_running = True
                self.server_thread = threading.Thread(target=self._run_server, daemon=True)
                self.server_thread.start()
                print(f"Servidor QR iniciado en puerto {self.port}")
            else:
                print(f"Puerto {self.port} no disponible, intentando puerto alternativo...")
                # Intentar puerto alternativo
                self.port = 5001
                if self._puerto_disponible():
                    self.is_running = True
                    self.server_thread = threading.Thread(target=self._run_server, daemon=True)
                    self.server_thread.start()
                    print(f"Servidor QR iniciado en puerto {self.port}")
                else:
                    raise Exception(f"No se pudo iniciar el servidor en puertos 5000 o 5001")
    
    def _puerto_disponible(self):
        """Verificar si el puerto está disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', self.port))
                return True
        except OSError:
            return False
    
    def _run_server(self):
        """Ejecutar servidor Flask optimizado"""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False, threaded=True)
    
    def stop_server(self):
        """Detener servidor"""
        self.is_running = False
        print("Servidor QR detenido")

    def get_network_info(self):
        """Obtener información de red para múltiples opciones de conexión"""
        import socket
        import subprocess
        import platform
        
        network_info = {
            'local_ip': 'localhost',
            'wifi_ip': None,
            'ethernet_ip': None,
            'hotspot_ip': None,
            'connection_options': []
        }
        
        try:
            # Obtener todas las interfaces de red
            hostname = socket.gethostname()
            
            # Intentar obtener IP local
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                network_info['local_ip'] = local_ip
            except:
                pass
            
            # Detectar diferentes tipos de conexión
            if platform.system() == "Windows":
                try:
                    # Ejecutar ipconfig para obtener información detallada
                    result = subprocess.run(['ipconfig'], capture_output=True, text=True)
                    output = result.stdout
                    
                    # Buscar IPs de diferentes adaptadores
                    lines = output.split('\n')
                    current_adapter = None
                    
                    for line in lines:
                        line = line.strip()
                        if 'Ethernet adapter' in line or 'Wireless LAN adapter' in line:
                            current_adapter = line
                        elif 'IPv4 Address' in line and ':' in line:
                            ip = line.split(':')[1].strip().split('(')[0].strip()
                            if ip and ip != '127.0.0.1':
                                if 'Wireless' in current_adapter:
                                    network_info['wifi_ip'] = ip
                                elif 'Ethernet' in current_adapter:
                                    network_info['ethernet_ip'] = ip
                                
                                # Agregar a opciones de conexión
                                adapter_name = current_adapter.split('adapter')[-1].strip().strip(':')
                                network_info['connection_options'].append({
                                    'type': 'WiFi' if 'Wireless' in current_adapter else 'Ethernet',
                                    'adapter': adapter_name,
                                    'ip': ip,
                                    'url': f'http://{ip}:{self.port}'
                                })
                except:
                    pass
            
            # Agregar opción de hotspot
            network_info['hotspot_ip'] = network_info['local_ip']
            network_info['connection_options'].append({
                'type': 'Hotspot',
                'adapter': 'Hotspot Local',
                'ip': network_info['local_ip'],
                'url': f'http://{network_info["local_ip"]}:{self.port}'
            })
            
        except Exception as e:
            print(f"Error obteniendo información de red: {e}")
        
        return network_info

    def render_network_info(self):
        """Renderizar página con información de red y opciones de conexión"""
        network_info = self.get_network_info()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Asistencia QR - Opciones de Conexión</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                .content {{
                    padding: 30px;
                }}
                .connection-option {{
                    background: #f8f9fa;
                    border: 2px solid #e9ecef;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 15px 0;
                    transition: all 0.3s ease;
                }}
                .connection-option:hover {{
                    border-color: #3498db;
                    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);
                }}
                .connection-option h3 {{
                    margin: 0 0 10px 0;
                    color: #2c3e50;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .connection-option p {{
                    margin: 5px 0;
                    color: #6c757d;
                }}
                .url-box {{
                    background: #e9ecef;
                    border: 1px solid #ced4da;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                    word-break: break-all;
                }}
                .status {{
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 20px;
                    font-size: 0.8em;
                    font-weight: bold;
                    text-transform: uppercase;
                }}
                .status.available {{
                    background: #d4edda;
                    color: #155724;
                }}
                .status.recommended {{
                    background: #d1ecf1;
                    color: #0c5460;
                }}
                .instructions {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .instructions h4 {{
                    margin: 0 0 10px 0;
                    color: #856404;
                }}
                .instructions ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .instructions li {{
                    margin: 5px 0;
                    color: #856404;
                }}
                .qr-section {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 10px;
                }}
                .qr-code {{
                    max-width: 200px;
                    margin: 20px auto;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📱 Sistema de Asistencia QR</h1>
                    <p>Selecciona la opción de conexión más adecuada para tu empresa</p>
                </div>
                
                <div class="content">
                    <div class="instructions">
                        <h4>🔧 Opciones de Configuración para Empresas Sin WiFi Compartido:</h4>
                        <ul>
                            <li><strong>Red Local Dedicada:</strong> Conecta un router dedicado solo para el sistema</li>
                            <li><strong>Hotspot del Computador:</strong> Crea una red WiFi desde el servidor</li>
                            <li><strong>Cable Ethernet:</strong> Conecta directamente con cables de red</li>
                            <li><strong>Router Móvil:</strong> Usa un router 4G/5G independiente</li>
                        </ul>
                    </div>
                    
                    <h2>🌐 Opciones de Conexión Disponibles:</h2>
        """
        
        # Agregar opciones de conexión
        for i, option in enumerate(network_info['connection_options']):
            status_class = "recommended" if i == 0 else "available"
            status_text = "Recomendado" if i == 0 else "Disponible"
            
            html += f"""
                    <div class="connection-option">
                        <h3>
                            {'📶' if option['type'] == 'WiFi' else '🔌' if option['type'] == 'Ethernet' else '📱'} 
                            {option['type']} - {option['adapter']}
                            <span class="status {status_class}">{status_text}</span>
                        </h3>
                        <p><strong>IP:</strong> {option['ip']}</p>
                        <p><strong>Puerto:</strong> {self.port}</p>
                        <div class="url-box">
                            {option['url']}
                        </div>
                        <p><strong>Instrucciones:</strong></p>
                        <ul>
            """
            
            if option['type'] == 'WiFi':
                html += f"""
                            <li>Conecta los dispositivos a la red WiFi de la empresa</li>
                            <li>Accede desde cualquier dispositivo en la misma red</li>
                            <li>Ideal para oficinas con WiFi corporativo</li>
                """
            elif option['type'] == 'Ethernet':
                html += f"""
                            <li>Conecta dispositivos mediante cable de red</li>
                            <li>Configura un switch o hub para múltiples dispositivos</li>
                            <li>Opción más estable y segura</li>
                """
            else:  # Hotspot
                html += f"""
                            <li>El servidor crea su propia red WiFi</li>
                            <li>Conecta dispositivos directamente al hotspot</li>
                            <li>No requiere red WiFi externa</li>
                """
            
            html += """
                        </ul>
                    </div>
            """
        
        # Agregar sección de configuración avanzada
        html += f"""
                    <div class="qr-section">
                        <h3>⚙️ Configuración Avanzada</h3>
                        <p>Si necesitas configurar una red dedicada:</p>
                        <div class="instructions">
                            <h4>📋 Pasos para Red Local Dedicada:</h4>
                            <ol>
                                <li>Conecta un router dedicado al servidor</li>
                                <li>Configura el router con IP estática: 192.168.1.1</li>
                                <li>Conecta los dispositivos de asistencia al router</li>
                                <li>Accede usando la IP del servidor en la red local</li>
                            </ol>
                        </div>
                    </div>
                    
                    <div class="instructions">
                        <h4>💡 Recomendaciones para Empresas:</h4>
                        <ul>
                            <li><strong>Opción 1:</strong> Router dedicado (más estable)</li>
                            <li><strong>Opción 2:</strong> Hotspot del servidor (más simple)</li>
                            <li><strong>Opción 3:</strong> Cable Ethernet directo (más seguro)</li>
                            <li><strong>Opción 4:</strong> Router móvil 4G/5G (más flexible)</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

        @self.app.route('/network_info')
        def network_info_page():
            """Página con información de red y opciones de conexión"""
            return self.render_network_info()
