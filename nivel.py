import pygame
import random
import os
from pared import pared
from salida import salida

# La textura se asignará desde main.py después de inicializar pygame
TEXTURA_SUELO = None  # Valor inicial, será reemplazado

class nivel:
    """Define un nivel con su laberinto, enemigos, salida y escondites"""
    def __init__(self, numero):
        # identificación del nivel
        self.numero = numero

        # listas de objetos del mapa
        self.muros = []
        self.salida = None
        self.spawn_enemigos = []
        self.escondites = []  # zonas seguras donde el jugador puede ocultarse

        # dimensiones generales del mapa (ajustadas para mazmorras más densas)
        self.ancho = 1900
        self.alto = 1450

        # generar estructura del nivel y escondites
        self.crear_nivel()
        self.generar_escondites_random(cantidad=random.randint(3, 5))

        self.bonus = [
            {"tipo": "vida", "rect": pygame.Rect(400, 300, 30, 30)},
            {"tipo": "arma", "rect": pygame.Rect(800, 500, 30, 30)},
        ]

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

        # parámetros del laberinto estilo mazmorra
        # Se aumentan las celdas y se reducen sus tamaños para crear pasillos estrechos
        # más laberínticos, similares a una mazmorra clásica
        cols, filas = 28, 21          # número de columnas y filas de celdas (más denso)
        tam = 65                     # tamaño de cada celda más pequeño (pasillos estrechos)
        esp = 18                     # grosor de los muros entre celdas
        carving_extra = 0.45         # más muros derribados para crear ciclos y bifurcaciones

        # genera la topología inicial del laberinto (celdas conectadas y paredes que las separan)
        celdas, paredes = self._generar_laberinto_por_celdas(cols, filas)

        # crea habitaciones amplias estilo caverna: más numerosas y espaciadas
        self._crear_habitaciones(celdas, paredes, cols, filas, num_habitaciones=max(8, (cols * filas) // 50))

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
        """Nivel 2: laberinto con forma de espiral hacia el centro con puertas y palancas"""
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

        # === PUERTAS Y PALANCAS DEL NIVEL 2 ===
        # Puerta 1: Bloquea paso en la espiral exterior (vertical)
        puerta1 = pared(1660, 600, 20, 100, puerta=True, abierta=False, id_puerta="N2_P1")
        self.muros.append(puerta1)
        
        # Puerta 2: Bloquea paso en zona intermedia (horizontal)
        puerta2 = pared(900, 370, 150, 20, puerta=True, abierta=False, id_puerta="N2_P2")
        self.muros.append(puerta2)
        
        # Puerta 3: Bloquea acceso al centro (vertical)
        puerta3 = pared(1000, 700, 20, 100, puerta=True, abierta=False, id_puerta="N2_P3")
        self.muros.append(puerta3)
        
        # Registrar puertas por ID
        self._puertas_por_id = {
            "N2_P1": [puerta1],
            "N2_P2": [puerta2],
            "N2_P3": [puerta3]
        }
        
        # Palancas para controlar las puertas (distribuidas estratégicamente)
        self.palancas = [
            pygame.Rect(1750, 250, 24, 24),   # Palanca para puerta 1 (esquina superior derecha)
            pygame.Rect(450, 450, 24, 24),     # Palanca para puerta 2 (zona izquierda)
            pygame.Rect(1250, 1150, 24, 24)    # Palanca para puerta 3 (zona inferior)
        ]

        # salida en el centro de la espiral
        self.salida = salida(1000, 750)

        # enemigos distribuidos por toda la espiral
        self.spawn_enemigos = [
            (250, 200), (1700, 300), (300, 1300),
            (500, 320), (1550, 600), (650, 1100),
            (900, 600), (1200, 800), (1100, 450),
            (700, 700), (1400, 500), (500, 900)
        ]
        
        # llaves en posiciones estratégicas (más difíciles de alcanzar)
        posiciones_llaves = [
            (1750, 500),   # Zona exterior derecha
            (300, 300),    # Zona exterior izquierda superior
            (450, 1250),   # Zona exterior izquierda inferior
            (850, 750),    # Zona intermedia
            (1250, 400)    # Zona intermedia derecha
        ]
        random.shuffle(posiciones_llaves)
        self.llaves_requeridas = 4  # Aumentado de 3 a 4 para más desafío
        self.llaves = []
        for i in range(self.llaves_requeridas):
            x, y = posiciones_llaves[i]
            self.llaves.append(pygame.Rect(x, y, 20, 20))

    def crear_nivel_3(self):
        """Nivel 3: laberinto caótico con múltiples cámaras, puertas y desafíos"""
        # bordes del mapa
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # secciones interconectadas con diseño más elaborado
        # Zona izquierda - laberinto denso
        self.muros.append(pared(150, 100, 20, 400))
        self.muros.append(pared(170, 480, 300, 20))
        self.muros.append(pared(300, 200, 20, 300))
        self.muros.append(pared(320, 200, 200, 20))
        self.muros.append(pared(200, 700, 400, 20))
        self.muros.append(pared(200, 720, 20, 400))
        self.muros.append(pared(220, 1100, 500, 20))
        self.muros.append(pared(350, 900, 150, 20))
        
        # Zona central - cámaras conectadas
        self.muros.append(pared(500, 100, 20, 600))
        self.muros.append(pared(700, 150, 20, 500))
        self.muros.append(pared(550, 630, 170, 20))
        self.muros.append(pared(700, 800, 20, 320))
        self.muros.append(pared(850, 250, 300, 20))
        self.muros.append(pared(900, 480, 250, 20))
        self.muros.append(pared(900, 750, 300, 20))
        self.muros.append(pared(850, 1000, 200, 20))
        self.muros.append(pared(600, 350, 80, 20))
        
        # Zona derecha - pasajes estrechos
        self.muros.append(pared(1130, 100, 20, 400))
        self.muros.append(pared(1300, 200, 20, 400))
        self.muros.append(pared(1320, 580, 400, 20))
        self.muros.append(pared(1500, 300, 220, 20))
        self.muros.append(pared(1700, 100, 20, 500))
        self.muros.append(pared(1180, 650, 20, 400))
        self.muros.append(pared(1200, 1030, 400, 20))
        self.muros.append(pared(1400, 850, 20, 200))
        self.muros.append(pared(1550, 700, 20, 400))
        self.muros.append(pared(1450, 450, 100, 20))
        self.muros.append(pared(1650, 1100, 20, 300))
        self.muros.append(pared(1670, 1380, 250, 20))
        self.muros.append(pared(1300, 1200, 250, 20))

        # === SISTEMA COMPLEJO DE PUERTAS Y PALANCAS DEL NIVEL 3 ===
        # Puerta 1: Bloquea entrada a zona central (vertical)
        puerta1 = pared(700, 400, 20, 150, puerta=True, abierta=False, id_puerta="N3_P1")
        self.muros.append(puerta1)
        
        # Puerta 2: Bloquea paso horizontal en zona central
        puerta2 = pared(900, 630, 200, 20, puerta=True, abierta=False, id_puerta="N3_P2")
        self.muros.append(puerta2)
        
        # Puerta 3: Bloquea entrada a zona derecha (vertical)
        puerta3 = pared(1130, 250, 20, 150, puerta=True, abierta=False, id_puerta="N3_P3")
        self.muros.append(puerta3)
        
        # Puerta 4: Bloquea acceso a la zona inferior derecha (horizontal)
        puerta4 = pared(1200, 850, 180, 20, puerta=True, abierta=False, id_puerta="N3_P4")
        self.muros.append(puerta4)
        
        # Puerta 5: Pasaje secreto en zona izquierda (horizontal)
        puerta5 = pared(320, 850, 150, 20, puerta=True, abierta=False, id_puerta="N3_P5")
        self.muros.append(puerta5)
        
        # Registrar puertas por ID
        self._puertas_por_id = {
            "N3_P1": [puerta1],
            "N3_P2": [puerta2],
            "N3_P3": [puerta3],
            "N3_P4": [puerta4],
            "N3_P5": [puerta5]
        }
        
        # Palancas distribuidas estratégicamente (una por cada puerta)
        self.palancas = [
            pygame.Rect(350, 350, 24, 24),     # Palanca 1 - zona izquierda superior
            pygame.Rect(650, 900, 24, 24),     # Palanca 2 - zona central inferior
            pygame.Rect(1600, 250, 24, 24),    # Palanca 3 - zona derecha superior
            pygame.Rect(1750, 1250, 24, 24),   # Palanca 4 - zona derecha inferior
            pygame.Rect(250, 1050, 24, 24)     # Palanca 5 - zona izquierda inferior (secreto)
        ]

        # salida en zona difícil de alcanzar (esquina inferior derecha)
        self.salida = salida(1750, 1300)

        # enemigos distribuidos agresivamente
        self.spawn_enemigos = [
            (200, 250), (400, 350), (250, 850), (550, 550),
            (650, 300), (950, 350), (1050, 200), (850, 900),
            (1100, 850), (1250, 350), (1600, 350), (1450, 950),
            (1300, 1250), (1750, 1200), (600, 700), (1000, 500)
        ]
        
        # llaves en las posiciones MÁS difíciles (requiere resolver puzzles de puertas)
        posiciones_llaves = [
            (250, 300),     # Zona inicial
            (600, 450),     # Tras puerta 1
            (1050, 650),    # Zona central tras puerta 2
            (1650, 250),    # Zona derecha tras puerta 3
            (1500, 1200),   # Zona final tras puerta 4
            (400, 1000)     # Zona secreta tras puerta 5
        ]
        random.shuffle(posiciones_llaves)
        self.llaves_requeridas = 5  # Nivel final: 5 llaves
        self.llaves = []
        for i in range(self.llaves_requeridas):
            x, y = posiciones_llaves[i]
            self.llaves.append(pygame.Rect(x, y, 20, 20))

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
        """Encuentra una posición de spawn válida para el jugador.
        
        Verifica que:
        - No esté dentro de paredes
        - No esté fuera del mapa
        - No esté demasiado cerca de enemigos
        - Esté en una zona segura con espacio suficiente
        """
        margen = 50  # Distancia mínima desde los bordes
        radio_seguridad = 200  # Distancia mínima desde enemigos
        max_intentos = 100
        
        muros_rects = [m.rect for m in self.muros]
        
        for _ in range(max_intentos):
            # Generar posición aleatoria con márgenes
            x = random.randint(margen, self.ancho - margen - tamaño_jugador)
            y = random.randint(margen, self.alto - margen - tamaño_jugador)
            
            # Crear rectángulo del jugador con un área de seguridad
            jugador_rect = pygame.Rect(x, y, tamaño_jugador, tamaño_jugador)
            area_seguridad = jugador_rect.inflate(20, 20)  # Área más grande para verificar
            
            # Verificar que no colisione con muros
            colision_muro = False
            for muro_rect in muros_rects:
                if area_seguridad.colliderect(muro_rect):
                    colision_muro = True
                    break
            
            if colision_muro:
                continue
            
            # Verificar que no esté muy cerca de la salida
            if self.salida and jugador_rect.inflate(100, 100).colliderect(self.salida.rect):
                continue
            
            # Verificar que no esté muy cerca de spawns de enemigos
            muy_cerca_enemigo = False
            for ex, ey in self.spawn_enemigos:
                distancia = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
                if distancia < radio_seguridad:
                    muy_cerca_enemigo = True
                    break
            
            if muy_cerca_enemigo:
                continue
            
            # Verificar que no esté muy cerca de llaves
            muy_cerca_llave = False
            for llave_rect in getattr(self, "llaves", []):
                if jugador_rect.inflate(80, 80).colliderect(llave_rect):
                    muy_cerca_llave = True
                    break
            
            if muy_cerca_llave:
                continue
            
            # Posición válida encontrada
            return (x, y)
        
        # Si no se encuentra posición después de muchos intentos, usar posición por defecto segura
        # Buscar el primer espacio libre cerca del inicio del mapa
        for y in range(50, 500, 50):
            for x in range(50, 500, 50):
                jugador_rect = pygame.Rect(x, y, tamaño_jugador, tamaño_jugador)
                area_seguridad = jugador_rect.inflate(20, 20)
                
                colision = False
                for muro_rect in muros_rects:
                    if area_seguridad.colliderect(muro_rect):
                        colision = True
                        break
                
                if not colision:
                    return (x, y)
        
        # Última opción: posición por defecto
        return (100, 100)

    def dibujar(self, ventana, camara):
        # dibuja el suelo como mosaico de la textura, ajustado por la cámara
        if TEXTURA_SUELO:
            tex_w, tex_h = TEXTURA_SUELO.get_width(), TEXTURA_SUELO.get_height()
            
            # Calcular el área visible en coordenadas del mundo
            cam_x = camara.x
            cam_y = camara.y
            ancho_ventana, alto_ventana = ventana.get_size()
            
            # Calcular los rangos de tiles a dibujar con un pequeño margen
            start_x = max(0, int(cam_x // tex_w) * tex_w - tex_w)
            start_y = max(0, int(cam_y // tex_h) * tex_h - tex_h)
            end_x = min(self.ancho, int((cam_x + ancho_ventana) // tex_w + 2) * tex_w)
            end_y = min(self.alto, int((cam_y + alto_ventana) // tex_h + 2) * tex_h)
            
            # Solo dibuja las texturas visibles en el viewport
            for xx in range(start_x, end_x, tex_w):
                for yy in range(start_y, end_y, tex_h):
                    rect = pygame.Rect(xx, yy, tex_w, tex_h)
                    rect_pantalla = camara.aplicar(rect)
                    ventana.blit(TEXTURA_SUELO, rect_pantalla)
        else:
            # fallback: rellena con un color oscuro en el área visible
            ventana.fill((20, 20, 20))

        # dibuja muros
        for muro in self.muros:
            muro.dibujar(ventana, camara)

        # Las zonas de escondites ya no se dibujan visualmente
        # (aún existen en la lógica pero no se muestran)

        # dibuja salida
        # la salida se colorea diferente si aún hay llaves pendientes
        bloqueada = False
        if hasattr(self, "llaves_requeridas"):
            bloqueada = len(self.llaves) > 0
        self.salida.dibujar(ventana, camara, bloqueada=bloqueada)

        # dibuja llaves con efecto visual mejorado
        import math
        import time
        for i, r in enumerate(getattr(self, "llaves", [])):
            rp = camara.aplicar(r)
            # Efecto de brillo pulsante
            pulso = math.sin(time.time() * 3 + i) * 0.3 + 0.7
            
            # Sombra
            sombra = pygame.Rect(rp.x + 2, rp.y + 2, rp.w, rp.h)
            pygame.draw.rect(ventana, (100, 90, 20), sombra, border_radius=4)
            
            # Cuerpo de la llave
            color_base = (int(240 * pulso), int(220 * pulso), int(40 * pulso))
            pygame.draw.rect(ventana, color_base, rp, border_radius=4)
            
            # Borde brillante
            pygame.draw.rect(ventana, (255, 255, 120), rp, 2, border_radius=4)
            
            # Detalles de la llave (cabeza y dientes)
            # Cabeza circular
            cabeza_x = rp.x + 5
            cabeza_y = rp.y + rp.h // 2
            pygame.draw.circle(ventana, (255, 255, 150), (cabeza_x, cabeza_y), 4)
            pygame.draw.circle(ventana, (255, 255, 200), (cabeza_x, cabeza_y), 2)
            
            # Dientes de la llave
            diente_y = rp.y + rp.h // 2
            pygame.draw.line(ventana, (255, 255, 150), (rp.x + 12, diente_y), (rp.x + 18, diente_y), 2)
            pygame.draw.line(ventana, (255, 255, 150), (rp.x + 14, diente_y), (rp.x + 14, diente_y + 3), 1)
            pygame.draw.line(ventana, (255, 255, 150), (rp.x + 17, diente_y), (rp.x + 17, diente_y + 2), 1)

        # dibuja palancas con efecto mejorado
        import time
        for i, r in enumerate(getattr(self, "palancas", [])):
            rp = camara.aplicar(r)
            
            # Efecto de brillo pulsante
            pulso = math.sin(time.time() * 2 + i * 0.5) * 0.2 + 0.8
            
            # Sombra
            sombra = pygame.Rect(rp.x + 3, rp.y + 3, rp.w, rp.h)
            pygame.draw.rect(ventana, (20, 50, 100), sombra, border_radius=4)
            
            # Base de la palanca (más oscuro)
            base_color = (int(40 * pulso), int(100 * pulso), int(200 * pulso))
            pygame.draw.rect(ventana, base_color, rp, border_radius=4)
            
            # Borde brillante
            borde_color = (int(120 * pulso), int(180 * pulso), int(255 * pulso))
            pygame.draw.rect(ventana, borde_color, rp, 3, border_radius=4)
            
            # Manija de la palanca (línea vertical en el centro)
            centro_x = rp.centerx
            inicio_y = rp.y + rp.h // 4
            fin_y = rp.y + 3 * rp.h // 4
            pygame.draw.line(ventana, (200, 220, 255), (centro_x, inicio_y), (centro_x, fin_y), 3)
            
            # Círculo en la punta
            pygame.draw.circle(ventana, (220, 240, 255), (centro_x, inicio_y), 4)
            pygame.draw.circle(ventana, (180, 200, 255), (centro_x, inicio_y), 2)

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
        """Genera habitaciones de tamaños variados uniendo completamente sus paredes.

        Crea habitaciones de diferentes tamaños (2×2, 3×3, 4×4, 5×5) para darle
        más variedad a la mazmorra. Selecciona posiciones al azar y elimina los muros
        internos que separan las celdas dentro de ese bloque, creando espacios abiertos
        tipo caverna. Las celdas se conectan en el grafo y las paredes se eliminan.
        """
        for _ in range(num_habitaciones):
            # Tamaño variable de habitación (2x2 a 5x5)
            tamaño_hab = random.choice([2, 2, 3, 3, 3, 4, 5])
            
            # elige la esquina superior izquierda de la habitación dentro de los límites
            cx = random.randint(1, max(1, cols - tamaño_hab))
            cy = random.randint(1, max(1, filas - tamaño_hab))
            
            # recorre las celdas dentro del bloque
            for dx in range(tamaño_hab):
                for dy in range(tamaño_hab):
                    # conecta con la celda de la derecha
                    if dx < tamaño_hab - 1:
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
                    if dy < tamaño_hab - 1:
                        a = (cx + dx, cy + dy)
                        b = (cx + dx, cy + dy + 1)
                        if b not in celdas.get(a, set()):
                            celdas.setdefault(a, set()).add(b)
                            celdas.setdefault(b, set()).add(a)
                            if (a[0], a[1], b[0], b[1]) in paredes:
                                paredes.discard((a[0], a[1], b[0], b[1]))
                            elif (b[0], b[1], a[0], a[1]) in paredes:
                                paredes.discard((b[0], b[1], a[0], a[1]))