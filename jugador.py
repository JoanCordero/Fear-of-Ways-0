import pygame
import math

BLANCO = (255, 255, 255)


def cargar_frames(ruta, ancho, alto, escala=1.0):
    """Corta un sprite sheet en frames individuales y aplica escala."""
    hoja = pygame.image.load(ruta).convert_alpha()
    hoja_w, hoja_h = hoja.get_size()
    frames = []

    # Ajustar número de columnas y filas en función del tamaño real
    columnas = hoja_w // ancho
    filas = hoja_h // alto

    for y in range(filas):
        for x in range(columnas):
            rect = pygame.Rect(x * ancho, y * alto, ancho, alto)
            frame = hoja.subsurface(rect)
            
            # Aplicar escala si es diferente de 1.0
            if escala != 1.0:
                nuevo_ancho = int(ancho * escala)
                nuevo_alto = int(alto * escala)
                frame = pygame.transform.scale(frame, (nuevo_ancho, nuevo_alto))
            
            frames.append(frame)
    return frames



class jugador:
    def __init__(self, nombre, color, velocidad, energia, vision, pos_inicial=None):
        # Identidad y apariencia
        self.nombre = nombre
        self.color = color

        # Movimiento e inercia
        self.velocidad_base = float(velocidad)
        if pos_inicial is None:
            pos_inicial = (100, 100)
        # Rectángulo de colisión más pequeño para pasar por pasillos estrechos (35x50)
        self.rect = pygame.Rect(pos_inicial[0], pos_inicial[1], 35, 50)
        self.pos_inicial = pos_inicial
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.aceleracion = 0.5
        self.friccion = 0.82

        # Dirección de mirada (para ataques o linterna)
        self.angulo_mira = 0.0
        self.ultima_direccion_x = 1.0
        self.ultima_direccion_y = 0.0

        # Linterna
        self.vision = float(vision)

        # Energía y sprint
        self.energia_max = float(energia)
        self.energia = float(energia)
        self.recuperacion_delay = 0

        # Vida e invulnerabilidad
        self.vida_max = 5
        self.vida = 5
        self.daño_cooldown = 0
        self.flash_timer = 0

        # Efectos de estado
        self.slow_ticks = 0
        self.oculto = False

        # Disparo / ataque
        self.cooldown_disparo = 0
        self.cooldown_ataque = 0

        # Estado y animación
        self.estado = "idle"
        self.frame_index = 0
        self.tiempo_anim = 0
        self.muriendo = False
        self.mirando_izquierda = False  # Para voltear el sprite

        # Cargar animaciones desde el sprite sheet
        # El sprite sheet es 1080x1080
        # Estructura: 5 columnas x 3 filas = 15 frames totales
        # Cada sprite: 200 ancho x 340 alto (ancho reducido para no capturar el sprite adyacente)
        ruta = "assets/ingeniero_sheet.png"
        frames = cargar_frames("assets/ingeniero_sheet.png", 200, 340, escala=0.18)

        self.animaciones = {
            "idle":     frames[0:5],    # primera fila: 5 frames
            "caminar":  frames[0:5],    # misma animación
            "disparar": frames[5:10],   # segunda fila: 5 frames
            "daño":     frames[10:15],  # tercera fila: 5 frames
            "morir":    frames[10:15],  # tercera fila
        }


        # Sonido de daño (opcional)
        try:
            self.sonido_daño = pygame.mixer.Sound("daño.mp3")
        except Exception:
            self.sonido_daño = None

    # -------------------------------------------------------
    # MOVIMIENTO
    # -------------------------------------------------------
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        if self.muriendo:
            self.estado = "morir"
            return

        dx = (1 if teclas[pygame.K_d] else 0) - (1 if teclas[pygame.K_a] else 0)
        dy = (1 if teclas[pygame.K_s] else 0) - (1 if teclas[pygame.K_w] else 0)

        # Normalizar vector
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx /= mag
            dy /= mag
            self.ultima_direccion_x = dx
            self.ultima_direccion_y = dy
            # Actualizar dirección de mirada
            if dx < 0:
                self.mirando_izquierda = True
            elif dx > 0:
                self.mirando_izquierda = False

        # Modificadores de velocidad
        slow_mult = 0.6 if self.slow_ticks > 0 else 1.0
        if self.slow_ticks > 0:
            self.slow_ticks -= 1

        sprint = (teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]) and self.energia > 0
        mult_velocidad = 1.8 if sprint else 1.0
        mult_aceleracion = 1.6 if sprint else 1.0
        friccion_actual = 0.88 if sprint else self.friccion
        velocidad = self.velocidad_base * slow_mult * mult_velocidad

        # Movimiento con aceleración progresiva
        self.vel_x += dx * self.aceleracion * mult_aceleracion
        self.vel_y += dy * self.aceleracion * mult_aceleracion

        self.vel_x *= friccion_actual
        self.vel_y *= friccion_actual

        limite_vel = velocidad
        vel_total = math.hypot(self.vel_x, self.vel_y)
        if vel_total > limite_vel:
            factor = limite_vel / vel_total
            self.vel_x *= factor
            self.vel_y *= factor

        # Sprint: energía
        if sprint and vel_total > 0.2:
            self.energia = max(0, self.energia - 0.5)
            self.recuperacion_delay = 40
        else:
            if self.recuperacion_delay > 0:
                self.recuperacion_delay -= 1
            else:
                self.energia = min(self.energia_max, self.energia + 0.3)

        # Movimiento con colisiones
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

        self.rect.clamp_ip(pygame.Rect(0, 0, ancho_mapa, alto_mapa))

        # Cooldowns
        if self.daño_cooldown > 0:
            self.daño_cooldown -= 1
        if self.cooldown_disparo > 0:
            self.cooldown_disparo -= 1
        if self.cooldown_ataque > 0:
            self.cooldown_ataque -= 1
        if self.flash_timer > 0:
            self.flash_timer -= 1

        # Actualizar estado según movimiento (solo si no está en una animación especial)
        if self.vida <= 0:
            self.estado = "morir"
            self.muriendo = True
        elif self.estado not in ["disparar", "daño", "morir"]:
            # Solo cambiar estado si no está en una acción especial
            if dx == 0 and dy == 0:
                self.estado = "idle"
            else:
                self.estado = "caminar"

    # -------------------------------------------------------
    # UTILIDADES
    # -------------------------------------------------------
    def resetear_posicion(self):
        self.rect.x, self.rect.y = self.pos_inicial
        self.vel_x = self.vel_y = 0

    def establecer_posicion_spawn(self, x, y):
        self.pos_inicial = (x, y)
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0

    # -------------------------------------------------------
    # ATAQUE CORTO
    # -------------------------------------------------------
    def atacar_corto(self, enemigos):
        if self.cooldown_ataque > 0 or self.muriendo:
            return

        self.estado = "disparar"  # usa animación de disparo también para ataque corto
        self.frame_index = 0  # Reiniciar animación desde el principio
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
        self.cooldown_ataque = 25

    # -------------------------------------------------------
    # DIBUJO
    # -------------------------------------------------------
    def dibujar(self, ventana, camara):
        if self.estado not in self.animaciones:
            self.estado = "idle"

        frames = self.animaciones[self.estado]
        if not frames:
            return

        self.tiempo_anim += 1
        velocidad_anim = 16  # Velocidad normal de animación (más rápida)
        
        # Animaciones especiales mucho más rápidas
        if self.estado in ["disparar", "daño"]:
            velocidad_anim = 8
        
        if self.tiempo_anim > velocidad_anim:
            self.tiempo_anim = 0

            # Si está muriendo, no ciclar animación
            if self.estado == "morir":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
            # Si está disparando o recibiendo daño, volver a idle al terminar
            elif self.estado in ["disparar", "daño"]:
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
                else:
                    # Termina la animación especial, volver a idle
                    self.estado = "idle"
                    self.frame_index = 0
            else:
                self.frame_index = (self.frame_index + 1) % len(frames)

        # Evitar error si el índice es mayor
        if self.frame_index >= len(frames):
            self.frame_index = len(frames) - 1

        frame = frames[self.frame_index]
        
        # Voltear sprite si mira a la izquierda
        if self.mirando_izquierda:
            frame = pygame.transform.flip(frame, True, False)
        
        # Escalar el frame según el zoom de la cámara
        frame_escalado = pygame.transform.scale(
            frame, 
            (int(frame.get_width() * camara.zoom), 
             int(frame.get_height() * camara.zoom))
        )
        
        # Obtener el rectángulo del jugador en pantalla
        rect_pantalla = camara.aplicar(self.rect)
        
        # Alinear el sprite desde la parte inferior para que se vean los pies
        # y centrado horizontalmente
        frame_rect = frame_escalado.get_rect(
            midbottom=rect_pantalla.midbottom
        )
        ventana.blit(frame_escalado, frame_rect)

    # -------------------------------------------------------
    # DAÑO Y VIDA
    # -------------------------------------------------------
    def recibir_daño(self, cantidad):
        if self.daño_cooldown <= 0 and not self.muriendo:
            self.vida = max(0, self.vida - cantidad)
            self.daño_cooldown = 120
            self.flash_timer = 20
            self.estado = "daño"
            self.frame_index = 0  # Reiniciar animación desde el principio
            if self.sonido_daño:
                self.sonido_daño.play()
            if self.vida <= 0:
                self.estado = "morir"
                self.muriendo = True
                self.frame_index = 0  # Reiniciar animación de muerte
