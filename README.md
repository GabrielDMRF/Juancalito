# 🏢 Sistema de Gestión Personal

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![SQLite](https://img.shields.io/badge/SQLite-Database-orange.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Sistema completo de gestión empresarial desarrollado en Python con interfaz gráfica Tkinter. Permite la administración integral de empleados, contratos, inventarios y alertas del sistema.

## ✨ Características Principales

### 👥 Gestión de Empleados
- ✅ Registro y edición de empleados
- ✅ Validación de datos automática
- ✅ Generación de contratos en Excel
- ✅ Búsqueda y filtros avanzados
- ✅ Exportación de datos

### 📄 Gestión de Contratos
- ✅ Creación de contratos laborales
- ✅ Seguimiento de fechas de vencimiento
- ✅ Generación automática de documentos
- ✅ Alertas de contratos próximos a vencer

### 📦 Gestión de Inventarios
- ✅ **Productos Químicos Agrícolas**
- ✅ **Inventario de Almacén General**
- ✅ **Productos de Poscosecha**
- ✅ Importación desde Excel
- ✅ Control de stock y movimientos
- ✅ Alertas de stock mínimo

### 🔔 Sistema de Alertas
- ✅ Monitoreo automático del sistema
- ✅ Alertas de contratos vencidos
- ✅ Alertas de stock bajo
- ✅ Centro de alertas integrado
- ✅ Historial de alertas

### ⚙️ Configuración y Seguridad
- ✅ Configuraciones del sistema
- ✅ Sistema de respaldos automáticos
- ✅ Optimización de base de datos
- ✅ Validación de datos
- ✅ Logs del sistema

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/sistema-gestion-personal.git
   cd sistema-gestion-personal
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar la aplicación**
   ```bash
   python src/main.py
   ```

## 📦 Dependencias

```
pandas>=1.5.0
openpyxl>=3.0.0
tkcalendar>=1.6.0
```

## 🖥️ Uso

### Inicio Rápido
1. Ejecuta `python src/main.py`
2. La aplicación se abrirá con la interfaz principal
3. Navega por las diferentes secciones usando los botones

### Funcionalidades Principales

#### Gestión de Empleados
- **Nuevo Empleado**: Registra un nuevo empleado con validación automática
- **Editar Empleado**: Modifica información de empleados existentes
- **Buscar**: Filtra empleados por diferentes criterios
- **Exportar**: Genera reportes en Excel

#### Inventarios
- **Importar Excel**: Carga productos desde archivos Excel
- **Nuevo Producto**: Agrega productos manualmente
- **Movimientos**: Registra entradas y salidas de stock
- **Alertas**: Monitorea stock mínimo automáticamente

#### Contratos
- **Nuevo Contrato**: Crea contratos laborales
- **Seguimiento**: Monitorea fechas de vencimiento
- **Generar Excel**: Exporta contratos a Excel

## 📁 Estructura del Proyecto

```
sistema-gestion-personal/
├── src/                    # Código fuente principal
│   ├── main.py            # Punto de entrada
│   ├── views/             # Interfaces gráficas
│   ├── models/            # Modelos de datos
│   ├── utils/             # Utilidades y helpers
│   └── alerts/            # Sistema de alertas
├── database/              # Bases de datos (generadas automáticamente)
├── config/                # Configuraciones (generadas automáticamente)
├── logs/                  # Logs del sistema (generados automáticamente)
├── reports/               # Reportes generados
├── requirements.txt       # Dependencias del proyecto
├── .gitignore            # Archivos ignorados por Git
└── README.md             # Este archivo
```

## 🔧 Configuración

### Variables de Entorno
El sistema crea automáticamente los directorios necesarios:
- `database/`: Bases de datos SQLite
- `config/`: Archivos de configuración
- `logs/`: Archivos de registro
- `reports/`: Reportes generados
- `temp/`: Archivos temporales

### Personalización
- Modifica `src/utils/settings_manager.py` para cambiar configuraciones
- Ajusta `src/utils/validators.py` para validaciones personalizadas
- Configura alertas en `src/alerts/notification_system.py`

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Error de importación de módulos**
   ```bash
   pip install -r requirements.txt
   ```

2. **Error de permisos en Windows**
   - Ejecutar como administrador
   - Verificar permisos de escritura en el directorio

3. **Base de datos no encontrada**
   - El sistema crea automáticamente las bases de datos
   - Verificar permisos de escritura

4. **Error de Tkinter**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # CentOS/RHEL
   sudo yum install tkinter
   ```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@ejemplo.com

## 🙏 Agradecimientos

- Python Software Foundation
- Tkinter Community
- SQLite Development Team
- Pandas Development Team

## 📊 Estado del Proyecto

- ✅ **Completado**: Gestión de empleados
- ✅ **Completado**: Sistema de inventarios
- ✅ **Completado**: Gestión de contratos
- ✅ **Completado**: Sistema de alertas
- ✅ **Completado**: Interfaz responsive
- 🔄 **En desarrollo**: Mejoras de rendimiento
- 📋 **Planificado**: Reportes avanzados

---

⭐ **Si este proyecto te es útil, ¡dale una estrella en GitHub!**
