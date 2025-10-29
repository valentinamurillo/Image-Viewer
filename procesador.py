# procesamiento de imágenes

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


class ProcesadorImagenes:
    
    def __init__(self):
        self.imagen_original = None
        self.imagen_fusion = None
    
    def cargar_imagen(self, ruta):
        self.imagen_original = Image.open(ruta).convert("RGB")
        return self.imagen_original
    
    def cargar_imagen2(self, ruta):
        self.imagen_fusion = Image.open(ruta).convert("RGB")
        return self.imagen_fusion
    
    def aplicar_brillo(self, imagen, factor_brillo):
        # convierte la imagen a un array numpy y normaliza
        img_array = np.array(imagen, dtype=np.float32) / 255.0
        img_array = np.clip(img_array * factor_brillo, 0, 1)
        return img_array
    
    def aplicar_contraste(self, img_array, factor_contraste):
        img_array = np.clip((img_array - 0.5) * factor_contraste + 0.5, 0, 1)
        return img_array
    
    def aplicar_rotacion(self, imagen, angulo):
        if angulo == 0:
            return imagen
        return imagen.rotate(-angulo, expand=True)
    
    # filtros
    def filtro_zonas_claras(self, imagen, umbral=0.5, intensidad=1.5):
        
        # convertir en array normalizado
        img_array = np.array(imagen, dtype=np.float32) / 255.0
        
        # Calcular brillo por píxel (promedio RGB)
        brillo = np.mean(img_array, axis=2, keepdims=True)
        
        # Crear máscara de zonas claras
        mascara = (brillo > umbral).astype(np.float32)
        
        # Aplicar intensidad solo a zonas claras
        img_array = img_array * (1 + mascara * (intensidad - 1))
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    

    def filtro_zonas_oscuras(self, imagen, umbral=0.5, intensidad=0.5):
        # convertir en array normalizado
        img_array = np.array(imagen, dtype=np.float32) / 255.0
        
        # Calcular brillo por píxel
        brillo = np.mean(img_array, axis=2, keepdims=True)
        
        # Crear máscara de zonas oscuras
        mascara = (brillo < umbral).astype(np.float32)
        
        # Oscurecer zonas oscuras
        img_array = img_array * (1 - mascara * (1 - intensidad))
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    

    def aplicar_canales_rgb(self, imagen, rojo=True, verde=True, azul=True):
        img_array = np.array(imagen, dtype=np.uint8)
        
        # Desactivar canales según selección
        if not rojo:
            img_array[:, :, 0] = 0  # Canal rojo = 0
        if not verde:
            img_array[:, :, 1] = 0  # Canal verde = 0
        if not azul:
            img_array[:, :, 2] = 0  # Canal azul = 0
        
        return Image.fromarray(img_array)
    
    def aplicar_canales_cmy(self, imagen, cian=True, magenta=True, amarillo=True):
        img_array = np.array(imagen, dtype=np.float32) / 255.0
        
        # Convertir RGB a CMY: CMY = 1 - RGB
        cmy_array = 1 - img_array
        
        # Desactivar canales según selección
        if not cian:
            cmy_array[:, :, 0] = 0  # Sin cian
        if not magenta:
            cmy_array[:, :, 1] = 0  # Sin magenta
        if not amarillo:
            cmy_array[:, :, 2] = 0  # Sin amarillo
        
        # Convertir de vuelta a RGB: RGB = 1 - CMY
        img_array = 1 - cmy_array
        img_array = np.clip(img_array, 0, 1)
        
        return Image.fromarray((img_array * 255).astype(np.uint8))
    
    def binarizar_imagen(self, imagen, umbral=128):
        # Convertir a escala de grises
        img_gray = imagen.convert('L')
        img_array = np.array(img_gray)
        
        # Aplicar umbral: pixels > umbral = 255 (blanco), sino 0 (negro)
        img_binaria = np.where(img_array > umbral, 255, 0).astype(np.uint8)
        
        # Convertir de vuelta a RGB para mantener compatibilidad
        return Image.fromarray(img_binaria).convert('RGB')
    
    def aplicar_negativo(self, imagen):
        img_array = np.array(imagen, dtype=np.uint8)
        
        # Invertir: nuevo_valor = 255 - valor_original
        img_negativo = 255 - img_array
        
        return Image.fromarray(img_negativo)
    
    def generar_histograma(self, imagen, parent_frame):
        img_array = np.array(imagen)
        
        # Crear figura de matplotlib
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
        ax.set_facecolor('black')
        
        # Calcular histogramas para cada canal
        colores = ['red', 'green', 'blue']
        nombres = ['Rojo', 'Verde', 'Azul']
        
        for i, (color, nombre) in enumerate(zip(colores, nombres)):
            histograma, bins = np.histogram(img_array[:, :, i].flatten(), bins=256, range=(0, 256))
            ax.plot(bins[:-1], histograma, color=color, alpha=0.7, linewidth=2, label=nombre)
        
        # Configurar gráfico
        ax.set_xlabel('Intensidad de Pixel', color='white', fontsize=10)
        ax.set_ylabel('Frecuencia', color='white', fontsize=10)
        ax.set_title('Histograma RGB', color='white', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white', labelsize=8)
        ax.legend(facecolor='gray', edgecolor='white', fontsize=9)
        ax.grid(True, alpha=0.2, color='gray')
        
        # Configurar spines
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        
        plt.tight_layout()
        
        return fig
    
    def procesar_imagen(self, brillo=1.0, contraste=1.0, rotacion=0, filtro_tipo=None, filtro_params=None):
        if not self.imagen_original:
            return None
        
        # Aplicar brillo
        img_array = self.aplicar_brillo(self.imagen_original, brillo)
        
        # Aplicar contraste
        img_array = self.aplicar_contraste(img_array, contraste)
        
        # Convertir de vuelta a imagen PIL
        img_uint8 = (img_array * 255).astype(np.uint8)
        imagen_procesada = Image.fromarray(img_uint8)
        
        # Aplicar rotación
        imagen_procesada = self.aplicar_rotacion(imagen_procesada, rotacion)
        
        # Aplicar filtros de color si están activados
        if filtro_tipo and filtro_params:

            if filtro_tipo == 'zonas_claras':
                imagen_procesada = self.filtro_zonas_claras(
                    imagen_procesada,
                    umbral=filtro_params.get('umbral', 0.5),
                    intensidad=filtro_params.get('intensidad', 1.5)
                )
            elif filtro_tipo == 'zonas_oscuras':
                imagen_procesada = self.filtro_zonas_oscuras(
                    imagen_procesada,
                    umbral=filtro_params.get('umbral', 0.5),
                    intensidad=filtro_params.get('intensidad', 0.5)
                )
            elif filtro_tipo == 'rgb':
                imagen_procesada = self.aplicar_canales_rgb(
                    imagen_procesada,
                    rojo=filtro_params.get('rojo', True),
                    verde=filtro_params.get('verde', True),
                    azul=filtro_params.get('azul', True)
                )
            elif filtro_tipo == 'cmy':
                imagen_procesada = self.aplicar_canales_cmy(
                    imagen_procesada,
                    cian=filtro_params.get('cian', True),
                    magenta=filtro_params.get('magenta', True),
                    amarillo=filtro_params.get('amarillo', True)
                )
            elif filtro_tipo == 'binarizar':
                imagen_procesada = self.binarizar_imagen(
                    imagen_procesada,
                    umbral=filtro_params.get('umbral', 128)
                )
            elif filtro_tipo == 'negativo':
                imagen_procesada = self.aplicar_negativo(imagen_procesada)
        
        return imagen_procesada

    def fusionar_imagenes(self, imagen_base, alpha):
        if not self.imagen_fusion or not imagen_base:
            return imagen_base
        
        # Redimensionar imagen de fusión al tamaño de la base
        img2_resized = self.imagen_fusion.resize(imagen_base.size)
        
        # Convertir a arrays normalizados
        arr1 = np.array(imagen_base, dtype=np.float32) / 255.0
        arr2 = np.array(img2_resized, dtype=np.float32) / 255.0
        
        # Realizar fusión
        arr_fusion = alpha * arr1 + (1 - alpha) * arr2
        arr_fusion = np.clip(arr_fusion, 0, 1)
        
        # Convertir de vuelta a imagen
        img_fusion = Image.fromarray((arr_fusion * 255).astype(np.uint8))
        return img_fusion
    
    def guardar_imagen(self, imagen, ruta):
        try:
            imagen.save(ruta)
            return True
        except Exception as e:
            raise Exception(f"Error al guardar imagen: {str(e)}")
    
    def obtener_dimensiones(self, imagen):
        return imagen.size if imagen else (0, 0)
    
    def redimensionar_para_mostrar(self, imagen, max_ancho=1000, max_alto=600):
        if not imagen:
            return None
        
        img_copia = imagen.copy()
        img_copia.thumbnail((max_ancho, max_alto), Image.Resampling.LANCZOS)
        return img_copia