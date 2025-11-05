import pygame
import sys
import random
import math

pygame.init()
ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ancho, alto = ventana.get_size()
pygame.display.set_caption("Fear of Ways")

# Colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
gris = (40, 40, 40)
rojo = (255, 0, 0)
amarillo = (255, 255, 0)
verde = (0, 255, 0)

reloj = pygame.time.Clock()

class camara:
    """Controla la vista del jugador siguiéndolo por el mapa"""
    def __init__(self, ancho_mapa, alto_mapa):
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar(self, rect_objetivo):
        """Centra la cámara en el objetivo (jugador)"""
        self.offset_x = rect_objetivo.centerx - ancho // 2
        self.offset_y = rect_objetivo.centery - alto // 2
        # Limitar la cámara a los bordes del mapa
        self.offset_x = max(0, min(self.offset_x, self.ancho_mapa - ancho))
        self.offset_y = max(0, min(self.offset_y, self.alto_mapa - alto))
    
    def aplicar(self, rect):
        """Convierte coordenadas del mundo a coordenadas de pantalla"""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height)
    
    def aplicar_pos(self, x, y):
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla"""
        return (x - self.offset_x, y - self.offset_y)


class pared:
    """Representa un muro del laberinto"""
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla)
        pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2)  # borde


class salida:
    """Representa la salida del nivel"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
        pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)


