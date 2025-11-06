import pygame
import random
import math

class enemigo:
    def __init__(self, x, y, velocidad, tipo=None):
        # tipos con vida distinta (no se muestra en pantalla)
        tipos_def = {
            "veloz": {
                "vida": 2,
                "color": (255, 255, 0),    # amarillo brillante
                "tam": 25                  # pequeño y rápido
            },
            "acechador": {
                "vida": 3,
                "color": (0, 255, 255),    # celeste
                "tam": 35                  # mediano
            },
            "bruto": {
                "vida": 5,
                "color": (255, 80, 80),    # rojo oscuro
                "tam": 50                  # grande y lento
            },
        }
        if tipo is None:
            tipo = random.choice(list(tipos_def.keys()))
        self.tipo = tipo
        self.vida_max = tipos_def[tipo]["vida"]
        self.vida = self.vida_max
        self.color_base = tipos_def[tipo]["color"]
        tam = tipos_def[tipo]["tam"]

        # rect y movimiento
        self.rect = pygame.Rect(x, y, tam, tam)
        self.velocidad = velocidad
        if tipo == "veloz":
            self.velocidad += 2
        elif tipo == "bruto":
            self.velocidad = max(1, velocidad - 1)

        # dirección inicial y sentido para patrulla (FALTABAN)
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1

        # percepción
        self.rango_deteccion = 250
        self.estado = "patrullando"   # "patrullando" | "persiguiendo"
        # usar la velocidad final ya ajustada por tipo
        self.velocidad_persecucion = self.velocidad + 1
        self.tiempo_perdida = 0


    def distancia_a(self, rect_jugador):
        dx = rect_jugador.centerx - self.rect.centerx
        dy = rect_jugador.centery - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def mover(self, muros, ancho_mapa, alto_mapa, rect_jugador=None):
        x_anterior, y_anterior = self.rect.x, self.rect.y

        # detección
        if rect_jugador:
            distancia = self.distancia_a(rect_jugador)
            if distancia <= self.rango_deteccion:
                self.estado = "persiguiendo"
                self.tiempo_perdida = 0
            elif self.estado == "persiguiendo":
                self.tiempo_perdida += 1
                if self.tiempo_perdida > 120:
                    self.estado = "patrullando"

        # comportamiento
        if self.estado == "persiguiendo" and rect_jugador:
            dx = rect_jugador.centerx - self.rect.centerx
            dy = rect_jugador.centery - self.rect.centery
            distancia = math.sqrt(dx * dx + dy * dy)
            if distancia > 0:
                vel_actual = self.velocidad_persecucion
                self.rect.x += int((dx / distancia) * vel_actual)
                self.rect.y += int((dy / distancia) * vel_actual)
        else:
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

    def dibujar(self, ventana, camara):
        rect_pantalla = camara.aplicar(self.rect)

        # color según estado (sin barra de vida)
        if self.estado == "persiguiendo":
            color_cuerpo = (min(self.color_base[0]+30,255), self.color_base[1], self.color_base[2])
            color_ojos = (255, 255, 0)
        else:
            color_cuerpo = self.color_base
            color_ojos = (200, 200, 100)

        pygame.draw.rect(ventana, color_cuerpo, rect_pantalla)
        pos_ojo1 = camara.aplicar_pos(self.rect.x + 10, self.rect.y + 10)
        pos_ojo2 = camara.aplicar_pos(self.rect.x + 25, self.rect.y + 10)
        pygame.draw.circle(ventana, color_ojos, pos_ojo1, 4)
        pygame.draw.circle(ventana, color_ojos, pos_ojo2, 4)

        if self.estado == "persiguiendo":
            pos_alerta = camara.aplicar_pos(self.rect.centerx, self.rect.y - 15)
            pygame.draw.circle(ventana, (255,255,0), pos_alerta, 8)
            pygame.draw.circle(ventana, (255,0,0), pos_alerta, 6)
