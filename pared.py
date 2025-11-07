import pygame

class pared:
    """Representa un muro del laberinto (puede ser puerta)."""
    def __init__(self, x, y, ancho, alto, puerta=False, abierta=False, id_puerta=None):
        # Rectángulo base del muro
        self.rect = pygame.Rect(x, y, ancho, alto)
        # Si es una puerta, puede abrirse/cerrarse
        self.puerta = bool(puerta)
        self.abierta = bool(abierta)
        self.id_puerta = id_puerta

    @property
    def bloquea(self):
        """Indica si el muro impide el paso (las puertas abiertas no)."""
        return not (self.puerta and self.abierta)

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        if self.puerta:
            # Colores distintos según estado
            color = (90, 60, 20) if self.abierta else (120, 80, 40)
            borde = (180, 140, 90) if self.abierta else (220, 190, 140)
            pygame.draw.rect(ventana, color, rect_pantalla)
            pygame.draw.rect(ventana, borde, rect_pantalla, 2)
        else:
            # Muro normal
            pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla)
            pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2)  # borde
