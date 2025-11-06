import pygame
import sys
from juego import juego

pygame.init()
ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fear of Ways")

if __name__ == "__main__":
    juego_inst = juego()
    juego_inst.ejecutar()
