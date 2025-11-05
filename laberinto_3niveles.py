import pygame
import sys
import random
import math

# Inicialización
pygame.init()
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El Laberinto de las Sombras Niveles")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (40, 40, 40)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)

clock = pygame.time.Clock()

# ------------------------
# Clases principales
# ------------------------

class Camera:
    """Controla la vista del jugador siguiéndolo por el mapa"""
    def __init__(self, ancho_mapa, alto_mapa):
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar(self, objetivo_rect):
        """Centra la cámara en el objetivo (jugador)"""
        # Calcular posición deseada (centrar al jugador)
        self.offset_x = objetivo_rect.centerx - ANCHO // 2
        self.offset_y = objetivo_rect.centery - ALTO // 2
        
        # Limitar la cámara a los bordes del mapa
        self.offset_x = max(0, min(self.offset_x, self.ancho_mapa - ANCHO))
        self.offset_y = max(0, min(self.offset_y, self.alto_mapa - ALTO))
    
    def aplicar(self, rect):
        """Convierte coordenadas del mundo a coordenadas de pantalla"""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height)
    
    def aplicar_pos(self, x, y):
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla"""
        return (x - self.offset_x, y - self.offset_y)


class Wall:
    """Representa un muro del laberinto"""
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla)
        pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2)  # borde


class Salida:
    """Representa la salida del nivel"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        # Dibujar como puerta brillante
        pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
        pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)


