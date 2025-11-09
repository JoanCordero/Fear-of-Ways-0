import pygame
import random
import math
import os

class enemigo:
    def __init__(self, x, y, velocidad, tipo=None):
        tipos_def = {
            "veloz":     {"vida": 2, "color": (255, 255,   0), "tam": 90, "imagen": "duende.png"},
            "acechador": {"vida": 3, "color": (  0, 255, 255), "tam": 100, "imagen": "esqueleto.png"},
            "bruto":     {"vida": 5, "color": (255,  80,  80), "tam": 120, "imagen": "Ogro.png"},
        }

        if tipo is None:
            tipo = random.choice(list(tipos_def.keys()))

        self.tipo = tipo
        self.vida = tipos_def[tipo]["vida"]
        self.color = tipos_def[tipo]["color"]
        tamano = tipos_def[tipo]["tam"]

        # Cargar imagen del enemigo
        ruta_imagen = os.path.join("images", tipos_def[tipo]["imagen"])
        try:
            # Cargar imagen preservando completamente la transparencia
            imagen_cargada = pygame.image.load(ruta_imagen)
            
            # Convertir a superficie con alpha antes de escalar
            imagen_con_alpha = imagen_cargada.convert_alpha()
            
            # Crear superficie transparente del tamaño final
            self.imagen_original = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
            self.imagen_original.fill((0, 0, 0, 0))  # Completamente transparente
            
            # Escalar la imagen con suavizado
            imagen_escalada = pygame.transform.smoothscale(imagen_con_alpha, (tamano, tamano))
            
            # Copiar la imagen escalada a la superficie final
            self.imagen_original.blit(imagen_escalada, (0, 0))
            
            self.imagen = self.imagen_original.copy()
            self.usa_imagen = True
            print(f"Imagen {tipos_def[tipo]['imagen']} cargada correctamente - Tamaño: {tamano}x{tamano}")
        except Exception as e:
            print(f"Error cargando imagen {ruta_imagen}: {e}")
            self.imagen_original = None
            self.imagen = None
            self.usa_imagen = False

        self.rect = pygame.Rect(x, y, tamano, tamano)
        self.velocidad = velocidad + (2 if tipo == "veloz" else 0)
        if tipo == "bruto":
            self.velocidad = max(1, velocidad - 1)
        
        # Variable para controlar la dirección visual
        self.mirando_derecha = True

        # Movimiento y detección - BALANCEADO
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1
        self.rango_deteccion = 250  # Reducido de 350 a 250
        self.estado = "patrullando"
        self.velocidad_persecucion = self.velocidad + 0.5  # Reducido de +1 a +0.5
        self.tiempo_perdida = 0
        
        # Sistema de ocultamiento - "Los peligros permanecen ocultos hasta que están cerca"
        self.oculto = True  # Comienza oculto
        self.rango_revelacion = 180  # Distancia a la que se revela al jugador
        self.alpha_actual = 0  # Nivel de transparencia (0 = invisible, 255 = visible)
        self.revelado_permanente = False  # Una vez revelado, permanece visible

        # Cooldowns - AUMENTADOS para menos daño
        self.tiempo_recarga = {"ataque": 0, "disparo": 0, "aura": 0}

        # Parámetros de ataques - BALANCEADOS
        self.alcance_melee = 35       # veloz - reducido de 40 a 35
        self.radio_aura = 100         # bruto - reducido de 120 a 100
        self.velocidad_disparo = 5    # acechador - reducido de 6 a 5

        # Proyectiles del acechador
        self.proyectiles = []  # {"rect": Rect, "vx": float, "vy": float, "dano": int, "activo": bool}
        
        # Comportamientos variables
        self.rutina = random.choice(["ronda", "zigzag", "pausa"])

        # Variables de movimiento progresivo (para IA con inercia)
        self.vel_x = 0.0
        self.vel_y = 0.0

        # Dirección inicial de patrulla (en radianes)
        self.ang_pat = random.uniform(0, math.pi * 2)

        # Estado interno de persecución
        self.objetivo_visible = False
        self.tiempo_sin_ver = 0

        # Dirección visual (rotación hacia el jugador)
        self.angulo_actual = 0.0
        
        # Preparación de ataque (telegrafía el ataque)
        self.preparando_ataque = 0  # Frames preparando el ataque
        
        # Sistema de animación - para que no se vean tiesos
        self.tiempo_animacion = random.uniform(0, math.pi * 2)  # Fase aleatoria inicial
        self.velocidad_animacion = random.uniform(0.08, 0.12)  # Velocidad de animación variable
        self.offset_y_flotacion = 0  # Offset vertical para efecto de flotación
        self.escala_respiracion = 1.0  # Escala para efecto de "respiración"
        
        # Animación específica por tipo
        if tipo == "veloz":
            self.velocidad_animacion = 0.15  # Más rápido, más nervioso
            self.amplitud_flotacion = 3  # Rebota un poco
            self.amplitud_respiracion = 0.03  # Respira rápido
        elif tipo == "acechador":
            self.velocidad_animacion = 0.08  # Lento, amenazante
            self.amplitud_flotacion = 5  # Flota más
            self.amplitud_respiracion = 0.05  # Respira profundo
        elif tipo == "bruto":
            self.velocidad_animacion = 0.06  # Muy lento, pesado
            self.amplitud_flotacion = 2  # Casi no flota
            self.amplitud_respiracion = 0.07  # Respira muy profundo (grande)
        
        # Efecto de sacudida al recibir daño
        self.sacudida_frames = 0  # Contador de frames de sacudida
        self.offset_sacudida_x = 0
        self.offset_sacudida_y = 0


    # --------------------------------------------------------
    # UTILIDADES Y RECARGAS
    # --------------------------------------------------------
    def reducir_recargas(self):
        """Reduce los tiempos de espera de cada ataque."""
        for clave in self.tiempo_recarga:
            if self.tiempo_recarga[clave] > 0:
                self.tiempo_recarga[clave] -= 1

    def distancia_a(self, objetivo):
        """Devuelve distancia y vector hacia el objetivo."""
        rect_objetivo = objetivo.rect if hasattr(objetivo, "rect") else objetivo
        dx = rect_objetivo.centerx - self.rect.centerx
        dy = rect_objetivo.centery - self.rect.centery
        distancia = math.hypot(dx, dy)
        return distancia, dx, dy


    # --------------------------------------------------------
    # ATAQUES POR TIPO
    # --------------------------------------------------------
    def ataque_veloz(self, jugador):
        """Ataque cuerpo a cuerpo del enemigo veloz con telegrafía."""
        distancia, _, _ = self.distancia_a(jugador)
        
        # Si está en rango y no hay cooldown, comenzar a preparar ataque
        if distancia < self.alcance_melee and self.tiempo_recarga["ataque"] == 0:
            if self.preparando_ataque == 0:
                self.preparando_ataque = 20  # 20 frames de preparación (~0.33 segundos)
            
            self.preparando_ataque -= 1
            
            # Ejecutar ataque al final de la preparación
            if self.preparando_ataque == 1:
                # Verificar si el jugador tiene escudo activo
                escudo = getattr(jugador, 'escudo_activo', False)
                jugador.recibir_daño(1, escudo_activo=escudo)
                self.tiempo_recarga["ataque"] = 90  # 1.5 segundos
                self.preparando_ataque = 0
        else:
            self.preparando_ataque = 0  # Cancelar preparación si se aleja

    def disparar_acechador(self, jugador):
        """Ataque de proyectil del acechador."""
        if self.tiempo_recarga["disparo"] > 0:
            return

        distancia, dx, dy = self.distancia_a(jugador)
        if distancia >= self.rango_deteccion:
            return

        d = max(1, distancia)
        vx, vy = (dx / d) * self.velocidad_disparo, (dy / d) * self.velocidad_disparo

        proyectil = {
            "rect": pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8),
            "vx": vx,
            "vy": vy,
            "dano": 1,
            "activo": True
        }
        self.proyectiles.append(proyectil)
        self.tiempo_recarga["disparo"] = 180  # 3 segundos - aumentado de 120

    def mover_proyectiles(self, muros, ancho_mapa, alto_mapa, jugador):
        """Actualiza proyectiles y revisa colisiones."""
        activos = []
        for p in self.proyectiles:
            if not p["activo"]:
                continue

            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])

            # Fuera del mapa
            if (p["rect"].right < 0 or p["rect"].left > ancho_mapa or
                p["rect"].bottom < 0 or p["rect"].top > alto_mapa):
                p["activo"] = False

            # Colisión con muros
            for muro in muros:
                if p["activo"] and p["rect"].colliderect(muro.rect):
                    p["activo"] = False
                    break

            # Colisión con jugador
            if p["activo"] and p["rect"].colliderect(jugador.rect):
                escudo = getattr(jugador, 'escudo_activo', False)
                jugador.recibir_daño(1, escudo_activo=escudo)
                p["activo"] = False

            if p["activo"]:
                activos.append(p)

        self.proyectiles = activos

    def aplicar_aura_bruto(self, jugador):
        """Aura del bruto: ralentiza y daña si hay contacto."""
        distancia, _, _ = self.distancia_a(jugador)
        if distancia < self.radio_aura:
            jugador.slow_ticks = max(jugador.slow_ticks, 30)  # Reducido de 45 a 30
        if self.rect.colliderect(jugador.rect) and self.tiempo_recarga["aura"] == 0:
            escudo = getattr(jugador, 'escudo_activo', False)
            jugador.recibir_daño(1, escudo_activo=escudo)
            self.tiempo_recarga["aura"] = 90  # Aumentado de 30 a 90


    # --------------------------------------------------------
    # MOVIMIENTO CON INERCIA Y DETECCIÓN
    # --------------------------------------------------------
    def mover(self, muros, ancho, alto, jugador, escondites):
        self.reducir_recargas()

        dx = jugador.rect.centerx - self.rect.centerx
        dy = jugador.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        self.angulo_actual = math.degrees(math.atan2(dy, dx)) if dist > 0 else 0

        # Sistema de ocultamiento: "Los peligros permanecen ocultos hasta que están cerca"
        if not self.revelado_permanente:
            if dist < self.rango_revelacion:
                # Jugador cerca - revelar gradualmente
                self.oculto = False
                if self.alpha_actual < 255:
                    self.alpha_actual = min(255, self.alpha_actual + 15)  # Aparición gradual
                if self.alpha_actual >= 255:
                    self.revelado_permanente = True  # Una vez completamente visible, se queda así
            else:
                # Jugador lejos - mantener oculto
                self.oculto = True
                if self.alpha_actual > 0:
                    self.alpha_actual = max(0, self.alpha_actual - 10)  # Desvanecimiento
        else:
            # Ya fue revelado permanentemente
            self.oculto = False
            self.alpha_actual = 255

        # Detectar jugador (visión + línea de visión)
        puede_ver = dist < self.rango_deteccion and not jugador.oculto and self.tiene_linea_de_vision(jugador, muros)

        if puede_ver:
            self.objetivo_visible = True
            self.tiempo_sin_ver = 0
        else:
            self.tiempo_sin_ver += 1
            if self.tiempo_sin_ver > 90:  # después de 1.5 segundos sin verlo - reducido de 120
                self.objetivo_visible = False

        # Movimiento base - MEJORADO
        if self.objetivo_visible:
            # Persecución más lenta y predecible
            if dist > 0:
                dirx, diry = dx / dist, dy / dist
            else:
                dirx = diry = 0
            # Velocidad reducida y más constante
            velocidad = self.velocidad_persecucion * 0.75  # Reducido considerablemente

            # Los enemigos mantienen distancia mínima (excepto veloz)
            if self.tipo != "veloz" and dist < 80:
                dirx *= -0.3  # Se alejan un poco si están muy cerca
                diry *= -0.3

        else:
            # Patrulla aleatoria más lenta
            if random.random() < 0.02:
                self.ang_pat = random.uniform(0, math.pi * 2)
            dirx, diry = math.cos(self.ang_pat), math.sin(self.ang_pat)
            velocidad = self.velocidad * 0.5  # Reducido de 0.6 a 0.5

        # Movimiento con suavizado
        self.vel_x += (dirx * velocidad - self.vel_x) * 0.2
        self.vel_y += (diry * velocidad - self.vel_y) * 0.2

        # Actualizar posición
        self.rect.x += int(self.vel_x)
        for m in muros:
            if self.rect.colliderect(m.rect):
                self.rect.right = m.rect.left if self.vel_x > 0 else m.rect.right
                self.vel_x *= -0.4

        self.rect.y += int(self.vel_y)
        for m in muros:
            if self.rect.colliderect(m.rect):
                self.rect.bottom = m.rect.top if self.vel_y > 0 else m.rect.bottom
                self.vel_y *= -0.4

        # Mantener dentro de límites
        self.rect.clamp_ip(pygame.Rect(0, 0, ancho, alto))

        # Actualizar animación continua
        self.actualizar_animacion()

        # Actualizar dirección visual basada en movimiento horizontal
        if self.usa_imagen and self.imagen_original:
            if self.vel_x > 0.5 and not self.mirando_derecha:
                # Se mueve a la derecha, voltear imagen a la derecha
                self.mirando_derecha = True
                self.imagen = self.imagen_original.copy()
            elif self.vel_x < -0.5 and self.mirando_derecha:
                # Se mueve a la izquierda, voltear imagen (flip horizontal)
                self.mirando_derecha = False
                self.imagen = pygame.transform.flip(self.imagen_original, True, False)

        # Acciones por tipo - SOLO si está revelado
        if not self.oculto and self.alpha_actual > 150:  # Solo atacan cuando están suficientemente visibles
            if self.tipo == "veloz":
                self.ataque_veloz(jugador)
            elif self.tipo == "bruto":
                self.aplicar_aura_bruto(jugador)
            elif self.tipo == "acechador":
                self.disparar_acechador(jugador)
        
        # Los proyectiles se mueven siempre (una vez disparados)
        if self.tipo == "acechador":
            self.mover_proyectiles(muros, ancho, alto, jugador)


    # --------------------------------------------------------
    # SISTEMA DE ANIMACIÓN
    # --------------------------------------------------------
    def actualizar_animacion(self):
        """Actualiza los parámetros de animación para dar vida al enemigo."""
        # Incrementar tiempo de animación
        self.tiempo_animacion += self.velocidad_animacion
        
        # Efecto de flotación (movimiento vertical suave)
        self.offset_y_flotacion = math.sin(self.tiempo_animacion) * self.amplitud_flotacion
        
        # Efecto de respiración (escala que crece y decrece)
        self.escala_respiracion = 1.0 + math.sin(self.tiempo_animacion * 1.5) * self.amplitud_respiracion
        
        # Efecto adicional: ligera inclinación al moverse
        if abs(self.vel_x) > 1 or abs(self.vel_y) > 1:
            # Se "inclina" levemente cuando se mueve rápido
            self.angulo_inclinacion = math.sin(self.tiempo_animacion * 2) * 2  # ±2 grados
        else:
            self.angulo_inclinacion = 0
        
        # Efecto de sacudida al recibir daño
        if self.sacudida_frames > 0:
            # Sacudida rápida y errática
            intensidad = self.sacudida_frames / 8.0  # Disminuye con el tiempo
            self.offset_sacudida_x = random.uniform(-3, 3) * intensidad
            self.offset_sacudida_y = random.uniform(-3, 3) * intensidad
            self.sacudida_frames -= 1
        else:
            self.offset_sacudida_x = 0
            self.offset_sacudida_y = 0
    
    def recibir_dano(self, cantidad=1):
        """Método para que el enemigo reciba daño con efecto visual."""
        self.vida -= cantidad
        self.sacudida_frames = 8  # 8 frames de sacudida
        return self.vida <= 0  # Retorna True si murió


    # --------------------------------------------------------
    # DIBUJO
    # --------------------------------------------------------
    def dibujar(self, ventana, camara):
        # No dibujar nada si está completamente oculto
        if self.alpha_actual <= 0:
            return
            
        rect_camara = camara.aplicar(self.rect)
        
        # Dibujar la imagen o un cuadrado como fallback
        if self.usa_imagen and self.imagen:
            # Aplicar animaciones a la imagen
            imagen_animada = self.imagen.copy()
            
            # 1. Aplicar escala de respiración
            ancho_original = imagen_animada.get_width()
            alto_original = imagen_animada.get_height()
            nuevo_ancho = int(ancho_original * self.escala_respiracion)
            nuevo_alto = int(alto_original * self.escala_respiracion)
            
            if nuevo_ancho > 0 and nuevo_alto > 0:
                imagen_animada = pygame.transform.smoothscale(imagen_animada, (nuevo_ancho, nuevo_alto))
            
            # 2. Aplicar rotación sutil (inclinación al moverse)
            if abs(self.angulo_inclinacion) > 0.5:
                imagen_animada = pygame.transform.rotate(imagen_animada, self.angulo_inclinacion)
            
            # 3. Aplicar transparencia
            imagen_animada.set_alpha(self.alpha_actual)
            
            # 4. Calcular posición con offset de flotación y sacudida
            pos_x = rect_camara.centerx - imagen_animada.get_width() // 2 + self.offset_sacudida_x
            pos_y = rect_camara.centery - imagen_animada.get_height() // 2 + self.offset_y_flotacion + self.offset_sacudida_y
            
            # Efecto visual adicional al recibir daño (flash blanco)
            if self.sacudida_frames > 0:
                # Crear overlay blanco parpadeante
                overlay = imagen_animada.copy()
                overlay.fill((255, 255, 255, min(180, self.sacudida_frames * 20)), special_flags=pygame.BLEND_RGBA_ADD)
                imagen_animada.blit(overlay, (0, 0))
            
            # Dibujar imagen animada
            ventana.blit(imagen_animada, (int(pos_x), int(pos_y)))
        else:
            # Fallback: dibujar cuadrado con transparencia
            if self.preparando_ataque > 0:
                intensidad = int(255 * (self.preparando_ataque % 10) / 10)
                color_actual = (255, intensidad, intensidad)
            elif self.objetivo_visible:
                color_actual = (255, 50, 50)
            else:
                color_actual = self.color
            
            # Crear superficie temporal con transparencia
            superficie = pygame.Surface((rect_camara.width, rect_camara.height), pygame.SRCALPHA)
            color_con_alpha = (*color_actual, self.alpha_actual)
            superficie.fill(color_con_alpha)
            ventana.blit(superficie, rect_camara.topleft)
        
        # Indicador visual de preparación de ataque (veloz) - solo si está visible
        if self.tipo == "veloz" and self.preparando_ataque > 0 and self.alpha_actual > 100:
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            radio_advertencia = int(self.alcance_melee * (self.preparando_ataque / 20))
            # Crear superficie temporal para el círculo con transparencia
            superficie_temp = pygame.Surface((radio_advertencia * 2 + 4, radio_advertencia * 2 + 4), pygame.SRCALPHA)
            alpha_circulo = min(255, self.alpha_actual)
            pygame.draw.circle(superficie_temp, (255, 100, 100, alpha_circulo), 
                             (radio_advertencia + 2, radio_advertencia + 2), radio_advertencia, 2)
            ventana.blit(superficie_temp, (int(cx) - radio_advertencia - 2, int(cy) - radio_advertencia - 2))

        # Aura del bruto - solo si está visible
        if self.tipo == "bruto" and self.alpha_actual > 100:
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            # Crear superficie temporal para el círculo con transparencia
            superficie_temp = pygame.Surface((self.radio_aura * 2 + 4, self.radio_aura * 2 + 4), pygame.SRCALPHA)
            alpha_circulo = min(255, self.alpha_actual)
            pygame.draw.circle(superficie_temp, (120, 120, 200, alpha_circulo), 
                             (self.radio_aura + 2, self.radio_aura + 2), self.radio_aura, 2)
            ventana.blit(superficie_temp, (int(cx) - self.radio_aura - 2, int(cy) - self.radio_aura - 2))

        # Proyectiles del acechador (estilo circular más sutil) - solo si está visible
        if self.tipo == "acechador" and self.alpha_actual > 100:
            for p in self.proyectiles:
                rect_p = camara.aplicar(p["rect"])
                cx = rect_p.centerx
                cy = rect_p.centery
                # Crear superficie temporal para el proyectil con transparencia
                superficie_temp = pygame.Surface((10, 10), pygame.SRCALPHA)
                alpha_proyectil = min(255, self.alpha_actual)
                pygame.draw.circle(superficie_temp, (255, 100, 100, alpha_proyectil), (5, 5), 4)
                pygame.draw.circle(superficie_temp, (255, 200, 200, alpha_proyectil), (5, 5), 2)
                ventana.blit(superficie_temp, (int(cx) - 5, int(cy) - 5))


    # --------------------------------------------------------
    # VISIÓN LINEAL
    # --------------------------------------------------------
    def tiene_linea_de_vision(self, jugador, muros):
        """Comprueba si hay muros bloqueando la visión hacia el jugador."""
        distancia, dx, dy = self.distancia_a(jugador)
        if distancia == 0:
            return True
        pasos = int(distancia / 20)
        for i in range(1, pasos):
            x = self.rect.centerx + (dx / pasos) * i
            y = self.rect.centery + (dy / pasos) * i
            punto = pygame.Rect(x, y, 4, 4)
            if any(punto.colliderect(m.rect) for m in muros):
                return False
        return True
    
    # --------------------------------------------------------
    # MÉTODOS ESTÁTICOS PARA GENERACIÓN DE PUNTOS
    # --------------------------------------------------------
    @staticmethod
    def generar_punto_spawn_aleatorio(ancho_mapa, alto_mapa, muros, jugador_pos, distancia_minima=300, intentos=50):
        """
        Genera un punto de spawn aleatorio válido para un enemigo.
        Los enemigos aparecen OCULTOS y lejos del jugador.
        
        Args:
            ancho_mapa: Ancho del mapa
            alto_mapa: Alto del mapa
            muros: Lista de muros para evitar colisiones
            jugador_pos: Posición del jugador (tuple x, y)
            distancia_minima: Distancia mínima del jugador
            intentos: Número máximo de intentos
        
        Returns:
            (x, y) o None si no encuentra punto válido
        """
        for _ in range(intentos):
            # Generar posición aleatoria
            x = random.randint(100, ancho_mapa - 100)
            y = random.randint(100, alto_mapa - 100)
            
            # Verificar distancia del jugador
            dist_jugador = math.hypot(x - jugador_pos[0], y - jugador_pos[1])
            if dist_jugador < distancia_minima:
                continue
            
            # Verificar que no esté en un muro
            rect_prueba = pygame.Rect(x - 60, y - 60, 120, 120)  # Área de seguridad
            colision = False
            for muro in muros:
                if rect_prueba.colliderect(muro.rect):
                    colision = True
                    break
            
            if not colision:
                return (x, y)
        
        return None
    
    @staticmethod
    def generar_multiples_spawns(cantidad, ancho_mapa, alto_mapa, muros, jugador_pos, distancia_minima=300):
        """
        Genera múltiples puntos de spawn para enemigos.
        
        Returns:
            Lista de tuplas (x, y)
        """
        puntos = []
        for _ in range(cantidad):
            punto = enemigo.generar_punto_spawn_aleatorio(
                ancho_mapa, alto_mapa, muros, jugador_pos, distancia_minima
            )
            if punto:
                puntos.append(punto)
        return puntos
