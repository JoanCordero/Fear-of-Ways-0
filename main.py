import pygame
import sys
import os
from juego import juego

pygame.init()
ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fear of Ways")

# cargar texturas después de iniciar pygame
def cargar_texturas():
    ruta_muro = os.path.join(os.path.dirname(__file__), 'wall_texture.png')
    ruta_suelo = os.path.join(os.path.dirname(__file__), 'floor_texture.png')
    try:
        textura_muro = pygame.image.load(ruta_muro).convert()
        textura_suelo = pygame.image.load(ruta_suelo).convert()
    except:
        textura_muro = None
        textura_suelo = None
    return textura_muro, textura_suelo

if __name__ == "__main__":
    # cargar texturas y crear juego
    textura_muro, textura_suelo = cargar_texturas()
    import pared
    import nivel
    pared.TEXTURA_MURO = textura_muro
    nivel.TEXTURA_SUELO = textura_suelo
    juego_inst = juego()
    juego_inst.ejecutar()
