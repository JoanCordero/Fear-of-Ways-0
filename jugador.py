import pygame
import math

BLANCO = (255, 255, 255)

class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision, pos_inicial=None):
        # Identidad y apariencia
        self.nombre = nombre
        self.color = color

        # Movimiento e inercia
        self.velocidad_base = float(velocidad)
        # Posición inicial (se puede establecer después)
        if pos_inicial is None:
            pos_inicial = (100, 100)  # Temporal, se actualizará
        self.rect = pygame.Rect(pos_inicial[0], pos_inicial[1], 30, 30)
        self.pos_inicial = pos_inicial
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.aceleracion = 0.5
        self.friccion = 0.82

        # Dirección de mirada (para ataques o linterna)
        self.angulo_mira = 0.0
        self.ultima_direccion_x = 1.0  # Dirección por defecto: derecha
        self.ultima_direccion_y = 0.0

        # Linterna
        self.vision = float(vision)

        # Energía y sprint
        self.energia_max = float(energia)
        self.energia = float(energia)
        self.recuperacion_delay = 0

        # Vida e invulnerabilidad - MEJORADO
        self.vida_max = 5  # Aumentado de 3 a 5
        self.vida = 5
        self.daño_cooldown = 0
        self.flash_timer = 0  # duración del parpadeo de daño

        # Efectos de estado
        self.slow_ticks = 0
        self.oculto = False

        # Disparo / ataque
        self.cooldown_disparo = 0
        self.cooldown_ataque = 0

        # Sonido de daño seguro
        try:
            self.sonido_daño = pygame.mixer.Sound("daño.mp3")
        except Exception:
            self.sonido_daño = None

    # -------------------------------------------------------
    # MOVIMIENTO HUMANO
    # -------------------------------------------------------
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        dx = (1 if teclas[pygame.K_d] else 0) - (1 if teclas[pygame.K_a] else 0)
        dy = (1 if teclas[pygame.K_s] else 0) - (1 if teclas[pygame.K_w] else 0)

        # Normalizar vector
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx /= mag
            dy /= mag
            # Actualizar la última dirección de movimiento
            self.ultima_direccion_x = dx
            self.ultima_direccion_y = dy

        # Modificadores de velocidad
        slow_mult = 0.6 if self.slow_ticks > 0 else 1.0
        if self.slow_ticks > 0:
            self.slow_ticks -= 1

        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0
        mult_velocidad = 1.8 if sprint else 1.0  # Aumento de velocidad máxima más notorio
        mult_aceleracion = 1.6 if sprint else 1.0  # Aceleración mucho más rápida durante sprint
        friccion_actual = 0.88 if sprint else self.friccion  # Menos fricción durante sprint
        velocidad = self.velocidad_base * slow_mult * mult_velocidad

        # Movimiento con aceleración progresiva (mayor aceleración durante sprint)
        self.vel_x += dx * self.aceleracion * mult_aceleracion
        self.vel_y += dy * self.aceleracion * mult_aceleracion

        # Aplicar fricción (reducida durante sprint)
        self.vel_x *= friccion_actual
        self.vel_y *= friccion_actual

        # Limitar velocidad máxima
        limite_vel = velocidad
        vel_total = math.hypot(self.vel_x, self.vel_y)
        if vel_total > limite_vel:
            factor = limite_vel / vel_total
            self.vel_x *= factor
            self.vel_y *= factor

        # Sprint: consumo y recuperación
        if sprint and vel_total > 0.2:
            self.energia = max(0, self.energia - 0.5)
            self.recuperacion_delay = 40
        else:
            if self.recuperacion_delay > 0:
                self.recuperacion_delay -= 1
            else:
                self.energia = min(self.energia_max, self.energia + 0.3)

        # Aplicar movimiento
        self.rect.x += int(self.vel_x)
        for m in muros:
            if self.rect.colliderect(m.rect):
                if self.vel_x > 0:
                    self.rect.right = m.rect.left
                elif self.vel_x < 0:
                    self.rect.left = m.rect.right
                self.vel_x = 0

        self.rect.y += int(self.vel_y)
        for m in muros:
            if self.rect.colliderect(m.rect):
                if self.vel_y > 0:
                    self.rect.bottom = m.rect.top
                elif self.vel_y < 0:
                    self.rect.top = m.rect.bottom
                self.vel_y = 0

        # Restringir al área jugable
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))

        # Actualizar cooldowns
        if self.daño_cooldown > 0:
            self.daño_cooldown -= 1
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1
        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

    # -------------------------------------------------------
    # UTILIDADES
    # -------------------------------------------------------
    def resetear_posicion(self):
        self.rect.x, self.rect.y = self.pos_inicial
        self.vel_x = self.vel_y = 0
    
    def establecer_posicion_spawn(self, x, y):
        """Establece una nueva posición de spawn para el jugador"""
        self.pos_inicial = (x, y)
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0

    # -------------------------------------------------------
    # ATAQUE CORTO (melee con click izquierdo)
    # -------------------------------------------------------
    def atacar_corto(self, enemigos):
        """Ataque cuerpo a cuerpo corto."""
        if self.cooldown_ataque > 0:
            return

        rango = 45
        area = pygame.Rect(
            self.rect.centerx - rango // 2,
            self.rect.centery - rango // 2,
            rango,
            rango
        )

        for e in list(enemigos):
            if area.colliderect(e.rect):
                e.vida -= 1
                e.color = (255, 120, 120)
                if e.vida <= 0:
                    enemigos.remove(e)
        self.cooldown_ataque = 25  # medio segundo

    # -------------------------------------------------------
    # DIBUJO
    # -------------------------------------------------------
    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)

        # Color de flash de daño
        if self.flash_timer > 0:
            color_actual = (255, 100, 100)
        else:
            color_actual = self.color

        # Cuerpo del jugador
        pygame.draw.rect(ventana, color_actual, rect_pantalla)
        pygame.draw.rect(ventana, BLANCO, rect_pantalla, 2)

    # -------------------------------------------------------
    # DAÑO Y VIDA
    # -------------------------------------------------------
    def recibir_daño(self, cantidad):
        if self.daño_cooldown <= 0:
            self.vida = max(0, self.vida - cantidad)
            self.daño_cooldown = 120  # 2 segundos de invencibilidad - aumentado de 60
            self.flash_timer = 20  # parpadeo más largo - aumentado de 15
            if self.sonido_daño:
                self.sonido_daño.play()

