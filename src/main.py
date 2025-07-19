import tkinter as tk
import sys
import os

# Agregar directorios al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow
from models.database import create_tables

def main():
    try:
        # Crear tablas si no existen
        print("Inicializando sistema...")
        create_tables()
        
        # Crear ventana principal
        root = tk.Tk()
        app = MainWindow(root)
        
        print("[OK] Sistema iniciado correctamente")
        root.mainloop()
        
    except Exception as e:
        print(f"[ERROR] Error al iniciar el sistema: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()