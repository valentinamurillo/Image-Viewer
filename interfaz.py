# interfaz grafica

import tkinter as tk
import numpy as np
from tkinter import Toplevel, filedialog, messagebox
import tkinter.simpledialog as sd
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class InterfazVisor:
    
    def __init__(self, root, procesador):

        self.root = root 
        self.procesador = procesador
        
        # Configurar ventana
        self.root.state("zoomed")
        self.root.configure(bg="black")
        self.root.title("Visor de Imágenes")
        
        # Variables de control
        self.ruta_imagen = tk.StringVar()
        self.rotacion_var = tk.DoubleVar(value=0)
        self.brillo_var = tk.DoubleVar(value=1.0)
        self.contraste_var = tk.DoubleVar(value=1.0)
        self.alpha_var = tk.DoubleVar(value=0.5)

        # Variables para filtros
        self.filtro_activo = tk.StringVar(value="ninguno")
        
        # Variables RGB
        self.rgb_rojo = tk.BooleanVar(value=True)
        self.rgb_verde = tk.BooleanVar(value=True)
        self.rgb_azul = tk.BooleanVar(value=True)
        
        # Variables CMY
        self.cmy_cian = tk.BooleanVar(value=True)
        self.cmy_magenta = tk.BooleanVar(value=True)
        self.cmy_amarillo = tk.BooleanVar(value=True)
        
        # Variables zonas claras/oscuras
        self.umbral_zonas = tk.DoubleVar(value=0.5)
        self.intensidad_zonas = tk.DoubleVar(value=1.5)

        # Efectos adicionales
        self.binarizar_activo = tk.BooleanVar(value=False)
        self.negativo_activo = tk.BooleanVar(value=False)

        # Variable para binarización
        self.umbral_binarizacion = tk.IntVar(value=128)
        
        # Estado de la imagen
        self.imagen_mostrada = None
        self.imagen_tk = None
        self.fusion_activa = False

        # Variables para zoom por selección
        self.zoom_inicio_x = None
        self.zoom_inicio_y = None
        self.zoom_rect = None
        self.imagen_original_vista = None 
        self.zoom_activo = False

        # Crear interfaz
        self.crear_frames()
        self.label_imagen()
        self.crear_controles()

        self.root.update_idletasks()
        self.actualizar_scroll_region()
        
    
    def crear_frames(self):

        self.frame_principal = tk.Frame(self.root, bg="black")
        self.frame_principal.pack(fill="both", expand=True)

        # Frame para mostrar imagen
        self.frame_imagen = tk.Frame(
            self.frame_principal,
            bg="black",
            width=980,
            height=580
        )
        self.frame_imagen.pack(side="left", fill="both", expand=True)
        
        # Frame para panel de controles
        self.frame_panel = tk.Frame(self.frame_principal, bg="black", width=320)
        self.frame_panel.pack(side="right", fill="y")
        self.frame_panel.pack_propagate(False)

        # Frame para controles (con scrollbar porque no cabe (: ))
        self.canvas_controles = tk.Canvas(
            self.frame_panel,
            bg="black",
            width=320,
            highlightthickness=0
        )
        self.canvas_controles.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.frame_panel,
            orient="vertical",
            command=self.canvas_controles.yview,
            bg="gray30"
        )
        self.scrollbar.pack(side="right", fill="y")
        
        # Configurar canvas para usar scrollbar
        self.canvas_controles.configure(yscrollcommand=self.scrollbar.set)
        
        # Frame interno para controles
        self.frame_controles = tk.Frame(self.canvas_controles, bg="black")
        
        # Crear ventana en el canvas
        self.canvas_window = self.canvas_controles.create_window(
            (0, 0), 
            window=self.frame_controles, 
            anchor="nw",
            width=300  # Ancho fijo para el frame interno
        )
        
        # Bind para actualizar scroll cuando cambie el tamaño
        self.frame_controles.bind(
            "<Configure>", 
            lambda e: self.actualizar_scroll_region()
        )
        
        # Habilitar scroll con rueda del mouse
        self.canvas_controles.bind_all("<MouseWheel>", self._on_mousewheel)
    
    #scroll con la rueda del mouse
    def _on_mousewheel(self, event):
        delta = int(-1 * (event.delta / 120))
        self.canvas_controles.yview_scroll(delta, "units")

    #actualizar region scrollable
    def actualizar_scroll_region(self):
        self.frame_controles.update_idletasks()
        self.canvas_controles.configure(scrollregion=self.canvas_controles.bbox("all"))
    
    def label_imagen(self):
        self.frame_imagen_contenedor = tk.Frame(
            self.frame_imagen,
            bg="black",
            width=1000,
            height=600
        )
        self.frame_imagen_contenedor.pack(expand=True, fill="both", padx=10, pady=10)

        self.canvas_imagen = tk.Canvas(
            self.frame_imagen_contenedor,
            bg="black",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas_imagen.pack(expand=True, fill="both")

        # Variables del zoom
        self.zoom_inicio_x = None
        self.zoom_inicio_y = None
        self.zoom_rect = None
        self.zoom_activo = False
        self.imagen_id = None
        self.imagen_original_vista = None

        # Eventos de mouse para zoom libre
        self.canvas_imagen.bind("<ButtonPress-1>", self.iniciar_zoom_rectangular)
        self.canvas_imagen.bind("<B1-Motion>", self.actualizar_zoom_rectangular)
        self.canvas_imagen.bind("<ButtonRelease-1>", self.aplicar_zoom_rectangular)

        self.ruta_entry = tk.Entry(
            self.frame_imagen,
            textvariable=self.ruta_imagen,
            width=40,
            font=("Arial", 12),
            bg="black",
            fg="light coral",
            relief="flat",
            insertbackground="white",
            justify="center"
        )
        self.ruta_entry.pack(pady=(10, 5), fill="x", padx=10)

    def crear_controles(self):
        # controles en el frame derecho
        # Título
        tk.Label(
            self.frame_controles,
            text="Controles",
            bg="black",
            fg="white",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(15, 10))
        
        # Separador
        tk.Frame(
            self.frame_controles,
            bg="gray30",
            height=2
        ).pack(fill="x", padx=20, pady=5)

        # Sección de carga de imágenes
        tk.Label(
            self.frame_controles,
            text="Imágenes",
            bg="black",
            fg="light blue",
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))
        
        # boton para cargar imagen
        tk.Button(
            self.frame_controles,
            text="Cargar Imagen",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.cargar_imagen
        ).pack(pady=5)
        
        # boton para cargar segunda imagen
        tk.Button(
            self.frame_controles,
            text="Fusionar Imagen",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.cargar_imagen2
        ).pack(pady=5)
        
        # Separador
        tk.Frame(
            self.frame_controles,
            bg="gray30",
            height=2
        ).pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            self.frame_controles,
            text="Ajustes de Imagen",
            bg="black",
            fg="light blue",
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))

        # Slider rotación
        tk.Scale(
            self.frame_controles,
            from_=0,
            to=360,
            orient="horizontal",
            length=240,
            label="Rotación (°)",
            variable=self.rotacion_var,
            bg="black",
            fg="white",
            troughcolor="gray30",
            highlightbackground="black",
            command=lambda v: self.actualizar_vista()
        ).pack(pady=8)
        
        # Slider brillo
        tk.Scale(
            self.frame_controles,
            from_=0.0,
            to=2.0,
            resolution=0.1,
            orient="horizontal",
            length=240,
            label="Brillo",
            variable=self.brillo_var,
            bg="black",
            fg="white",
            troughcolor="gray30",
            highlightbackground="black",
            command=lambda v: self.actualizar_vista()
        ).pack(pady=8)
        
        # Slider contraste
        tk.Scale(
            self.frame_controles,
            from_=0.0,
            to=3.0,
            resolution=0.1,
            orient="horizontal",
            length=240,
            label="Contraste",
            variable=self.contraste_var,
            bg="black",
            fg="white",
            troughcolor="gray30",
            highlightbackground="black",
            command=lambda v: self.actualizar_vista()
        ).pack(pady=8)


        self.frame_transparencia = tk.Frame(self.frame_controles, bg="black")
        # slider transparencia
        tk.Scale(
            self.frame_transparencia,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            length=240,
            label="Transparencia Fusión",
            variable=self.alpha_var,
            bg="black",
            fg="light pink",
            troughcolor="gray30",
            highlightbackground="black",
            command=lambda v: self.actualizar_vista()
        ).pack(pady=8)
        
        
        # Separador
        tk.Frame(
            self.frame_controles,
            bg="gray30",
            height=2
        ).pack(fill="x", padx=20, pady=10)

        # Sección de filtros
        tk.Label(
            self.frame_controles,
            text="Filtros",
            bg="black",
            fg="light blue",
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))

        # Frame para opciones de filtros
        frame_filtros = tk.Frame(self.frame_controles, bg="black")
        frame_filtros.pack(pady=5)
        
        tk.Radiobutton( #ningun filtro
            frame_filtros,
            text="Ninguno",
            variable=self.filtro_activo,
            value="ninguno",
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.cambiar_filtro
        ).pack(anchor="w")
        
        tk.Radiobutton( #zonas claras
            frame_filtros,
            text="Zonas Claras",
            variable=self.filtro_activo,
            value="zonas_claras",
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.cambiar_filtro
        ).pack(anchor="w")

        tk.Radiobutton( #zonas oscuras
            frame_filtros,
            text="Zonas Oscuras",
            variable=self.filtro_activo,
            value="zonas_oscuras",
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.cambiar_filtro
        ).pack(anchor="w")

        tk.Radiobutton( #capas rgb
            frame_filtros,
            text="Canales RGB",
            variable=self.filtro_activo,
            value="rgb",
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.cambiar_filtro
        ).pack(anchor="w")
        
        tk.Radiobutton( #capas cmy
            frame_filtros,
            text="Canales CMY",
            variable=self.filtro_activo,
            value="cmy",
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.cambiar_filtro
        ).pack(anchor="w")
        
        # Frame dinámico para opciones de filtro
        self.frame_opciones_filtro = tk.Frame(self.frame_controles, bg="black")
        self.frame_opciones_filtro.pack(pady=10)

        # Separador
        tk.Frame(
            self.frame_controles,
            bg="gray30",
            height=2
        ).pack(fill="x", padx=20, pady=10)

        tk.Label(
            self.frame_controles,
            text="Efectos Adicionales",
            bg="black",
            fg="light blue",
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))

        frame_efectos = tk.Frame(self.frame_controles, bg="black")
        frame_efectos.pack(pady=5)

        # Check para binarizar
        tk.Checkbutton(
            frame_efectos,
            text="Binarizar",
            variable=self.binarizar_activo,
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.actualizar_vista
        ).pack(anchor="w", padx=20)

        # Check para negativo
        tk.Checkbutton(
            frame_efectos,
            text="Negativo",
            variable=self.negativo_activo,
            bg="black",
            fg="white",
            selectcolor="gray30",
            activebackground="black",
            activeforeground="white",
            command=self.actualizar_vista
        ).pack(anchor="w", padx=20)


        # Separador
        tk.Frame(
            self.frame_controles,
            bg="gray30",
            height=2
        ).pack(fill="x", padx=20, pady=10)

        # Sección de herramientas
        tk.Label(
            self.frame_controles,
            text="Herramientas",
            bg="black",
            fg="light blue",
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))

        # Botón para zoom con coordenadas
        tk.Button(
            self.frame_controles,
            text="Zoom con Coordenadas",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.zoom_coordenadas
        ).pack(pady=5)

        # Botón para ver histograma
        tk.Button(
            self.frame_controles,
            text="Ver Histograma",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.mostrar_histograma
        ).pack(pady=5)

        # Botón para eliminar zoom
        tk.Button(
            self.frame_controles,
            text="Eliminar Zoom",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.restaurar_vista_original
        ).pack(pady=5)

        # Botón para resetear ajustes
        tk.Button(
            self.frame_controles,
            text="Resetear Ajustes",
            width=20,
            font=("Helvetica", 11),
            bg="light pink",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.resetear_ajustes
        ).pack(pady=5)

        # Boton para guardar imagen
        tk.Button(
            self.frame_controles,
            text="Guardar Imagen",
            width=20,
            font=("Helvetica", 11),
            bg="light coral",
            fg="black",
            relief="flat",
            cursor="hand2",
            command=self.guardar_imagen
        ).pack(pady=5)

        # Espaciado final
        tk.Label(
            self.frame_controles, 
            text="", 
            bg="black", 
            height=2
        ).pack()

        self.actualizar_scroll_region()
 
    def cambiar_filtro(self):
        # Limpiar frame de opciones
        for widget in self.frame_opciones_filtro.winfo_children():
            widget.destroy()
        
        filtro = self.filtro_activo.get()
        
        if filtro == "zonas_claras" or filtro == "zonas_oscuras":
            # Controles para zonas claras/oscuras
            tk.Label(
                self.frame_opciones_filtro,
                text="Ajustes:",
                bg="black",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack()
            
            tk.Scale(
                self.frame_opciones_filtro,
                from_=0.0, to=1.0,
                resolution=0.05,
                orient="horizontal",
                length=260,
                label="Umbral",
                variable=self.umbral_zonas,
                bg="black",
                fg="white",
                troughcolor="gray30",
                highlightbackground="black",
                command=lambda v: self.actualizar_vista()
            ).pack(pady=3)
            
            if filtro == "zonas_claras":
                self.intensidad_zonas.set(1.5)
                tk.Scale(
                    self.frame_opciones_filtro,
                    from_=1.0, to=3.0,
                    resolution=0.1,
                    orient="horizontal",
                    length=260,
                    label="Intensidad (brillo)",
                    variable=self.intensidad_zonas,
                    bg="black",
                    fg="white",
                    troughcolor="gray30",
                    highlightbackground="black",
                    command=lambda v: self.actualizar_vista()
                ).pack(pady=3)
            else:
                self.intensidad_zonas.set(0.5)
                tk.Scale(
                    self.frame_opciones_filtro,
                    from_=0.0, to=1.0,
                    resolution=0.05,
                    orient="horizontal",
                    length=260,
                    label="Intensidad (oscuridad)",
                    variable=self.intensidad_zonas,
                    bg="black",
                    fg="white",
                    troughcolor="gray30",
                    highlightbackground="black",
                    command=lambda v: self.actualizar_vista()
                ).pack(pady=3)
        
        elif filtro == "rgb":
            # Checkboxes para RGB
            tk.Label(
                self.frame_opciones_filtro,
                text="Selecciona canales:",
                bg="black",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack()
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Rojo",
                variable=self.rgb_rojo,
                bg="black",
                fg="red",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="red",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Verde",
                variable=self.rgb_verde,
                bg="black",
                fg="green",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="green",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Azul",
                variable=self.rgb_azul,
                bg="black",
                fg="blue",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="blue",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)
        
        elif filtro == "cmy":
            # Checkboxes para CMY
            tk.Label(
                self.frame_opciones_filtro,
                text="Selecciona canales:",
                bg="black",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack()
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Cian",
                variable=self.cmy_cian,
                bg="black",
                fg="cyan",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="cyan",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Magenta",
                variable=self.cmy_magenta,
                bg="black",
                fg="magenta",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="magenta",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)
            
            tk.Checkbutton(
                self.frame_opciones_filtro,
                text="Amarillo",
                variable=self.cmy_amarillo,
                bg="black",
                fg="yellow",
                selectcolor="gray30",
                activebackground="black",
                activeforeground="yellow",
                command=self.actualizar_vista
            ).pack(anchor="w", padx=20)

        elif filtro == "binarizar":
            # Control de umbral para binarización
            tk.Label(
                self.frame_opciones_filtro,
                text="Ajustes:",
                bg="black",
                fg="white",
                font=("Arial", 10, "bold")
            ).pack()
            
            tk.Scale(
                self.frame_opciones_filtro,
                from_=0, to=255,
                resolution=1,
                orient="horizontal",
                length=260,
                label="Umbral",
                variable=self.umbral_binarizacion,
                bg="black",
                fg="white",
                troughcolor="gray30",
                highlightbackground="black",
                command=lambda v: self.actualizar_vista()
            ).pack(pady=3)

        
        self.actualizar_scroll_region()
        self.actualizar_vista()
    
    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Selecciona una imagen",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if ruta:
            self.procesador.cargar_imagen(ruta)
            self.ruta_imagen.set(ruta)
            self.fusion_activa = False
            self.resetear_ajustes()
            self.actualizar_vista()
        
    def cargar_imagen2(self):
        if not self.procesador.imagen_original:
            messagebox.showwarning(
                "Advertencia", 
                "Primero carga una imagen principal"
            )
            return
        
        ruta = filedialog.askopenfilename(
            title="Selecciona la segunda imagen para fusionar",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if ruta:
            self.procesador.cargar_imagen2(ruta)
            self.fusion_activa = True
            
            # Mostrar el slider de transparencia
            self.frame_transparencia.pack(after=self.frame_controles.winfo_children()[8], pady=8)
            self.actualizar_scroll_region()
            
            self.actualizar_vista()
            messagebox.showinfo(
                "Éxito",
                "Segunda imagen cargada.\nUsa el slider de transparencia para ajustar."
        )
    
    #actualiza la imagen automaticamente con los cambios efectuados
    def actualizar_vista(self):
        if not self.procesador.imagen_original:
            return
        
        # Si hay zoom activo, restaurar primero
        if self.zoom_activo:
            self.zoom_activo = False
            self.imagen_original_vista = None
        
        # Aplicar parametros de filtro
        filtro_tipo = self.filtro_activo.get()
        filtro_params = None
        
        if filtro_tipo != "ninguno":
            if filtro_tipo == "zonas_claras":
                filtro_params = {
                    'umbral': self.umbral_zonas.get(),
                    'intensidad': self.intensidad_zonas.get()
                }
            elif filtro_tipo == "zonas_oscuras":
                filtro_params = {
                    'umbral': self.umbral_zonas.get(),
                    'intensidad': self.intensidad_zonas.get()
                }
            elif filtro_tipo == "rgb":
                filtro_params = {
                    'rojo': self.rgb_rojo.get(),
                    'verde': self.rgb_verde.get(),
                    'azul': self.rgb_azul.get()
                }
            elif filtro_tipo == "cmy":
                filtro_params = {
                    'cian': self.cmy_cian.get(),
                    'magenta': self.cmy_magenta.get(),
                    'amarillo': self.cmy_amarillo.get()
                }
            elif filtro_tipo == "binarizar":
                filtro_params = {
                    'umbral': self.umbral_binarizacion.get()
                }
            elif filtro_tipo == "negativo":
                filtro_params = {"": None}
        
        # Procesar imagen con ajustes
        imagen_procesada = self.procesador.procesar_imagen(
            brillo=self.brillo_var.get(),
            contraste=self.contraste_var.get(),
            rotacion=self.rotacion_var.get(),
            filtro_tipo=filtro_tipo if filtro_tipo != "ninguno" else None,
            filtro_params=filtro_params
        )

        if self.binarizar_activo.get():
            imagen_procesada = self.procesador.binarizar_imagen(
                imagen_procesada,
                umbral=self.umbral_binarizacion.get()
            )

        if self.negativo_activo.get():
            imagen_procesada = self.procesador.aplicar_negativo(imagen_procesada)

        
        # Aplicar fusión si está activa
        if self.fusion_activa and self.procesador.imagen_fusion:
            self.imagen_mostrada = self.procesador.fusionar_imagenes(
                imagen_procesada,
                self.alpha_var.get()
            )
        else:
            self.imagen_mostrada = imagen_procesada
        
        # Mostrar en interfaz
        self.mostrar_imagen()
    
    def iniciar_zoom_rectangular(self, event):
        if not self.imagen_mostrada or self.zoom_activo:
            return
        
        self.zoom_inicio_x = event.x
        self.zoom_inicio_y = event.y
        
        # Dibujar rectángulo de selección
        if self.zoom_rect:
            self.canvas_imagen.delete(self.zoom_rect)
        
        self.zoom_rect = self.canvas_imagen.create_rectangle(
            self.zoom_inicio_x, self.zoom_inicio_y,
            self.zoom_inicio_x, self.zoom_inicio_y,
            outline="red", width=2
        )

    def actualizar_zoom_rectangular(self, event):
        if self.zoom_rect and not self.zoom_activo:
            self.canvas_imagen.coords(
                self.zoom_rect, 
                self.zoom_inicio_x, 
                self.zoom_inicio_y, 
                event.x, 
                event.y
            )

    def aplicar_zoom_rectangular(self, event):
        if not self.zoom_rect or not self.imagen_mostrada or self.zoom_activo:
            if self.zoom_rect:
                self.canvas_imagen.delete(self.zoom_rect)
                self.zoom_rect = None
            return

        # Obtener coordenadas del rectángulo en el canvas
        x1, y1, x2, y2 = self.canvas_imagen.coords(self.zoom_rect)
        self.canvas_imagen.delete(self.zoom_rect)
        self.zoom_rect = None

        if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
            return

        # Normalizar coordenadas 
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        canvas_w = self.canvas_imagen.winfo_width()
        canvas_h = self.canvas_imagen.winfo_height()

        # Obtener imagen redimensionada que se está mostrando
        img_display = self.procesador.redimensionar_para_mostrar(
            self.imagen_mostrada, max_ancho=1000, max_alto=600
        )
        img_w, img_h = img_display.size

        # centrar imagen con zoom
        img_x = (canvas_w - img_w) // 2
        img_y = (canvas_h - img_h) // 2

        img_x1 = int(x1 - img_x)
        img_y1 = int(y1 - img_y)
        img_x2 = int(x2 - img_x)
        img_y2 = int(y2 - img_y)

        img_x1 = max(0, min(img_w, img_x1))
        img_x2 = max(0, min(img_w, img_x2))
        img_y1 = max(0, min(img_h, img_y1))
        img_y2 = max(0, min(img_h, img_y2))

        # Validar que las coordenadas sean válidas
        if img_x2 <= img_x1 or img_y2 <= img_y1:
            return

        # Recortar región de la imagen
        arr = np.array(img_display)
        region = arr[img_y1:img_y2, img_x1:img_x2]
        
        if region.size == 0:
            return

        # Calcular proporción de la región seleccionada
        region_h, region_w = region.shape[:2]
        aspect_ratio = region_w / region_h
        canvas_aspect = canvas_w / canvas_h

        if aspect_ratio > canvas_aspect:

            new_w = canvas_w
            new_h = int(new_w / aspect_ratio)
        else:
            # La región es más alta, limitar por altura
            new_h = canvas_h
            new_w = int(new_h * aspect_ratio)

        new_w = max(100, new_w)
        new_h = max(100, new_h)

        zoom_img = Image.fromarray(region).resize((new_w, new_h), Image.LANCZOS)

        self.imagen_original_vista = self.imagen_mostrada.copy()
        self.imagen_mostrada = zoom_img
        self.zoom_activo = True
        self.mostrar_imagen()

    def restaurar_vista_original(self):
        if not self.zoom_activo or not self.imagen_original_vista:
            messagebox.showinfo("Zoom", "No hay zoom activo para restaurar.")
            return

        self.imagen_mostrada = self.imagen_original_vista
        self.zoom_activo = False
        self.imagen_original_vista = None
    
        self.mostrar_imagen()
        self.canvas_imagen.config(cursor="crosshair")

    def zoom_coordenadas(self):
        if not self.imagen_mostrada:
            messagebox.showwarning(
                "Advertencia",
                "Primero carga una imagen"
            )
            return
        
        # Obtener dimensiones de la imagen original
        ancho_orig, alto_orig = self.imagen_mostrada.size
        
        # Crear ventana para ingresar datos
        ventana_input = Toplevel(self.root)
        ventana_input.title("Zoom con Coordenadas")
        ventana_input.configure(bg="black")
        ventana_input.geometry("350x250")
        ventana_input.resizable(False, False)
        
        # Título
        tk.Label(
            ventana_input,
            text="Ingresa las coordenadas",
            bg="black",
            fg="light blue",
            font=("Helvetica", 12, "bold")
        ).pack(pady=10)
        
        # Frame para inputs
        frame_inputs = tk.Frame(ventana_input, bg="black")
        frame_inputs.pack(pady=10)
        
        # Coordenada x
        tk.Label(
            frame_inputs,
            text=f"Coordenada X (0 - {ancho_orig}):",
            bg="black",
            fg="white",
            font=("Helvetica", 10)
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        entrada_x = tk.Entry(frame_inputs, width=15, font=("Helvetica", 10))
        entrada_x.grid(row=0, column=1, padx=10, pady=5)
        
        # Coordenada y
        tk.Label(
            frame_inputs,
            text=f"Coordenada Y (0 - {alto_orig}):",
            bg="black",
            fg="white",
            font=("Helvetica", 10)
        ).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        entrada_y = tk.Entry(frame_inputs, width=15, font=("Helvetica", 10))
        entrada_y.grid(row=1, column=1, padx=10, pady=5)
        
        # Tamaño del zoom
        tk.Label(
            frame_inputs,
            text="Tamaño del área (50-300):",
            bg="black",
            fg="white",
            font=("Helvetica", 10)
        ).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        entrada_size = tk.Entry(frame_inputs, width=15, font=("Helvetica", 10))
        entrada_size.insert(0, "150")  # Valor por defecto
        entrada_size.grid(row=2, column=1, padx=10, pady=5)
        
        # Función para aplicar el zoom
        def aplicar_zoom():
            try:
                x = int(entrada_x.get())
                y = int(entrada_y.get())
                zoom_size = int(entrada_size.get())
                
                # Validar rangos
                if not (0 <= x < ancho_orig):
                    messagebox.showerror(
                        "Error",
                        f"La coordenada X debe estar entre 0 y {ancho_orig-1}"
                    )
                    return
                
                if not (0 <= y < alto_orig):
                    messagebox.showerror(
                        "Error",
                        f"La coordenada Y debe estar entre 0 y {alto_orig-1}"
                    )
                    return
                
                if not (50 <= zoom_size <= 300):
                    messagebox.showerror(
                        "Error",
                        "El tamaño del área debe estar entre 50 y 300"
                    )
                    return
                
                # Cerrar ventana de input
                ventana_input.destroy()
                
                # Realizar zoom en la imagen original (no redimensionada)
                arr_original = np.array(self.imagen_mostrada)
                h, w, _ = arr_original.shape
                
                # Ajustar coordenadas si están fuera de rango
                x = np.clip(x, 0, w - 1)
                y = np.clip(y, 0, h - 1)
                
                # Crear ventana de zoom
                self._crear_ventana_zoom(arr_original, x, y, zoom_size, h, w)
                
            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Por favor ingresa valores numéricos válidos"
                )
        
        # Frame para botones
        frame_botones = tk.Frame(ventana_input, bg="black")
        frame_botones.pack(pady=15)
        
        # Botón aplicar
        tk.Button(
            frame_botones,
            text="Aplicar Zoom",
            command=aplicar_zoom,
            bg="light green",
            fg="black",
            font=("Helvetica", 10),
            relief="flat",
            cursor="hand2",
            width=12
        ).pack(side="left", padx=5)
        
        # Botón cancelar
        tk.Button(
            frame_botones,
            text="Cancelar",
            command=ventana_input.destroy,
            bg="light coral",
            fg="black",
            font=("Helvetica", 10),
            relief="flat",
            cursor="hand2",
            width=12
        ).pack(side="left", padx=5)
        
        # Enfocar en el primer campo
        entrada_x.focus()
    
    def _crear_ventana_zoom(self, arr_imagen, x, y, zoom_size, h, w):
        # Tamaño del área de zoom
        zoom_size = int(zoom_size / 2)
        left = max(x - zoom_size, 0)
        upper = max(y - zoom_size, 0)
        right = min(x + zoom_size, w)
        lower = min(y + zoom_size, h)

        # Recortar región usando NumPy
        region = arr_imagen[int(upper):int(lower), int(left):int(right)]

        # Escalar usando Pillow solo para mostrar
        region_zoom = Image.fromarray(region).resize((300, 300), Image.LANCZOS)

        # Crear ventana flotante para el zoom
        top = tk.Toplevel(self.root)
        top.title(f"Zoom en ({x}, {y})")
        top.configure(bg="black")

        # Frame para la imagen
        frame_zoom = tk.Frame(top, bg="black")
        frame_zoom.pack(padx=10, pady=10)

        zoom_img_tk = ImageTk.PhotoImage(region_zoom)
        lbl_zoom = tk.Label(frame_zoom, image=zoom_img_tk, bg="black")
        lbl_zoom.image = zoom_img_tk  # mantener referencia
        lbl_zoom.pack()
        
        # Label con información
        tk.Label(
            top,
            text=f"Coordenadas: X={x}, Y={y} | Área: {zoom_size*2}x{zoom_size*2}",
            bg="black",
            fg="white",
            font=("Helvetica", 9)
        ).pack(pady=(0, 10))

    def mostrar_imagen(self):
        if not self.imagen_mostrada:
            return

        # Redimensionar para mostrar
        img_display = self.procesador.redimensionar_para_mostrar(
            self.imagen_mostrada,
            max_ancho=1000,
            max_alto=600
        )

        self.imagen_tk = ImageTk.PhotoImage(img_display)
        self.canvas_imagen.delete("all")

        # Dibujar imagen centrada en el canvas
        w = self.canvas_imagen.winfo_width()
        h = self.canvas_imagen.winfo_height()
        img_w, img_h = img_display.size
        x = w // 2
        y = h // 2
        self.imagen_id = self.canvas_imagen.create_image(x, y, image=self.imagen_tk, anchor="center")
    
    #mostarr histograma en una ventana nueva
    def mostrar_histograma(self):
        if not self.imagen_mostrada:
            messagebox.showwarning(
                "Advertencia",
                "Primero carga una imagen"
            )
            return
        
        # Crear ventana nueva para el histograma
        ventana_histograma = Toplevel(self.root)
        ventana_histograma.title("Histograma RGB")
        ventana_histograma.configure(bg="black")
        ventana_histograma.geometry("650x500")
        
        # Generar figura del histograma
        fig = self.procesador.generar_histograma(
            self.imagen_mostrada,
            ventana_histograma
        )
        
        # Crear canvas para mostrar el histograma
        canvas = FigureCanvasTkAgg(fig, master=ventana_histograma)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


        # Resetear filtros
    
    def resetear_ajustes(self):
        self.rotacion_var.set(0)
        self.brillo_var.set(1.0)
        self.contraste_var.set(1.0)
        self.alpha_var.set(0.5)

        # Resetear filtros
        self.filtro_activo.set("ninguno")
        self.rgb_rojo.set(True)
        self.rgb_verde.set(True)
        self.rgb_azul.set(True)
        self.cmy_cian.set(True)
        self.cmy_magenta.set(True)
        self.cmy_amarillo.set(True)
        self.umbral_zonas.set(0.5)
        self.intensidad_zonas.set(1.5)
        self.umbral_binarizacion.set(128)
        self.binarizar_activo.set(False)
        self.negativo_activo.set(False)


        # Limpiar opciones de filtro
        for widget in self.frame_opciones_filtro.winfo_children():
            widget.destroy()

        # Eliminar la segunda imagen si estaba cargada
        self.procesador.imagen_fusion = None
        self.fusion_activa = False

        # Ocultar el slider de transparencia
        self.frame_transparencia.pack_forget()
        self.actualizar_scroll_region()

        if self.procesador.imagen_original:
            self.actualizar_vista()

    
    def guardar_imagen(self):
        #guarda la imagen mostrada
        if not self.imagen_mostrada:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar")
            return
        
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tiff")
            ],
            title="Guardar imagen como"
        )
        
        if ruta:
            self.procesador.guardar_imagen(self.imagen_mostrada, ruta)
            messagebox.showinfo("Éxito", "Imagen guardada correctamente")
    
    def ejecutar(self):
        self.root.mainloop()