import pygame
import math

class proyectil:
    """Proyectil disparado por el jugador"""
    def __init__(self, x, y, destino_x, destino_y, color):
        self.color = color
        self.velocidad = 10
        self.radio = 5
        self.rect = pygame.Rect(x, y, self.radio * 2, self.radio * 2)

        # dirección normalizada
        dx = destino_x - x
        dy = destino_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        self.dir_x = dx / dist
        self.dir_y = dy / dist

        # distancia máxima que puede recorrer
        self.alcance = 500
        self.distancia_recorrida = 0

    def mover(self, muros):
        # movimiento
        self.rect.x += int(self.dir_x * self.velocidad)
        self.rect.y += int(self.dir_y * self.velocidad)
        self.distancia_recorrida += self.velocidad

        # colisión con muros
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                return False  # desaparece si toca un muro

        # desaparecer si se aleja demasiado
        if self.distancia_recorrida >= self.alcance:
            return False

        return True  # sigue activo

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.circle(
            ventana,
            self.color,
            rect_pantalla.center,
            self.radio
        )
