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
        """
        Nivel 1: genera un laberinto procedural por celdas con llaves, puertas y palancas.

        Este método reemplaza el diseño fijo del nivel 1 por uno generado con
        un algoritmo DFS (backtracker) en una grilla de celdas. También coloca
        llaves en callejones sin salida, una puerta bloqueando un cuello de
        botella y una palanca en otro sector que la abre.
        """
        # Bordes del mapa (límites duros): agregamos muros en los márgenes
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto - 20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho - 20, 0, 20, self.alto))

        # Parámetros del generador de laberinto
        cols, filas = 28, 20         # número de columnas y filas de celdas
        tam = 60                    # tamaño de cada celda en píxeles (incluye pasillo)
        esp = 16                    # grosor de los muros generados
        carving_extra = 0.11        # porcentaje de paredes extra a romper para crear ciclos

        # Generamos la estructura del laberinto usando DFS
        celdas, paredes = self._generar_laberinto_por_celdas(cols, filas)
        # Construimos los muros físicos a partir de las paredes entre celdas
        self._levantar_paredes_de_celdas(paredes, tam, esp)
        # Rompemos algunas paredes al azar para abrir rutas alternativas (ciclos)
        cantidad_romper = int(cols * filas * carving_extra)
        self._romper_paredes_aleatorias(paredes, cols, filas, cantidad_romper, tam, esp)

        # Calculamos la celda más lejana desde el origen para colocar la salida
        origen = (0, 0)
        celda_fin = self._celda_mas_lejana_desde(origen, celdas, cols, filas)
        sx, sy = celda_fin
        # Centro de la celda de destino ajustado a las coordenadas del mapa
        self.salida = salida(20 + sx * tam + tam // 2, 20 + sy * tam + tam // 2)

        # Distribuimos posiciones de spawn de enemigos en celdas separadas
        self.spawn_enemigos = self._spawns_distribuidos(celdas, cols, filas, tam, cuantos=9)

        # Preparación de llaves: elegir callejones sin salida como objetivos
        # Calculamos cuántas llaves se requieren (3–4 habitualmente)
        # Los callejones son celdas con un único vecino en el grafo del laberinto
        callejones = [c for c in celdas if len(celdas[c]) == 1 and c != celda_fin]
        random.shuffle(callejones)
        self.llaves = []
        # Al menos 3 llaves y a lo sumo 4, o en función del tamaño del laberinto
        # Calculamos cuántas llaves requerimos en función de los callejones disponibles
        self.llaves_requeridas = min(4, max(3, len(callejones) // 6))
        # Ajustamos si hay menos callejones de los planeados
        num_llaves = min(self.llaves_requeridas, len(callejones))
        self.llaves_requeridas = num_llaves
        for i in range(num_llaves):
            cx, cy = callejones[i]
            # Centramos la llave dentro de la celda (20 px de margen)
            rx = 20 + cx * tam + tam // 2 - 10
            ry = 20 + cy * tam + tam // 2 - 10
            self.llaves.append(pygame.Rect(rx, ry, 20, 20))

        # Colocamos una puerta que bloquea un cuello de botella del laberinto
        # Y una palanca en una zona remota que la abre
        self.palancas = []
        self._puertas_por_id = {}
        cuello = self._elige_cuello_bottleneck(celdas, cols, filas)
        if cuello:
            (a, b) = cuello
            # Colocamos una puerta entre las dos celdas a y b
            self._colocar_puerta_entre(a, b, tam, esp, puerta_id="A1")
            # Para la palanca, buscamos la celda más alejada del lado b
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
        # Dibuja muros y puertas
        for muro in self.muros:
            muro.dibujar(ventana, camara)

        # Dibuja zonas seguras semitransparentes
        for r in self.escondites:
            rp = camara.aplicar(r)
            zona = pygame.Surface((rp.w, rp.h), pygame.SRCALPHA)
            zona.fill((30, 120, 180, 90))
            pygame.draw.rect(zona, (220, 240, 255, 140), zona.get_rect(), 2)
            ventana.blit(zona, (rp.x, rp.y))

        # Dibuja llaves (si existen)
        for r in getattr(self, "llaves", []):
            rp = camara.aplicar(r)
            pygame.draw.rect(ventana, (240, 220, 40), rp)
            pygame.draw.rect(ventana, (255, 255, 120), rp, 2)

        # Dibuja palancas (si existen)
        for r in getattr(self, "palancas", []):
            rp = camara.aplicar(r)
            pygame.draw.rect(ventana, (60, 140, 255), rp)
            pygame.draw.rect(ventana, (180, 220, 255), rp, 2)

        # Dibuja la salida; si se requiere recolectar llaves, muéstrala bloqueada hasta tenerlas todas
        bloqueada = False
        if hasattr(self, "llaves_requeridas"):
            bloqueada = len(getattr(self, "llaves", [])) > 0
        # Pasamos el estado de bloqueada al método dibujar de la salida
        # (fall back al método original si no tiene parámetro)
        try:
            self.salida.dibujar(ventana, camara, bloqueada=bloqueada)
        except TypeError:
            # método antiguo sin parámetro bloqueada
            self.salida.dibujar(ventana, camara)

    # --- Funciones auxiliares para la generación procedural del laberinto ---
    def _idx(self, x: int, y: int, cols: int, filas: int) -> bool:
        """Devuelve True si (x,y) está dentro de los límites de la grilla."""
        return 0 <= x < cols and 0 <= y < filas

    def _vecinos_cardinales(self, x: int, y: int, cols: int, filas: int):
        """
        Genera las coordenadas de los vecinos cardinales (arriba, abajo, izquierda, derecha)
        de la celda (x, y) dentro de la grilla de cols x filas.
        """
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self._idx(nx, ny, cols, filas):
                yield (nx, ny)

    def _generar_laberinto_por_celdas(self, cols: int, filas: int):
        """
        Utiliza un algoritmo de backtracking (DFS) para generar un laberinto conectado.
        Devuelve un diccionario de celdas con sus vecinos conectados y un conjunto de
        paredes representadas como tuplas (x, y, nx, ny).
        """
        visitadas = set()
        stack = [(0, 0)]
        visitadas.add((0, 0))
        celdas = {(0, 0): set()}
        paredes = set()
        while stack:
            x, y = stack[-1]
            # elegimos vecinos no visitados de forma aleatoria
            candidatos = [(nx, ny) for nx, ny in self._vecinos_cardinales(x, y, cols, filas) if (nx, ny) not in visitadas]
            if candidatos:
                nx, ny = random.choice(candidatos)
                visitadas.add((nx, ny))
                stack.append((nx, ny))
                # conectamos ambos lados en el grafo
                celdas.setdefault((x, y), set()).add((nx, ny))
                celdas.setdefault((nx, ny), set()).add((x, y))
            else:
                stack.pop()
        # Generar el conjunto de paredes entre pares de celdas no conectadas
        for y in range(filas):
            for x in range(cols):
                for nx, ny in self._vecinos_cardinales(x, y, cols, filas):
                    if (nx, ny) not in celdas.get((x, y), set()):
                        # evita duplicados ordenando la tupla
                        if (x, y, nx, ny) < (nx, ny, x, y):
                            paredes.add((x, y, nx, ny))
        return celdas, paredes

    def _levantar_paredes_de_celdas(self, paredes: set, tam: int, esp: int):
        """
        A partir de un conjunto de paredes entre celdas, crea instancias de la clase
        pared correspondientes en la lista self.muros. Cada pared se traduce a un
        rectángulo en coordenadas del mundo según el tamaño de celda (tam) y el grosor
        del muro (esp).
        """
        for (x, y, nx, ny) in paredes:
            if x == nx:
                # pared horizontal entre filas
                miny = min(y, ny)
                rx = 20 + x * tam
                ry = 20 + (miny + 1) * tam - esp // 2
                self.muros.append(pared(rx, ry, tam, esp))
            else:
                # pared vertical entre columnas
                minx = min(x, nx)
                rx = 20 + (minx + 1) * tam - esp // 2
                ry = 20 + y * tam
                self.muros.append(pared(rx, ry, esp, tam))

    def _romper_paredes_aleatorias(self, paredes: set, cols: int, filas: int, cantidad: int, tam: int, esp: int):
        """
        Elimina aleatoriamente `cantidad` de paredes en self.muros (si no son puertas) para crear
        rutas alternativas. Utiliza la lista de paredes provistas para mapear cada rectángulo.
        """
        paredes_lista = list(paredes)
        random.shuffle(paredes_lista)
        rotas = 0
        i = 0
        while rotas < cantidad and i < len(paredes_lista):
            x, y, nx, ny = paredes_lista[i]
            i += 1
            # calculamos las coordenadas del rectángulo que representa la pared
            if x == nx:
                # horizontal
                rx = 20 + x * tam
                ry = 20 + (min(y, ny) + 1) * tam - esp // 2
                w, h = tam, esp
            else:
                # vertical
                rx = 20 + (min(x, nx) + 1) * tam - esp // 2
                ry = 20 + y * tam
                w, h = esp, tam
            # buscamos en self.muros el muro correspondiente y lo eliminamos
            for m in list(self.muros):
                if (
                    m.rect.x == rx
                    and m.rect.y == ry
                    and m.rect.w == w
                    and m.rect.h == h
                    and not getattr(m, "puerta", False)
                ):
                    self.muros.remove(m)
                    rotas += 1
                    break

    def _dist_bfs(self, origen: tuple, celdas: dict, cols: int, filas: int):
        """Calcula la distancia (en número de aristas) desde `origen` a todas las celdas con BFS."""
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

    def _celda_mas_lejana_desde(self, origen: tuple, celdas: dict, cols: int, filas: int):
        """Devuelve la celda con mayor distancia desde `origen` en el grafo de celdas."""
        dist = self._dist_bfs(origen, celdas, cols, filas)
        # seleccionamos la celda con distancia máxima
        return max(dist, key=dist.get)

    def _spawns_distribuidos(self, celdas: dict, cols: int, filas: int, tam: int, cuantos: int = 8):
        """
        Elige `cuantos` puntos de spawn distribuidos por el laberinto. Utiliza una heurística
        para que estén separados (distancia Manhattan >= 6 celdas).
        """
        todas = list(celdas.keys())
        random.shuffle(todas)
        elegidas = []
        for c in todas:
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

    def _elige_cuello_bottleneck(self, celdas: dict, cols: int, filas: int):
        """
        Selecciona aleatoriamente una arista entre dos celdas cuyo grado combinado es alto,
        lo cual suele corresponder a un cuello de botella en la estructura del laberinto.
        Devuelve una tupla ((x, y), (nx, ny)) o None.
        """
        candidatos = []
        for (x, y), vecinos in celdas.items():
            for (nx, ny) in vecinos:
                if (x, y) < (nx, ny):  # evitamos duplicados
                    grado = len(vecinos) + len(celdas.get((nx, ny), []))
                    if grado >= 5:
                        candidatos.append(((x, y), (nx, ny)))
        return random.choice(candidatos) if candidatos else None

    def _colocar_puerta_entre(self, a: tuple, b: tuple, tam: int, esp: int, puerta_id: str = "A1"):
        """
        Coloca una puerta (muro con capacidad de abrirse) entre las celdas `a` y `b`.
        Registra la puerta en el diccionario self._puertas_por_id para poder manipularla
        posteriormente con una palanca.
        """
        (x, y), (nx, ny) = a, b
        if x == nx:
            # horizontal entre filas
            rx = 20 + x * tam
            ry = 20 + (min(y, ny) + 1) * tam - esp // 2
            w, h = tam, esp
        else:
            # vertical entre columnas
            rx = 20 + (min(x, nx) + 1) * tam - esp // 2
            ry = 20 + y * tam
            w, h = esp, tam
        # Antes de colocar la puerta, eliminamos cualquier muro existente en esa posición
        for m in list(self.muros):
            if (
                m.rect.x == rx
                and m.rect.y == ry
                and m.rect.w == w
                and m.rect.h == h
                and not getattr(m, "puerta", False)
            ):
                self.muros.remove(m)
        # Creamos una puerta cerrada inicialmente
        p = pared(rx, ry, w, h, puerta=True, abierta=False, id_puerta=puerta_id)
        self.muros.append(p)
        self._puertas_por_id.setdefault(puerta_id, []).append(p)