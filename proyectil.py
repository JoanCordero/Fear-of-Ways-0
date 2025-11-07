import pygame
import math

class proyectil:
    """Proyectil disparado por el jugador"""
    def __init__(self, x, y, destino_x, destino_y, color):
        # apariencia y propiedades básicas
        self.color = color
        self.velocidad = 10
        self.radio = 5
        self.rect = pygame.Rect(x, y, self.radio * 2, self.radio * 2)

        # dirección normalizada hacia el punto destino
        dx = destino_x - x
        dy = destino_y - y
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            distancia = 1
        self.dir_x = dx / distancia
        self.dir_y = dy / distancia

        # distancia máxima y progreso actual
        self.alcance = 500
        self.distancia_recorrida = 0

    def mover(self, muros):
        # avanza según su dirección y velocidad
        self.rect.x += int(self.dir_x * self.velocidad)
        self.rect.y += int(self.dir_y * self.velocidad)
        self.distancia_recorrida += self.velocidad

        # desaparece si choca con un muro
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                return False

        # desaparece si supera su alcance
        if self.distancia_recorrida >= self.alcance:
            return False

        return True  # sigue activo

    def dibujar(self, ventana, camara):
        # dibuja el proyectil como un pequeño círculo
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.circle(
            ventana,
            self.color,
            rect_pantalla.center,
            self.radio
        )