# 🚀 Guía para Crear Instalador - Sistema de Gestión Personal

## 📋 Pasos Rápidos

### 1. Preparar Entorno
```bash
# Instalar dependencias de construcción
pip install -r requirements_build.txt
```

### 2. Crear Ejecutable Automáticamente
```bash
python build_installer.py
```

### 3. Crear Instalador de Windows (Opcional)
1. Descarga **NSIS**: https://nsis.sourceforge.io/
2. Ejecuta: `makensis installer.nsi`

---

## 🛠️ Opciones Manuales

### PyInstaller (Línea de Comandos)
```bash
# Ejecutable básico
pyinstaller --onefile src/main.py

# Ejecutable completo con recursos
pyinstaller --onefile --windowed --name "SistemaGestionPersonal" --add-data "database;database" --add-data "templates;templates" src/main.py

# Con icono personalizado
pyinstaller --onefile --windowed --icon=icon.ico src/main.py
```

### Auto-py-to-exe (Interfaz Gráfica)
```bash
# Instalar
pip install auto-py-to-exe

# Ejecutar interfaz
auto-py-to-exe
```

**En la interfaz:**
- Script Location: `src/main.py`
- Onefile: ✅ One File
- Console Window: ❌ Window Based (hide the console)
- Icon: Seleccionar `icon.ico` si existe
- Additional Files: Agregar carpetas `database`, `templates`, etc.

---

## 📁 Estructura Final

```
dist/
├── SistemaGestionPersonal.exe    # Tu aplicación ejecutable
└── ...

build/                            # Archivos temporales (se pueden eliminar)

SistemaGestionPersonal_Installer.exe  # Instalador completo (si usas NSIS)
```

---

## 🎯 Distribución

### Para Usuarios Finales:
1. **Ejecutable Simple**: Comparte solo `SistemaGestionPersonal.exe`
2. **Instalador Completo**: Comparte `SistemaGestionPersonal_Installer.exe`

### Ventajas del Instalador:
- ✅ Accesos directos automáticos
- ✅ Registro en Windows
- ✅ Desinstalador incluido
- ✅ Aspecto más profesional

---

## 🔧 Solución de Problemas

### Error: "Failed to execute script"
- Verifica que todas las dependencias estén en `requirements.txt`
- Usa `--hidden-import` para módulos no detectados

### Ejecutable muy grande
- Usa `--exclude-module` para módulos no necesarios
- Considera usar `--upx` para comprimir

### No encuentra archivos
- Verifica las rutas en `--add-data`
- Usa rutas relativas desde el directorio raíz

---

## 💡 Consejos

1. **Prueba siempre** el ejecutable en una máquina limpia
2. **Incluye un archivo README** para usuarios finales
3. **Considera firmar digitalmente** para mayor confianza
4. **Versiona tus releases** para control de actualizaciones

---

## 🎉 ¡Listo!

Tu Sistema de Gestión Personal ahora puede distribuirse como una aplicación profesional de Windows.