import pygame

# la textura se cargará desde main.py
TEXTURA_MURO = None


class pared:
    """Representa un muro del laberinto."""

    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)

    @property
    def bloquea(self) -> bool:
        """Devuelve True si este muro bloquea al jugador/enemigos."""
        return True

    def dibujar(self, ventana: pygame.Surface, camara) -> None:
        """Dibuja el muro sobre la superficie de la ventana usando la cámara."""
        rect_pantalla = camara.aplicar(self.rect)
        # Muro normal: intenta usar textura. Los bordes tienen radios más suaves para
        # evitar una apariencia completamente cuadrada. Incrementamos el radio para
        # que el efecto sea visible incluso con texturas.
        borde_radio = 8
        if TEXTURA_MURO:
            # Escalar la textura al tamaño del muro en pantalla
            textura_escalada = pygame.transform.scale(TEXTURA_MURO, (rect_pantalla.w, rect_pantalla.h))
            ventana.blit(textura_escalada, rect_pantalla)
            # Dibujar un contorno oscuro con bordes redondeados
            pygame.draw.rect(ventana, (30, 30, 30), rect_pantalla, 1, border_radius=borde_radio)
        else:
            # Fallback: color sólido con bordes redondeados si no hay textura cargada
            pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla, border_radius=borde_radio)
            pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2, border_radius=borde_radio)
