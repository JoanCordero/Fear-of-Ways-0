import pygame
import random
from pared import pared
from salida import salida

class nivel:
    """Define un nivel con su laberinto, enemigos y salida"""
    def __init__(self, numero):
        self.numero = numero
        self.muros = []
        self.salida = None
        self.spawn_enemigos = []
        # Dimensiones del mapa (más grandes que la pantalla)
        self.ancho = 2000
        self.alto = 1500
        self.crear_nivel()
    
    def crear_nivel(self):
        if self.numero == 1:
            self.crear_nivel_1()
        elif self.numero == 2:
            self.crear_nivel_2()
        elif self.numero == 3:
            self.crear_nivel_3()
    
    def crear_nivel_1(self):
        """Nivel 1: Laberinto expandido con múltiples cámaras"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))  # arriba
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))  # abajo
        self.muros.append(pared(0, 0, 20, self.alto))  # izquierda
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))  # derecha

        # Pasillo principal horizontal
        self.muros.append(pared(200, 300, 600, 20))
        self.muros.append(pared(200, 320, 20, 300))

        # Cámara izquierda
        self.muros.append(pared(400, 500, 200, 20))
        self.muros.append(pared(400, 700, 20, 200))

        # Pasillo central
        self.muros.append(pared(800, 200, 20, 400))
        self.muros.append(pared(820, 580, 300, 20))

        # Cámara superior derecha
        self.muros.append(pared(1200, 100, 20, 400))
        self.muros.append(pared(1000, 480, 220, 20))

        # Pasillo inferior
        self.muros.append(pared(300, 900, 800, 20))
        self.muros.append(pared(1100, 700, 20, 220))

        # Cámara derecha 
        self.muros.append(pared(1400, 300, 20, 600))
        self.muros.append(pared(1420, 300, 300, 20))
        self.muros.append(pared(1420, 880, 300, 20))

        # Obstáculos adicionales
        self.muros.append(pared(600, 1000, 150, 20))
        self.muros.append(pared(1000, 1100, 200, 20))
        self.muros.append(pared(1500, 1000, 20, 300))

        # Posiciones posibles para la salida
        posiciones_salida = [
            (1900, 1420),
            (300, 1350),
            (1850, 100),
            (650, 150),
            (1600, 700),
            (500, 800)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Spawn points
        self.spawn_enemigos = [
            (300, 400),
            (500, 600),
            (900, 350),
            (1100, 250),
            (1300, 800),
            (700, 1050),
            (1600, 500)
        ]
    
    def crear_nivel_2(self):
        """Nivel 2: Laberinto en espiral expandido"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))
        
        # Espiral exterior a interior
        self.muros.append(pared(150, 150, 1700, 20))
        self.muros.append(pared(1830, 170, 20, 1200))
        self.muros.append(pared(200, 1350, 1650, 20))
        self.muros.append(pared(200, 250, 20, 1120))
        
        # Segunda capa
        self.muros.append(pared(350, 250, 1330, 20))
        self.muros.append(pared(1660, 270, 20, 950))
        self.muros.append(pared(400, 1200, 1280, 20))
        self.muros.append(pared(400, 370, 20, 850))
        
        # Tercera capa
        self.muros.append(pared(550, 370, 970, 20))
        self.muros.append(pared(1500, 390, 20, 690))
        self.muros.append(pared(600, 1060, 920, 20))
        self.muros.append(pared(600, 490, 20, 590))
        
        # Centro con obstáculos
        self.muros.append(pared(750, 550, 600, 20))
        self.muros.append(pared(1330, 570, 20, 380))
        self.muros.append(pared(800, 930, 550, 20))
        self.muros.append(pared(800, 650, 20, 300))
        
        # Obstáculos adicionales
        self.muros.append(pared(950, 700, 200, 20))
        self.muros.append(pared(1000, 800, 150, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1000, 750),
            (250, 200),
            (1800, 1300),
            (450, 1250),
            (1600, 450),
            (700, 600)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Enemigos
        self.spawn_enemigos = [
            (250, 200),
            (1700, 300),
            (300, 1300),
            (500, 320),
            (1550, 600),
            (650, 1100),
            (900, 600),
            (1200, 800),
            (1100, 450)
        ]
    
    def crear_nivel_3(self):
        """Nivel 3: Laberinto caótico expandido"""
        # Bordes exteriores
        self.muros.append(pared(0, 0, self.ancho, 20))
        self.muros.append(pared(0, self.alto-20, self.ancho, 20))
        self.muros.append(pared(0, 0, 20, self.alto))
        self.muros.append(pared(self.ancho-20, 0, 20, self.alto))
        
        # Red de pasillos complejos - sección izquierda
        self.muros.append(pared(150, 100, 20, 400))
        self.muros.append(pared(170, 480, 300, 20))
        self.muros.append(pared(300, 200, 20, 300))
        self.muros.append(pared(320, 200, 200, 20))
        self.muros.append(pared(500, 100, 20, 600))
        
        # Sección central
        self.muros.append(pared(700, 150, 20, 500))
        self.muros.append(pared(550, 630, 170, 20))
        self.muros.append(pared(850, 250, 300, 20))
        self.muros.append(pared(1130, 100, 20, 400))
        self.muros.append(pared(900, 480, 250, 20))
        
        # Cámaras inferiores
        self.muros.append(pared(200, 700, 400, 20))
        self.muros.append(pared(200, 720, 20, 400))
        self.muros.append(pared(220, 1100, 500, 20))
        self.muros.append(pared(700, 800, 20, 320))
        
        # Sección derecha superior
        self.muros.append(pared(1300, 200, 20, 400))
        self.muros.append(pared(1320, 580, 400, 20))
        self.muros.append(pared(1500, 300, 220, 20))
        self.muros.append(pared(1700, 100, 20, 500))
        
        # Sección derecha inferior
        self.muros.append(pared(900, 750, 300, 20))
        self.muros.append(pared(1180, 650, 20, 400))
        self.muros.append(pared(1200, 1030, 400, 20))
        self.muros.append(pared(1400, 850, 20, 200))
        self.muros.append(pared(1550, 700, 20, 400))
        
        # Obstáculos adicionales dispersos
        self.muros.append(pared(350, 900, 150, 20))
        self.muros.append(pared(850, 1000, 200, 20))
        self.muros.append(pared(1300, 1200, 250, 20))
        self.muros.append(pared(600, 350, 80, 20))
        self.muros.append(pared(1450, 450, 100, 20))
        
        # Laberinto final hacia la salida
        self.muros.append(pared(1650, 1100, 20, 300))
        self.muros.append(pared(1670, 1380, 250, 20))
        
        # Posiciones posibles para la salida
        posiciones_salida = [
            (1900, 1420),
            (100, 100),
            (1850, 200),
            (350, 1350),
            (1250, 1300),
            (850, 1150),
            (1550, 950)
        ]
        salida_pos = random.choice(posiciones_salida)
        self.salida = salida(salida_pos[0], salida_pos[1])
        
        # Muchos enemigos distribuidos
        self.spawn_enemigos = [
            (200, 250),
            (400, 350),
            (250, 850),
            (550, 550),
            (650, 300),
            (950, 350),
            (1050, 200),
            (850, 900),
            (1100, 850),
            (1250, 350),
            (1600, 350),
            (1450, 950),
            (1300, 1250),
            (1750, 1200)
        ]
    
    def dibujar(self, ventana, camara):
        for muro in self.muros:
            muro.dibujar(ventana, camara)
        self.salida.dibujar(ventana, camara)
