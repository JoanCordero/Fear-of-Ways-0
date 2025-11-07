import pygame

class salida:
    """Representa la salida del nivel."""
    def __init__(self, x: int, y: int):
        # la salida ocupa un cuadrado de 50×50 píxeles
        self.rect = pygame.Rect(x, y, 50, 50)

    def dibujar(self, ventana: pygame.Surface, camara, bloqueada: bool = False) -> None:
        """Dibuja la salida. Si está bloqueada (faltan llaves), se colorea más oscura."""
        rect_pantalla = camara.aplicar(self.rect)
        if bloqueada:
            pygame.draw.rect(ventana, (30, 120, 30), rect_pantalla)
            pygame.draw.rect(ventana, (0, 180, 0), rect_pantalla, 3)
        else:
            pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
            pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)
