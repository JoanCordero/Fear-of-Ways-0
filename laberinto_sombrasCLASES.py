import pygame
import sys
import random

# Inicialización
pygame.init()
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
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
    def __init__(self, nombre, color, velocidad, energia, vision):
        self.nombre = nombre
        self.color = color
        self.velocidad = velocidad
        self.energia = energia
        self.vision = vision  # radio de linterna
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

        # Mantener dentro de pantalla
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
        # Personajes predeterminados
        if tipo == 1:
            self.jugador = Player("Explorador", AMARILLO, velocidad=5, energia=100, vision=150)
        elif tipo == 2:
            self.jugador = Player("Cazador", VERDE, velocidad=7, energia=70, vision=120)
        elif tipo == 3:
            self.jugador = Player("Ingeniero", (0, 150, 255), velocidad=4, energia=120, vision=180)

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
        self.dibujar_texto(f"Energía: {self.jugador.energia}", 30, BLANCO, 10, 10, centrado=False)

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
        # Enmascara todo menos un círculo alrededor del jugador
        mask = pygame.Surface((ANCHO, ALTO))
        mask.fill(NEGRO)
        pygame.draw.circle(mask, (0, 0, 0, 0), self.jugador.rect.center, self.jugador.vision)
        mask.set_colorkey((0, 0, 0))
        mask.set_alpha(220)
        ventana.blit(mask, (0, 0))

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
