import pygame
import random
from pared import pared
from salida import salida

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

        # dimensiones generales del mapa (más grandes que la pantalla)
        self.ancho = 2000
        self.alto = 1500

        # generar estructura del nivel y escondites
        self.crear_nivel()
        self.generar_escondites_random(cantidad=random.randint(3, 5))

    def crear_nivel(self):
        # selecciona qué versión de nivel crear
        if self.numero == 1:
            self.crear_nivel_1()
        elif self.numero == 2:
            self.crear_nivel_2()
        elif self.numero == 3:
            self.crear_nivel_3()

    def crear_nivel_1(self):
        """Nivel 1: Procedural por celdas con habitaciones (estilo cueva)."""
        # limpia muros previos por si acaso
        self.muros = []
        # bordes del mapa (mantiene límites duros)
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # parámetros del generador de celdas
        cols, filas = 22, 16  # número de celdas en x,y (menos celdas -> celdas más grandes)
        tam = 80              # tamaño de cada celda (define ancho de pasillos)
        esp = 16              # grosor de muro
        carving_extra = 0.15  # porcentaje de paredes a romper para ciclos
        num_habitaciones = max(2, (cols * filas) // 50)  # número aproximado de habitaciones

        # genera estructura base del laberinto
        celdas, paredes = self._generar_laberinto_por_celdas(cols, filas)

        # crea habitaciones al estilo cueva: abre clusters de celdas
        self._crear_habitaciones(celdas, paredes, cols, filas, num_habitaciones)

        # levanta muros basados en la estructura resultante
        self._levantar_paredes_de_celdas(paredes, tam, esp)

        # carving extra: rompe algunos muros aleatorios para crear rutas alternativas y espacios abiertos
        self._romper_paredes_aleatorias(paredes, cols, filas, cantidad=int(cols*filas*carving_extra), tam=tam, esp=esp)

        # define celda de inicio y busca la más lejana para colocar la salida
        origen = (0, 0)
        destino = self._celda_mas_lejana_desde(origen, celdas, cols, filas)
        dx, dy = destino
        # posiciona la salida en el centro de la celda destino
        self.salida = salida(20 + dx * tam + tam // 2, 20 + dy * tam + tam // 2)

        # define puntos de spawn de enemigos dispersos
        self.spawn_enemigos = self._spawns_distribuidos(celdas, cols, filas, tam, cuantos=10)

        # coloca llaves en callejones sin salida
        dead_ends = [c for c in celdas if len(celdas[c]) == 1 and c != destino]
        random.shuffle(dead_ends)
        self.llaves = []
        self.llaves_requeridas = min(5, max(3, len(dead_ends)//5))
        for i in range(self.llaves_requeridas):
            cx, cy = dead_ends[i]
            # posición de la llave dentro de la celda
            rx = 20 + cx * tam + tam // 2 - 10
            ry = 20 + cy * tam + tam // 2 - 10
            self.llaves.append(pygame.Rect(rx, ry, 20, 20))

        # coloca una puerta y una palanca para forzar backtracking
        self.palancas = []
        self._puertas_por_id = {}
        cuello = self._elige_cuello_bottleneck(celdas, cols, filas)
        if cuello:
            (a, b) = cuello
            self._colocar_puerta_entre(a, b, tam, esp, puerta_id="A1")
            # coloca la palanca en un punto alejado del cuello
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

    def dibujar(self, ventana, camara):
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
        self.salida.dibujar(ventana, camara)

        # dibuja llaves si existen
        if hasattr(self, "llaves"):
            for r in self.llaves:
                rp = camara.aplicar(r)
                # cuerpo de la llave
                pygame.draw.rect(ventana, (240, 220, 40), rp)
                # borde
                pygame.draw.rect(ventana, (255, 255, 120), rp, 2)

        # dibuja palancas si existen
        if hasattr(self, "palancas"):
            for r in self.palancas:
                rp = camara.aplicar(r)
                pygame.draw.rect(ventana, (60, 140, 255), rp)
                pygame.draw.rect(ventana, (180, 220, 255), rp, 2)

    # -----------------------------------------------------------------------
    # Métodos auxiliares para generación procedural del laberinto

    def _idx(self, x, y, cols, filas):
        """Retorna True si la posición (x,y) está dentro de los límites de la grilla"""
        return 0 <= x < cols and 0 <= y < filas

    def _vecinos_cardinales(self, x, y, cols, filas):
        """Itera sobre los vecinos en cuatro direcciones (N, S, E, O)"""
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self._idx(nx, ny, cols, filas):
                yield (nx, ny)

    def _generar_laberinto_por_celdas(self, cols, filas):
        """Genera un laberinto por celdas usando DFS (backtracker). Devuelve un grafo de celdas y un set de paredes"""
        visitadas = set()
        stack = [(0, 0)]
        visitadas.add((0, 0))
        celdas = {(0, 0): set()}
        paredes = set()
        while stack:
            x, y = stack[-1]
            # lista de vecinos no visitados
            opciones = [(nx, ny) for (nx, ny) in self._vecinos_cardinales(x, y, cols, filas) if (nx, ny) not in visitadas]
            if opciones:
                nx, ny = random.choice(opciones)
                visitadas.add((nx, ny))
                stack.append((nx, ny))
                # conecta ambos lados
                celdas.setdefault((x, y), set()).add((nx, ny))
                celdas.setdefault((nx, ny), set()).add((x, y))
            else:
                stack.pop()

        # crea set inicial de paredes entre pares no conectados
        for y in range(filas):
            for x in range(cols):
                for nx, ny in self._vecinos_cardinales(x, y, cols, filas):
                    if (nx, ny) not in celdas.get((x, y), set()):
                        # usa orden para evitar duplicados
                        if (x, y, nx, ny) < (nx, ny, x, y):
                            paredes.add((x, y, nx, ny))
        return celdas, paredes

    def _crear_habitaciones(self, celdas, paredes, cols, filas, num_habitaciones):
        """Expande ciertas regiones para crear espacios abiertos (habitaciones)."""
        # evita bordes para no salir del mapa
        posibles = [(x, y) for x in range(1, cols - 1) for y in range(1, filas - 1)]
        random.shuffle(posibles)
        seleccionadas = posibles[:num_habitaciones]
        for cx, cy in seleccionadas:
            # define la región 3x3 alrededor del centro
            region = [(x, y) for x in range(cx - 1, cx + 2) for y in range(cy - 1, cy + 2)
                      if self._idx(x, y, cols, filas)]
            # conecta todas las celdas cardinalmente dentro de la región
            for x, y in region:
                for nx, ny in self._vecinos_cardinales(x, y, cols, filas):
                    if (nx, ny) in region:
                        # actualiza celdas para incluir la conexión
                        celdas.setdefault((x, y), set()).add((nx, ny))
                        celdas.setdefault((nx, ny), set()).add((x, y))
                        # elimina la pared si existe entre estos dos
                        par = (x, y, nx, ny)
                        inverso = (nx, ny, x, y)
                        if par in paredes:
                            paredes.discard(par)
                        elif inverso in paredes:
                            paredes.discard(inverso)

    def _levantar_paredes_de_celdas(self, paredes, tam, esp):
        """Convierte cada arista-muro en un rectángulo de pygame y lo añade a la lista de muros"""
        for (x, y, nx, ny) in paredes:
            if x == nx:
                # muro horizontal entre filas
                miny = min(y, ny)
                rx = 20 + x * tam
                ry = 20 + (miny + 1) * tam - esp // 2
                self.muros.append(pared(rx, ry, tam, esp))
            else:
                # muro vertical entre columnas
                minx = min(x, nx)
                rx = 20 + (minx + 1) * tam - esp // 2
                ry = 20 + y * tam
                self.muros.append(pared(rx, ry, esp, tam))

    def _romper_paredes_aleatorias(self, paredes, cols, filas, cantidad, tam, esp):
        """Rompe un número dado de paredes al azar (que no sean puertas) para crear ciclos"""
        paredes_lista = list(paredes)
        random.shuffle(paredes_lista)
        rotas = 0
        i = 0
        while rotas < cantidad and i < len(paredes_lista):
            (x, y, nx, ny) = paredes_lista[i]
            i += 1
            # calcula las coordenadas del muro en pantalla
            if x == nx:
                rx = 20 + x * tam
                ry = 20 + (min(y, ny) + 1) * tam - esp // 2
                w, h = tam, esp
            else:
                rx = 20 + (min(x, nx) + 1) * tam - esp // 2
                ry = 20 + y * tam
                w, h = esp, tam
            # busca y elimina el muro correspondiente, si no es puerta
            for m in list(self.muros):
                if m.rect.x == rx and m.rect.y == ry and m.rect.w == w and m.rect.h == h and not getattr(m, 'puerta', False):
                    self.muros.remove(m)
                    rotas += 1
                    break

    def _dist_bfs(self, origen, celdas, cols, filas):
        """Calcula las distancias BFS desde la celda origen en el grafo de celdas"""
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
        """Devuelve la celda con mayor distancia BFS desde el origen"""
        dist = self._dist_bfs(origen, celdas, cols, filas)
        return max(dist, key=dist.get)

    def _spawns_distribuidos(self, celdas, cols, filas, tam, cuantos=8):
        """Elige celdas espaciadas para generar apariciones de enemigos"""
        todas = list(celdas.keys())
        random.shuffle(todas)
        elegidas = []
        for c in todas:
            # evita que spawns estén demasiado cerca entre sí
            if all(abs(c[0] - e[0]) + abs(c[1] - e[1]) >= 5 for e in elegidas):
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
        """Heurística para elegir una arista concurrida donde colocar la puerta"""
        candidatos = []
        for (x, y), vecinos in celdas.items():
            for (nx, ny) in vecinos:
                if (x, y) < (nx, ny):
                    grado = len(vecinos) + len(celdas.get((nx, ny), []))
                    if grado >= 6:
                        candidatos.append(((x, y), (nx, ny)))
        return random.choice(candidatos) if candidatos else None

    def _colocar_puerta_entre(self, a, b, tam, esp, puerta_id="A1"):
        """Coloca un muro especial (puerta) entre dos celdas adyacentes"""
        (x, y), (nx, ny) = a, b
        if x == nx:
            # puerta horizontal
            rx = 20 + x * tam
            ry = 20 + (min(y, ny) + 1) * tam - esp // 2
            w, h = tam, esp
        else:
            # puerta vertical
            rx = 20 + (min(x, nx) + 1) * tam - esp // 2
            ry = 20 + y * tam
            w, h = esp, tam
        p = pared(rx, ry, w, h, puerta=True, abierta=False, id_puerta=puerta_id)
        self.muros.append(p)
        self._puertas_por_id.setdefault(puerta_id, []).append(p)