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
        
        # Daño / invulnerabilidad
        self.daño_cooldown = 0  # frames restantes sin recibir daño

        self.slow_ticks = 0
        
    #####################
    # Moviemiento de correr y colision por ejes
    #####################
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        # Direcciones simples
        dx = (1 if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) else 0) - \
            (1 if (teclas[pygame.K_a] or teclas[pygame.K_LEFT]) else 0)
        dy = (1 if (teclas[pygame.K_s] or teclas[pygame.K_DOWN])  else 0) - \
            (1 if (teclas[pygame.K_w] or teclas[pygame.K_UP])    else 0)

        # Normalizar para que la diagonal no sea más rápida
        mag = math.hypot(dx, dy)
        if mag != 0:
            dx /= mag
            dy /= mag

        # --- LENTITUD (aura del bruto) ---
        # si estás afectado, reducimos la velocidad y descontamos el contador
        slow_mult = 0.55 if self.slow_ticks > 0 else 1.0
        if self.slow_ticks > 0:
            self.slow_ticks -= 1

        # Sprint: más velocidad, consume energía; si no, regenera
        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0.1
        velocidad = self.velocidad_base * (1.6 if sprint else 1.0) * slow_mult

        if sprint and mag != 0:
            # consumo por frame (ajusta a tu gusto)
            self.energia -= 0.6
        else:
            # regeneración suave
            self.energia += 0.35

        # Limitar energía a [0, energia_max]
        if self.energia < 0:
            self.energia = 0.0
        if self.energia > self.energia_max:
            self.energia = self.energia_max

        # Movimiento y colisión por ejes (suave)
        # --- Eje X ---
        if dx != 0:
            paso_x = int(round(dx * velocidad))
            if paso_x != 0:
                self.rect.x += paso_x
                for muro in muros:
                    if self.rect.colliderect(muro.rect):
                        if paso_x > 0:
                            self.rect.right = muro.rect.left
                        else:
                            self.rect.left = muro.rect.right

        # --- Eje Y ---
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
        # Reducir cooldown si esta activo
        if self.daño_cooldown > 0:
            self.daño_cooldown -= 1
            
        ## mantener dentro de los limites del mapa
            if paso_y != 0:
                self.rect.y += paso_y
                for muro in muros:
                    if self.rect.colliderect(muro.rect):
                        if paso_y > 0:
                            self.rect.bottom = muro.rect.top
                        else:
                            self.rect.top = muro.rect.bottom

        # Mantener dentro de los límites del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))

                        
    def resetear_posicion(self):
        """Resetea la posición del jugador al inicio"""
        self.rect.x, self.rect.y = self.pos_inicial

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, self.color, rect_pantalla)
        pygame.draw.rect(ventana, blanco, rect_pantalla, 2)
      
    def recibir_daño(self, cantidad):
        """
        Reduce la vida y activa un tiempo de invulnerabilidad
        """
        if self.daño_cooldown <= 0: # Solo si puede recibir daño
            self.vida -= cantidad
            self.daño_cooldown = 60
            if self.vida < 0:
                self.vida = 0
                
