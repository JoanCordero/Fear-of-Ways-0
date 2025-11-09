import pygame
import random
import math

class enemigo:
    def __init__(self, x, y, velocidad, tipo=None):
        tipos_def = {
            "veloz":     {"vida": 2, "color": (255, 255,   0), "tam": 25},
            "acechador": {"vida": 3, "color": (  0, 255, 255), "tam": 35},
            "bruto":     {"vida": 5, "color": (255,  80,  80), "tam": 50},
        }

        if tipo is None:
            tipo = random.choice(list(tipos_def.keys()))

        self.tipo = tipo
        self.vida = tipos_def[tipo]["vida"]
        self.color = tipos_def[tipo]["color"]
        tamano = tipos_def[tipo]["tam"]

        self.rect = pygame.Rect(x, y, tamano, tamano)
        self.velocidad = velocidad + (2 if tipo == "veloz" else 0)
        if tipo == "bruto":
            self.velocidad = max(1, velocidad - 1)

        # Movimiento y detección - BALANCEADO
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1
        self.rango_deteccion = 250  # Reducido de 350 a 250
        self.estado = "patrullando"
        self.velocidad_persecucion = self.velocidad + 0.5  # Reducido de +1 a +0.5
        self.tiempo_perdida = 0

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

        # Acciones por tipo
        if self.tipo == "veloz":
            self.ataque_veloz(jugador)
        elif self.tipo == "bruto":
            self.aplicar_aura_bruto(jugador)
        elif self.tipo == "acechador":
            self.disparar_acechador(jugador)
            self.mover_proyectiles(muros, ancho, alto, jugador)


    # --------------------------------------------------------
    # DIBUJO
    # --------------------------------------------------------
    def dibujar(self, ventana, camara):
        # Color adaptativo si está persiguiendo o preparando ataque
        if self.preparando_ataque > 0:
            # Parpadeo rojo intenso cuando prepara ataque
            intensidad = int(255 * (self.preparando_ataque % 10) / 10)
            color_actual = (255, intensidad, intensidad)
        elif self.objetivo_visible:
            color_actual = (255, 50, 50)
        else:
            color_actual = self.color
        
        pygame.draw.rect(ventana, color_actual, camara.aplicar(self.rect))
        
        # Indicador visual de preparación de ataque (veloz)
        if self.tipo == "veloz" and self.preparando_ataque > 0:
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            radio_advertencia = int(self.alcance_melee * (self.preparando_ataque / 20))
            pygame.draw.circle(ventana, (255, 100, 100), (int(cx), int(cy)), radio_advertencia, 2)

        # Aura del bruto
        if self.tipo == "bruto":
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            pygame.draw.circle(ventana, (120, 120, 200), (int(cx), int(cy)), self.radio_aura, 2)

        # Proyectiles del acechador (estilo circular más sutil)
        if self.tipo == "acechador":
            for p in self.proyectiles:
                rect_p = camara.aplicar(p["rect"])
                # Dibujar como círculo en lugar de rectángulo
                cx = rect_p.centerx
                cy = rect_p.centery
                pygame.draw.circle(ventana, (255, 100, 100), (int(cx), int(cy)), 4)  # Círculo rojo pequeño
                pygame.draw.circle(ventana, (255, 200, 200), (int(cx), int(cy)), 2)  # Centro brillante


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
