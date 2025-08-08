# 🔒 Sistema de Validación y Backup - Documentación

## 📋 Resumen

Se han implementado mejoras significativas en el **Sistema de Gestión de Personal** para garantizar la **integridad de datos** y **seguridad de la información**:

### ✨ Nuevas Funcionalidades

1. **🔍 Validación Estricta de Datos**
   - Validación de cédula colombiana con algoritmo oficial
   - Validación de formato de email
   - Validación de teléfonos colombianos
   - Prevención de empleados duplicados
   - Validación de archivos subidos

2. **💾 Sistema de Backup Automático**
   - Backup diario automático de la base de datos
   - Backup manual con interfaz gráfica
   - Restauración de backups con confirmación
   - Gestión de versiones de backup
   - Backup comprimido completo del sistema

3. **🔧 Panel de Configuración de Seguridad**
   - Interfaz gráfica para gestionar validaciones
   - Configuración de backup automático
   - Pruebas de validación en tiempo real
   - Estado del sistema de seguridad

---

## 🚀 Instalación y Configuración

### Requisitos Previos
```bash
# Instalar dependencias adicionales (si no están en requirements.txt)
pip install mimetypes
```

### Archivos Nuevos
```
src/utils/validators.py           # Sistema de validación
src/utils/backup_manager.py       # Sistema de backup
src/views/backup_config_view.py   # Interfaz de configuración
test_validacion_backup.py         # Script de pruebas
```

### Configuración Inicial
1. Ejecutar el script de pruebas para verificar la instalación:
   ```bash
   python test_validacion_backup.py
   ```

2. Acceder a la configuración desde el menú principal:
   - Botón **"🔧 Seguridad"** en la ventana principal

---

## 🔍 Sistema de Validación

### Validación de Cédula Colombiana
```python
from utils.validators import DataValidator

# Validar cédula
es_valida, mensaje = DataValidator.validar_cedula_colombiana("1234567890")
```

**Características:**
- ✅ Algoritmo oficial de la DIAN
- ✅ Soporte para cédulas de 8-12 dígitos
- ✅ Validación de dígito verificador
- ✅ Limpieza automática de caracteres especiales

### Validación de Email
```python
es_valido, mensaje = DataValidator.validar_email("usuario@dominio.com")
```

**Características:**
- ✅ Formato RFC 5322
- ✅ Validación de dominio
- ✅ Límite de 50 caracteres
- ✅ Campo opcional

### Validación de Teléfono
```python
es_valido, mensaje = DataValidator.validar_telefono("3001234567")
```

**Características:**
- ✅ Códigos de área colombianos
- ✅ 7-10 dígitos
- ✅ Solo números
- ✅ Campo opcional

### Validación Completa de Empleado
```python
datos_empleado = {
    'nombre_completo': 'Juan Pérez',
    'cedula': '1234567890',
    'telefono': '3001234567',
    'email': 'juan@test.com',
    # ... otros campos
}

es_valido, errores = DataValidator.validar_empleado_completo(db, datos_empleado)
```

---

## 💾 Sistema de Backup

### Backup Automático
```python
from utils.backup_manager import BackupManager

# Crear instancia
backup_manager = BackupManager(db_path)

# Iniciar backup automático
backup_manager.start_auto_backup()
```

**Características:**
- 🔄 Backup diario automático
- 📁 Gestión de directorios de backup
- 🗂️ Metadatos de cada backup
- 🧹 Limpieza automática de backups antiguos
- ⚙️ Configuración personalizable

### Backup Manual
```python
# Crear backup inmediato
success, message = backup_manager.create_backup()

# Crear backup con nombre personalizado
success, message = backup_manager.create_backup("backup_especial.db")

# Crear backup comprimido completo
success, message = backup_manager.create_compressed_backup()
```

### Restauración
```python
# Restaurar backup específico
success, message = backup_manager.restore_backup("backup_20241201_143022.db")
```

**Características de Restauración:**
- 🔒 Backup de seguridad antes de restaurar
- ✅ Verificación de integridad
- 📋 Lista de backups disponibles
- ⚠️ Confirmación antes de restaurar

---

## 🔧 Panel de Configuración

### Acceso
- Botón **"🔧 Seguridad"** en la ventana principal
- Interfaz con pestañas organizadas

### Pestañas Disponibles

#### 1. 💾 Backup Automático
- **Configuración:**
  - Habilitar/deshabilitar backup automático
  - Intervalo de backup (1-168 horas)
  - Máximo número de backups (5-100)
  - Directorio de backup personalizable

- **Acciones:**
  - Crear backup manual
  - Crear backup comprimido
  - Restaurar backup seleccionado
  - Lista de backups disponibles

