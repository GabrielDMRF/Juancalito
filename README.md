# Sistema de Gestión de Personal - V1.0

## 📋 Descripción

Sistema integral de gestión de personal desarrollado en Python que permite administrar empleados, contratos, inventarios y generar reportes de manera eficiente y automatizada.

## 🚀 Instalación Rápida

### Para Usuarios Finales:
1. **Descargue** todos los archivos del proyecto
2. **Navegue** a la carpeta `instalacion/`
3. **Ejecute** `INSTALAR_SISTEMA.bat` como administrador
4. **Siga** las instrucciones del instalador
5. **¡Listo!** El sistema estará disponible en su escritorio

### Para Desarrolladores:
```bash
# Clonar o descargar el proyecto
cd sistema_gestion_personal

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el sistema
python src/main.py
```

## 📁 Estructura del Proyecto

```
sistema_gestion_personal/
├── src/                    # Código fuente del sistema
│   ├── main.py            # Punto de entrada principal
│   ├── views/             # Interfaces de usuario
│   ├── models/            # Modelos de datos
│   ├── controllers/       # Lógica de negocio
│   ├── utils/             # Utilidades y helpers
│   └── alerts/            # Sistema de alertas
├── instalacion/           # Archivos de instalación
│   ├── installer.py       # Instalador automático
│   ├── INSTALAR_SISTEMA.bat # Ejecutable de instalación
│   ├── README_INSTALACION.md # Guía de instalación
│   ├── VERIFICACION_ENTREGA.md # Checklist de verificación
│   └── RESUMEN_EJECUTIVO.md # Resumen del proyecto
├── database/              # Bases de datos (se crean automáticamente)
├── logs/                  # Archivos de registro
├── reports/               # Reportes generados
├── empleados_data/        # Datos de empleados
├── templates_contratos/   # Plantillas de contratos
├── requirements.txt       # Dependencias de Python
└── README.md              # Este archivo
```

## 🎯 Funcionalidades Principales

### ✅ Gestión de Empleados
- Registro completo de información personal y laboral
- Búsqueda y filtros avanzados
- Edición y eliminación de registros
- Exportación a Excel con formato profesional

### ✅ Sistema de Contratos
- Generación automática de contratos laborales
- Plantillas personalizables en Word
- Gestión de fechas y renovaciones
- Exportación a múltiples formatos

### ✅ Inventarios Integrados
- **Químicos**: Control de productos químicos
- **Almacén**: Gestión de productos generales
- **Poscosecha**: Control de productos agrícolas
- Importación desde Excel con validación
- Alertas de stock automáticas

### ✅ Sistema de Alertas
- Monitoreo automático 24/7
- Alertas de stock bajo en tiempo real
- Notificaciones de productos por vencer
- Centro de alertas integrado

### ✅ Reportes y Exportación
- Reportes completos por módulo
- Exportación a Excel, CSV y PDF
- Estadísticas del sistema
- Backup automático de datos

## 🔧 Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11
- **Python**: Versión 3.8 o superior
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB)
- **Espacio en disco**: 500MB libres
- **Conexión a internet**: Para descargar dependencias

## 📦 Dependencias

El sistema utiliza las siguientes dependencias principales:
- `sqlalchemy==2.0.23` - ORM para base de datos
- `pillow==10.1.0` - Procesamiento de imágenes
- `python-docx==1.1.0` - Generación de documentos Word
- `reportlab==4.0.7` - Generación de PDFs
- `openpyxl==3.1.2` - Manejo de archivos Excel
- `tkcalendar==1.6.1` - Calendario para la interfaz
- `psutil==5.9.6` - Monitoreo del sistema

## 🚀 Uso del Sistema

### Ejecutar el Sistema
- **Desde escritorio**: Doble clic en "Sistema Gestion Personal.bat"
- **Manualmente**: `python src/main.py`

### Gestión de Empleados
1. Haga clic en "Nuevo Empleado"
2. Complete la información requerida
3. Guarde el empleado
4. Use "Editar Empleado" para modificaciones

### Generar Contratos
1. Seleccione un empleado
2. Haga clic en "Contratos"
3. Complete los datos del contrato
4. Genere y guarde el documento

### Gestionar Inventarios
1. Haga clic en "Inventarios"
2. Seleccione el tipo (Químicos/Almacén/Poscosecha)
3. Agregue productos o importe desde Excel
4. Monitoree stock y alertas

## 🔧 Configuración Avanzada

### Configuración de Base de Datos
- Las bases de datos se crean automáticamente en `database/`
- Backup automático configurado
- Optimización automática de consultas

### Configuración de Logs
- Ubicación: `logs/`
- Rotación automática de archivos
- Niveles de log configurables

### Personalización de Plantillas
- Ubicación: `templates_contratos/`
- Formato Word (.docx)
- Variables personalizables

## 🛠️ Solución de Problemas

### Error: "Python no se reconoce"
- Instale Python desde [python.org](https://python.org)
- Asegúrese de marcar "Add to PATH" durante la instalación

### Error: "Módulo no encontrado"
- Ejecute: `pip install -r requirements.txt`
- Verifique la conexión a internet

### Error: "Base de datos corrupta"
- Elimine archivos en `database/`
- Reinicie el sistema (se recrearán automáticamente)

### Error: "Permisos denegados"
- Ejecute como administrador
- Verifique permisos de escritura en la carpeta

## 📞 Soporte

### Archivos de Log
- Revise `logs/` para errores detallados
- Último log: `logs/system.log`

### Documentación Adicional
- `instalacion/README_INSTALACION.md` - Guía completa de instalación
- `instalacion/VERIFICACION_ENTREGA.md` - Checklist de verificación
- `instalacion/RESUMEN_EJECUTIVO.md` - Resumen ejecutivo del proyecto

## 📊 Métricas del Proyecto

- **Líneas de código**: ~15,000 líneas
- **Archivos Python**: 25+ archivos
- **Módulos principales**: 8 módulos
- **Bases de datos**: 4 bases de datos
- **Dependencias**: 8 paquetes externos

## 🔄 Actualizaciones

Para actualizar el sistema:
1. Descargue la nueva versión
2. Haga backup de `database/` y `empleados_data/`
3. Reemplace archivos del sistema
4. Ejecute el instalador nuevamente

## 📄 Licencia

Este software es de uso interno y confidencial.
Desarrollado para gestión empresarial.

## 🎉 Estado del Proyecto

**✅ COMPLETADO Y LISTO PARA ENTREGA**

- Todas las funcionalidades implementadas
- Sistema probado y funcionando correctamente
- Instalador automático configurado
- Documentación completa incluida
- Errores críticos corregidos

---

**¡Gracias por usar el Sistema de Gestión de Personal!**

**Versión**: 1.0  
**Fecha**: Diciembre 2024  
**Estado**: ✅ APROBADO PARA ENTREGA
