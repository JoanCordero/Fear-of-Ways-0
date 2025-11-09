from pathlib import Path

import pygame


class salida:
    """Representa la salida del nivel."""

    def __init__(self, x: int, y: int):
        # La salida ahora es del tamaño del jugador (35x50 píxeles)
        # y se posiciona usando coordenadas centradas para coincidir con
        # la celda objetivo del laberinto.
        self._ancho_base, self._alto_base = 35, 50
        ancho, alto = self._ancho_base, self._alto_base
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.rect.center = (x, y)
        self.color_bloqueada = (100, 40, 40)
        self.color_abierta = (40, 160, 80)

        # Directorio base para intentar cargar texturas opcionales
        self._dir = Path(__file__).resolve().parent
        self._asset_dir = self._dir / "images"
        self._textura_bloqueada = self._cargar_textura(
            "salida_bloqueada.png", fallback="puerta.png"
        )
        self._textura_abierta = self._cargar_textura(
            "salida_abierta.png", fallback="puerta_abierta.png"
        )

    def dibujar(self, ventana: pygame.Surface, camara, bloqueada: bool = False) -> None:
        """Dibuja la salida. Cambia el color según si aún faltan llaves."""
        rect_pantalla = camara.aplicar(self.rect)

        # Escalar según el zoom de la cámara
        ancho_escalado = max(1, int(self._ancho_base * camara.zoom))
        alto_escalado = max(1, int(self._alto_base * camara.zoom))

        textura = self._textura_bloqueada if bloqueada else self._textura_abierta

        if textura:
            img_escalada = pygame.transform.smoothscale(
                textura, (ancho_escalado, alto_escalado)
            )
            ventana.blit(img_escalada, rect_pantalla.topleft)
        else:
            superficie = pygame.Surface((ancho_escalado, alto_escalado), pygame.SRCALPHA)
            color_fondo = self.color_bloqueada if bloqueada else self.color_abierta
            pygame.draw.rect(
                superficie,
                (*color_fondo, 220),
                superficie.get_rect(),
                border_radius=6,
            )
            pygame.draw.rect(
                superficie,
                (255, 255, 255, 180),
                superficie.get_rect(),
                3,
                border_radius=6,
            )
            ventana.blit(superficie, rect_pantalla.topleft)

    def verificar_proximidad_jugador(self, jugador_rect, llaves_restantes: int) -> tuple:
        """
        Verifica si el jugador está cerca de la salida.
        Retorna (bool, str): (está_cerca, mensaje)
        """
        # Expandir el área de detección para que sea más generosa
        area_deteccion = self.rect.inflate(60, 60)

        if area_deteccion.colliderect(jugador_rect):
            if llaves_restantes > 0:
                return (True, f"Salida bloqueada. Necesitas {llaves_restantes} llave{'s' if llaves_restantes > 1 else ''} más")
            else:
                return (True, "¡Salida libre! Presiona para avanzar")

        return (False, "")

    def _cargar_textura(self, nombre_principal: str, fallback: str | None = None):
        """Intenta cargar y escalar una textura opcional para la salida."""

        for nombre in filter(None, (nombre_principal, fallback)):
            ruta = (self._asset_dir / nombre).resolve()
            if ruta.exists():
                try:
                    return pygame.image.load(str(ruta)).convert_alpha()
                except pygame.error:
                    continue

        return None
