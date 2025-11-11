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
        ancho_pantalla, alto_pantalla = pygame.display.get_surface().get_size()
        # Tamaño visible del mundo en función del zoom
        ancho_mundo_visible = ancho_pantalla / self.zoom
        alto_mundo_visible = alto_pantalla / self.zoom
        # Centrar la cámara en el objetivo
        self.offset_x = rect_objetivo.centerx - ancho_mundo_visible / 2
        self.offset_y = rect_objetivo.centery - alto_mundo_visible / 2
        # Limitar a los bordes del mapa para no mostrar área vacía
        self.offset_x = max(0.0, min(self.offset_x, self.ancho_mapa - ancho_mundo_visible))
        self.offset_y = max(0.0, min(self.offset_y, self.alto_mapa - alto_mundo_visible))
        # Actualizar alias
        self.x = self.offset_x
        self.y = self.offset_y

    def aplicar(self, rect: pygame.Rect) -> pygame.Rect:
        """Convierte un rectángulo del mundo a coordenadas de pantalla aplicando zoom."""
        pos_x_pantalla = (rect.x - self.offset_x) * self.zoom
        pos_y_pantalla = (rect.y - self.offset_y) * self.zoom
        ancho_escalado = rect.width * self.zoom
        alto_escalado = rect.height * self.zoom
        return pygame.Rect(int(pos_x_pantalla), int(pos_y_pantalla), int(ancho_escalado), int(alto_escalado))

    def aplicar_pos(self, posicion_x: float, posicion_y: float) -> tuple[int, int]:
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla con zoom."""
        pos_x_pantalla = (posicion_x - self.offset_x) * self.zoom
        pos_y_pantalla = (posicion_y - self.offset_y) * self.zoom
        return int(pos_x_pantalla), int(pos_y_pantalla)