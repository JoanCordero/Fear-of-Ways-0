import pygame
import os

# la textura se cargará desde main.py
TEXTURA_MURO = None


class pared:
    """Representa un muro del laberinto (puede ser puerta)."""

    def __init__(self, x, y, ancho, alto, puerta: bool = False, abierta: bool = False, id_puerta=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.puerta = bool(puerta)
        self.abierta = bool(abierta)
        self.id_puerta = id_puerta

    @property
    def bloquea(self) -> bool:
        """Devuelve True si este muro bloquea al jugador/enemigos. Las puertas abiertas no bloquean."""
        return not (self.puerta and self.abierta)

    def dibujar(self, ventana: pygame.Surface, camara) -> None:
        """Dibuja el muro sobre la superficie de la ventana usando la cámara."""
        rect_pantalla = camara.aplicar(self.rect)
        # Si es puerta, dibujamos un rectángulo con color diferente
        if self.puerta:
            if self.abierta:
                # Puerta abierta: verde oscuro translúcido
                color_fondo = (40, 100, 40)
                color_borde = (80, 200, 80)
                # Dibujar con efecto de apertura
                pygame.draw.rect(ventana, color_fondo, rect_pantalla)
                pygame.draw.rect(ventana, color_borde, rect_pantalla, 3)
                # Líneas diagonales para indicar apertura
                pygame.draw.line(ventana, (120, 255, 120), 
                               rect_pantalla.topleft, rect_pantalla.bottomright, 2)
                pygame.draw.line(ventana, (120, 255, 120),
                               rect_pantalla.topright, rect_pantalla.bottomleft, 2)
            else:
                # Puerta cerrada: marrón oscuro sólido
                color_fondo = (120, 80, 40)
                color_borde = (220, 190, 140)
                pygame.draw.rect(ventana, color_fondo, rect_pantalla)
                # Detalles de madera
                num_tablas = max(3, rect_pantalla.h // 30) if rect_pantalla.h > rect_pantalla.w else max(3, rect_pantalla.w // 30)
                for i in range(1, num_tablas):
                    if rect_pantalla.h > rect_pantalla.w:  # Puerta vertical
                        y_pos = rect_pantalla.y + (rect_pantalla.h * i // num_tablas)
                        pygame.draw.line(ventana, (90, 60, 30),
                                       (rect_pantalla.x, y_pos), (rect_pantalla.right, y_pos), 1)
                    else:  # Puerta horizontal
                        x_pos = rect_pantalla.x + (rect_pantalla.w * i // num_tablas)
                        pygame.draw.line(ventana, (90, 60, 30),
                                       (x_pos, rect_pantalla.y), (x_pos, rect_pantalla.bottom), 1)
                pygame.draw.rect(ventana, color_borde, rect_pantalla, 3)
        else:
            # Muro normal: intentar usar textura
            if TEXTURA_MURO:
                # Escalar la textura al tamaño del muro en pantalla
                textura_escalada = pygame.transform.scale(TEXTURA_MURO, (rect_pantalla.w, rect_pantalla.h))
                ventana.blit(textura_escalada, rect_pantalla)
                # Opcionalmente dibujar borde oscuro para delimitar
                pygame.draw.rect(ventana, (30, 30, 30), rect_pantalla, 1)
            else:
                # Fallback: color sólido si no hay textura cargada
                pygame.draw.rect(ventana, (60, 60, 60), rect_pantalla)
                pygame.draw.rect(ventana, (80, 80, 80), rect_pantalla, 2)