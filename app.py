from flask import Flask, render_template_string, request, jsonify, redirect
import sqlite3
import os
import hashlib
from datetime import datetime, date
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar la base de datos para Railway
DATABASE_PATH = '/tmp/asistencia_qr.db' if os.environ.get('RAILWAY_ENVIRONMENT') else 'database/asistencia_qr.db'

def init_database():
    """Inicializar la base de datos con la misma estructura que el servidor QR local"""
    try:
        # Crear directorio si no estamos en Railway
        if not os.environ.get('RAILWAY_ENVIRONMENT'):
            os.makedirs('database', exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Crear tabla empleados (misma estructura que el servidor QR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT UNIQUE NOT NULL,
                nombre_completo TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                fecha_ingreso DATE,
                area_trabajo TEXT,
                cargo TEXT,
                salario_base INTEGER,
                estado BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla asistencias (misma estructura que el servidor QR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                hora_entrada DATETIME,
                hora_salida DATETIME,
                tipo_registro TEXT DEFAULT 'entrada',
                token_qr TEXT,
                ip_registro TEXT,
                dispositivo TEXT,
                FOREIGN KEY (empleado_id) REFERENCES empleados (id)
            )
        ''')
        
        # Crear tabla tokens_qr (misma estructura que el servidor QR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens_qr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                fecha_generacion DATE NOT NULL,
                fecha_expiracion DATETIME NOT NULL,
                activo BOOLEAN DEFAULT 1,
                usado_por TEXT,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        return False

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=20.0)
        conn.row_factory = sqlite3.Row
        # Configurar para evitar bloqueos
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        raise

def verificar_token(token):
    """Verificar si el token es válido y no ha expirado"""
    try:
        # Para tokens con formato fecha_hash, verificar solo la fecha
        if token and '_' in token:
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
        
        # Si no es un token con formato fecha_hash, verificar en la base de datos
        conn = get_db_connection()
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
        logger.error(f"Error verificando token: {e}")
        return False

def generar_token_diario():
    """Generar token único para el día"""
    try:
        fecha_actual = date.today()
        token_base = f"{fecha_actual.isoformat()}_{hashlib.md5(str(fecha_actual).encode()).hexdigest()[:8]}"
        
        # Primero verificar que la base de datos esté inicializada
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tokens_qr'
        """)
        
        if not cursor.fetchone():
            # Si la tabla no existe, crearla
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens_qr (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE NOT NULL,
                    fecha_generacion DATE NOT NULL,
                    fecha_expiracion DATETIME NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    usado_por TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        
        # Buscar token existente para hoy
        cursor.execute("""
            SELECT token FROM tokens_qr 
            WHERE fecha_generacion = ? AND activo = 1
        """, (fecha_actual,))
        
        existing_token = cursor.fetchone()
        
        if existing_token:
            token = existing_token[0]
        else:
            token = token_base
            fecha_expiracion = datetime.combine(fecha_actual, datetime.max.time())
            
            cursor.execute("""
                INSERT INTO tokens_qr (token, fecha_generacion, fecha_expiracion, activo)
                VALUES (?, ?, ?, 1)
            """, (token, fecha_actual, fecha_expiracion))
            
            conn.commit()
        
        conn.close()
        return token
        
    except Exception as e:
        logger.error(f"Error generando token: {e}")
        # En caso de error, devolver un token básico
        fecha_actual = date.today()
        return f"{fecha_actual.isoformat()}_fallback"

@app.route('/')
def home():
    """Página principal - redirigir al formulario de asistencia"""
    try:
        token = generar_token_diario()
        if token:
            return redirect(f'/asistencia?token={token}')
        else:
            return "Error: No se pudo generar token", 500
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        return "Error interno del servidor", 500

@app.route('/asistencia')
def asistencia():
    """Página de registro de asistencia"""
    token = request.args.get('token')
    if not token:
        return "Token no válido", 400
    
    if not verificar_token(token):
        return "Token expirado o no válido", 400
    
    return render_formulario_asistencia(token)

@app.route('/registrar_asistencia', methods=['POST'])
def registrar_asistencia():
    """Procesar registro de asistencia"""
    try:
        token = request.form.get('token')
        documento = request.form.get('documento')
        nombre = request.form.get('nombre')
        tipo_registro = request.form.get('tipo_registro', 'entrada')
        
        if not all([token, documento, nombre]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        if not verificar_token(token):
            return jsonify({'error': 'Token expirado'}), 400
        
        resultado = procesar_asistencia(token, documento, nombre, request, tipo_registro)
        
        if resultado['success']:
            return render_exito(resultado['mensaje'], tipo_registro, token)
        else:
            return render_error(resultado['mensaje'])
            
    except Exception as e:
        logger.error(f"Error registrando asistencia: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def procesar_asistencia(token, documento, nombre, request, tipo_registro='entrada'):
    """Procesar el registro de asistencia"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar y crear tablas si no existen
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='empleados'
        """)
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empleados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula TEXT UNIQUE NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    fecha_ingreso DATE,
                    area_trabajo TEXT,
                    cargo TEXT,
                    salario_base INTEGER,
                    estado BOOLEAN DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='asistencias'
        """)
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS asistencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    empleado_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    hora_entrada DATETIME,
                    hora_salida DATETIME,
                    tipo_registro TEXT DEFAULT 'entrada',
                    token_qr TEXT,
                    ip_registro TEXT,
                    dispositivo TEXT,
                    FOREIGN KEY (empleado_id) REFERENCES empleados (id)
                )
            ''')
            conn.commit()
        
        # Buscar empleado por documento
        cursor.execute("""
            SELECT id, nombre_completo FROM empleados 
            WHERE cedula = ? AND estado = 1
        """, (documento,))
        
        empleado = cursor.fetchone()
        if not empleado:
            # Crear nuevo empleado si no existe
            cursor.execute("""
                INSERT INTO empleados (cedula, nombre_completo, estado, fecha_creacion)
                VALUES (?, ?, 1, ?)
            """, (documento, nombre, datetime.now()))
            empleado_id = cursor.lastrowid
        else:
            empleado_id = empleado[0]
        
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
                cursor.execute("""
                    UPDATE asistencias 
                    SET hora_entrada = ?, tipo_registro = 'entrada'
                    WHERE id = ?
                """, (ahora, registro_existente[0]))
            else:
                cursor.execute("""
                    INSERT INTO asistencias (empleado_id, fecha, hora_entrada, tipo_registro, token_qr, ip_registro, dispositivo)
                    VALUES (?, ?, ?, 'entrada', ?, ?, ?)
                """, (empleado_id, hoy, ahora, token, request.remote_addr, request.headers.get('User-Agent', '')))
            
            mensaje = f"Entrada registrada exitosamente a las {ahora.strftime('%H:%M:%S')}"
            
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
            
            mensaje = f"Salida registrada exitosamente a las {ahora.strftime('%H:%M:%S')}<br>Horas trabajadas: {horas:.2f} horas"
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'mensaje': mensaje}
        
    except Exception as e:
        logger.error(f"Error procesando asistencia: {e}")
        return {'success': False, 'mensaje': f'Error interno: {str(e)}'}