class Nivel:
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
        self.muros.append(Wall(0, 0, self.ancho, 20))  # arriba
        self.muros.append(Wall(0, self.alto-20, self.ancho, 20))  # abajo
        self.muros.append(Wall(0, 0, 20, self.alto))  # izquierda
        self.muros.append(Wall(self.ancho-20, 0, 20, self.alto))  # derecha
        
        # Pasillo principal horizontal
        self.muros.append(Wall(200, 300, 600, 20))
        self.muros.append(Wall(200, 320, 20, 300))
        
        # Cámara izquierda
        self.muros.append(Wall(400, 500, 200, 20))
        self.muros.append(Wall(400, 700, 20, 200))
        
        # Pasillo central
        self.muros.append(Wall(800, 200, 20, 400))
        self.muros.append(Wall(820, 580, 300, 20))
        
        # Cámara superior derecha
        self.muros.append(Wall(1200, 100, 20, 400))
        self.muros.append(Wall(1000, 480, 220, 20))
        
        # Pasillo inferior
        self.muros.append(Wall(300, 900, 800, 20))
        self.muros.append(Wall(1100, 700, 20, 220))
        
        # Cámara derecha compleja
        self.muros.append(Wall(1400, 300, 20, 600))
        self.muros.append(Wall(1420, 300, 300, 20))
        self.muros.append(Wall(1420, 880, 300, 20))
        
        # Obstáculos adicionales
        self.muros.append(Wall(600, 1000, 150, 20))
        self.muros.append(Wall(1000, 1100, 200, 20))
        self.muros.append(Wall(1500, 1000, 20, 300))
        
        # Posiciones posibles para la salida (diferentes ubicaciones estratégicas)
        posiciones_salida = [
            (1900, 1420),  # esquina inferior derecha
            (300, 1350),   # zona inferior izquierda
            (1850, 100),   # esquina superior derecha
            (650, 150),    # zona superior central
            (1600, 700),   # zona media derecha
            (500, 800)     # zona media izquierda
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = Salida(salida_pos[0], salida_pos[1])
        
        # Spawn points distribuidos por el mapa
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
        self.muros.append(Wall(0, 0, self.ancho, 20))
        self.muros.append(Wall(0, self.alto-20, self.ancho, 20))
        self.muros.append(Wall(0, 0, 20, self.alto))
        self.muros.append(Wall(self.ancho-20, 0, 20, self.alto))
        
        # Espiral exterior a interior
        self.muros.append(Wall(150, 150, 1700, 20))  # top
        self.muros.append(Wall(1830, 170, 20, 1200))  # right
        self.muros.append(Wall(200, 1350, 1650, 20))  # bottom
        self.muros.append(Wall(200, 250, 20, 1120))  # left
        
        # Segunda capa
        self.muros.append(Wall(350, 250, 1330, 20))
        self.muros.append(Wall(1660, 270, 20, 950))
        self.muros.append(Wall(400, 1200, 1280, 20))
        self.muros.append(Wall(400, 370, 20, 850))
        
        # Tercera capa
        self.muros.append(Wall(550, 370, 970, 20))
        self.muros.append(Wall(1500, 390, 20, 690))
        self.muros.append(Wall(600, 1060, 920, 20))
        self.muros.append(Wall(600, 490, 20, 590))
        
        # Centro con obstáculos
        self.muros.append(Wall(750, 550, 600, 20))
        self.muros.append(Wall(1330, 570, 20, 380))
        self.muros.append(Wall(800, 930, 550, 20))
        self.muros.append(Wall(800, 650, 20, 300))
        
        # Obstáculos adicionales
        self.muros.append(Wall(950, 700, 200, 20))
        self.muros.append(Wall(1000, 800, 150, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1000, 750),   # centro del laberinto
            (250, 200),    # zona exterior superior izquierda
            (1800, 1300),  # zona exterior inferior derecha
            (450, 1250),   # zona exterior inferior izquierda
            (1600, 450),   # zona intermedia derecha
            (700, 600)     # zona intermedia
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = Salida(salida_pos[0], salida_pos[1])
        
        # Enemigos en diferentes capas
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
        self.muros.append(Wall(0, 0, self.ancho, 20))
        self.muros.append(Wall(0, self.alto-20, self.ancho, 20))
        self.muros.append(Wall(0, 0, 20, self.alto))
        self.muros.append(Wall(self.ancho-20, 0, 20, self.alto))
        
        # Red de pasillos complejos - sección izquierda
        self.muros.append(Wall(150, 100, 20, 400))
        self.muros.append(Wall(170, 480, 300, 20))
        self.muros.append(Wall(300, 200, 20, 300))
        self.muros.append(Wall(320, 200, 200, 20))
        self.muros.append(Wall(500, 100, 20, 600))
        
        # Sección central
        self.muros.append(Wall(700, 150, 20, 500))
        self.muros.append(Wall(550, 630, 170, 20))
        self.muros.append(Wall(850, 250, 300, 20))
        self.muros.append(Wall(1130, 100, 20, 400))
        self.muros.append(Wall(900, 480, 250, 20))
        
        # Cámaras inferiores
        self.muros.append(Wall(200, 700, 400, 20))
        self.muros.append(Wall(200, 720, 20, 400))
        self.muros.append(Wall(220, 1100, 500, 20))
        self.muros.append(Wall(700, 800, 20, 320))
        
        # Sección derecha superior
        self.muros.append(Wall(1300, 200, 20, 400))
        self.muros.append(Wall(1320, 580, 400, 20))
        self.muros.append(Wall(1500, 300, 220, 20))
        self.muros.append(Wall(1700, 100, 20, 500))
        
        # Sección derecha inferior
        self.muros.append(Wall(900, 750, 300, 20))
        self.muros.append(Wall(1180, 650, 20, 400))
        self.muros.append(Wall(1200, 1030, 400, 20))
        self.muros.append(Wall(1400, 850, 20, 200))
        self.muros.append(Wall(1550, 700, 20, 400))
        
        # Obstáculos adicionales dispersos
        self.muros.append(Wall(350, 900, 150, 20))
        self.muros.append(Wall(850, 1000, 200, 20))
        self.muros.append(Wall(1300, 1200, 250, 20))
        self.muros.append(Wall(600, 350, 80, 20))
        self.muros.append(Wall(1450, 450, 100, 20))
        
        # Laberinto final hacia la salida
        self.muros.append(Wall(1650, 1100, 20, 300))
        self.muros.append(Wall(1670, 1380, 250, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1900, 1420),  # esquina inferior derecha (clásica)
            (100, 100),    # esquina superior izquierda
            (1850, 200),   # zona superior derecha
            (350, 1350),   # zona inferior izquierda
            (1250, 1300),  # zona inferior centro-derecha
            (850, 1150),   # zona inferior central
            (1550, 950)    # zona media derecha
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = Salida(salida_pos[0], salida_pos[1])
        
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


class Player:
    def __init__(self, nombre, color, velocidad, energia, vision):
        self.nombre = nombre
        self.color = color
        self.velocidad = velocidad
        self.energia = energia
        self.vision = vision  # radio de linterna
        self.rect = pygame.Rect(50, 50, 30, 30)  # spawn inicial
        self.pos_inicial = (50, 50)

    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        # Guardar posición anterior
        old_x, old_y = self.rect.x, self.rect.y
        
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
                # Revertir movimiento
                self.rect.x, self.rect.y = old_x, old_y
                break
    
    def resetear_posicion(self):
        """Resetea la posición del jugador al inicio"""
        self.rect.x, self.rect.y = self.pos_inicial

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, self.color, rect_pantalla)
        # Borde para mejor visibilidad
        pygame.draw.rect(ventana, BLANCO, rect_pantalla, 2)


class Enemy:
    def __init__(self, x, y, velocidad):
        self.rect = pygame.Rect(x, y, 35, 35)
        self.velocidad = velocidad
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1
        self.tiempo_cambio = 0  # para cambiar dirección ocasionalmente
        
        # Sistema de detección y persecución
        self.rango_deteccion = 250  # píxeles de rango para detectar al jugador
        self.estado = "patrullando"  # puede ser "patrullando" o "persiguiendo"
        self.velocidad_persecucion = velocidad + 1  # más rápido al perseguir
        self.tiempo_perdida = 0  # tiempo desde que perdió al jugador

    def calcular_distancia(self, jugador_rect):
        """Calcula la distancia al jugador"""
        dx = jugador_rect.centerx - self.rect.centerx
        dy = jugador_rect.centery - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def mover(self, muros, ancho_mapa, alto_mapa, jugador_rect=None):
        # Guardar posición anterior
        old_x, old_y = self.rect.x, self.rect.y
        
        # Verificar si detecta al jugador
        if jugador_rect:
            distancia = self.calcular_distancia(jugador_rect)
            
            if distancia <= self.rango_deteccion:
                self.estado = "persiguiendo"
                self.tiempo_perdida = 0
            elif self.estado == "persiguiendo":
                # Si estaba persiguiendo, mantener un poco más antes de volver a patrullar
                self.tiempo_perdida += 1
                if self.tiempo_perdida > 120:  # ~2 segundos a 60 FPS
                    self.estado = "patrullando"
        
        # Comportamiento según el estado
        if self.estado == "persiguiendo" and jugador_rect:
            # Perseguir al jugador directamente
            dx = jugador_rect.centerx - self.rect.centerx
            dy = jugador_rect.centery - self.rect.centery
            distancia = math.sqrt(dx * dx + dy * dy)
            
            if distancia > 0:
                # Normalizar y aplicar velocidad
                vel_actual = self.velocidad_persecucion
                self.rect.x += int((dx / distancia) * vel_actual)
                self.rect.y += int((dy / distancia) * vel_actual)
        else:
            # Patrullar normalmente
            if self.direccion == "horizontal":
                self.rect.x += self.velocidad * self.sentido
                # Cambiar sentido si toca los bordes del mapa
                if self.rect.left <= 20 or self.rect.right >= ancho_mapa - 20:
                    self.sentido *= -1
            else:
                self.rect.y += self.velocidad * self.sentido
                # Cambiar sentido si toca los bordes del mapa
                if self.rect.top <= 20 or self.rect.bottom >= alto_mapa - 20:
                    self.sentido *= -1
        
        # Detectar colisión con muros y cambiar dirección
        colision = False
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                colision = True
                # Revertir movimiento
                self.rect.x, self.rect.y = old_x, old_y
                
                if self.estado == "patrullando":
                    # Cambiar sentido o dirección
                    self.sentido *= -1
                    # Ocasionalmente cambiar de dirección completamente
                    if random.random() < 0.3:
                        self.direccion = "vertical" if self.direccion == "horizontal" else "horizontal"
                else:
                    # Si está persiguiendo y choca, intentar rodear
                    if random.random() < 0.5:
                        self.rect.x = old_x + random.randint(-3, 3)
                    else:
                        self.rect.y = old_y + random.randint(-3, 3)
                break

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        
        # Color según estado
        if self.estado == "persiguiendo":
            color_cuerpo = (255, 50, 50)  # Rojo más intenso
            color_ojos = (255, 255, 0)     # Amarillo brillante
        else:
            color_cuerpo = ROJO
            color_ojos = (200, 200, 100)   # Amarillo apagado
        
        pygame.draw.rect(ventana, color_cuerpo, rect_pantalla)
        
        # Efecto de ojos
        pos_ojo1 = camara.aplicar_pos(self.rect.x + 10, self.rect.y + 10)
        pos_ojo2 = camara.aplicar_pos(self.rect.x + 25, self.rect.y + 10)
        pygame.draw.circle(ventana, color_ojos, pos_ojo1, 4)
        pygame.draw.circle(ventana, color_ojos, pos_ojo2, 4)
        
        # Indicador visual adicional cuando persigue
        if self.estado == "persiguiendo":
            # Dibujar signo de exclamación encima
            pos_alerta = camara.aplicar_pos(self.rect.centerx, self.rect.y - 15)
            pygame.draw.circle(ventana, AMARILLO, pos_alerta, 8)
            pygame.draw.circle(ventana, ROJO, pos_alerta, 6)


class Game:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.nivel_actual = None
        self.numero_nivel = 1
        self.enemigos = []
        self.resultado = ""
        self.fuente = pygame.font.Font(None, 36)
        self.camara = None

    # ----------- PANTALLAS -----------

    def menu(self):
        ventana.fill(NEGRO)
        self.dibujar_texto("El Laberinto de las Sombras", 60, BLANCO, ANCHO//2, 120)
        self.dibujar_texto("3 Niveles de Mazmorras Expandidas", 35, AMARILLO, ANCHO//2, 200)
        self.dibujar_texto("Selecciona tu personaje:", 35, BLANCO, ANCHO//2, 270)
        self.dibujar_texto("[1] Explorador  [2] Cazador  [3] Ingeniero", 28, BLANCO, ANCHO//2, 320)
        self.dibujar_texto("Encuentra la salida verde en cada nivel", 25, VERDE, ANCHO//2, 380)
        self.dibujar_texto("Evita a los enemigos rojos", 25, ROJO, ANCHO//2, 410)
        self.dibujar_texto("La cámara te seguirá por el mapa", 25, (100, 200, 255), ANCHO//2, 440)
        self.dibujar_texto("ESC para salir", 25, BLANCO, ANCHO//2, 480)

    def iniciar_juego(self, tipo):
        # Personajes predeterminados
        if tipo == 1:
            self.jugador = Player("Explorador", AMARILLO, velocidad=4, energia=100, vision=150)
        elif tipo == 2:
            self.jugador = Player("Cazador", VERDE, velocidad=6, energia=70, vision=120)
        elif tipo == 3:
            self.jugador = Player("Ingeniero", (0, 150, 255), velocidad=3, energia=120, vision=180)

        # Iniciar en nivel 1
        self.numero_nivel = 1
        self.cargar_nivel(1)
        self.resultado = ""
        self.estado = "jugando"
    
    def cargar_nivel(self, numero):
        """Carga un nivel específico"""
        self.numero_nivel = numero
        self.nivel_actual = Nivel(numero)
        
        # Crear cámara con dimensiones del nivel
        self.camara = Camera(self.nivel_actual.ancho, self.nivel_actual.alto)
        
        # Crear enemigos en los spawn points del nivel
        self.enemigos = []
        for spawn_x, spawn_y in self.nivel_actual.spawn_enemigos:
            vel = random.randint(2, 4)
            self.enemigos.append(Enemy(spawn_x, spawn_y, vel))
        
        # Resetear posición del jugador
        self.jugador.resetear_posicion()

    def jugar(self):
        ventana.fill(GRIS)
        
        # Actualizar cámara para seguir al jugador
        self.camara.actualizar(self.jugador.rect)
        
        # Dibujar nivel (muros y salida)
        self.nivel_actual.dibujar(ventana, self.camara)
        
        # Mover jugador
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas, self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto)

        # Mover y dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.mover(self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto, self.jugador.rect)
            enemigo.dibujar(ventana, self.camara)

            # Colisión jugador - enemigo
            if self.jugador.rect.colliderect(enemigo.rect):
                self.resultado = "perdiste"
                self.estado = "fin"

        # Dibujar jugador
        self.jugador.dibujar(ventana, self.camara)

        # Dibujar linterna (visión circular)
        self.dibujar_linterna()

        # Verificar si llegó a la salida
        if self.jugador.rect.colliderect(self.nivel_actual.salida.rect):
            if self.numero_nivel < 3:
                # Pasar al siguiente nivel
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                # Completó todos los niveles
                self.resultado = "ganaste"
                self.estado = "fin"

        # UI
        self.dibujar_texto(f"Nivel: {self.numero_nivel}/3", 30, BLANCO, 10, 10, centrado=False)
        self.dibujar_texto(f"Energía: {int(self.jugador.energia)}", 30, BLANCO, 10, 40, centrado=False)

    def pantalla_final(self):
        ventana.fill(NEGRO)
        if self.resultado == "ganaste":
            color = VERDE
            mensaje = "¡Escapaste de las 3 mazmorras!"
            submensaje = f"Completaste todos los niveles con {self.jugador.nombre}"
        else:
            color = ROJO
            mensaje = "Fuiste atrapado en la oscuridad..."
            submensaje = f"Llegaste hasta el nivel {self.numero_nivel}"
        
        self.dibujar_texto(mensaje, 50, color, ANCHO // 2, 220)
        self.dibujar_texto(submensaje, 30, BLANCO, ANCHO // 2, 290)
        self.dibujar_texto("ENTER para volver al menú", 30, BLANCO, ANCHO // 2, 380)

    # ----------- UTILIDADES -----------

    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        font = pygame.font.Font(None, tam)
        superficie = font.render(texto, True, color)
        rect = superficie.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        ventana.blit(superficie, rect)

    def dibujar_linterna(self):
        # Crear superficie de sombra (negra semitransparente)
        sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 240))

        # Superficie para dibujar el haz de luz (gradiente)
        luz = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

        # Centro de la linterna (player en coordenadas de pantalla)
        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        mx, my = pygame.mouse.get_pos()

        # Si el mouse coincide con el centro, usar dirección por defecto
        dx, dy = mx - cx, my - cy
        if dx == 0 and dy == 0:
            angle = 0.0
        else:
            angle = math.atan2(dy, dx)

        # Parámetros del cono
        radius = max(1, int(self.jugador.vision))
        half_angle = math.radians(35)  # semiancho del haz (ajusta aquí el "amplitud")
        steps = 48  # cuantos anillos/pasos para el degradado (más = más suave)

        # Dibujar el haz como un conjunto de triángulos (fan) con alpha decreciente
        # Dibujamos de fuera hacia dentro para que las capas internas atenúen correctamente
        for i in range(steps, 0, -1):
            r = radius * (i / steps)
            a = half_angle * (i / steps)

            left = (cx + r * math.cos(angle - a), cy + r * math.sin(angle - a))
            right = (cx + r * math.cos(angle + a), cy + r * math.sin(angle + a))

            # Alpha: más oscuro hacia el borde del cono, más claro hacia el centro
            # Normalizamos al rango 0..240 (coincide con la opacidad de la sombra)
            alpha = int(240 * (i / steps))
            alpha = max(0, min(240, alpha))

            # Dibujar triángulo en la superficie de luz usando blanco semi-transparente
            pygame.draw.polygon(
                luz,
                (255, 255, 255, alpha),
                [(cx, cy), left, right]
            )

        # Restar la superficie de luz de la sombra para crear el efecto de "agujero" iluminado
        sombra.blit(luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Colocar la máscara encima de todo lo dibujado
        ventana.blit(sombra, (0, 0))

    # ----------- LOOP PRINCIPAL -----------

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
            clock.tick(60)


# ------------------------
# Ejecución
# ------------------------
if __name__ == "__main__":
    juego = Game()
    juego.ejecutar()
