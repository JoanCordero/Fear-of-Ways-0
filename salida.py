import pygame



class salida:
    """Representa la salida del nivel."""

    def __init__(self, x: int, y: int):
        # La salida ahora es del tamaño del jugador (35x50 píxeles)
        self.rect = pygame.Rect(x, y, 35, 50)
        self.color_bloqueada = (100, 40, 40)
        self.color_abierta = (40, 160, 80)
        
        # Cargar imágenes de puerta cerrada y abierta
        self._dir = os.path.dirname(__file__)
        try:
            self.img_cerrada = pygame.image.load(os.path.join(self._dir, 'images', 'puerta.png')).convert_alpha()
            print("Imagen de puerta cerrada cargada correctamente")
        except (pygame.error, FileNotFoundError) as e:
            self.img_cerrada = None
            print(f"Advertencia: No se pudo cargar images/puerta.png - {e}")
        
        try:
            self.img_abierta = pygame.image.load(os.path.join(self._dir, 'images', 'puerta_abierta.png')).convert_alpha()
            print("Imagen de puerta abierta cargada correctamente")
        except (pygame.error, FileNotFoundError) as e:
            self.img_abierta = None
            print(f"Advertencia: No se pudo cargar images/puerta_abierta.png - {e}")

    def dibujar(self, ventana: pygame.Surface, camara, bloqueada: bool = False) -> None:
        """Dibuja la salida. Cambia el color según si aún faltan llaves."""
        rect_pantalla = camara.aplicar(self.rect)

        # Escalar según el zoom de la cámara
        ancho_escalado = max(1, int(35 * camara.zoom))
        alto_escalado = max(1, int(50 * camara.zoom))

        superficie = pygame.Surface((ancho_escalado, alto_escalado), pygame.SRCALPHA)
        color_fondo = self.color_bloqueada if bloqueada else self.color_abierta
        pygame.draw.rect(superficie, (*color_fondo, 220), superficie.get_rect(), border_radius=6)
        pygame.draw.rect(superficie, (255, 255, 255, 180), superficie.get_rect(), 3, border_radius=6)
        ventana.blit(superficie, rect_pantalla.topleft)
        # Usar imagen si está disponible, sino fallback a rectángulo
        img_actual = self.img_cerrada if bloqueada else self.img_abierta
        
        if img_actual:
            # Escalar la imagen al tamaño con zoom
            img_escalada = pygame.transform.smoothscale(img_actual, (ancho_escalado, alto_escalado))
            ventana.blit(img_escalada, rect_pantalla.topleft)
        else:
            # Fallback: dibujar rectángulo con color
            superficie = pygame.Surface((ancho_escalado, alto_escalado), pygame.SRCALPHA)
            color_fondo = self.color_bloqueada if bloqueada else self.color_abierta
            pygame.draw.rect(superficie, (*color_fondo, 220), superficie.get_rect(), border_radius=6)
            pygame.draw.rect(superficie, (255, 255, 255, 180), superficie.get_rect(), 3, border_radius=6)
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
            ruta = os.path.join(self._asset_dir, nombre)
            if os.path.exists(ruta):
                try:
                    return pygame.image.load(ruta).convert_alpha()
                except pygame.error:
                    continue

        return None
