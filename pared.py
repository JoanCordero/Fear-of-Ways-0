import pygame

class pared:
    """Representa un muro del laberinto"""
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla)
        pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2)  # borde
