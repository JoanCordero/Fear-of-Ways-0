import pygame

class salida:
    """Representa la salida del nivel"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
    
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
        pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)
