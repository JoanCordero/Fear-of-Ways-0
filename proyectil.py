import pygame
import math

class proyectil:
    """Proyectil disparado por el jugador"""
    def __init__(self, pos_inicial_x, pos_inicial_y, destino_x, destino_y, color):
        # apariencia y propiedades básicas
        self.color = color
        self.velocidad = 10
        self.radio = 5
        self.rect = pygame.Rect(pos_inicial_x, pos_inicial_y, self.radio * 2, self.radio * 2)

        # dirección normalizada hacia el punto destino
        diferencia_x = destino_x - pos_inicial_x
        diferencia_y = destino_y - pos_inicial_y
        distancia = math.hypot(diferencia_x, diferencia_y)
        if distancia == 0:
            distancia = 1
        self.direccion_x = diferencia_x / distancia
        self.direccion_y = diferencia_y / distancia

        # distancia máxima y progreso actual
        self.alcance_maximo = 500
        self.distancia_recorrida = 0

    def mover(self, muros):
        # avanza según su dirección y velocidad
        self.rect.x += int(self.direccion_x * self.velocidad)
        self.rect.y += int(self.direccion_y * self.velocidad)
        self.distancia_recorrida += self.velocidad

        # desaparece si choca con un muro
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                return False

        # desaparece si supera su alcance
        if self.distancia_recorrida >= self.alcance_maximo:
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