import pygame
import math

BLANCO = (255, 255, 255)


def cargar_frames(ruta, ancho, alto, escala=1.0, margen=30, margen_inferior_extra=15):
    """Corta un sprite sheet en frames individuales y aplica escala con recorte preciso.
    
    Args:
        margen: Margen general en todos los lados
        margen_inferior_extra: Margen adicional en la parte inferior para evitar artefactos
    """
    sprite_sheet = pygame.image.load(ruta).convert_alpha()
    ancho_sprite_sheet, alto_sprite_sheet = sprite_sheet.get_size()
    frames = []

    # Ajustar número de columnas y filas en función del tamaño real
    numero_columnas = ancho_sprite_sheet // ancho
    numero_filas = alto_sprite_sheet // alto

    for fila_actual in range(numero_filas):
        for columna_actual in range(numero_columnas):
            # Detectar si es la fila de disparo (segunda fila, fila_actual=1, frames 5-9)
            # Para disparo, usar márgenes más pequeños arriba y a la derecha
            es_fila_disparo = (fila_actual == 1)
            
            if es_fila_disparo:
                # Márgenes personalizados para disparo: más espacio arriba y a la derecha
                margen_superior = max(5, margen - 25)  # Expandir 5px más arriba para ver el pelo
                margen_inferior = margen + margen_inferior_extra + 10  # Más recorte abajo
                margen_izquierdo = margen  # Normal a la izquierda
                margen_derecho = max(5, margen - 20)  # Mucho menos recorte a la derecha (mínimo 5px)
            else:
                # Márgenes normales para otras animaciones
                margen_superior = margen
                margen_inferior = margen + margen_inferior_extra
                margen_izquierdo = margen
                margen_derecho = margen
            
            # Calcular posición exacta del frame con márgenes personalizados
            posicion_x_frame = columna_actual * ancho + margen_izquierdo
            posicion_y_frame = fila_actual * alto + margen_superior
            ancho_frame = ancho - margen_izquierdo - margen_derecho
            alto_frame = alto - margen_superior - margen_inferior
            
            # Asegurar que no salimos de los límites de la hoja
            if posicion_x_frame < 0:
                posicion_x_frame = 0
            if posicion_y_frame < 0:
                posicion_y_frame = 0
            if posicion_x_frame + ancho_frame > ancho_sprite_sheet:
                ancho_frame = ancho_sprite_sheet - posicion_x_frame
            if posicion_y_frame + alto_frame > alto_sprite_sheet:
                alto_frame = alto_sprite_sheet - posicion_y_frame
            
            # Solo crear el frame si tiene tamaño válido
            if ancho_frame > 0 and alto_frame > 0:
                rectangulo_frame = pygame.Rect(posicion_x_frame, posicion_y_frame, ancho_frame, alto_frame)
                frame = sprite_sheet.subsurface(rectangulo_frame).copy()  # Copiar para evitar referencias
                
                # Crear una superficie limpia con canal alpha para evitar artefactos
                frame_limpio = pygame.Surface((ancho_frame, alto_frame), pygame.SRCALPHA)
                frame_limpio.blit(frame, (0, 0))
                frame = frame_limpio
                
                # Aplicar escala si es diferente de 1.0
                if escala != 1.0:
                    nuevo_ancho = max(1, int(ancho_frame * escala))
                    nuevo_alto = max(1, int(alto_frame * escala))
                    # Usar smoothscale para mejor calidad al reducir
                    frame = pygame.transform.smoothscale(frame, (nuevo_ancho, nuevo_alto))
                
                frames.append(frame)
            else:
                # Si el frame no es válido, crear uno vacío transparente
                frames.append(pygame.Surface((max(1, int(ancho * escala)), max(1, int(alto * escala))), pygame.SRCALPHA))
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
        self.angulo_linterna = 0.0  # Ángulo de la linterna (hacia el mouse)

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
        # Cada sprite: 216 ancho x 360 alto (1080/5 = 216 por columna, 1080/3 = 360 por fila)
        ruta = "images/ingeniero_sheet.png"
        # Aumentar margen general y recorte extra en la parte inferior para evitar artefactos
        frames = cargar_frames("images/ingeniero_sheet.png", 216, 360, escala=0.18, margen=40, margen_inferior_extra=5)

        self.animaciones = {
            "idle":     [frames[0]],    # primera fila: solo primer frame para estar quieto
            "caminar":  frames[1:5],    # primera fila: frames 2-5 para caminar
            "disparar": frames[5:10],   # segunda fila: 5 frames
            "morir":    frames[10:15],  # tercera fila: 5 frames
        }


        # Sonido de daño (opcional)
        try:
            self.sonido_daño = pygame.mixer.Sound("audio/daño.mp3")
        except Exception:
            self.sonido_daño = None

    # MOVIMIENTO
    def mover(self, teclas, muros, ancho_mapa, alto_mapa):
        if self.muriendo:
            self.estado = "morir"
            return

        direccion_x = (1 if teclas[pygame.K_d] else 0) - (1 if teclas[pygame.K_a] else 0)
        direccion_y = (1 if teclas[pygame.K_s] else 0) - (1 if teclas[pygame.K_w] else 0)

        # Normalizar vector
        magnitud_vector = math.hypot(direccion_x, direccion_y)
        if magnitud_vector > 0:
            direccion_x /= magnitud_vector
            direccion_y /= magnitud_vector
            self.ultima_direccion_x = direccion_x
            self.ultima_direccion_y = direccion_y
            # Actualizar dirección de mirada
            if direccion_x < 0:
                self.mirando_izquierda = True
            elif direccion_x > 0:
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
        self.vel_x += direccion_x * self.aceleracion * mult_aceleracion
        self.vel_y += direccion_y * self.aceleracion * mult_aceleracion

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
            if self.estado != "morir":
                self.estado = "morir"
                self.muriendo = True
                self.frame_index = 0
        elif self.estado not in ["disparar", "morir"]:
            # Solo cambiar estado si no está en una acción especial
            # Verificar si realmente se está moviendo (velocidad significativa)
            velocidad_total = math.hypot(self.vel_x, self.vel_y)
            if velocidad_total < 0.3:  # Umbral más alto para evitar micro-movimientos
                self.estado = "idle"
            else:
                self.estado = "caminar"

    # UTILIDADES
    def resetear_posicion(self):
        self.rect.x, self.rect.y = self.pos_inicial
        self.vel_x = self.vel_y = 0

    def establecer_posicion_spawn(self, x, y):
        self.pos_inicial = (x, y)
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0

    # ATAQUE CORTO
    def atacar_corto(self, enemigos):
        if self.cooldown_ataque > 0 or self.muriendo:
            return

        self.estado = "disparar"  # usa animación de disparo también para ataque corto
        self.frame_index = 0  # Reiniciar animación desde el principio
        self.tiempo_anim = 0  # Resetear contador de tiempo
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
    
    # DISPARO (nuevo método)
    def iniciar_disparo(self):
        """Inicia la animación de disparo"""
        if self.cooldown_disparo > 0 or self.muriendo:
            return False
        
        self.estado = "disparar"
        self.frame_index = 0
        self.tiempo_anim = 0
        return True

    # DIBUJO
    def actualizar_angulo_linterna(self, mouse_x, mouse_y, camara):
        """Actualiza el ángulo de la linterna hacia la posición del mouse"""
        # Obtener posición del jugador en pantalla
        jugador_pantalla = camara.aplicar(self.rect)
        posicion_jugador_x, posicion_jugador_y = jugador_pantalla.centerx, jugador_pantalla.centery
        
        # Calcular dirección desde el jugador al mouse
        diferencia_x = mouse_x - posicion_jugador_x
        diferencia_y = mouse_y - posicion_jugador_y
        
        # Si el mouse está muy cerca, usar la última dirección de movimiento
        distancia_mouse = math.hypot(diferencia_x, diferencia_y)
        if distancia_mouse < 20:
            diferencia_x = self.ultima_direccion_x * 100
            diferencia_y = self.ultima_direccion_y * 100
            distancia_mouse = math.hypot(diferencia_x, diferencia_y)
        
        if distancia_mouse > 0:
            self.angulo_linterna = math.atan2(diferencia_y, diferencia_x)
        else:
            # Si no hay movimiento, mantener el último ángulo
            self.angulo_linterna = math.atan2(self.ultima_direccion_y, self.ultima_direccion_x)

    def dibujar(self, ventana, camara):
        if self.estado not in self.animaciones:
            self.estado = "idle"

        frames = self.animaciones[self.estado]
        if not frames:
            return

        self.tiempo_anim += 1
        
        # Velocidades de animación ajustadas para cada estado (valores más bajos = más rápido)
        # Valores reducidos para animaciones más fluidas y responsivas
        if self.estado == "idle":
            velocidad_anim = 12  # Animación suave en idle
        elif self.estado == "caminar":
            velocidad_anim = 2  # Animación muy fluida al caminar (rápida)
        elif self.estado == "disparar":
            velocidad_anim = 1  # Animación extremadamente rápida para disparo
        else:
            velocidad_anim = 3  # Velocidad por defecto rápida
        
        if self.tiempo_anim > velocidad_anim:
            self.tiempo_anim = 0

            # Si está muriendo, no ciclar animación
            if self.estado == "morir":
                if self.frame_index < len(frames) - 1:
                    self.frame_index += 1
            # Si está disparando, volver a idle al terminar
            elif self.estado == "disparar":
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

        frame = frames[self.frame_index].copy()  # Copiar para evitar modificar el frame original
        
        # Voltear sprite si mira a la izquierda
        if self.mirando_izquierda:
            frame = pygame.transform.flip(frame, True, False)
        
        # Efecto visual de flash cuando recibe daño (sin cambiar animación)
        if self.flash_timer > 0 and self.flash_timer % 4 < 2:
            # Aplicar efecto de flash rojo directamente al frame
            frame.fill((255, 150, 150), special_flags=pygame.BLEND_RGB_ADD)
        
        # Escalar el frame según el zoom de la cámara usando smoothscale para mejor calidad
        nuevo_ancho = max(1, int(frame.get_width() * camara.zoom))
        nuevo_alto = max(1, int(frame.get_height() * camara.zoom))
        frame_escalado = pygame.transform.smoothscale(frame, (nuevo_ancho, nuevo_alto))
        
        # Obtener el rectángulo del jugador en pantalla
        rect_pantalla = camara.aplicar(self.rect)
        
        # Alinear el sprite desde la parte inferior para que se vean los pies
        # y centrado horizontalmente
        frame_rect = frame_escalado.get_rect(
            midbottom=rect_pantalla.midbottom
        )
        ventana.blit(frame_escalado, frame_rect)

    # DAÑO Y VIDA
    def recibir_daño(self, cantidad, escudo_activo=False):
        # Si el escudo está activo, no recibir daño
        if escudo_activo:
            return
        
        if self.daño_cooldown <= 0 and not self.muriendo:
            self.vida = max(0, self.vida - cantidad)
            self.daño_cooldown = 120
            self.flash_timer = 20  # Efecto visual de flash sin cambiar animación
            # NO cambiar el estado a "daño", mantener el estado actual
            # Detener movimiento momentáneamente al recibir daño
            self.vel_x *= 0.3
            self.vel_y *= 0.3
            if self.sonido_daño:
                self.sonido_daño.play()
            if self.vida <= 0:
                self.estado = "morir"
                self.muriendo = True
                self.frame_index = 0  # Reiniciar animación de muerte
                self.vel_x = 0
                self.vel_y = 0
