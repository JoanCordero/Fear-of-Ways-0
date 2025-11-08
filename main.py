import pygame
import sys
import os
from juego import juego

pygame.init()
info = pygame.display.Info()
ventana = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)


pygame.mixer.init()
pygame.mixer.music.load("musica_fondo.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)



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
    # Cargar icono de llave para usar tanto en el HUD como en el mapa
    ruta_llave = os.path.join(os.path.dirname(__file__), 'key_icon.png')
    try:
        icono_llave = pygame.image.load(ruta_llave).convert_alpha()
    except Exception:
        icono_llave = None
    nivel.ICONO_LLAVE = icono_llave
    juego_inst = juego()
    juego_inst.ejecutar()
