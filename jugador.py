import pygame
import math

blanco = (255, 255, 255)

class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision):
        # identidad y apariencia
        self.nombre = nombre
        self.color = color

        # movimiento base
        self.velocidad_base = float(velocidad)
        self.rect = pygame.Rect(50, 50, 30, 30)   # spawn inicial
        self.pos_inicial = (50, 50)

        # linterna
        self.vision = float(vision)

        # energía (para sprint)
        self.energia_max = float(energia)
        self.energia = float(energia)

        # vida e invulnerabilidad temporal tras recibir daño
        self.vida_max = 3
        self.vida = 3
        self.daño_cooldown = 0  # frames de invulnerabilidad restantes

        # efecto de lentitud aplicado por enemigos (contador en frames)
        self.slow_ticks = 0

        # estado de oculto (se activa si entra a un escondite del nivel)
        self.oculto = False

    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        # leer dirección con WASD/flechas
        dx = (1 if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) else 0) - \
             (1 if (teclas[pygame.K_a] or teclas[pygame.K_LEFT])  else 0)
        dy = (1 if (teclas[pygame.K_s] or teclas[pygame.K_DOWN])  else 0) - \
             (1 if (teclas[pygame.K_w] or teclas[pygame.K_UP])    else 0)

        # normalizar para que la diagonal no sea más rápida
        mag = math.hypot(dx, dy)
        if mag != 0:
            dx /= mag
            dy /= mag

        # aplicar lentitud si está activo el debuff
        slow_mult = 0.55 if self.slow_ticks > 0 else 1.0
        if self.slow_ticks > 0:
            self.slow_ticks -= 1

        # sprint con shift: más velocidad, gasta energía; si no, regenera
        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0.1
        velocidad = self.velocidad_base * (1.6 if sprint else 1.0) * slow_mult

        if sprint and mag != 0:
            self.energia -= 0.6          # consumo por frame
        else:
            self.energia += 0.35         # regeneración por frame

        # acotar energía al rango válido
        self.energia = max(0.0, min(self.energia, self.energia_max))

        # mover y resolver colisiones por ejes para empuje suave
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

        if dy != 0:
            paso_y = int(round(dy * velocidad))
            if paso_y != 0:
                self.rect.y += paso_y
                for muro in muros:
                    if self.rect.colliderect(muro.rect):
                        if paso_y > 0:
                            self.rect.bottom = muro.rect.top
                        else:
                            self.rect.top = muro.rect.bottom

        # contar hacia abajo el tiempo de invulnerabilidad
        if self.daño_cooldown > 0:
            self.daño_cooldown -= 1

        # mantener dentro de los límites del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))

    def resetear_posicion(self):
        # regresa al punto de inicio
        self.rect.x, self.rect.y = self.pos_inicial

    def dibujar(self, ventana, camara):
        # rectángulo del jugador con borde blanco
        rect_pantalla = camara.aplicar(self.rect)
        pygame.draw.rect(ventana, self.color, rect_pantalla)
        pygame.draw.rect(ventana, blanco, rect_pantalla, 2)

    def recibir_daño(self, cantidad):
        # resta vida y activa invulnerabilidad breve si no está en cooldown
        if self.daño_cooldown <= 0:
            self.vida -= cantidad
            self.daño_cooldown = 60      # ~1s a 60 FPS
            if self.vida < 0:
                self.vida = 0