def render_formulario_asistencia(token):
    """Renderizar formulario de asistencia (exactamente igual al servidor QR local)"""
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
                font-size: 24px;
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
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
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
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
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
            .icon {{
                font-size: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 Registro de Asistencia</h1>
            
            <div class="info">
                <h2>📅 Informacion del Registro</h2>
                <p><strong>Fecha:</strong> <span id="fecha-actual">{date.today().strftime('%d/%m/%Y')}</span></p>
                <p><strong>Hora:</strong> <span id="hora-actual"></span></p>
                <p><strong>Token QR:</strong> <span style="font-family: monospace; font-size: 12px;">{token[:20]}...</span></p>
            </div>
            
            <form id="asistenciaForm">
                <input type="hidden" name="token" value="{token}">
                <input type="hidden" name="tipo_registro" id="tipo_registro" value="entrada">
                
                <div class="form-group">
                    <label for="documento">Numero de Documento:</label>
                    <input type="text" id="documento" name="documento" required 
                           placeholder="Ej: 12345678" maxlength="20">
                </div>
                
                <div class="form-group">
                    <label for="nombre">Nombre Completo:</label>
                    <input type="text" id="nombre" name="nombre" required 
                           placeholder="Ej: Juan Perez Gonzalez" maxlength="100">
                </div>
                
                <div class="btn-container">
                    <button type="button" class="btn-entrada" onclick="registrarAsistencia('entrada')">
                        <span class="icon">✓</span> Marcar Entrada
                    </button>
                    <button type="button" class="btn-salida" onclick="registrarAsistencia('salida')">
                        <span class="icon">🚪</span> Marcar Salida
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
                    mostrarError('Error de conexion. Intente nuevamente.');
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

def render_exito(mensaje, tipo_registro='entrada', token=None):
    """Renderizar página de éxito"""
    icono = "Entrada" if tipo_registro == 'entrada' else "Salida"
    color = "#27ae60" if tipo_registro == 'entrada' else "#e74c3c"
    titulo = "Entrada Registrada!" if tipo_registro == 'entrada' else "Salida Registrada!"
    
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
                <strong>Fecha:</strong> {date.today().strftime('%d/%m/%Y')}<br>
                <strong>Hora:</strong> <span id="hora-actual"></span><br>
                <strong>Dispositivo:</strong> {request.headers.get('User-Agent', 'No disponible')[:50]}...
            </div>
            <div class="btn-container">
                <a href="/asistencia?token={token}" class="btn">Nuevo Registro</a>
                <a href="/" class="btn btn-secundario">Volver al Inicio</a>
                <a href="javascript:window.close()" class="btn btn-secundario">Cerrar</a>
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
        </script>
    </body>
    </html>
    """
    return html

def render_error(mensaje):
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
            <div class="error-icon">Error</div>
            <h1>Error en el Registro</h1>
            <div class="mensaje">
                {mensaje}
            </div>
            <div class="btn-container">
                <a href="/" class="volver">Volver al Inicio</a>
                <a href="javascript:window.close()" class="volver" style="margin-left: 10px;">Cerrar</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health_check():
    """Endpoint para verificar el estado del servidor"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM empleados')
        empleados_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'empleados_count': empleados_count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/sync_data')
def sync_data():
    """Endpoint para obtener todos los datos para sincronización"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener empleados
        cursor.execute("""
            SELECT cedula, nombre_completo, telefono, email, direccion, 
                   fecha_ingreso, area_trabajo, cargo, salario_base, estado
            FROM empleados
        """)
        empleados = []
        for row in cursor.fetchall():
            empleados.append({
                'cedula': row[0],
                'nombre_completo': row[1],
                'telefono': row[2],
                'email': row[3],
                'direccion': row[4],
                'fecha_ingreso': row[5],
                'area_trabajo': row[6],
                'cargo': row[7],
                'salario_base': row[8],
                'estado': row[9]
            })
        
        # Obtener asistencias
        cursor.execute("""
            SELECT a.fecha, a.hora_entrada, a.hora_salida, a.tipo_registro,
                   a.token_qr, a.ip_registro, a.dispositivo,
                   e.cedula, e.nombre_completo
            FROM asistencias a
            JOIN empleados e ON a.empleado_id = e.id
        """)
        asistencias = []
        for row in cursor.fetchall():
            asistencias.append({
                'fecha': row[0],
                'hora_entrada': row[1],
                'hora_salida': row[2],
                'tipo_registro': row[3],
                'token_qr': row[4],
                'ip_registro': row[5],
                'dispositivo': row[6],
                'cedula_empleado': row[7],
                'nombre_empleado': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'empleados': empleados,
            'asistencias': asistencias,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en sync_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sync_recent_asistencias')
def sync_recent_asistencias():
    """Endpoint para sincronizar solo asistencias recientes (más eficiente)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener solo asistencias de los últimos 7 días
        cursor.execute("""
            SELECT a.fecha, a.hora_entrada, a.hora_salida, a.tipo_registro,
                   a.token_qr, a.ip_registro, a.dispositivo,
                   e.cedula, e.nombre_completo
            FROM asistencias a
            JOIN empleados e ON a.empleado_id = e.id
            WHERE a.fecha >= date('now', '-7 days')
            ORDER BY a.fecha DESC, a.hora_entrada DESC
        """)
        asistencias = []
        for row in cursor.fetchall():
            asistencias.append({
                'fecha': row[0],
                'hora_entrada': row[1],
                'hora_salida': row[2],
                'tipo_registro': row[3],
                'token_qr': row[4],
                'ip_registro': row[5],
                'dispositivo': row[6],
                'cedula_empleado': row[7],
                'nombre_empleado': row[8]
            })
        
        conn.close()
        
        return jsonify({
            'asistencias': asistencias,
            'count': len(asistencias),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error en sync_recent_asistencias: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sync_empleado', methods=['POST'])
def sync_empleado():
    """Endpoint para sincronizar un empleado desde la app local"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO empleados 
            (cedula, nombre_completo, telefono, email, direccion, 
             fecha_ingreso, area_trabajo, cargo, salario_base, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['cedula'], data['nombre_completo'],
            data.get('telefono'), data.get('email'),
            data.get('direccion'), data.get('fecha_ingreso'),
            data.get('area_trabajo'), data.get('cargo'),
            data.get('salario_base'), data.get('estado', 1)
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Empleado sincronizado'})
        
    except Exception as e:
        logger.error(f"Error sincronizando empleado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sync_asistencia', methods=['POST'])
def sync_asistencia():
    """Endpoint para sincronizar una asistencia desde la app local"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener o crear empleado
        cursor.execute("SELECT id FROM empleados WHERE cedula = ?", (data['cedula_empleado'],))
        empleado_result = cursor.fetchone()
        
        if empleado_result:
            empleado_id = empleado_result[0]
        else:
            # Crear empleado si no existe
            cursor.execute("""
                INSERT INTO empleados (cedula, nombre_completo, estado)
                VALUES (?, ?, 1)
            """, (data['cedula_empleado'], data['nombre_empleado']))
            empleado_id = cursor.lastrowid
        
        # Insertar asistencia
        cursor.execute("""
            INSERT OR REPLACE INTO asistencias 
            (empleado_id, fecha, hora_entrada, hora_salida, 
             tipo_registro, token_qr, ip_registro, dispositivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            empleado_id, data['fecha'], data.get('hora_entrada'),
            data.get('hora_salida'), data.get('tipo_registro'),
            data.get('token_qr'), data.get('ip_registro'),
            data.get('dispositivo')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Asistencia sincronizada'})
        
    except Exception as e:
        logger.error(f"Error sincronizando asistencia: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Inicializar base de datos al arrancar
    if init_database():
        logger.info("Aplicacion iniciada correctamente")
    else:
        logger.error("Error al inicializar la aplicacion")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
