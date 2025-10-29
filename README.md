# Visor de Imágenes Interactivo
**Autora:** *Valentina Murillo Muñoz*  
**Proyecto:** Computación Gráfica – Visor de Imágenes - Octubre 2025
**Lenguaje:** Python


##  Descripción del Proyecto

Este proyecto implementa un **visor de imágenes interactivo** en Python usando Tkinter, PIL, Numpy y Matplotlib, que permite:
-  Cargar imágenes desde el sistema de archivos.  
-  Aplicar filtros de color y transformaciones (brillo, contraste, rotación, negativo, binarización, zonas claras, zonas oscuras y fusion de dos imagenes.).  
-  Hacer **zoom dinámico** en cualquier punto de la imagen con una seleccion del ratón.  
-  Activar y desactivar canales RGB o CMY.  
-  Mostrar el histograma de la imagen con la distribución de cada canal RGB.
-  Deshacer cambios y guardar imagen.
-  Navegar fácilmente por los controles con **scrollbar fluida**.  

La aplicación está compuesta por módulos que separan la lógica, la interfaz y el procesamiento de imágenes. (Compilar el main).

---

##  Requisitos

- Python **3.9 o superior**  
- Tkinter *(incluido por defecto con Python)*  

###  Dependencias externas

Instálalas con:
```bash
pip install pillow numpy matplotlib


