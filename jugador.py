import pygame
import math

blanco = (255, 255, 255)

class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision):
        # Identidad y apariencia
        self.nombre = nombre
        self.color = color

        # Movimiento e inercia
        self.velocidad_base = float(velocidad)
        self.rect = pygame.Rect(50, 50, 30, 30)
        self.pos_inicial = (50, 50)
        self.vel_x = 0
        self.vel_y = 0
        self.aceleracion = 0.4
        self.friccion = 0.85

        # Linterna
        self.vision = float(vision)

        # Energía y sprint
        self.energia_max = float(energia)
        self.energia = float(energia)
        self.recuperacion_delay = 0  # para evitar regeneración inmediata

        # Vida e invulnerabilidad
        self.vida_max = 3
        self.vida = 3
        self.daño_cooldown = 0

        # Efectos de estado
        self.slow_ticks = 0
        self.oculto = False

        # Disparo
        self.cooldown_disparo = 0

        # Sonido precargado (seguro si no existe)
        try:
            self.sonido_daño = pygame.mixer.Sound("daño.mp3")
        except Exception:
            self.sonido_daño = None

    # -------------------------------------------------------
    # MOVIMIENTO
    # -------------------------------------------------------
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        # Leer dirección (WASD o flechas)
        dx = (1 if (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) else 0) - \
             (1 if (teclas[pygame.K_a] or teclas[pygame.K_LEFT])  else 0)
        dy = (1 if (teclas[pygame.K_s] or teclas[pygame.K_DOWN])  else 0) - \
             (1 if (teclas[pygame.K_w] or teclas[pygame.K_UP])    else 0)

        # Normalizar
        mag = math.hypot(dx, dy)
        if mag != 0:
            dx /= mag
            dy /= mag

        # Lentitud aplicada por enemigos
        slow_mult = 0.55 if self.slow_ticks > 0 else 1.0
        if self.slow_ticks > 0:
            self.slow_ticks -= 1

        # Sprint (usa energía)
        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0.1
        velocidad = self.velocidad_base * (1.6 if sprint else 1.0) * slow_mult

        # Consumo / recuperación de energía con delay
        if sprint and mag > 0.1:
            self.energia -= 0.6
            self.recuperacion_delay = 30  # medio segundo
        else:
            if self.recuperacion_delay > 0:
                self.recuperacion_delay -= 1
            else:
                self.energia += 0.35

        self.energia = max(0.0, min(self.energia, self.energia_max))

        # Movimiento con inercia
        self.vel_x += dx * self.aceleracion * velocidad
        self.vel_y += dy * self.aceleracion * velocidad

        # Aplicar fricción y límite mínimo
        self.vel_x *= self.friccion
        self.vel_y *= self.friccion
        if abs(self.vel_x) < 0.05:
            self.vel_x = 0
        if abs(self.vel_y) < 0.05:
            self.vel_y = 0

        # Movimiento y colisiones por ejes
        self.rect.x += int(self.vel_x)
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if self.vel_x > 0:
                    self.rect.right = muro.rect.left
                elif self.vel_x < 0:
                    self.rect.left = muro.rect.right

        self.rect.y += int(self.vel_y)
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                if self.vel_y > 0:
                    self.rect.bottom = muro.rect.top
                elif self.vel_y < 0:
                    self.rect.top = muro.rect.bottom

        # Mantener dentro del mapa
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))

        # Control de cooldowns
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1
        if self.daño_cooldown > 0:
            self.daño_cooldown -= 1

    # -------------------------------------------------------
    # UTILIDAD
    # -------------------------------------------------------
    def resetear_posicion(self):
        self.rect.x, self.rect.y = self.pos_inicial
        self.vel_x = 0
        self.vel_y = 0

    # -------------------------------------------------------
    # DIBUJO
    # -------------------------------------------------------
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)
        color_actual = getattr(self, "color_flash", None)

        # Validar que el color sea una tupla RGB válida
        if not isinstance(color_actual, tuple) or len(color_actual) != 3:
            color_actual = self.color

        # Dibujar jugador y borde
        pygame.draw.rect(ventana, color_actual, rect_pantalla)
        pygame.draw.rect(ventana, blanco, rect_pantalla, 2)

        # Resetear el flash de daño
        self.color_flash = None

    # -------------------------------------------------------
    # DAÑO Y VIDA
    # -------------------------------------------------------
    def recibir_daño(self, cantidad):
        if self.daño_cooldown <= 0:
            self.vida -= cantidad
            self.daño_cooldown = 60  # ~1 segundo de invulnerabilidad
            self.color_flash = (255, 100, 100)
            if self.sonido_daño:
                self.sonido_daño.play()
            if self.vida < 0:
                self.vida = 0
