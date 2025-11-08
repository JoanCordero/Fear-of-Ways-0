import pygame

class camara:
    """Controla la vista del jugador siguiéndolo por el mapa con soporte de zoom.

    Este comportamiento permite acercar o alejar la imagen con respecto al personaje.
    Ajustando el atributo ``zoom`` se puede obtener un efecto de cámara más próxima
    al jugador para dar la sensación de un entorno más grande sin modificar el
    tamaño real del laberinto.
    """

    def __init__(self, ancho_mapa: int, alto_mapa: int) -> None:
        # dimensiones del mapa en coordenadas del mundo
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        # desplazamiento de la cámara respecto al origen del mapa
        self.offset_x = 0.0
        self.offset_y = 0.0
        # factor de zoom; valores mayores acercan la cámara al jugador
        # Un valor de aproximadamente 2.2 acerca más la vista al personaje,
        # dando una sensación de mapa más grande sin alterar el tamaño real del nivel.
        self.zoom = 2.2
        # alias para compatibilidad con código existente
        self.x = 0.0
        self.y = 0.0

    def actualizar(self, rect_objetivo: pygame.Rect) -> None:
        """Centra la cámara en el rectángulo objetivo (jugador) aplicando zoom.

        Calcula los offsets ``offset_x`` y ``offset_y`` de forma que el
        objetivo quede centrado en pantalla. El factor de zoom reduce la
        porción visible del mapa y aumenta el tamaño aparente de los objetos.
        """
        ancho, alto = pygame.display.get_surface().get_size()
        # Tamaño visible del mundo en función del zoom
        vis_mundo_ancho = ancho / self.zoom
        vis_mundo_alto = alto / self.zoom
        # Centrar la cámara en el objetivo
        self.offset_x = rect_objetivo.centerx - vis_mundo_ancho / 2
        self.offset_y = rect_objetivo.centery - vis_mundo_alto / 2
        # Limitar a los bordes del mapa para no mostrar área vacía
        self.offset_x = max(0.0, min(self.offset_x, self.ancho_mapa - vis_mundo_ancho))
        self.offset_y = max(0.0, min(self.offset_y, self.alto_mapa - vis_mundo_alto))
        # Actualizar alias
        self.x = self.offset_x
        self.y = self.offset_y

    def aplicar(self, rect: pygame.Rect) -> pygame.Rect:
        """Convierte un rectángulo del mundo a coordenadas de pantalla aplicando zoom."""
        x = (rect.x - self.offset_x) * self.zoom
        y = (rect.y - self.offset_y) * self.zoom
        w = rect.width * self.zoom
        h = rect.height * self.zoom
        return pygame.Rect(int(x), int(y), int(w), int(h))

    def aplicar_pos(self, x: float, y: float) -> tuple[int, int]:
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla con zoom."""
        px = (x - self.offset_x) * self.zoom
        py = (y - self.offset_y) * self.zoom
        return int(px), int(py)
