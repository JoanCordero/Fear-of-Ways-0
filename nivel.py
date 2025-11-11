import pygame
import random
import json
from pathlib import Path
from pared import pared
from salida import salida

# Carga opcional de un icono de llave desde el código principal.
# Este icono se dibujará sobre las llaves en el mapa si está definido.
ICONO_LLAVE = None

# La textura se asignará desde main.py después de inicializar pygame
TEXTURA_SUELO = None  # Valor inicial, será reemplazado

class nivel:
    """Define un nivel con su laberinto, enemigos y salida"""
    def __init__(self, numero, semilla=None):
        # identificación del nivel
        self.numero = numero
        
        # Semilla para generación procedural consistente
        if semilla is None:
            # Generar nueva semilla basada en el nivel y tiempo actual
            import time
            self.semilla = hash((numero, time.time())) % (2**32)
        else:
            self.semilla = semilla
        
        # Establecer la semilla de random para generación consistente
        random.seed(self.semilla)

        # listas de objetos del mapa
        self.muros = []
        self.salida = None
        self.spawn_enemigos = []

        # dimensiones generales del mapa (más grandes que la pantalla)
        self.ancho = 2000
        self.alto = 1500

        # generar estructura del nivel
        self.crear_nivel()
        # una vez creado el nivel, pre-renderizar el suelo a una superficie grande
        # Esto evita artefactos de bordes y garantiza que el suelo cubra todo el laberinto.
        self._crear_surface_suelo()

        # Restaurar random a estado no determinista después de generar
        random.seed()

    def crear_nivel(self):
        # selecciona qué versión de nivel crear
        if self.numero == 1:
            self.crear_nivel_1()
        elif self.numero == 2:
            self.crear_nivel_2()
        elif self.numero == 3:
            self.crear_nivel_3()

    def _cargar_nivel_desde_txt(self, numero_nivel):
        """Carga la configuración del nivel desde un archivo TXT.
        
        Formato del archivo TXT:
        - MURO x y w h
        - LLAVE x y w h
        - SPAWN x y
        - SALIDA x y
        - Líneas que comienzan con # son comentarios
        
        Retorna True si se cargó exitosamente, False en caso contrario.
        """
        try:
            base = Path(__file__).resolve().parent
            archivo_txt = base / f'mapas_export_nivel_{numero_nivel}.txt'
            
            if not archivo_txt.exists():
                return False
            
            # Inicializar listas
            self.llaves = []
            self.spawn_enemigos = []
            
            with open(archivo_txt, 'r', encoding='utf-8') as f:
                for linea in f:
                    # Eliminar espacios y saltos de línea
                    linea = linea.strip()
                    
                    # Ignorar líneas vacías y comentarios
                    if not linea or linea.startswith('#'):
                        continue
                    
                    # Dividir la línea en partes
                    partes = linea.split()
                    
                    if not partes:
                        continue
                    
                    tipo = partes[0].upper()
                    
                    try:
                        if tipo == 'MURO' and len(partes) >= 5:
                            x = int(partes[1])
                            y = int(partes[2])
                            w = int(partes[3])
                            h = int(partes[4])
                            self.muros.append(pared(x, y, w, h))
                        
                        elif tipo == 'LLAVE' and len(partes) >= 5:
                            x = int(partes[1])
                            y = int(partes[2])
                            w = int(partes[3])
                            h = int(partes[4])
                            self.llaves.append(pygame.Rect(x, y, w, h))
                        
                        elif tipo == 'SPAWN' and len(partes) >= 3:
                            x = int(partes[1])
                            y = int(partes[2])
                            self.spawn_enemigos.append((x, y))
                        
                        elif tipo == 'SALIDA' and len(partes) >= 3:
                            x = int(partes[1])
                            y = int(partes[2])
                            self.salida = salida(x, y)
                    
                    except (ValueError, IndexError) as e:
                        # Si hay error parseando una línea, continuar con la siguiente
                        print(f"Error parseando línea '{linea}': {e}")
                        continue
            
            # Establecer número de llaves requeridas
            self.llaves_requeridas = len(self.llaves)
            
            # Si no se definió salida, usar posición por defecto
            if self.salida is None:
                self.salida = salida(self.ancho - 200, self.alto - 200)
            
            return True
            
        except Exception as e:
            print(f"Error cargando nivel desde TXT: {e}")
            return False

    def crear_nivel_1(self):
        """Nivel 1: Mazmorra orgánica estilo caverna con pasillos interconectados.
        
        Diseño inspirado en mazmorras clásicas con formas orgánicas:
        - Sin habitaciones cuadradas aisladas
        - Pasillos conectados y curvos estilo caverna
        - Áreas amplias naturales (100-150px de ancho)
        - Múltiples rutas alternativas
        - 3 llaves en alcobas accesibles
        - Salida al final del recorrido
        """
        # Cargar desde archivo TXT si existe
        if self._cargar_nivel_desde_txt(1):
            return

        # Bordes del mapa (marco perimetral)
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # === LABERINTO DE ANILLOS CONCÉNTRICOS (estilo circular) ===
        # Aproximación a un laberinto circular usando marcos rectangulares
        # concéntricos con aperturas alternadas. Pasillos >= 110 px.

        centro_x, centro_y = self.ancho // 2, self.alto // 2
        grosor_muro = 30               # grosor de muro
        ancho_pasillo = 120             # ancho mínimo de pasillo
        numero_anillos = 5               # número de anillos
        ancho_hueco = 160               # ancho de cada apertura
        mitad_interior = 140          # semitamaño de la cámara central

        def agregar_division_horizontal(x_inicio, x_fin, y_posicion, centro_hueco=None):
            """Añade una pared horizontal con hueco opcional."""
            if centro_hueco is None:
                self.muros.append(pared(x_inicio, y_posicion, x_fin - x_inicio, grosor_muro))
                return
            hueco_izquierda = max(x_inicio, int(centro_hueco - ancho_hueco // 2))
            hueco_derecha = min(x_fin, int(centro_hueco + ancho_hueco // 2))
            if hueco_izquierda - x_inicio > 0:
                self.muros.append(pared(x_inicio, y_posicion, hueco_izquierda - x_inicio, grosor_muro))
            if x_fin - hueco_derecha > 0:
                self.muros.append(pared(hueco_derecha, y_posicion, x_fin - hueco_derecha, grosor_muro))

        def agregar_division_vertical(y_inicio, y_fin, x_posicion, centro_hueco=None):
            """Añade una pared vertical con hueco opcional."""
            if centro_hueco is None:
                self.muros.append(pared(x_posicion, y_inicio, grosor_muro, y_fin - y_inicio))
                return
            hueco_arriba = max(y_inicio, int(centro_hueco - ancho_hueco // 2))
            hueco_abajo = min(y_fin, int(centro_hueco + ancho_hueco // 2))
            if hueco_arriba - y_inicio > 0:
                self.muros.append(pared(x_posicion, y_inicio, grosor_muro, hueco_arriba - y_inicio))
            if y_fin - hueco_abajo > 0:
                self.muros.append(pared(x_posicion, hueco_abajo, grosor_muro, y_fin - hueco_abajo))

        # Construcción de anillos desde el centro hacia afuera
        posiciones_aperturas = ['top', 'right', 'bottom', 'left']
        for indice_anillo in range(numero_anillos):
            mitad_anillo = mitad_interior + indice_anillo * (ancho_pasillo + grosor_muro)
            borde_izquierdo = centro_x - mitad_anillo
            borde_derecho = centro_x + mitad_anillo
            borde_superior = centro_y - mitad_anillo
            borde_inferior = centro_y + mitad_anillo

            lado_apertura = posiciones_aperturas[indice_anillo % 4]
            if lado_apertura == 'top':
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_superior - grosor_muro, centro_hueco=centro_x)
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_inferior, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_izquierdo - grosor_muro, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_derecho, centro_hueco=None)
            elif lado_apertura == 'right':
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_superior - grosor_muro, centro_hueco=None)
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_inferior, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_derecho, centro_hueco=centro_y)
                agregar_division_vertical(borde_superior, borde_inferior, borde_izquierdo - grosor_muro, centro_hueco=None)
            elif lado_apertura == 'bottom':
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_inferior, centro_hueco=centro_x)
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_superior - grosor_muro, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_izquierdo - grosor_muro, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_derecho, centro_hueco=None)
            else:  # left
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_superior - grosor_muro, centro_hueco=None)
                agregar_division_horizontal(borde_izquierdo, borde_derecho, borde_inferior, centro_hueco=None)
                agregar_division_vertical(borde_superior, borde_inferior, borde_izquierdo - grosor_muro, centro_hueco=centro_y)
                agregar_division_vertical(borde_superior, borde_inferior, borde_derecho, centro_hueco=None)

        # Cámara central abierta y salida cerca del centro
        self.salida = salida(centro_x - 40, centro_y - 40)

        # Preparar valores para colocar llaves en distintos anillos
        mitad_exterior = mitad_interior + (numero_anillos - 1) * (ancho_pasillo + grosor_muro)
        # Coordenadas en mitad de pasillos (alejado de paredes)
        desplazamiento_llave = ancho_pasillo // 2

        # === LLAVES (3 requeridas en anillos distintos) ===
        self.llaves = [
            pygame.Rect(centro_x + mitad_exterior - desplazamiento_llave - 10, centro_y - 10, 20, 20),          # Anillo exterior lado derecho
            pygame.Rect(centro_x - 10, centro_y - mitad_exterior + desplazamiento_llave - 10, 20, 20),          # Anillo exterior parte superior
            pygame.Rect(centro_x - mitad_exterior + desplazamiento_llave - 10, centro_y + 30, 20, 20),          # Anillo exterior lado izquierdo inferior
        ]
        self.llaves_requeridas = 3

        # === SPAWNS DE ENEMIGOS (distribuidos por anillos) ===
        self.spawn_enemigos = []
        # Añadir spawns en diferentes anillos
        for radio_anillo in range(numero_anillos):
            mitad_anillo_actual = mitad_interior + radio_anillo * (ancho_pasillo + grosor_muro)
            if radio_anillo % 2 == 0:
                # posiciones cardinales
                self.spawn_enemigos.append((centro_x + mitad_anillo_actual - desplazamiento_llave, centro_y))
                self.spawn_enemigos.append((centro_x - mitad_anillo_actual + desplazamiento_llave, centro_y))
            else:
                self.spawn_enemigos.append((centro_x, centro_y + mitad_anillo_actual - desplazamiento_llave))
                self.spawn_enemigos.append((centro_x, centro_y - mitad_anillo_actual + desplazamiento_llave))
        # Limitar cantidad razonable
        self.spawn_enemigos = self.spawn_enemigos[:10]

    def crear_nivel_2(self):
        """Nivel 2: laberinto con forma de espiral hacia el centro"""
        # Cargar desde archivo TXT si existe
        if self._cargar_nivel_desde_txt(2):
            return
        # bordes del mapa
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))
        
        # === DISEÑO RADIAL: rayos + anillos parciales ===
        centro_x, centro_y = self.ancho // 2, self.alto // 2
        grosor_muro = 30
        ancho_pasillo = 120
        ancho_hueco = 160

        def dividir_horizontal(x_inicio, x_fin, y_posicion, centro_hueco=None):
            if centro_hueco is None:
                self.muros.append(pared(x_inicio, y_posicion, x_fin - x_inicio, grosor_muro))
            else:
                hueco_izquierda = max(x_inicio, int(centro_hueco - ancho_hueco // 2))
                hueco_derecha = min(x_fin, int(centro_hueco + ancho_hueco // 2))
                if hueco_izquierda > x_inicio:
                    self.muros.append(pared(x_inicio, y_posicion, hueco_izquierda - x_inicio, grosor_muro))
                if x_fin > hueco_derecha:
                    self.muros.append(pared(hueco_derecha, y_posicion, x_fin - hueco_derecha, grosor_muro))

        def dividir_vertical(y_inicio, y_fin, x_posicion, centro_hueco=None):
            if centro_hueco is None:
                self.muros.append(pared(x_posicion, y_inicio, grosor_muro, y_fin - y_inicio))
            else:
                hueco_arriba = max(y_inicio, int(centro_hueco - ancho_hueco // 2))
                hueco_abajo = min(y_fin, int(centro_hueco + ancho_hueco // 2))
                if hueco_arriba > y_inicio:
                    self.muros.append(pared(x_posicion, y_inicio, grosor_muro, hueco_arriba - y_inicio))
                if y_fin > hueco_abajo:
                    self.muros.append(pared(x_posicion, hueco_abajo, grosor_muro, y_fin - hueco_abajo))

        # Anillos parciales (tres "círculos" cuadrados con aberturas alternadas)
        mitad_interior = 200
        for indice_anillo in range(3):
            mitad_anillo = mitad_interior + indice_anillo * (ancho_pasillo + grosor_muro)
            borde_izquierdo, borde_derecho = centro_x - mitad_anillo, centro_x + mitad_anillo
            borde_superior, borde_inferior = centro_y - mitad_anillo, centro_y + mitad_anillo
            # Top con hueco centrado
            dividir_horizontal(borde_izquierdo, borde_derecho, borde_superior - grosor_muro, centro_hueco=centro_x if indice_anillo % 2 == 0 else None)
            # Bottom con hueco alternado
            dividir_horizontal(borde_izquierdo, borde_derecho, borde_inferior, centro_hueco=None if indice_anillo % 2 == 0 else centro_x)
            # Left con hueco alternado vertical
            dividir_vertical(borde_superior, borde_inferior, borde_izquierdo - grosor_muro, centro_hueco=None if indice_anillo % 2 == 0 else centro_y)
            # Right con hueco vertical alternado
            dividir_vertical(borde_superior, borde_inferior, borde_derecho, centro_hueco=centro_y if indice_anillo % 2 == 0 else None)

        # Rayos (pasillos radiales) formando una rosa de 8 direcciones con cortes
        radio_interno = mitad_interior - ancho_pasillo // 2
        radio_externo = mitad_interior + 2 * (ancho_pasillo + grosor_muro)
        # Horizontal
        self.muros.append(pared(centro_x - radio_externo, centro_y - grosor_muro//2, radio_externo - radio_interno, grosor_muro))  # izquierda
        self.muros.append(pared(centro_x + radio_interno, centro_y - grosor_muro//2, radio_externo - radio_interno, grosor_muro))  # derecha
        # Vertical
        self.muros.append(pared(centro_x - grosor_muro//2, centro_y - radio_externo, grosor_muro, radio_externo - radio_interno))  # arriba
        self.muros.append(pared(centro_x - grosor_muro//2, centro_y + radio_interno, grosor_muro, radio_externo - radio_interno))  # abajo
        # Diagonales (aproximadas con bloques escalonados)
        tamano_paso = 100
        for distancia in range(radio_interno + tamano_paso, radio_externo, tamano_paso):
            desplazamiento_diagonal = int(distancia * 0.7)
            # up-left
            self.muros.append(pared(centro_x - desplazamiento_diagonal - 40, centro_y - distancia, 80, grosor_muro))
            self.muros.append(pared(centro_x - distancia, centro_y - desplazamiento_diagonal - 40, grosor_muro, 80))
            # up-right
            self.muros.append(pared(centro_x + desplazamiento_diagonal - 40, centro_y - distancia, 80, grosor_muro))
            self.muros.append(pared(centro_x + distancia, centro_y - desplazamiento_diagonal - 40, grosor_muro, 80))
            # down-left
            self.muros.append(pared(centro_x - desplazamiento_diagonal - 40, centro_y + distancia, 80, grosor_muro))
            self.muros.append(pared(centro_x - distancia, centro_y + desplazamiento_diagonal - 40, grosor_muro, 80))
            # down-right
            self.muros.append(pared(centro_x + desplazamiento_diagonal - 40, centro_y + distancia, 80, grosor_muro))
            self.muros.append(pared(centro_x + distancia, centro_y + desplazamiento_diagonal - 40, grosor_muro, 80))

        # === LLAVES (4) en cuadrantes distintos ===
        desplazamiento_llave = mitad_interior + ancho_pasillo
        self.llaves = [
            pygame.Rect(centro_x + desplazamiento_llave, centro_y - 10, 20, 20),         # Este
            pygame.Rect(centro_x - desplazamiento_llave - 20, centro_y - 10, 20, 20),    # Oeste
            pygame.Rect(centro_x - 10, centro_y - desplazamiento_llave - 20, 20, 20),    # Norte
            pygame.Rect(centro_x - 10, centro_y + desplazamiento_llave, 20, 20),         # Sur
        ]
        self.llaves_requeridas = 4

        # === SALIDA (cercana al centro) ===
        self.salida = salida(centro_x - 40, centro_y - 40)

        # Spawns distribuidos en anillos
        self.spawn_enemigos = [
            (centro_x + desplazamiento_llave + 150, centro_y), (centro_x - desplazamiento_llave - 150, centro_y),
            (centro_x, centro_y + desplazamiento_llave + 150), (centro_x, centro_y - desplazamiento_llave - 150),
            (centro_x + 300, centro_y + 300), (centro_x - 300, centro_y + 300),
            (centro_x + 300, centro_y - 300), (centro_x - 300, centro_y - 300)
        ]

    def crear_nivel_3(self):
        """Nivel 3: laberinto más caótico con muchas rutas"""
        # Cargar desde archivo TXT si existe
        if self._cargar_nivel_desde_txt(3):
            return
        # bordes del mapa
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))
        
        # === DISEÑO EN ZIG-ZAG POR CAPAS (con loops) ===
        grosor_muro = 30
        ancho_pasillo = 120
        margen_borde = 120
        # Tres bandas horizontales principales separadas por pasillos anchos
        # Bandas: superior, media, inferior con cortes de zig-zag que se alternan
        # Superior
        self.muros.append(pared(margen_borde, 200, 500, grosor_muro))
        self.muros.append(pared(800, 200, 400, grosor_muro))
        self.muros.append(pared(1300, 200, 500, grosor_muro))
        # Media (desfasada)
        self.muros.append(pared(300, 600, 400, grosor_muro))
        self.muros.append(pared(800, 600, 400, grosor_muro))
        self.muros.append(pared(1300, 600, 400, grosor_muro))
        # Inferior
        self.muros.append(pared(margen_borde, 1000, 500, grosor_muro))
        self.muros.append(pared(800, 1000, 400, grosor_muro))
        self.muros.append(pared(1300, 1000, 500, grosor_muro))

        # Conectores verticales que crean el zig-zag y loops entre bandas
        self.muros.append(pared(700, 200, grosor_muro, 350))   # baja desde superior a media
        self.muros.append(pared(1200, 200, grosor_muro, 350))  # baja desde superior a media
        self.muros.append(pared(500, 600, grosor_muro, 350))   # baja desde media a inferior
        self.muros.append(pared(1000, 600, grosor_muro, 350))  # baja desde media a inferior
        self.muros.append(pared(1500, 600, grosor_muro, 350))  # baja desde media a inferior

        # Barreras internas para estrechar decisiones sin cerrar espacios
        self.muros.append(pared(250, 350, 200, grosor_muro))
        self.muros.append(pared(1550, 350, 200, grosor_muro))
        self.muros.append(pared(250, 850, 200, grosor_muro))
        self.muros.append(pared(1550, 850, 200, grosor_muro))

        # Grandes pilares que funcionan como esquinas suaves
        self.muros.append(pared(600, 300, grosor_muro, 200))
        self.muros.append(pared(1400, 300, grosor_muro, 200))
        self.muros.append(pared(600, 700, grosor_muro, 200))
        self.muros.append(pared(1400, 700, grosor_muro, 200))

        # Cierre parcial inferior derecha para forzar recorrido hacia la salida
        self.muros.append(pared(1600, 1150, 250, grosor_muro))
        self.muros.append(pared(1850, 800, grosor_muro, 350))

        # === LLAVES (5) colocadas en rutas distintas ===
        self.llaves = [
            pygame.Rect(400, 250, 20, 20),     # banda superior izq
            pygame.Rect(1450, 250, 20, 20),    # banda superior der
            pygame.Rect(600, 650, 20, 20),     # conector media
            pygame.Rect(1100, 1050, 20, 20),   # banda inferior centro
            pygame.Rect(1800, 900, 20, 20),    # cierre inferior der
        ]
        self.llaves_requeridas = 5

        # === SALIDA (abajo-derecha, tras recoger 5 llaves) ===
        self.salida = salida(1800, 1350)

        # Spawns distribuidos por capas
        self.spawn_enemigos = [
            (300, 300), (900, 250), (1650, 300),
            (350, 700), (1000, 700), (1550, 700),
            (350, 1100), (900, 1100), (1650, 1100)
        ]

    def obtener_spawn_jugador_seguro(self, tamaño_jugador=30):
        """Encuentra una posición inicial válida para el jugador.

        Esta función intenta varias veces generar una posición aleatoria dentro
        del mapa que cumpla las siguientes condiciones:

        - No colisionar con muros ni estar demasiado cerca de ellos.
        - No comenzar demasiado cerca de la salida.
        - No situarse en las inmediaciones de los puntos de spawn de enemigos.
        - Evitar colocar al jugador encima de llaves.

        Si tras varios intentos no se encuentra una posición adecuada, la función
        recorre una cuadrícula de posiciones cerca del origen del mapa hasta
        localizar un hueco. Como último recurso devuelve una posición por defecto.
        """
        margen = 50  # margen mínimo desde los bordes del mapa
        radio_seguridad = 200  # distancia mínima a spawns de enemigos
        max_intentos = 100

        # Precalcular rectángulos de muros para acelerar las colisiones
        muros_rects = [m.rect for m in self.muros]

        for _ in range(max_intentos):
            # Genera posición aleatoria dentro de los límites seguros
            x = random.randint(margen, self.ancho - margen - tamaño_jugador)
            y = random.randint(margen, self.alto - margen - tamaño_jugador)
            jugador_rect = pygame.Rect(x, y, tamaño_jugador, tamaño_jugador)
            area_seguridad = jugador_rect.inflate(20, 20)

            # Colisión con muros
            if any(area_seguridad.colliderect(muro) for muro in muros_rects):
                continue

            # Cercanía a la salida
            if self.salida and jugador_rect.inflate(100, 100).colliderect(self.salida.rect):
                continue

            # Cercanía a spawns de enemigos
            muy_cerca_enemigo = False
            for ex, ey in self.spawn_enemigos:
                distancia = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                if distancia < radio_seguridad:
                    muy_cerca_enemigo = True
                    break
            if muy_cerca_enemigo:
                continue

            # Cercanía a llaves
            muy_cerca_llave = False
            for llave_rect in getattr(self, "llaves", []):
                if jugador_rect.inflate(80, 80).colliderect(llave_rect):
                    muy_cerca_llave = True
                    break
            if muy_cerca_llave:
                continue

            # Posición válida encontrada
            return (x, y)

        # Si no se encuentra en los intentos aleatorios, probar posiciones en una rejilla
        for y in range(50, 500, 50):
            for x in range(50, 500, 50):
                jugador_rect = pygame.Rect(x, y, tamaño_jugador, tamaño_jugador)
                area_seguridad = jugador_rect.inflate(20, 20)
                if any(area_seguridad.colliderect(muro) for muro in muros_rects):
                    continue
                return (x, y)

        # Última opción: devolver posición por defecto
        return (100, 100)

    def dibujar(self, ventana, camara):
        # dibuja el suelo: usa una superficie pre-renderizada si está disponible
        if hasattr(self, 'surface_suelo') and self.surface_suelo:
            # Calcular el área visible del mundo según la cámara
            ancho_pantalla, alto_pantalla = ventana.get_size()
            vis_mundo_ancho = ancho_pantalla / camara.zoom
            vis_mundo_alto = alto_pantalla / camara.zoom
            
            # Área visible en coordenadas del mundo
            area_visible_mundo = pygame.Rect(
                int(camara.offset_x),
                int(camara.offset_y),
                int(vis_mundo_ancho),
                int(vis_mundo_alto)
            )
            
            # Asegurar que el área visible esté dentro de los límites del mapa
            area_visible_mundo.x = max(0, min(area_visible_mundo.x, self.ancho - area_visible_mundo.width))
            area_visible_mundo.y = max(0, min(area_visible_mundo.y, self.alto - area_visible_mundo.height))
            area_visible_mundo.width = min(area_visible_mundo.width, self.ancho - area_visible_mundo.x)
            area_visible_mundo.height = min(area_visible_mundo.height, self.alto - area_visible_mundo.y)
            
            # Extraer la porción visible del suelo y escalarla al tamaño del área de juego
            try:
                porcion_suelo = self.surface_suelo.subsurface(area_visible_mundo)
                # Escalar al tamaño completo del área de juego para cubrir toda la pantalla
                porcion_escalada = pygame.transform.scale(porcion_suelo, (ancho_pantalla, alto_pantalla))
                # Dibujar en la posición (0, 0) del área de juego
                ventana.blit(porcion_escalada, (0, 0))
            except (ValueError, pygame.error):
                # Si hay error con subsurface (por ejemplo, área fuera de límites), usar fallback
                # Dibujar el suelo completo escalado
                suelo_escalado = pygame.transform.scale(
                    self.surface_suelo,
                    (int(self.ancho * camara.zoom), int(self.alto * camara.zoom))
                )
                rect_pantalla = camara.aplicar(pygame.Rect(0, 0, self.ancho, self.alto))
                ventana.blit(suelo_escalado, (rect_pantalla.x, rect_pantalla.y))
        elif TEXTURA_SUELO:
            # Fallback: recorre el área total del nivel y repite la textura
            tex_w, tex_h = TEXTURA_SUELO.get_width(), TEXTURA_SUELO.get_height()
            # Calcular el área visible para optimizar el dibujado
            ancho_pantalla, alto_pantalla = ventana.get_size()
            vis_mundo_ancho = ancho_pantalla / camara.zoom
            vis_mundo_alto = alto_pantalla / camara.zoom
            
            # Rango de texturas a dibujar (solo las visibles)
            inicio_x = max(0, int((camara.offset_x - tex_w) // tex_w) * tex_w)
            fin_x = min(self.ancho, int((camara.offset_x + vis_mundo_ancho + tex_w) // tex_w) * tex_w)
            inicio_y = max(0, int((camara.offset_y - tex_h) // tex_h) * tex_h)
            fin_y = min(self.alto, int((camara.offset_y + vis_mundo_alto + tex_h) // tex_h) * tex_h)
            
            for xx in range(inicio_x, fin_x, tex_w):
                for yy in range(inicio_y, fin_y, tex_h):
                    rect = pygame.Rect(xx, yy, tex_w, tex_h)
                    ventana.blit(TEXTURA_SUELO, camara.aplicar(rect))
        else:
            # Si no hay textura, rellena con un color oscuro
            area_total = pygame.Rect(0, 0, self.ancho, self.alto)
            rect_pantalla = camara.aplicar(area_total)
            ventana.fill((20, 20, 20), rect_pantalla)

        # dibuja muros
        for muro in self.muros:
            muro.dibujar(ventana, camara)

        # dibuja salida
        # la salida se colorea diferente si aún hay llaves pendientes
        bloqueada = False
        if hasattr(self, "llaves_requeridas"):
            bloqueada = len(self.llaves) > 0
        self.salida.dibujar(ventana, camara, bloqueada=bloqueada)

        # dibuja llaves
        for r in getattr(self, "llaves", []):
            rp = camara.aplicar(r)
            # Si hay un icono de llave definido a nivel de módulo, usarlo y escalarlo al tamaño de la celda
            if ICONO_LLAVE:
                # Escalar el icono a las dimensiones de la celda
                try:
                    icono_escalado = pygame.transform.smoothscale(ICONO_LLAVE, (rp.w, rp.h))
                    ventana.blit(icono_escalado, (rp.x, rp.y))
                except Exception:
                    pygame.draw.rect(ventana, (240, 220, 40), rp)
                    pygame.draw.rect(ventana, (255, 255, 120), rp, 2)
            else:
                # Fallback: rectángulo visible
                pygame.draw.rect(ventana, (240, 220, 40), rp)
                pygame.draw.rect(ventana, (255, 255, 120), rp, 2)

    def _crear_surface_suelo(self):
        """Pre-renderiza el suelo en una superficie del tamaño del mapa.
        Esto evita huecos entre teselas al aplicar zoom.
        """
        global TEXTURA_SUELO
        try:
            # Si existe una textura de suelo, crear una superficie grande y repetir la textura
            if TEXTURA_SUELO:
                self.surface_suelo = pygame.Surface((self.ancho, self.alto))
                tex_w, tex_h = TEXTURA_SUELO.get_width(), TEXTURA_SUELO.get_height()
                for xx in range(0, self.ancho, tex_w):
                    for yy in range(0, self.alto, tex_h):
                        self.surface_suelo.blit(TEXTURA_SUELO, (xx, yy))
            else:
                self.surface_suelo = None
        except Exception:
            self.surface_suelo = None

    # ------------------------------------------------------------
    # Métodos auxiliares para generación procedural
    def _idx(self, posicion_x, posicion_y, numero_columnas, numero_filas):
        """Devuelve True si la posición (posicion_x, posicion_y) está dentro de los límites."""
        return 0 <= posicion_x < numero_columnas and 0 <= posicion_y < numero_filas

    def _vecinos_cardinales(self, posicion_x, posicion_y, numero_columnas, numero_filas):
        """Genera las celdas vecinas en las direcciones arriba, abajo, izquierda, derecha."""
        for desplazamiento_x, desplazamiento_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vecino_x, vecino_y = posicion_x + desplazamiento_x, posicion_y + desplazamiento_y
            if self._idx(vecino_x, vecino_y, numero_columnas, numero_filas):
                yield (vecino_x, vecino_y)

    def _generar_laberinto_por_celdas(self, numero_columnas, numero_filas):
        """Genera un laberinto perfecto mediante un algoritmo DFS (backtracker).

        Devuelve un diccionario `celdas` donde cada clave es una tupla (x, y) y su
        valor es el conjunto de celdas vecinas conectadas (sin muro). También
        devuelve un conjunto `paredes` con todas las paredes entre celdas no
        conectadas.
        """
        celdas_visitadas = set()
        pila_celdas = [(0, 0)]
        celdas_visitadas.add((0, 0))
        celdas_conectadas = {(0, 0): set()}
        conjunto_paredes = set()
        while pila_celdas:
            celda_x, celda_y = pila_celdas[-1]
            # elige vecinos no visitados
            vecinos_no_visitados = [(vecino_x, vecino_y) for (vecino_x, vecino_y) in self._vecinos_cardinales(celda_x, celda_y, numero_columnas, numero_filas) if (vecino_x, vecino_y) not in celdas_visitadas]
            if vecinos_no_visitados:
                siguiente_x, siguiente_y = random.choice(vecinos_no_visitados)
                celdas_visitadas.add((siguiente_x, siguiente_y))
                pila_celdas.append((siguiente_x, siguiente_y))
                # conecta ambos lados
                celdas_conectadas.setdefault((celda_x, celda_y), set()).add((siguiente_x, siguiente_y))
                celdas_conectadas.setdefault((siguiente_x, siguiente_y), set()).add((celda_x, celda_y))
            else:
                pila_celdas.pop()
        # genera paredes entre pares no conectados (almacenando cada una solo una vez)
        for fila in range(numero_filas):
            for columna in range(numero_columnas):
                for vecino_x, vecino_y in self._vecinos_cardinales(columna, fila, numero_columnas, numero_filas):
                    if (vecino_x, vecino_y) not in celdas_conectadas.get((columna, fila), set()):
                        # orienta la tupla para evitar duplicados
                        if (columna, fila, vecino_x, vecino_y) < (vecino_x, vecino_y, columna, fila):
                            conjunto_paredes.add((columna, fila, vecino_x, vecino_y))
        return celdas_conectadas, conjunto_paredes

    def _levantar_paredes_de_celdas(self, paredes, tam, esp):
        """Convierte cada pared entre celdas en un objeto `pared` (rectángulo).

        La posición se calcula a partir del tamaño de las celdas (`tam`) y
        del grosor del muro (`esp`). Los muros se insertan en la lista
        `self.muros`.
        """
        for (x, y, nx, ny) in paredes:
            if x == nx:
                # muro horizontal entre filas (vertical en orientación)
                miny = min(y, ny)
                rx = 20 + x * tam
                ry = 20 + (miny + 1) * tam - esp // 2
                self.muros.append(pared(rx, ry, tam, esp))
            else:
                # muro vertical entre columnas (horizontal en orientación)
                minx = min(x, nx)
                rx = 20 + (minx + 1) * tam - esp // 2
                ry = 20 + y * tam
                self.muros.append(pared(rx, ry, esp, tam))

    def _romper_paredes_aleatorias(self, paredes, cols, filas, cantidad, tam, esp):
        """Elimina `cantidad` de muros de la lista de muros para crear rutas alternativas.

        Se basa en las posiciones de `self.muros` para identificar el rectángulo
        asociado a la pared dentro del mapa generado.
        """
        paredes_lista = list(paredes)
        random.shuffle(paredes_lista)
        rotas = 0
        i = 0
        while rotas < cantidad and i < len(paredes_lista):
            (x, y, nx, ny) = paredes_lista[i]
            i += 1
            # calcula la posición del muro en coordenadas de mapa
            if x == nx:
                rx = 20 + x * tam
                ry = 20 + (min(y, ny) + 1) * tam - esp // 2
                w, h = tam, esp
            else:
                rx = 20 + (min(x, nx) + 1) * tam - esp // 2
                ry = 20 + y * tam
                w, h = esp, tam
            # busca ese muro en la lista y lo elimina
            for m in list(self.muros):
                if m.rect.x == rx and m.rect.y == ry and m.rect.w == w and m.rect.h == h:
                    self.muros.remove(m)
                    rotas += 1
                    break

    def _dist_bfs(self, origen, celdas, cols, filas):
        """Calcula distancias mínimas desde `origen` a todas las celdas mediante BFS."""
        from collections import deque
        q = deque([origen])
        dist = {origen: 0}
        while q:
            u = q.popleft()
            for v in celdas.get(u, []):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    def _celda_mas_lejana_desde(self, origen, celdas, cols, filas):
        """Devuelve la celda más alejada (mayor distancia BFS) desde `origen`."""
        dist = self._dist_bfs(origen, celdas, cols, filas)
        return max(dist, key=dist.get)

    def _spawns_distribuidos(self, celdas, cols, filas, tam, cuantos=8):
        """Elige celdas espaciadas para spawns evitando que queden muy cerca unas de otras."""
        todas = list(celdas.keys())
        random.shuffle(todas)
        elegidas = []
        for c in todas:
            # evita colocar spawn demasiado cerca de otros (distancia Manhattan >= 6)
            if all(abs(c[0] - e[0]) + abs(c[1] - e[1]) >= 6 for e in elegidas):
                elegidas.append(c)
                if len(elegidas) >= cuantos:
                    break
        pts = []
        for cx, cy in elegidas:
            px = 20 + cx * tam + tam // 2
            py = 20 + cy * tam + tam // 2
            pts.append((px, py))
        return pts

    def _crear_habitaciones(self, celdas, paredes, cols, filas, num_habitaciones=4):
        """Genera habitaciones de 3×3 celdas uniendo completamente sus paredes.

        Selecciona `num_habitaciones` posiciones al azar (sin acercarse al borde) y
        elimina los muros internos que separan las celdas dentro de ese bloque.
        Esto crea espacios amplios similares a cavernas. Además, las celdas se
        conectan en el grafo `celdas` y las paredes correspondientes se eliminan
        del conjunto `paredes`.
        """
        for _ in range(num_habitaciones):
            # elige la esquina superior izquierda de la habitación dentro de los límites
            cx = random.randint(1, max(1, cols - 3))
            cy = random.randint(1, max(1, filas - 3))
            # recorre las celdas dentro del bloque 3×3
            for dx in range(3):
                for dy in range(3):
                    # conecta con la celda de la derecha
                    if dx < 2:
                        a = (cx + dx, cy + dy)
                        b = (cx + dx + 1, cy + dy)
                        if b not in celdas.get(a, set()):
                            celdas.setdefault(a, set()).add(b)
                            celdas.setdefault(b, set()).add(a)
                            # elimina la pared entre ambas celdas, si existe
                            if (a[0], a[1], b[0], b[1]) in paredes:
                                paredes.discard((a[0], a[1], b[0], b[1]))
                            elif (b[0], b[1], a[0], a[1]) in paredes:
                                paredes.discard((b[0], b[1], a[0], a[1]))
                    # conecta con la celda de abajo
                    if dy < 2:
                        a = (cx + dx, cy + dy)
                        b = (cx + dx, cy + dy + 1)
                        if b not in celdas.get(a, set()):
                            celdas.setdefault(a, set()).add(b)
                            celdas.setdefault(b, set()).add(a)
                            if (a[0], a[1], b[0], b[1]) in paredes:
                                paredes.discard((a[0], a[1], b[0], b[1]))
                            elif (b[0], b[1], a[0], a[1]) in paredes:
                                paredes.discard((b[0], b[1], a[0], a[1]))