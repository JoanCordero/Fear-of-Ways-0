import pygame
import os

class salida:
    """Representa la salida del nivel."""
    def __init__(self, x: int, y: int):
        # La salida ahora es del tamaño del jugador (35x50 píxeles)
        self.rect = pygame.Rect(x, y, 35, 50)
        
        # Cargar las imágenes de la puerta
        try:
            self.img_cerrada = pygame.image.load("images/puerta.png").convert_alpha()
            self.img_cerrada = pygame.transform.scale(self.img_cerrada, (35, 50))
        except:
            self.img_cerrada = None
            
        try:
            self.img_abierta = pygame.image.load("images/puerta_abierta.png").convert_alpha()
            self.img_abierta = pygame.transform.scale(self.img_abierta, (35, 50))
        except:
            self.img_abierta = None

    def dibujar(self, ventana: pygame.Surface, camara, bloqueada: bool = False) -> None:
        """Dibuja la salida. Si está bloqueada (faltan llaves), muestra puerta cerrada, sino abierta."""
        rect_pantalla = camara.aplicar(self.rect)
        
        # Escalar la imagen según el zoom de la cámara
        ancho_escalado = max(1, int(35 * camara.zoom))
        alto_escalado = max(1, int(50 * camara.zoom))
        
        if bloqueada:
            # Puerta cerrada (sin llaves)
            if self.img_cerrada:
                img_escalada = pygame.transform.smoothscale(self.img_cerrada, (ancho_escalado, alto_escalado))
                ventana.blit(img_escalada, rect_pantalla.topleft)
            else:
                # Fallback: cuadrado verde oscuro
                pygame.draw.rect(ventana, (30, 120, 30), rect_pantalla)
                pygame.draw.rect(ventana, (0, 180, 0), rect_pantalla, 3)
        else:
            # Puerta abierta (con llaves)
            if self.img_abierta:
                img_escalada = pygame.transform.smoothscale(self.img_abierta, (ancho_escalado, alto_escalado))
                ventana.blit(img_escalada, rect_pantalla.topleft)
            else:
                # Fallback: cuadrado verde brillante
                pygame.draw.rect(ventana, (0, 200, 0), rect_pantalla)
                pygame.draw.rect(ventana, (0, 255, 0), rect_pantalla, 3)
    
    def verificar_proximidad_jugador(self, jugador_rect, llaves_restantes: int) -> tuple:
        """
        Verifica si el jugador está cerca de la puerta.
        Retorna (bool, str): (está_cerca, mensaje)
        """
        # Expandir el área de detección para que sea más generosa
        area_deteccion = self.rect.inflate(60, 60)
        
        if area_deteccion.colliderect(jugador_rect):
            if llaves_restantes > 0:
                return (True, f"Puerta cerrada. Necesitas {llaves_restantes} llave{'s' if llaves_restantes > 1 else ''} más")
            else:
                return (True, "¡Puerta abierta! Presiona para avanzar")
        
        return (False, "")
