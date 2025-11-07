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

        # movimiento y detección
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1
        self.rango_deteccion = 350  
        self.estado = "patrullando"
        self.velocidad_persecucion = self.velocidad + 1
        self.tiempo_perdida = 0

        # cooldowns
        self.tiempo_recarga = {"ataque": 0, "disparo": 0, "aura": 0}

        # parámetros de ataques
        self.alcance_melee = 40       # veloz
        self.radio_aura = 120         # bruto
        self.velocidad_disparo = 6    # acechador

        # proyectiles del acechador
        self.proyectiles = []  # cada uno: {"rect": Rect, "vx": float, "vy": float, "dano": int, "activo": bool}
        
        # Comportamientos variables
        self.rutina = random.choice(["ronda", "zigzag", "pausa"])


    # FUNCIONES INTERNAS Y GENERALES
    def reducir_recargas(self):
        """Reduce los tiempos de espera de cada ataque."""
        for clave in self.tiempo_recarga:
            if self.tiempo_recarga[clave] > 0:
                self.tiempo_recarga[clave] -= 1

    def distancia_a(self, objetivo):
        """Devuelve la distancia y dirección hacia el objetivo (jugador o rect)."""
        rect_objetivo = objetivo.rect if hasattr(objetivo, "rect") else objetivo
        dx = rect_objetivo.centerx - self.rect.centerx
        dy = rect_objetivo.centery - self.rect.centery
        distancia = math.hypot(dx, dy)
        return distancia, dx, dy

    # ATAQUES POR TIPO
    def ataque_veloz(self, jugador):
        """Ataque cuerpo a cuerpo del enemigo veloz."""
        distancia, _, _ = self.distancia_a(jugador)
        if distancia < self.alcance_melee and self.tiempo_recarga["ataque"] == 0:
            jugador.energia = max(0, jugador.energia - 1)
            self.tiempo_recarga["ataque"] = 35  # ~0.6 segundos

    def disparar_acechador(self, jugador):
        """Disparo de proyectil del acechador."""
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
        self.tiempo_recarga["disparo"] = 120  # 2 segundos

    def mover_proyectiles(self, muros, ancho_mapa, alto_mapa, jugador):
        """Actualiza proyectiles y revisa colisiones."""
        activos = []
        for p in self.proyectiles:
            if not p["activo"]:
                continue

            # mover proyectil
            p["rect"].x += int(p["vx"])
            p["rect"].y += int(p["vy"])

            # fuera del mapa
            if (p["rect"].right < 0 or p["rect"].left > ancho_mapa or
                p["rect"].bottom < 0 or p["rect"].top > alto_mapa):
                p["activo"] = False

            # colisión con muros
            for muro in muros:
                if p["activo"] and p["rect"].colliderect(muro.rect):
                    p["activo"] = False
                    break

            # colisión con jugador
            if p["activo"] and p["rect"].colliderect(jugador.rect):
                jugador.energia = max(0, jugador.energia - p["dano"])
                p["activo"] = False

            if p["activo"]:
                activos.append(p)

        self.proyectiles = activos

    def aplicar_aura_bruto(self, jugador):
        """Aura del bruto: ralentiza y daña si hay contacto."""
        distancia, _, _ = self.distancia_a(jugador)
        if distancia < self.radio_aura:
            jugador.slow_ticks = max(jugador.slow_ticks, 45)
        if self.rect.colliderect(jugador.rect) and self.tiempo_recarga["aura"] == 0:
            jugador.energia = max(0, jugador.energia - 1)
            self.tiempo_recarga["aura"] = 30

    # MOVIMIENTO Y DETECCIÓN
    def mover(self, muros, ancho_mapa, alto_mapa, jugador=None, zonas_seguras=None):
        if zonas_seguras is None:
            zonas_seguras = []

        x_anterior, y_anterior = self.rect.x, self.rect.y

        # detección del jugador
        jugador_oculto = getattr(jugador, "oculto", False) if jugador else False

        if jugador and not jugador_oculto:
            distancia, dx, dy = self.distancia_a(jugador)
            if distancia <= self.rango_deteccion:
                self.estado = "persiguiendo"
                self.tiempo_perdida = 0
            elif self.estado == "persiguiendo":
                self.tiempo_perdida += 1
                if self.tiempo_perdida > 120:
                    self.estado = "patrullando"
        elif self.estado == "persiguiendo":
            self.tiempo_perdida += 1
            if self.tiempo_perdida > 45:
                self.estado = "patrullando"
        if jugador and self.tiene_linea_de_vision(jugador, muros):
            self.estado = "persiguiendo"


        # movimiento general
        if self.estado == "persiguiendo" and jugador and not jugador_oculto:
            distancia, dx, dy = self.distancia_a(jugador)
            if distancia > 0:
                vel = self.velocidad_persecucion
                self.rect.x += int((dx / distancia) * vel)
                self.rect.y += int((dy / distancia) * vel)
        else:
            # patrulla básica
            if self.direccion == "horizontal":
                self.rect.x += self.velocidad * self.sentido
                if self.rect.left <= 20 or self.rect.right >= ancho_mapa - 20:
                    self.sentido *= -1
            else:
                self.rect.y += self.velocidad * self.sentido
                if self.rect.top <= 20 or self.rect.bottom >= alto_mapa - 20:
                    self.sentido *= -1

        # colisión con muros
        for muro in muros:
            if self.rect.colliderect(muro.rect):
                self.rect.x, self.rect.y = x_anterior, y_anterior
                self.sentido *= -1
                if random.random() < 0.3:
                    self.direccion = "vertical" if self.direccion == "horizontal" else "horizontal"
                break

        # colisión con zonas seguras (bloquean a enemigos)
        for zona in zonas_seguras:
            if self.rect.colliderect(zona):
                self.rect.x, self.rect.y = x_anterior, y_anterior
                self.sentido *= -1
                if random.random() < 0.4:
                    self.direccion = "vertical" if self.direccion == "horizontal" else "horizontal"
                break

        # ataques
        if jugador:
            if self.tipo == "veloz":
                self.ataque_veloz(jugador)
            elif self.tipo == "acechador":
                self.disparar_acechador(jugador)
                self.mover_proyectiles(muros, ancho_mapa, alto_mapa, jugador)
            elif self.tipo == "bruto":
                self.aplicar_aura_bruto(jugador)
        if self.rutina == "zigzag":
            self.rect.x += self.velocidad * self.sentido
            if random.random() < 0.05:
                self.rect.y += random.choice([-self.velocidad, self.velocidad])
        elif self.rutina == "pausa" and random.random() < 0.01:
            self.sentido *= -1


    # DIBUJO
    def dibujar(self, ventana, camara):
        pygame.draw.rect(ventana, self.color, camara.aplicar(self.rect))

        if self.tipo == "bruto":
            cx, cy = camara.aplicar_pos(self.rect.centerx, self.rect.centery)
            pygame.draw.circle(ventana, (120, 120, 200), (int(cx), int(cy)), self.radio_aura, 2)

        if self.tipo == "acechador":
            for p in self.proyectiles:
                pygame.draw.rect(ventana, (255, 255, 120), camara.aplicar(p["rect"]))
   
    def tiene_linea_de_vision(self, jugador, muros):
        distancia, dx, dy = self.distancia_a(jugador)
        pasos = int(distancia / 20)
        for i in range(1, pasos):
            x = self.rect.centerx + (dx / pasos) * i
            y = self.rect.centery + (dy / pasos) * i
            punto = pygame.Rect(x, y, 4, 4)
            if any(punto.colliderect(m.rect) for m in muros):
                return False
        return True