#### 2. ✅ Validación de Datos
- **Configuración:**
  - Habilitar validación estricta
  - Validar algoritmo de cédula
  - Validar formato de email
  - Validar teléfono colombiano
  - Prevenir duplicados
  - Validar archivos

- **Pruebas:**
  - Validar cédula de prueba
  - Validar email de prueba
  - Validar teléfono de prueba
  - Resultados en tiempo real

#### 3. 📊 Estado del Sistema
- **Información:**
  - Último backup realizado
  - Total de backups
  - Estado del backup automático
  - Contador de backups
  - Ruta de base de datos
  - Tamaño de base de datos
  - Directorio de backup

---

## 🧪 Pruebas y Verificación

### Script de Pruebas
```bash
# Ejecutar todas las pruebas
python test_validacion_backup.py
```

### Pruebas Incluidas
1. **Validadores:**
   - Cédula colombiana
   - Formato de email
   - Teléfonos colombianos
   - Nombres completos

2. **Backup Manager:**
   - Creación de backup
   - Listado de backups
   - Estado del sistema

3. **Integración:**
   - Validación completa de empleado
   - Verificación de duplicados
   - Conexión con base de datos

---

## 📁 Estructura de Archivos

### Directorios de Backup
```
database/
├── gestion_personal.db          # Base de datos principal
└── backups/                     # Directorio de backups
    ├── backup_config.json       # Configuración de backup
    ├── backup_20241201_143022.db
    ├── backup_20241201_143022_metadata.json
    ├── backup_completo_20241201_143022.zip
    └── ...
```

### Metadatos de Backup
```json
{
  "fecha_creacion": "2024-12-01T14:30:22",
  "tamaño_original": 1024000,
  "tamaño_backup": 1024000,
  "version_sistema": "1.2",
  "descripcion": "backup_20241201_143022.db"
}
```

---

## ⚠️ Consideraciones de Seguridad

### Para Uso Individual de RRHH
- ✅ **Validación estricta** previene errores de entrada
- ✅ **Backup automático** protege contra pérdida de datos
- ✅ **Prevención de duplicados** mantiene integridad
- ✅ **Validación de archivos** previene malware
- ✅ **Restauración segura** con backup de seguridad

### Recomendaciones
1. **Configurar backup automático** al menos diario
2. **Mantener máximo 30 backups** para optimizar espacio
3. **Probar validaciones** antes de usar en producción
4. **Revisar estado del sistema** regularmente
5. **Crear backup manual** antes de cambios importantes

---

## 🔄 Migración desde Versión Anterior

### Cambios Automáticos
- ✅ Las validaciones se aplican automáticamente
- ✅ El sistema de backup se inicializa automáticamente
- ✅ No se requieren cambios en datos existentes

### Verificación Post-Migración
1. Ejecutar script de pruebas
2. Verificar configuración de seguridad
3. Crear primer backup manual
4. Probar validaciones con datos existentes

---

## 🆘 Solución de Problemas

### Error: "Módulo no encontrado"
```bash
# Verificar que los archivos estén en la ubicación correcta
ls src/utils/validators.py
ls src/utils/backup_manager.py
ls src/views/backup_config_view.py
```

### Error: "Base de datos no existe"
```bash
# Crear tablas si no existen
python -c "from models.database import create_tables; create_tables()"
```

### Error: "Permisos de escritura"
```bash
# Verificar permisos del directorio de backup
chmod 755 database/backups/
```

### Backup no se crea automáticamente
1. Verificar configuración en panel de seguridad
2. Revisar logs del sistema
3. Verificar espacio en disco
4. Comprobar permisos de escritura

---

## 📞 Soporte

### Logs del Sistema
- Los errores se registran en la consola
- Mensajes informativos para operaciones exitosas
- Detalles de errores para diagnóstico

### Información de Debug
```python
# Obtener estado detallado del sistema
status = backup_manager.get_backup_status()
print(status)

# Listar todos los backups
backups = backup_manager.list_backups()
for backup in backups:
    print(f"Backup: {backup['nombre']}, Tamaño: {backup['tamaño']}")
```

---

## 🎯 Próximas Mejoras

### Funcionalidades Planificadas
- 🔐 Encriptación de backups
- 📧 Notificaciones por email
- 🔄 Sincronización en la nube
- 📊 Reportes de auditoría
- 🎨 Temas visuales personalizables

### Contribuciones
Para reportar bugs o sugerir mejoras:
1. Ejecutar script de pruebas
2. Documentar el problema
3. Incluir logs de error
4. Proponer solución

---

## 📄 Licencia

Este sistema de validación y backup es parte del **Sistema de Gestión de Personal** y mantiene la misma licencia del proyecto principal.

---

*Documentación actualizada: Diciembre 2024*
*Versión del sistema: 1.2* 