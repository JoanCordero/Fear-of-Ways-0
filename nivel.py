import pygame
import random
import os
from pared import pared
from salida import salida

# Carga opcional de un icono de llave desde el código principal.
# Este icono se dibujará sobre las llaves en el mapa si está definido.
ICONO_LLAVE = None

# La textura se asignará desde main.py después de inicializar pygame
TEXTURA_SUELO = None  # Valor inicial, será reemplazado

class nivel:
    """Define un nivel con su laberinto, enemigos, salida y escondites"""
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
        self.escondites = []  # zonas seguras donde el jugador puede ocultarse

        # dimensiones generales del mapa (más grandes que la pantalla)
        self.ancho = 2000
        self.alto = 1500

        # generar estructura del nivel y escondites
        self.crear_nivel()
        # una vez creado el nivel, pre-renderizar el suelo a una superficie grande
        # Esto evita artefactos de bordes y garantiza que el suelo cubra todo el laberinto.
        self._crear_surface_suelo()
        self.generar_escondites_random(cantidad=random.randint(3, 5))
        
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

    def crear_nivel_1(self):
        """Nivel 1: Genera un laberinto procedural con habitaciones estilo cueva,
        llaves repartidas, una puerta controlada por palanca y spawns distribuidos.

        Este método reemplaza el diseño estático anterior por un algoritmo basado
        en celdas conectadas. Se construye una grilla (cols × filas) donde cada
        celda se convierte en un bloque de pasillo de tamaño `tam`. Las paredes
        exteriores delimitan el área jugable. Utiliza un backtracker DFS para
        generar un laberinto perfecto y luego rompe aleatoriamente algunas
        paredes (carving extra) para crear ciclos y ampliar espacios. Además,
        se crean varias “habitaciones” cuadradas que generan espacios amplios
        tipo cueva al unir grupos de 3×3 celdas.
        """
        # bordes del mapa (marco perimetral)
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # parámetros del laberinto
        # Se reduce el número de celdas y se incrementa el tamaño de cada celda para
        # incrementar el espacio libre entre muros. Con estas dimensiones el
        # laberinto ocupa menos celdas pero cada una es más grande.
        # Ajustar el tamaño de las celdas y el espesor de los muros para dar la sensación
        # de un mapa más amplio. Se mantiene el mismo tamaño general del laberinto,
        # pero aumentando el grosor de los muros y disminuyendo ligeramente el
        # espacio libre por celda. Esto produce pasillos más estrechos y muros más gruesos
        # sin cambiar la disposición global de celdas.
        cols, filas = 16, 12          # número de columnas y filas de celdas
        tam = 100                    # tamaño de cada celda (incluye pasillo)
        # Aumentar grosor de los muros: 40 en lugar de 20. De esta forma el laberinto
        # ocupa la misma anchura total, pero los muros se perciben más gruesos.
        esp = 40                     # grosor de los muros entre celdas
        carving_extra = 0.35         # proporción de muros derribados extra para formar ciclos

        # genera la topología inicial del laberinto (celdas conectadas y paredes que las separan)
        celdas, paredes = self._generar_laberinto_por_celdas(cols, filas)

        # crea habitaciones amplias: selecciona varias regiones 3×3 para unirlas completamente
        self._crear_habitaciones(celdas, paredes, cols, filas, num_habitaciones=max(4, (cols * filas) // 60))

        # levanta físicamente las paredes en la lista de muros
        self._levantar_paredes_de_celdas(paredes, tam, esp)

        # carving extra: elimina muros adicionales al azar para abrir más rutas
        self._romper_paredes_aleatorias(paredes, cols, filas,
                                        cantidad=int(cols * filas * carving_extra),
                                        tam=tam, esp=esp)

        # determina celda de inicio y celda final (más alejada desde el origen)
        start = (0, 0)
        fin = self._celda_mas_lejana_desde(start, celdas, cols, filas)
        sx, sy = fin
        # coloca la salida en el centro de la celda final
        self.salida = salida(20 + sx * tam + tam // 2, 20 + sy * tam + tam // 2)

        # genera puntos de spawn de enemigos distribuidos en el laberinto
        self.spawn_enemigos = self._spawns_distribuidos(celdas, cols, filas, tam, cuantos=9)

        # coloca llaves en algunos callejones sin salida distintos de la salida
        dead_ends = [c for c in celdas if len(celdas[c]) == 1 and c != fin]
        random.shuffle(dead_ends)
        self.llaves = []
        # número de llaves: al menos 3 y al máximo 4 o proporción de dead ends
        self.llaves_requeridas = min(4, max(3, len(dead_ends) // 6))
        for i in range(self.llaves_requeridas):
            cx, cy = dead_ends[i]
            rx = 20 + cx * tam + tam // 2 - 10
            ry = 20 + cy * tam + tam // 2 - 10
            self.llaves.append(pygame.Rect(rx, ry, 20, 20))

        # prepara puertas y palancas
        self.palancas = []
        self._puertas_por_id = {}
        # elige un cuello de botella en el grafo y coloca una puerta entre esas dos celdas
        cuello = self._elige_cuello_bottleneck(celdas, cols, filas)
        if cuello:
            a, b = cuello
            self._colocar_puerta_entre(a, b, tam, esp, puerta_id="A1")
            # coloca la palanca en la celda más lejana desde b
            px, py = self._celda_mas_lejana_desde(b, celdas, cols, filas)
            prx = 20 + px * tam + tam // 2 - 12
            pry = 20 + py * tam + tam // 2 - 12
            self.palancas.append(pygame.Rect(prx, pry, 24, 24))

    def crear_nivel_2(self):
        """Nivel 2: laberinto con forma de espiral hacia el centro"""
        # bordes del mapa
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # capas de la espiral y obstáculos centrales
        self.muros.append(pared(150, 150, 1700, 20))
        self.muros.append(pared(1830, 170, 20, 1200))
        self.muros.append(pared(200, 1350, 1650, 20))
        self.muros.append(pared(200, 250, 20, 1120))
        self.muros.append(pared(350, 250, 1330, 20))
        self.muros.append(pared(1660, 270, 20, 950))
        self.muros.append(pared(400, 1200, 1280, 20))
        self.muros.append(pared(400, 370, 20, 850))
        self.muros.append(pared(550, 370, 970, 20))
        self.muros.append(pared(1500, 390, 20, 690))
        self.muros.append(pared(600, 1060, 920, 20))
        self.muros.append(pared(600, 490, 20, 590))
        self.muros.append(pared(750, 550, 600, 20))
        self.muros.append(pared(1330, 570, 20, 380))
        self.muros.append(pared(800, 930, 550, 20))
        self.muros.append(pared(800, 650, 20, 300))
        self.muros.append(pared(950, 700, 200, 20))
        self.muros.append(pared(1000, 800, 150, 20))

        # salida
        posiciones_salida = [(1000, 750), (250, 200), (1800, 1300),
                             (450, 1250), (1600, 450), (700, 600)]
        x, y = random.choice(posiciones_salida)
        self.salida = salida(x, y)

        # enemigos
        self.spawn_enemigos = [
            (250, 200), (1700, 300), (300, 1300),
            (500, 320), (1550, 600), (650, 1100),
            (900, 600), (1200, 800), (1100, 450)
        ]

    def crear_nivel_3(self):
        """Nivel 3: laberinto más caótico con muchas rutas"""
        # bordes del mapa
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # secciones interconectadas (izquierda, centro, derecha)
        self.muros.append(pared(150, 100, 20, 400))
        self.muros.append(pared(170, 480, 300, 20))
        self.muros.append(pared(300, 200, 20, 300))
        self.muros.append(pared(320, 200, 200, 20))
        self.muros.append(pared(500, 100, 20, 600))
        self.muros.append(pared(700, 150, 20, 500))
        self.muros.append(pared(550, 630, 170, 20))
        self.muros.append(pared(850, 250, 300, 20))
        self.muros.append(pared(1130, 100, 20, 400))
        self.muros.append(pared(900, 480, 250, 20))
        self.muros.append(pared(200, 700, 400, 20))
        self.muros.append(pared(200, 720, 20, 400))
        self.muros.append(pared(220, 1100, 500, 20))
        self.muros.append(pared(700, 800, 20, 320))
        self.muros.append(pared(1300, 200, 20, 400))
        self.muros.append(pared(1320, 580, 400, 20))
        self.muros.append(pared(1500, 300, 220, 20))
        self.muros.append(pared(1700, 100, 20, 500))
        self.muros.append(pared(900, 750, 300, 20))
        self.muros.append(pared(1180, 650, 20, 400))
        self.muros.append(pared(1200, 1030, 400, 20))
        self.muros.append(pared(1400, 850, 20, 200))
        self.muros.append(pared(1550, 700, 20, 400))
        self.muros.append(pared(350, 900, 150, 20))
        self.muros.append(pared(850, 1000, 200, 20))
        self.muros.append(pared(1300, 1200, 250, 20))
        self.muros.append(pared(600, 350, 80, 20))
        self.muros.append(pared(1450, 450, 100, 20))
        self.muros.append(pared(1650, 1100, 20, 300))
        self.muros.append(pared(1670, 1380, 250, 20))

        # salida
        posiciones_salida = [(1900, 1420), (100, 100), (1850, 200),
                             (350, 1350), (1250, 1300), (850, 1150), (1550, 950)]
        x, y = random.choice(posiciones_salida)
        self.salida = salida(x, y)

        # enemigos
        self.spawn_enemigos = [
            (200, 250), (400, 350), (250, 850), (550, 550),
            (650, 300), (950, 350), (1050, 200), (850, 900),
            (1100, 850), (1250, 350), (1600, 350), (1450, 950),
            (1300, 1250), (1750, 1200)
        ]

    def generar_escondites_random(self, cantidad=3, tam=(140, 100), margen=30, intentos_max=400):
        """Crea zonas seguras aleatorias evitando muros, salida y spawns"""
        w, h = tam
        self.escondites = []
        muros_rects = [m.rect for m in self.muros]
        salida_rect = self.salida.rect if self.salida else None

        # verifica si choca con muros
        def choca_con_muros(r):
            inflados = [m.inflate(margen * 2, margen * 2) for m in muros_rects]
            return any(r.colliderect(mr) for mr in inflados)

        # evita cercanía a los puntos de spawn
        def cerca_de_spawns(r, radio=120):
            for sx, sy in self.spawn_enemigos:
                area_spawn = pygame.Rect(sx - radio, sy - radio, radio * 2, radio * 2)
                if r.colliderect(area_spawn):
                    return True
            return False

        intentos = 0
        while len(self.escondites) < cantidad and intentos < intentos_max:
            intentos += 1
            x = random.randint(20, self.ancho - w - 20)
            y = random.randint(20, self.alto - h - 20)
            zona = pygame.Rect(x, y, w, h)

            if choca_con_muros(zona):
                continue
            if salida_rect and zona.inflate(40, 40).colliderect(salida_rect):
                continue
            if any(zona.inflate(20, 20).colliderect(e) for e in self.escondites):
                continue
            if cerca_de_spawns(zona, radio=140):
                continue

            self.escondites.append(zona)

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

        # dibuja zonas seguras semitransparentes
        for r in self.escondites:
            rp = camara.aplicar(r)
            zona = pygame.Surface((rp.w, rp.h), pygame.SRCALPHA)
            zona.fill((30, 120, 180, 90))
            pygame.draw.rect(zona, (220, 240, 255, 140), zona.get_rect(), 2)
            ventana.blit(zona, (rp.x, rp.y))

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

        # dibuja palancas
        for r in getattr(self, "palancas", []):
            rp = camara.aplicar(r)
            pygame.draw.rect(ventana, (60, 140, 255), rp)
            pygame.draw.rect(ventana, (180, 220, 255), rp, 2)

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
    def _idx(self, x, y, cols, filas):
        """Devuelve True si la posición (x, y) está dentro de los límites."""
        return 0 <= x < cols and 0 <= y < filas

    def _vecinos_cardinales(self, x, y, cols, filas):
        """Genera las celdas vecinas en las direcciones arriba, abajo, izquierda, derecha."""
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self._idx(nx, ny, cols, filas):
                yield (nx, ny)

    def _generar_laberinto_por_celdas(self, cols, filas):
        """Genera un laberinto perfecto mediante un algoritmo DFS (backtracker).

        Devuelve un diccionario `celdas` donde cada clave es una tupla (x, y) y su
        valor es el conjunto de celdas vecinas conectadas (sin muro). También
        devuelve un conjunto `paredes` con todas las paredes entre celdas no
        conectadas.
        """
        visit = set()
        stack = [(0, 0)]
        visit.add((0, 0))
        celdas = {(0, 0): set()}
        paredes = set()
        while stack:
            x, y = stack[-1]
            # elige vecinos no visitados
            candidatos = [(nx, ny) for (nx, ny) in self._vecinos_cardinales(x, y, cols, filas) if (nx, ny) not in visit]
            if candidatos:
                nx, ny = random.choice(candidatos)
                visit.add((nx, ny))
                stack.append((nx, ny))
                # conecta ambos lados
                celdas.setdefault((x, y), set()).add((nx, ny))
                celdas.setdefault((nx, ny), set()).add((x, y))
            else:
                stack.pop()
        # genera paredes entre pares no conectados (almacenando cada una solo una vez)
        for y in range(filas):
            for x in range(cols):
                for nx, ny in self._vecinos_cardinales(x, y, cols, filas):
                    if (nx, ny) not in celdas.get((x, y), set()):
                        # orienta la tupla para evitar duplicados
                        if (x, y, nx, ny) < (nx, ny, x, y):
                            paredes.add((x, y, nx, ny))
        return celdas, paredes

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

        Solo considera muros que no son puertas. Se basa en las posiciones de
        `self.muros` para identificar el rectángulo asociado a la pared.
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
            # busca ese muro en la lista y lo elimina si no es puerta
            for m in list(self.muros):
                if m.rect.x == rx and m.rect.y == ry and m.rect.w == w and m.rect.h == h and not getattr(m, "puerta", False):
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

    def _elige_cuello_bottleneck(self, celdas, cols, filas):
        """Selecciona un par de celdas conectadas que forman un cuello de botella.

        Busca aristas entre celdas cuyo grado combinado sea alto (es decir, están
        en una intersección concurrida), de modo que bloquearlas tenga un
        impacto notable en la navegación.
        """
        candidatos = []
        for (x, y), vs in celdas.items():
            for (nx, ny) in vs:
                if (x, y) < (nx, ny):
                    grado = len(vs) + len(celdas.get((nx, ny), []))
                    if grado >= 5:
                        candidatos.append(((x, y), (nx, ny)))
        return random.choice(candidatos) if candidatos else None

    def _colocar_puerta_entre(self, a, b, tam, esp, puerta_id="A1"):
        """Coloca una puerta entre dos celdas adyacentes y la registra por id."""
        (x, y), (nx, ny) = a, b
        if x == nx:
            rx = 20 + x * tam
            ry = 20 + (min(y, ny) + 1) * tam - esp // 2
            w, h = tam, esp
        else:
            rx = 20 + (min(x, nx) + 1) * tam - esp // 2
            ry = 20 + y * tam
            w, h = esp, tam
        p = pared(rx, ry, w, h, puerta=True, abierta=False, id_puerta=puerta_id)
        self.muros.append(p)
        self._puertas_por_id.setdefault(puerta_id, []).append(p)

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