class nivel:
    """Define un nivel con su laberinto, enemigos y salida"""
    def __init__(self, numero):
        self.numero = numero
        self.muros = []
        self.salida = None
        self.spawn_enemigos = []
        # Dimensiones del mapa (más grandes que la pantalla)
        self.ancho = 2000
        self.alto = 1500
        self.crear_nivel()
    
    def crear_nivel(self):
        if self.numero == 1:
            self.crear_nivel_1()
        elif self.numero == 2:
            self.crear_nivel_2()
        elif self.numero == 3:
            self.crear_nivel_3()
    
    def crear_nivel_1(self):
        """Nivel 1: Laberinto expandido con múltiples cámaras"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))  # arriba
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))  # abajo
        self.muros.append(pared(0, 0, 20, self.alto))  # izquierda
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))  # derecha

        # Pasillo principal horizontal
        self.muros.append(pared(200, 300, 600, 20))
        self.muros.append(pared(200, 320, 20, 300))

        # Cámara izquierda
        self.muros.append(pared(400, 500, 200, 20))
        self.muros.append(pared(400, 700, 20, 200))

        # Pasillo central
        self.muros.append(pared(800, 200, 20, 400))
        self.muros.append(pared(820, 580, 300, 20))

        # Cámara superior derecha
        self.muros.append(pared(1200, 100, 20, 400))
        self.muros.append(pared(1000, 480, 220, 20))

        # Pasillo inferior
        self.muros.append(pared(300, 900, 800, 20))
        self.muros.append(pared(1100, 700, 20, 220))

        # Cámara derecha 
        self.muros.append(pared(1400, 300, 20, 600))
        self.muros.append(pared(1420, 300, 300, 20))
        self.muros.append(pared(1420, 880, 300, 20))

        # Obstáculos adicionales
        self.muros.append(pared(600, 1000, 150, 20))
        self.muros.append(pared(1000, 1100, 200, 20))
        self.muros.append(pared(1500, 1000, 20, 300))

        # Posiciones posibles para la salida
        posiciones_salida = [
            (1900, 1420),
            (300, 1350),
            (1850, 100),
            (650, 150),
            (1600, 700),
            (500, 800)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Spawn points
        self.spawn_enemigos = [
            (300, 400),
            (500, 600),
            (900, 350),
            (1100, 250),
            (1300, 800),
            (700, 1050),
            (1600, 500)
        ]
    
    def crear_nivel_2(self):
        """Nivel 2: Laberinto en espiral expandido"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))
        
        # Espiral exterior a interior
        self.muros.append(pared(150, 150, 1700, 20))
        self.muros.append(pared(1830, 170, 20, 1200))
        self.muros.append(pared(200, 1350, 1650, 20))
        self.muros.append(pared(200, 250, 20, 1120))
        
        # Segunda capa
        self.muros.append(pared(350, 250, 1330, 20))
        self.muros.append(pared(1660, 270, 20, 950))
        self.muros.append(pared(400, 1200, 1280, 20))
        self.muros.append(pared(400, 370, 20, 850))
        
        # Tercera capa
        self.muros.append(pared(550, 370, 970, 20))
        self.muros.append(pared(1500, 390, 20, 690))
        self.muros.append(pared(600, 1060, 920, 20))
        self.muros.append(pared(600, 490, 20, 590))
        
        # Centro con obstáculos
        self.muros.append(pared(750, 550, 600, 20))
        self.muros.append(pared(1330, 570, 20, 380))
        self.muros.append(pared(800, 930, 550, 20))
        self.muros.append(pared(800, 650, 20, 300))
        
        # Obstáculos adicionales
        self.muros.append(pared(950, 700, 200, 20))
        self.muros.append(pared(1000, 800, 150, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1000, 750),
            (250, 200),
            (1800, 1300),
            (450, 1250),
            (1600, 450),
            (700, 600)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Enemigos
        self.spawn_enemigos = [
            (250, 200),
            (1700, 300),
            (300, 1300),
            (500, 320),
            (1550, 600),
            (650, 1100),
            (900, 600),
            (1200, 800),
            (1100, 450)
        ]
    
    def crear_nivel_3(self):
        """Nivel 3: Laberinto caótico expandido"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))
        
        # Red de pasillos complejos - sección izquierda
        self.muros.append(pared(150, 100, 20, 400))
        self.muros.append(pared(170, 480, 300, 20))
        self.muros.append(pared(300, 200, 20, 300))
        self.muros.append(pared(320, 200, 200, 20))
        self.muros.append(pared(500, 100, 20, 600))
        
        # Sección central
        self.muros.append(pared(700, 150, 20, 500))
        self.muros.append(pared(550, 630, 170, 20))
        self.muros.append(pared(850, 250, 300, 20))
        self.muros.append(pared(1130, 100, 20, 400))
        self.muros.append(pared(900, 480, 250, 20))
        
        # Cámaras inferiores
        self.muros.append(pared(200, 700, 400, 20))
        self.muros.append(pared(200, 720, 20, 400))
        self.muros.append(pared(220, 1100, 500, 20))
        self.muros.append(pared(700, 800, 20, 320))
        
        # Sección derecha superior
        self.muros.append(pared(1300, 200, 20, 400))
        self.muros.append(pared(1320, 580, 400, 20))
        self.muros.append(pared(1500, 300, 220, 20))
        self.muros.append(pared(1700, 100, 20, 500))
        
        # Sección derecha inferior
        self.muros.append(pared(900, 750, 300, 20))
        self.muros.append(pared(1180, 650, 20, 400))
        self.muros.append(pared(1200, 1030, 400, 20))
        self.muros.append(pared(1400, 850, 20, 200))
        self.muros.append(pared(1550, 700, 20, 400))
        
        # Obstáculos adicionales dispersos
        self.muros.append(pared(350, 900, 150, 20))
        self.muros.append(pared(850, 1000, 200, 20))
        self.muros.append(pared(1300, 1200, 250, 20))
        self.muros.append(pared(600, 350, 80, 20))
        self.muros.append(pared(1450, 450, 100, 20))
        
        # Laberinto final hacia la salida
        self.muros.append(pared(1650, 1100, 20, 300))
        self.muros.append(pared(1670, 1380, 250, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1900, 1420),
            (100, 100),
            (1850, 200),
            (350, 1350),
            (1250, 1300),
            (850, 1150),
            (1550, 950)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Muchos enemigos distribuidos
        self.spawn_enemigos = [
            (200, 250),
            (400, 350),
            (250, 850),
            (550, 550),
            (650, 300),
            (950, 350),
            (1050, 200),
            (850, 900),
            (1100, 850),
            (1250, 350),
            (1600, 350),
            (1450, 950),
            (1300, 1250),
            (1750, 1200)
        ]
    
    def dibujar(self, ventana, camara):
        for muro in self.muros:
            muro.dibujar(ventana, camara)
        self.salida.dibujar(ventana, camara)


class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision):
        self.nombre = nombre
        self.color = color
        self.velocidad = velocidad
        self.energia = energia
        self.vision = vision  # radio de linterna
        self.rect = pygame.Rect(50, 50, 30, 30)  # spawn inicial
        self.pos_inicial = (50, 50)

    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        x_anterior, y_anterior = self.rect.x, self.rect.y
        
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad

        # Mantener dentro de los límites del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))
        
        # Detectar colisión con muros
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                self.rect.x, self.rect.y = x_anterior, y_anterior
                break
    
    def resetear_posicion(self):
        """Resetea la posición del jugador al inicio"""
        self.rect.x, self.rect.y = self.pos_inicial

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, self.color, rect_pantalla)
        pygame.draw.rect(ventana, blanco, rect_pantalla, 2)


class enemigo:
    def __init__(self, x, y, velocidad, tipo=None):
        # tipos con vida distinta (no se muestra en pantalla)
        tipos_def = {
            "veloz": {
                "vida": 2,
                "color": (255, 255, 0),    # amarillo brillante
                "tam": 25                  # pequeño y rápido
            },
            "acechador": {
                "vida": 3,
                "color": (0, 255, 255),    # celeste
                "tam": 35                  # mediano
            },
            "bruto": {
                "vida": 5,
                "color": (255, 80, 80),    # rojo oscuro
                "tam": 50                  # grande y lento
            },
        }
        if tipo is None:
            tipo = random.choice(list(tipos_def.keys()))
        self.tipo = tipo
        self.vida_max = tipos_def[tipo]["vida"]
        self.vida = self.vida_max
        self.color_base = tipos_def[tipo]["color"]
        tam = tipos_def[tipo]["tam"]

        # rect y movimiento
        self.rect = pygame.Rect(x, y, tam, tam)
        self.velocidad = velocidad
        if tipo == "veloz":
            self.velocidad += 2
        elif tipo == "bruto":
            self.velocidad = max(1, velocidad - 1)

        # percepción
        self.rango_deteccion = 250
        self.estado = "patrullando"   # "patrullando" | "persiguiendo"
        self.velocidad_persecucion = velocidad + 1
        self.tiempo_perdida = 0

    def distancia_a(self, rect_jugador):
        dx = rect_jugador.centerx - self.rect.centerx
        dy = rect_jugador.centery - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def mover(self, muros, ancho_mapa, alto_mapa, rect_jugador=None):
        x_anterior, y_anterior = self.rect.x, self.rect.y

        # detección
        if rect_jugador:
            distancia = self.distancia_a(rect_jugador)
            if distancia <= self.rango_deteccion:
                self.estado = "persiguiendo"
                self.tiempo_perdida = 0
            elif self.estado == "persiguiendo":
                self.tiempo_perdida += 1
                if self.tiempo_perdida > 120:
                    self.estado = "patrullando"

        # comportamiento
        if self.estado == "persiguiendo" and rect_jugador:
            dx = rect_jugador.centerx - self.rect.centerx
            dy = rect_jugador.centery - self.rect.centery
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia > 0:
                vel_actual = self.velocidad_persecucion
                self.rect.x += int((dx / distancia) * vel_actual)
                self.rect.y += int((dy / distancia) * vel_actual)
        else:
            if self.direccion == "horizontal":
                self.rect.x += self.velocidad * self.sentido
                if self.rect.left <= 20 or self.rect.right >= ancho_mapa - 20:
                    self.sentido *= -1
            else:
                self.rect.y += self.velocidad * self.sentido
                if self.rect.top <= 20 or self.rect.bottom >= alto_mapa - 20:
                    self.sentido *= -1

        # colisión con muros
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                self.rect.x, self.rect.y = x_anterior, y_anterior
                if self.estado == "patrullando":
                    self.sentido *= -1
                    if random.random() < 0.3:
                        self.direccion = "vertical" if self.direccion == "horizontal" else "horizontal"
                else:
                    if random.random() < 0.5:
                        self.rect.x = x_anterior + random.randint(-3, 3)
                    else:
                        self.rect.y = y_anterior + random.randint(-3, 3)
                break

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)

        # color según estado (sin barra de vida)
        if self.estado == "persiguiendo":
            color_cuerpo = (min(self.color_base[0]+30,255), self.color_base[1], self.color_base[2])
            color_ojos = (255, 255, 0)
        else:
            color_cuerpo = self.color_base
            color_ojos = (200, 200, 100)

        pygame.draw.rect(ventana, color_cuerpo, rect_pantalla)
        pos_ojo1 = camara.aplicar_pos(self.rect.x + 10, self.rect.y + 10)
        pos_ojo2 = camara.aplicar_pos(self.rect.x + 25, self.rect.y + 10)
        pygame.draw.circle(ventana, color_ojos, pos_ojo1, 4)
        pygame.draw.circle(ventana, color_ojos, pos_ojo2, 4)

        if self.estado == "persiguiendo":
            pos_alerta = camara.aplicar_pos(self.rect.centerx, self.rect.y - 15)
            pygame.draw.circle(ventana, (255,255,0), pos_alerta, 8)
            pygame.draw.circle(ventana, (255,0,0), pos_alerta, 6)

class juego:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.nivel_actual = None
        self.numero_nivel = 1
        self.enemigos = []
        self.resultado = ""
        self.camara = None

    # Pantallas

    def menu(self):
        ventana.fill(negro)
        self.dibujar_texto("Fear of Ways", 60, blanco, ancho//2, 120)
        self.dibujar_texto("3 Niveles de Mazmorras Expandidas", 35, amarillo, ancho//2, 200)
        self.dibujar_texto("Selecciona tu personaje:", 35, blanco, ancho//2, 270)
        self.dibujar_texto("1 Explorador  2 Cazador  3 Ingeniero", 28, blanco, ancho//2, 320)
        self.dibujar_texto("Encuentra la salida verde en cada nivel", 25, verde, ancho//2, 380)
        self.dibujar_texto("Evita a los enemigos rojos", 25, rojo, ancho//2, 410)
        self.dibujar_texto("La cámara te seguirá por el mapa", 25, (100, 200, 255), ancho//2, 440)
        self.dibujar_texto("ESC para salir", 25, blanco, ancho//2, 480)

    def iniciar_juego(self, tipo):
        if tipo == 1:
            self.jugador = jugador("Explorador", amarillo, velocidad=4, energia=100, vision=150)
        elif tipo == 2:
            self.jugador = jugador("Cazador", verde, velocidad=6, energia=70, vision=120)
        elif tipo == 3:
            self.jugador = jugador("Ingeniero", (0, 150, 255), velocidad=3, energia=120, vision=180)

        self.numero_nivel = 1
        self.cargar_nivel(1)
        self.resultado = ""
        self.estado = "jugando"
    
    def cargar_nivel(self, numero):
        """Carga un nivel específico"""
        self.numero_nivel = numero
        self.nivel_actual = nivel(numero)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)
        
        # Crear enemigos
        self.enemigos = []
        spawns = list(self.nivel_actual.spawn_enemigos)

        # forzar al menos 1 de cada tipo (si hay >=3 spawns)
        tipos_base = ["veloz", "acechador", "bruto"]
        random.shuffle(spawns)
        for t in tipos_base:
            if spawns:
                sx, sy = spawns.pop()
                vel = random.randint(2, 4)
                self.enemigos.append(enemigo(sx, sy, vel, tipo=t))

        # el resto, aleatorios con pesos
        for sx, sy in spawns:
            vel = random.randint(2, 4)
            tipo = random.choices(["veloz","acechador","bruto"], weights=[0.45,0.35,0.20], k=1)[0]
            self.enemigos.append(enemigo(sx, sy, vel, tipo=tipo))

        
        # Resetear posición del jugador
        self.jugador.resetear_posicion()

    def jugar(self):
        ventana.fill(gris)
        
        # Actualizar cámara
        self.camara.actualizar(self.jugador.rect)
        
        # Dibujar nivel
        self.nivel_actual.dibujar(ventana, self.camara)
        
        # Mover jugador
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas, self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto)

        # Mover y dibujar enemigos
        for enemigo_actual in self.enemigos:
            enemigo_actual.mover(self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto, self.jugador.rect)
            enemigo_actual.dibujar(ventana, self.camara)

            # Colisión jugador - enemigo (tal como lo tenías)
            if self.jugador.rect.colliderect(enemigo_actual.rect):
                self.resultado = "perdiste"
                self.estado = "fin"

        # Dibujar jugador
        self.jugador.dibujar(ventana, self.camara)

        # Dibujar linterna
        self.dibujar_linterna()

        # Verificar salida
        if self.jugador.rect.colliderect(self.nivel_actual.salida.rect):
            if self.numero_nivel < 3:
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                self.resultado = "ganaste"
                self.estado = "fin"

        # UI
        self.dibujar_texto(f"Nivel: {self.numero_nivel}/3", 30, blanco, 10, 10, centrado=False)
        self.dibujar_texto(f"Energía: {int(self.jugador.energia)}", 30, blanco, 10, 40, centrado=False)

    def pantalla_final(self):
        ventana.fill(negro)
        if self.resultado == "ganaste":
            color = verde
            mensaje = "¡Escapaste de las 3 mazmorras!"
            submensaje = f"Completaste todos los niveles con {self.jugador.nombre}"
        else:
            color = rojo
            mensaje = "Fuiste atrapado en la oscuridad..."
            submensaje = f"Llegaste hasta el nivel {self.numero_nivel}"
        
        self.dibujar_texto(mensaje, 50, color, ancho // 2, 220)
        self.dibujar_texto(submensaje, 30, blanco, ancho // 2, 290)
        self.dibujar_texto("ENTER para volver al menú", 30, blanco, ancho // 2, 380)

    # Utilidades

    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        fuente_local = pygame.font.Font(None, tam)
        superficie = fuente_local.render(texto, True, color)
        rect = superficie.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        ventana.blit(superficie, rect)

    def dibujar_linterna(self):
        sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 240))

        luz = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        mx, my = pygame.mouse.get_pos()

        dx, dy = mx - cx, my - cy
        if dx == 0 and dy == 0:
            angulo = 0.0
        else:
            angulo = math.atan2(dy, dx)

        radio = max(1, int(self.jugador.vision))
        semiancho = math.radians(35)
        pasos = 48

        for i in range(pasos, 0, -1):
            r = radio * (i / pasos)
            a = semiancho * (i / pasos)

            izquierdo = (cx + r * math.cos(angulo - a), cy + r * math.sin(angulo - a))
            derecho = (cx + r * math.cos(angulo + a), cy + r * math.sin(angulo + a))

            alpha = int(240 * (i / pasos))
            alpha = max(0, min(240, alpha))

            pygame.draw.polygon(
                luz,
                (255, 255, 255, alpha),
                [(cx, cy), izquierdo, derecho]
            )

        sombra.blit(luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        ventana.blit(sombra, (0, 0))

    # LOOP PRINCIPAL

    def ejecutar(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.estado == "menu":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if e.key == pygame.K_1:
                            self.iniciar_juego(1)
                        if e.key == pygame.K_2:
                            self.iniciar_juego(2)
                        if e.key == pygame.K_3:
                            self.iniciar_juego(3)

                elif self.estado == "fin":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                        self.estado = "menu"

            if self.estado == "menu":
                self.menu()
            elif self.estado == "jugando":
                self.jugar()
            elif self.estado == "fin":
                self.pantalla_final()

            pygame.display.flip()
            reloj.tick(60)

# Ejecución
if __name__ == "__main__":
    juego = juego()
    juego.ejecutar()

