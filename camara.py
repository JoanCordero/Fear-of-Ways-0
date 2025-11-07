import pygame

class camara:
    """Controla la vista del jugador siguiéndolo por el mapa con zoom"""
    def __init__(self, ancho_mapa, alto_mapa):
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.8  # Factor de zoom (más grande = más cerca)
        # Propiedades para acceso directo
        self.x = 0
        self.y = 0
    
    def actualizar(self, rect_objetivo):
        """Centra la cámara en el objetivo (jugador) con zoom"""
        ancho, alto = pygame.display.get_surface().get_size()
        # Ajustar el offset considerando el zoom
        self.offset_x = rect_objetivo.centerx - (ancho / self.zoom) // 2
        self.offset_y = rect_objetivo.centery - (alto / self.zoom) // 2
        # Limitar la cámara a los bordes del mapa
        self.offset_x = max(0, min(self.offset_x, self.ancho_mapa - ancho / self.zoom))
        self.offset_y = max(0, min(self.offset_y, self.alto_mapa - alto / self.zoom))
        # Actualizar propiedades de acceso directo
        self.x = self.offset_x
        self.y = self.offset_y
    
    def aplicar(self, rect):
        """Convierte coordenadas del mundo a coordenadas de pantalla con zoom"""
        x = (rect.x - self.offset_x) * self.zoom
        y = (rect.y - self.offset_y) * self.zoom
        w = rect.width * self.zoom
        h = rect.height * self.zoom
        return pygame.Rect(int(x), int(y), int(w), int(h))
    
    def aplicar_pos(self, x, y):
        """Convierte una posición (x, y) del mundo a coordenadas de pantalla con zoom"""
        px = (x - self.offset_x) * self.zoom
        py = (y - self.offset_y) * self.zoom
        return (int(px), int(py))
