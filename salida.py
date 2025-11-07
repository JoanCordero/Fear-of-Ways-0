import pygame

class salida:
    """Representa la salida del nivel"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)

    def dibujar(self, ventana, camara, bloqueada=False):
        """Dibuja la salida, opcionalmente con color distinto si está bloqueada."""
        rect_pantalla = camara.aplicar(self.rect)
        if bloqueada:
            # Color más oscuro para indicar que no se puede usar aún
            pygame.draw.rect(ventana, (30, 120, 30), rect_pantalla)
            pygame.draw.rect(ventana, (0, 180, 0), rect_pantalla, 3)
        else:
            pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
            pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)
