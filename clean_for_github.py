#!/usr/bin/env python3
"""
Script para limpiar archivos innecesarios antes de subir a GitHub
Ejecutar: python clean_for_github.py
"""

import os
import shutil
import glob
from pathlib import Path

def clean_project():
    """Limpiar archivos y directorios innecesarios para GitHub"""
    
    print("🧹 Limpiando proyecto para GitHub...")
    
    # Directorios a eliminar
    dirs_to_remove = [
        'database',
        'config', 
        'logs',
        'temp',
        'reports',
        'empleados_data',
        'venv',
        '__pycache__',
        '.pytest_cache',
        'dist',
        'build',
        '*.egg-info'
    ]
    
    # Archivos a eliminar
    files_to_remove = [
        '*.log',
        '*.sqlite3',
        '*.db',
        '*.pyc',
        '*.pyo',
        '*.tmp',
        '*.temp',
        '*.bak',
        '*.backup',
        '*.old',
        'Thumbs.db',
        '.DS_Store',
        'desktop.ini'
    ]
    
    # Eliminar directorios
    for dir_pattern in dirs_to_remove:
        if '*' in dir_pattern:
            # Patrón con wildcard
            for dir_path in glob.glob(dir_pattern):
                if os.path.isdir(dir_path):
                    print(f"🗑️  Eliminando directorio: {dir_path}")
                    shutil.rmtree(dir_path, ignore_errors=True)
        else:
            # Directorio específico
            if os.path.exists(dir_pattern):
                print(f"🗑️  Eliminando directorio: {dir_pattern}")
                shutil.rmtree(dir_pattern, ignore_errors=True)
    
    # Eliminar archivos
    for file_pattern in files_to_remove:
        for file_path in glob.glob(file_pattern, recursive=True):
            if os.path.isfile(file_path):
                print(f"🗑️  Eliminando archivo: {file_path}")
                os.remove(file_path)
    
    # Eliminar archivos __pycache__ recursivamente
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_dir = os.path.join(root, dir_name)
                print(f"🗑️  Eliminando cache: {cache_dir}")
                shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Eliminar archivos .pyc recursivamente
    for pyc_file in glob.glob('**/*.pyc', recursive=True):
        print(f"🗑️  Eliminando archivo compilado: {pyc_file}")
        os.remove(pyc_file)
    
    print("✅ Limpieza completada!")
    print("\n📋 Archivos y directorios eliminados:")
    print("   - Bases de datos (*.sqlite3, *.db)")
    print("   - Logs (*.log)")
    print("   - Archivos temporales (*.tmp, *.temp)")
    print("   - Archivos de caché (__pycache__)")
    print("   - Archivos compilados (*.pyc)")
    print("   - Entorno virtual (venv/)")
    print("   - Directorios de configuración")
    print("   - Archivos de sistema (.DS_Store, Thumbs.db)")
    
    print("\n🚀 Tu proyecto está listo para subir a GitHub!")
    print("💡 Recuerda ejecutar estos comandos:")
    print("   git add .")
    print("   git commit -m 'Initial commit'")
    print("   git push origin main")

if __name__ == "__main__":
    try:
        clean_project()
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        print("💡 Asegúrate de tener permisos de escritura en el directorio")
