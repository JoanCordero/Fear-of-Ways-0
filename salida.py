import pygame

class salida:
    """Representa la salida del nivel"""
    def __init__(self, x, y):
        # rectángulo de la salida
        self.rect = pygame.Rect(x, y, 50, 50)

    def dibujar(self, ventana, camara, bloqueada: bool = False):
        """
        Dibuja la salida. Si está bloqueada (p.ej. faltan llaves), usa colores más oscuros.

        Args:
            ventana: superficie donde dibujar.
            camara: cámara para ajustar las coordenadas.
            bloqueada: muestra si aún no se puede usar la salida.
        """
        rect_pantalla = camara.aplicar(self.rect)
        if bloqueada:
            # salida bloqueada: colores más apagados
            pygame.draw.rect(ventana, (30, 120, 30), rect_pantalla)
            pygame.draw.rect(ventana, (0, 180, 0), rect_pantalla, 3)
        else:
            pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
            pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)
