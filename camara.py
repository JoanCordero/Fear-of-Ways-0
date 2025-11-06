import pygame

class camara:
    """Controla la vista del jugador siguiéndolo por el mapa"""
    def __init__(self, ancho_mapa, alto_mapa):
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        self.offset_x = 0
        self.offset_y = 0
    
    def actualizar(self, rect_objetivo):
        """Centra la cámara en el objetivo (jugador)"""
        ancho, alto = pygame.display.get_surface().get_size()
        self.offset_x = rect_objetivo.centerx - ancho // 2
        self.offset_y = rect_objetivo.centery - alto // 2
        # Limitar la cámara a los bordes del mapa
        self.offset_x = max(0, min(self.offset_x, self.ancho_mapa - ancho))
        self.offset_y = max(0, min(self.offset_y, self.alto_mapa - alto))
    
    def aplicar(self, rect):
        """Convierte coordenadas del mundo a coordenadas de pantalla"""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height)
    
    def aplicar_pos(self, x, y):
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla"""
        return (x - self.offset_x, y - self.offset_y)
