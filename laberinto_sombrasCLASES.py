import pygame
import sys
import random
import math

# Inicialización
pygame.init()
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h # capta direcamente la resolucion del monitor para pantalla completa
ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("El Laberinto de las Sombras")

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

class Player:
    def __init__(self, nombre, color, velocidad, vida, vision):
        self.nombre = nombre
        self.color = color
        self.velocidad = velocidad
        self.vida = vida          # ← ahora sí existe
        self.vision = vision
        self.rect = pygame.Rect(380, 280, 40, 40)

    def mover(self, teclas):
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad

        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))


    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, self.rect)


class Enemy:
    def __init__(self, x, y, velocidad):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.velocidad = velocidad
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1

    def mover(self):
        if self.direccion == "horizontal":
            self.rect.x += self.velocidad * self.sentido
            if self.rect.left <= 0 or self.rect.right >= ANCHO:
                self.sentido *= -1
        else:
            self.rect.y += self.velocidad * self.sentido
            if self.rect.top <= 0 or self.rect.bottom >= ALTO:
                self.sentido *= -1

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, ROJO, self.rect)


class Game:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.enemigos = []
        self.resultado = ""
        self.fuente = pygame.font.Font(None, 36)

    # ----------- PANTALLAS -----------

    def menu(self):
        ventana.fill(NEGRO)
        self.dibujar_texto("El Laberinto de las Sombras", 60, BLANCO, ANCHO//2, 150)
        self.dibujar_texto("Selecciona tu personaje:", 40, BLANCO, ANCHO//2, 250)
        self.dibujar_texto("[1] Explorador  [2] Cazador  [3] Ingeniero", 30, BLANCO, ANCHO//2, 320)
        self.dibujar_texto("ESC para salir", 30, BLANCO, ANCHO//2, 370)
    def iniciar_juego(self, tipo):
        if tipo == 1:
            self.jugador = Player("Explorador", AMARILLO, velocidad=5, vida=100, vision=150)
        elif tipo == 2:
            self.jugador = Player("Cazador", VERDE, velocidad=7, vida=70, vision=120)
        elif tipo == 3:
            self.jugador = Player("Ingeniero", (0, 150, 255), velocidad=4, vida=120, vision=180)

        # Crear enemigos
        self.enemigos = [Enemy(random.randint(100, 700), random.randint(100, 500), random.randint(2, 4)) for _ in range(4)]
        self.resultado = ""
        self.estado = "jugando"

    def jugar(self):
        ventana.fill(GRIS)
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas)

        # Mover y dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.mover()
            enemigo.dibujar(ventana)

            # Colisión jugador - enemigo
            if self.jugador.rect.colliderect(enemigo.rect):
                self.resultado = "perdiste"
                self.estado = "fin"

        # Dibujar jugador
        self.jugador.dibujar(ventana)

        # Dibujar linterna (visión circular)
        self.dibujar_linterna()

        # Condición de victoria: esquina inferior derecha
        if self.jugador.rect.x > 750 and self.jugador.rect.y > 550:
            self.resultado = "ganaste"
            self.estado = "fin"

        # UI simple
        # Mostrar en pantalla
        self.dibujar_texto(f"Vida: {self.jugador.vida}", 30, BLANCO, 10, 10, centrado=False)

    def pantalla_final(self):
        ventana.fill(NEGRO)
        if self.resultado == "ganaste":
            color = VERDE
            mensaje = "¡Escapaste del laberinto!"
        else:
            color = ROJO
            mensaje = "Fuiste atrapado en la oscuridad..."
        self.dibujar_texto(mensaje, 50, color, ANCHO // 2, 250)
        self.dibujar_texto("ENTER para volver al menú", 30, BLANCO, ANCHO // 2, 350)

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

        # Centro de la linterna (player) y objetivo (mouse)
        cx, cy = self.jugador.rect.center
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
            # (al blitearlo sobre la sombra con BLEND_RGBA_SUB reduciremos la opacidad
            #  de la sombra en las zonas donde la luz está presente)
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
