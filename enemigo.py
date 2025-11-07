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
        self.vida       = tipos_def[tipo]["vida"]
        self.color_base = tipos_def[tipo]["color"]
        tam             = tipos_def[tipo]["tam"]

        self.rect = pygame.Rect(x, y, tam, tam)
        self.velocidad = velocidad + (2 if tipo == "veloz" else 0)
        if tipo == "bruto":
            self.velocidad = max(1, velocidad - 1)

        # patrulla / persecución
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido   = 1
        self.rango_deteccion       = 350  # Aumentado desde 250
        self.estado                = "patrullando"
        self.velocidad_persecucion = self.velocidad + 1
        self.tiempo_perdida        = 0

        # cooldowns de ataques
        self.cd = {"melee": 0, "shoot": 0, "aura": 0}

        # parámetros de ataques
        self.melee_alcance = 40           # veloz
        self.aura_radio    = 120          # bruto
        self.shoot_vel     = 6            # acechador


# -----------------------------
        # Proyectiles del ACECHADOR
        # -----------------------------
        # Cada proyectil es un dict: {"rect": Rect, "vx": float, "vy": float, "dmg": int, "vivo": bool}
        self.proyectiles_acechador = []

    # ---------- utilidades internas ----------
    def _bajar_cd(self):
        for k in self.cd:
            if self.cd[k] > 0:
                self.cd[k] -= 1

    def distancia_a(self, objetivo):
        """Calcula la distancia al centro de un rectángulo o jugador y devuelve distancia, dx, dy."""
        if isinstance(objetivo, pygame.Rect):
            rect_objetivo = objetivo
        else:
            rect_objetivo = objetivo.rect  # Asume que es un jugador

        dx = rect_objetivo.centerx - self.rect.centerx
        dy = rect_objetivo.centery - self.rect.centery
        distancia = math.sqrt(dx * dx + dy * dy)
        return distancia, dx, dy


    # ==========================================================
    # ===============   ATAQUES POR TIPO   =====================
    # ==========================================================

    # ---- Veloz: Cuerpo a cuerpo (quita 1 energía) ----
    def ataque_veloz_cuerpo_a_cuerpo(self, jugador):
        dist, _, _ = self.distancia_a(jugador.rect)
        if dist < self.melee_alcance and self.cd["melee"] == 0:
            jugador.energia = max(0, jugador.energia - 1)
            self.cd["melee"] = 35  # ~0.6s a 60 FPS

    # ---- Acechador: Proyectil ----
    def proyectil_acechador_disparar(self, jugador):
        """Crea un proyectil hacia el jugador si está en rango y no hay CD."""
        if self.cd["shoot"] > 0:
            return
        dist, dx, dy = self.distancia_a(jugador.rect)
        if dist >= self.rango_deteccion:
            return
        d = max(1, dist)
        vx, vy = (dx / d) * self.shoot_vel, (dy / d) * self.shoot_vel
        proj = {
            "rect": pygame.Rect(self.rect.centerx, self.rect.centery, 8, 8),
            "vx": vx, "vy": vy, "dmg": 1, "vivo": True
        }
        self.proyectiles_acechador.append(proj)
        self.cd["shoot"] = 240  # 4 segundos a 60 FPS

    def proyectil_acechador_mover_y_colisionar(self, muros, ancho_mapa, alto_mapa, jugador):
        """Mueve proyectiles, detecta colisiones con muros, fuera de mapa y jugador."""
        vivos = []
        for p in self.proyectiles_acechador:
            if not p["vivo"]:
                continue

            # mover
            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])

            # fuera del mapa
            if (p["rect"].right < 0 or p["rect"].left > ancho_mapa or
                p["rect"].bottom < 0 or p["rect"].top > alto_mapa):
                p["vivo"] = False

            # muros
            if p["vivo"]:
                for m in muros:
                    if p["rect"].colliderect(m.rect):
                        p["vivo"] = False
                        break

            # jugador
            if p["vivo"] and p["rect"].colliderect(jugador.rect):
                jugador.energia = max(0, jugador.energia - p["dmg"])
                p["vivo"] = False

            if p["vivo"]:
                vivos.append(p)

        self.proyectiles_acechador = vivos

    def proyectil_acechador_dibujar(self, ventana, camara):
        for p in self.proyectiles_acechador:
            pygame.draw.rect(ventana, (255, 255, 120), camara.aplicar(p["rect"]))

    # ---- Bruto: Aura de lentitud + golpe si toca (quita 1 energía en contacto) ----
    def aura_bruto_aplicar(self, jugador):
        # si el jugador está dentro del radio, aplica lentitud (contador en el jugador)
        dist, _, _ = self.distancia_a(jugador.rect)
        if dist < self.aura_radio:
            jugador.slow_ticks = max(jugador.slow_ticks, 45)  # ~0.75s
        # si hay contacto directo, daña
        if self.rect.colliderect(jugador.rect) and self.cd["aura"] == 0:
            jugador.energia = max(0, jugador.energia - 1)
            self.cd["aura"] = 30

    # ==========================================================
    # ===============   CICLOS MOVER / DIBUJAR   ===============
    # ==========================================================

    def mover(self, muros, ancho_mapa, alto_mapa, jugador=None):  # Cambiado de rect_jugador a jugador
        x_anterior, y_anterior = self.rect.x, self.rect.y

        # --- detección ---
        if jugador:
            dist, _, _ = self.distancia_a(jugador.rect)
            if dist <= self.rango_deteccion:
                self.estado = "persiguiendo"
                self.tiempo_perdida = 0
            elif self.estado == "persiguiendo":
                self.tiempo_perdida += 1
                if self.tiempo_perdida > 120:
                    self.estado = "patrullando"

        # --- comportamiento ---
        if self.estado == "persiguiendo" and jugador:
            dist, dx_to, dy_to = self.distancia_a(jugador.rect)
            if dist > 0:
                vel_actual = self.velocidad_persecucion
                self.rect.x += int((dx_to / dist) * vel_actual)
                self.rect.y += int((dy_to / dist) * vel_actual)
        else:
            if self.direccion == "horizontal":
                self.rect.x += self.velocidad * self.sentido
                if self.rect.left <= 20 or self.rect.right >= ancho_mapa - 20:
                    self.sentido *= -1
            else:
                self.rect.y += self.velocidad * self.sentido
                if self.rect.top <= 20 or self.rect.bottom >= alto_mapa - 20:
                    self.sentido *= -1

        # --- colisión con muros (igual que antes) ---
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                self.rect.x, self.rect.y = x_anterior, y_anterior
                if self.estado == "patrullando":
                    self.sentido *= -1
                    if random.random() < 0.3:
                        self.direccion = "vertical" if self.direccion == "horizontal" else "horizontal"
                else:
                    if random.random() < 0.5:
                        self.rect.x = x_anterior + random.randint(-3, 3)
                    else:
                        self.rect.y = y_anterior + random.randint(-3, 3)
                break

        # ataques por tipo
        if jugador is not None:
            if self.tipo == "veloz":
                self.ataque_veloz_cuerpo_a_cuerpo(jugador)
            elif self.tipo == "acechador":
                self.proyectil_acechador_disparar(jugador)
                self.proyectil_acechador_mover_y_colisionar(muros, ancho_mapa, alto_mapa, jugador)
            elif self.tipo == "bruto":
                self.aura_bruto_aplicar(jugador)

    def dibujar(self, ventana, camara):
        # cuerpo
        pygame.draw.rect(ventana, self.color_base, camara.aplicar(self.rect))

        # ojos / alerta simple
        # (opcionalmente puedes mantener tus ojos y circulitos de alerta aquí)

        # aura visible del bruto
        if self.tipo == "bruto":
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            pygame.draw.circle(ventana, (120, 120, 200), (int(cx), int(cy)), self.aura_radio, 2)

        # proyectiles del acechador
        if self.tipo == "acechador":
            self.proyectil_acechador_dibujar(ventana, camara)