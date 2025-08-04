#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear instalador del Sistema de Gestión Personal
Usar: python build_installer.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando PyInstaller: {e}")
            return False

def create_spec_file():
    """Crear archivo .spec personalizado para PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database', 'database'),
        ('templates', 'templates'),
        ('templates_contratos', 'templates_contratos'),
        ('empleados_data', 'empleados_data'),
        ('reports', 'reports'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'sqlite3',
        'datetime',
        'openpyxl',
        'pathlib',
        'subprocess',
        'threading',
        'csv',
        'json',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SistemaGestionPersonal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola (aplicación de ventana)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('SistemaGestionPersonal.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ Archivo .spec creado")

def build_executable():
    """Construir el ejecutable"""
    print("🔨 Construyendo ejecutable...")
    try:
        # Usar el archivo .spec
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "SistemaGestionPersonal.spec"
        ])
        print("✅ Ejecutable creado exitosamente en 'dist/' folder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo ejecutable: {e}")
        return False

def create_installer_nsis():
    """Crear script NSIS para instalador de Windows"""
    nsis_script = '''
; Script de instalador NSIS para Sistema de Gestión Personal
!define APPNAME "Sistema de Gestión Personal"
!define COMPANYNAME "Tu Empresa"
!define DESCRIPTION "Sistema completo de gestión de personal e inventarios"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "http://..." ; "Support Information" link
!define UPDATEURL "http://..." ; "Product Updates" link
!define ABOUTURL "http://..." ; "Publisher" link

!define INSTALLSIZE 150000 ; Estimado en KB

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"

Name "${APPNAME}"
Icon "icon.ico"
outFile "SistemaGestionPersonal_Installer.exe"

!include LogicLib.nsh

page directory
page instfiles

section "install"
    setOutPath $INSTDIR
    
    ; Archivos principales
    file "dist\\SistemaGestionPersonal.exe"
    
    ; Crear acceso directo en escritorio
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\SistemaGestionPersonal.exe"
    
    ; Crear acceso directo en menú inicio
    createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\SistemaGestionPersonal.exe"
    
    ; Información del registro
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; Crear desinstalador
    writeUninstaller "$INSTDIR\\uninstall.exe"
sectionEnd

section "uninstall"
    delete "$INSTDIR\\SistemaGestionPersonal.exe"
    delete "$INSTDIR\\uninstall.exe"
    
    ; Eliminar accesos directos
    delete "$DESKTOP\\${APPNAME}.lnk"
    delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${COMPANYNAME}"
    
    ; Eliminar directorio de instalación
    rmDir $INSTDIR
    
    ; Eliminar información del registro
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd
'''
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    print("✅ Script NSIS creado (installer.nsi)")
    print("💡 Para crear el instalador, necesitas NSIS: https://nsis.sourceforge.io/")

def main():
    """Función principal"""
    print("🚀 CONSTRUCTOR DE INSTALADOR - Sistema de Gestión Personal")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('src/main.py'):
        print("❌ Error: No se encuentra src/main.py")
        print("   Ejecuta este script desde la carpeta raíz del proyecto")
        return False
    
    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Paso 2: Crear archivo .spec
    create_spec_file()
    
    # Paso 3: Construir ejecutable
    if not build_executable():
        return False
    
    # Paso 4: Crear script para instalador
    create_installer_nsis()
    
    print("\n🎉 ¡PROCESO COMPLETADO!")
    print("=" * 60)
    print(f"📁 Ejecutable creado en: {os.path.abspath('dist')}")
    print("📝 Para crear instalador completo:")
    print("   1. Descarga NSIS: https://nsis.sourceforge.io/")
    print("   2. Ejecuta: makensis installer.nsi")
    print("\n🚀 ¡Tu aplicación está lista para distribuir!")
    
    return True

if __name__ == "__main__":
    main()