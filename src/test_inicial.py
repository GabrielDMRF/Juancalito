import tkinter as tk
from tkinter import ttk, messagebox

def test_sistema():
    root = tk.Tk()
    root.title("Sistema de Gestión - Prueba")
    root.geometry("400x200")
    
    label = ttk.Label(root, text="¡Sistema funcionando!", font=('Arial', 14))
    label.pack(pady=50)
    
    def mostrar_mensaje():
        messagebox.showinfo("Éxito", "¡Todo configurado correctamente!")
    
    boton = ttk.Button(root, text="Probar", command=mostrar_mensaje)
    boton.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_sistema()