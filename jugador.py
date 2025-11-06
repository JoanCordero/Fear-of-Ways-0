import pygame
import math

blanco = (255, 255, 255)

class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision):
        #Identidad
        self.nombre = nombre
        self.color = color
        #Moviemiento base
        self.velocidad_base = float(velocidad) #velocidad cuando camina
        self.rect = pygame.Rect(50,50,30,30)  #spawn inicial
        self.pos_inicial = (50, 50)
        
        #Linterna
        self.vision = float(vision)  # radio de linterna

        #Energia (para correr)
        self.energia_max = float(energia)
        self.energia = float(energia)
        
        # Vida (aun no se usa en la logica global; la vamos activar cuando agreguemos daño)
        self.vida_max = 3
        self.vida = 3
        
    #####################
    # Moviemiento de correr y colision por ejes
    #####################
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        # Direcciones simples
        dx = (1 if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) else 0) - \
                (1 if(teclas[pygame.K_a] or teclas[pygame.K_LEFT]) else 0)
        dy = (1 if (teclas[pygame.K_s] or teclas[pygame.K_DOWN])  else 0) - \
             (1 if (teclas[pygame.K_w] or teclas[pygame.K_UP])    else 0)
        
        # evitar problemas en las diagonales para que no sean tan rapidas
        mag = math.hypot(dx, dy)
        if mag != 0:
            dx /= mag
            dy /= mag
            
        # Correr con shift: mas velocidad pero gastamos mas energia; si no regenera
        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0.1
        velocidad = self.velocidad_base * (1.6 if sprint else 1.0)    
        
        if sprint and mag != 0:
            #Consumo por frame (60 FPS): Para ajustar se puede poner mas o menos exigente
            self.energia -= 0.6
        else:
            # Regeneracion suave
            self.energia += 0.35
        
        # limitar la energia a [0, energia_max]
        if self.energia < 0: self.energia = 0.0
        if self.energia > self.energia_max: self.energia = self.energia_max
        
        # Movimiento y colision por ejes (mas suave que "rebotar completo")
        ### eje X
        if dx != 0:
            paso_x = int(round(dx * velocidad))
            self.rect.x += paso_x
            # resolver colisiones solo en X
            for muro in muros:
                if self.rect.colliderect(muro.rect):
                    if paso_x > 0:
                        self.rect.right = muro.rect.left
                    else:
                        self.rect.left = muro.rect.right
        ### eje Y
        if dy != 0:
            paso_y = int(round(dy * velocidad))
            self.rect.y += paso_y
            # resolver colisiones solo en y
            for muro in muros:
                if self.rect.colliderect(muro.rect):
                    if paso_y > 0:
                        self.rect.bottom = muro.rect.top
                    else: 
                        self.rect.top = muro.rect.bottom
        
        ## mantener dentro de los limites del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))
                        
    def resetear_posicion(self):
        """Resetea la posición del jugador al inicio"""
        self.rect.x, self.rect.y = self.pos_inicial

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, self.color, rect_pantalla)
        pygame.draw.rect(ventana, blanco, rect_pantalla, 2)
