#VISOR DE IMAGENES - VALENTINA MURILLO MUÑOZ
import tkinter as tk
from procesador import ProcesadorImagenes
from interfaz import InterfazVisor


def main():
    
    # Crear ventana principal
    root = tk.Tk()
    
    # Crear instancia del procesador de imágenes
    procesador = ProcesadorImagenes()
    
    # Crear interfaz gráfica pasando el procesador
    app = InterfazVisor(root, procesador)
    
    # Iniciar aplicación
    app.ejecutar()


if __name__ == "__main__":
    main()