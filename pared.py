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
            # Tiling (repetir) de la textura para evitar estirados en muros grandes.
            tex = TEXTURA_MURO
            tex_w, tex_h = tex.get_size()

            # Crear una superficie temporal del tamaño del rect en pantalla
            try:
                superficie = pygame.Surface((rect_pantalla.w, rect_pantalla.h)).convert()
            except Exception:
                superficie = pygame.Surface((rect_pantalla.w, rect_pantalla.h))

            # Rellenar repitiendo la textura de forma simple (tiling) para evitar estirados
            for sx in range(0, rect_pantalla.w, tex_w):
                for sy in range(0, rect_pantalla.h, tex_h):
                    superficie.blit(tex, (sx, sy))

            ventana.blit(superficie, rect_pantalla)
            # Dibujar un contorno oscuro con bordes redondeados
            pygame.draw.rect(ventana, (30, 30, 30), rect_pantalla, 1, border_radius=borde_radio)
        else:
            # Fallback: color sólido con bordes redondeados si no hay textura cargada
            pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla, border_radius=borde_radio)
            pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2, border_radius=borde_radio)
