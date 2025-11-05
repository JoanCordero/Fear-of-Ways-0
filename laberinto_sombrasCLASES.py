import pygame
import sys
import random
import math
import os
from datetime import datetime

# Inicialización
pygame.init()
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h # capta direcamente la resolucion del monitor para pantalla completa
ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
# Inicializar mixer de sonido si es posible
try:
    pygame.mixer.init()
except Exception:
    # si falla el mezclador, seguimos sin sonido
    pass
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El Laberinto de las Sombras")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (40, 40, 40)
ROJO = (255, 0, 0)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)

clock = pygame.time.Clock()

# ------------------------
# Clases principales
# ------------------------

class Player:
    def __init__(self, nombre, color, velocidad, vida, vision):
        self.nombre = nombre
        self.color = color
        self.velocidad = velocidad
        self.vida = vida
        self.max_vida = vida
        self.vision = vision
        self.energia = energia
        self.max_energia = energia
        self.vision = vision  # radio de linterna
        self.rect = pygame.Rect(380, 280, 40, 40)
        self._last_pos = self.rect.topleft

    def mover(self, teclas):
        moved = False
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
            moved = True
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
            moved = True
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
            moved = True
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad
            moved = True

        # Mantener dentro de pantalla
        self.rect.clamp_ip(pygame.Rect(0, 0, ANCHO, ALTO))

        # actualizar última posición para detectar si está quieto
        now_pos = self.rect.topleft
        still = (now_pos == self._last_pos)
        self._last_pos = now_pos
        return moved, still

    def actualizar_energia(self, dt, linterna_encendida, moving, still):
        """dt: segundos desde último frame. linterna_encendida: bool."""
        # Consumo por segundo cuando la linterna está encendida
        drain_rate = 18.0  # energía por segundo

        # Regeneración cuando está quieto (parcial)
        regen_rate_still = 12.0  # energía por segundo cuando quieto

        if linterna_encendida and self.energia > 0:
            self.energia -= drain_rate * dt
        else:
            # pequeña regeneración si la linterna está apagada
            if not linterna_encendida and not moving:
                self.energia += 6.0 * dt

        # regeneración adicional si está quieto
        if still:
            self.energia += regen_rate_still * dt

        # clamp
        if self.energia > self.max_energia:
            self.energia = self.max_energia
        if self.energia < 0:
            self.energia = 0

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, self.color, self.rect)



class Enemy:
    def __init__(self, x, y, velocidad):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.velocidad = velocidad
        self.direccion = random.choice(["horizontal", "vertical"])
        self.sentido = 1

        # comportamiento de detección y persecución
        self.detection_range = 180
        self.chasing = False
        self.chase_speed_multiplier = 1.8

    def mover(self):
        # movimiento patrullando
        if not self.chasing:
            if self.direccion == "horizontal":
                self.rect.x += self.velocidad * self.sentido
                if self.rect.left <= 0 or self.rect.right >= ANCHO:
                    self.sentido *= -1
            else:
                self.rect.y += self.velocidad * self.sentido
                if self.rect.top <= 0 or self.rect.bottom >= ALTO:
                    self.sentido *= -1

    def detectar_y_perseguir(self, jugador, dt):
        # detectar jugador por proximidad
        ex, ey = self.rect.center
        px, py = jugador.rect.center
        dx = px - ex
        dy = py - ey
        distancia = math.hypot(dx, dy)

        if distancia <= self.detection_range:
            self.chasing = True
        else:
            # si el jugador se aleja mucho, dejar de perseguir
            if distancia > self.detection_range * 1.25:
                self.chasing = False

        if self.chasing and distancia > 1:
            # mover hacia el jugador (velocidad dependiente de dt)
            nx = dx / distancia
            ny = dy / distancia
            speed = self.velocidad * self.chase_speed_multiplier
            # multiplicador 60 para hacer el movimiento similar a frames por segundo
            self.rect.x += int(nx * speed * dt * 60)
            self.rect.y += int(ny * speed * dt * 60)

    def dibujar(self, ventana):
        color = (255, 120, 120) if self.chasing else ROJO
        pygame.draw.rect(ventana, color, self.rect)


class Game:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.enemigos = []
        self.resultado = ""
        self.fuente = pygame.font.Font(None, 36)
        # pantalla completa por defecto apagada
        self.fullscreen = False

        # cargar sonidos (opcional). Coloca archivos en carpeta 'sounds' o en el mismo directorio.
        self.sounds = {}
        base = os.path.dirname(__file__)
        sound_files = {
            'ambient': os.path.join(base, 'sounds', 'ambient.wav'),
            'start': os.path.join(base, 'sounds', 'start.wav'),
            'victory': os.path.join(base, 'sounds', 'victory.wav'),
            'lose': os.path.join(base, 'sounds', 'lose.wav'),
        }
        for key, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[key] = pygame.mixer.Sound(path)
            except Exception:
                self.sounds[key] = None

        # archivo donde guardar partidas
        self.save_file = os.path.join(base, 'partidas.txt')

    # ----------- PANTALLAS -----------

    def menu(self):
        ventana.fill(NEGRO)
        self.dibujar_texto("El Laberinto de las Sombras", 60, BLANCO, ANCHO//2, 150)
        self.dibujar_texto("Selecciona tu personaje:", 40, BLANCO, ANCHO//2, 250)
        self.dibujar_texto("[1] Explorador  [2] Cazador  [3] Ingeniero", 30, BLANCO, ANCHO//2, 320)
        self.dibujar_texto("ESC para salir", 30, BLANCO, ANCHO//2, 370)
        # Opción de pantalla completa
        fs_text = "ON" if self.fullscreen else "OFF"
        self.dibujar_texto(f"[F] Pantalla completa: {fs_text}", 24, BLANCO, ANCHO//2, 420)
        self.dibujar_texto("Mantén SPACE para encender la linterna", 20, BLANCO, ANCHO//2, 460)

    def iniciar_juego(self, tipo):
        if tipo == 1:
            self.jugador = Player("Explorador", AMARILLO, velocidad=5, vida=100, vision=150)
        elif tipo == 2:
            self.jugador = Player("Cazador", VERDE, velocidad=7, vida=70, vision=120)
        elif tipo == 3:
            self.jugador = Player("Ingeniero", (0, 150, 255), velocidad=4, vida=120, vision=180)

        # Crear enemigos
        self.enemigos = [Enemy(random.randint(100, 700), random.randint(100, 500), random.randint(2, 4)) for _ in range(4)]
        self.resultado = ""
        self.estado = "jugando"

        # Ajustar modo pantalla según opción
        global ventana
        if self.fullscreen:
            ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        else:
            ventana = pygame.display.set_mode((ANCHO, ALTO))

        # reproducir sonido de inicio si existe
        if 'start' in self.sounds and self.sounds.get('start'):
            try:
                self.sounds['start'].play()
            except Exception:
                pass

        # reproducir ambiente en loop si existe
        if 'ambient' in self.sounds and self.sounds.get('ambient'):
            try:
                self.sounds['ambient'].play(loops=-1)
            except Exception:
                pass

    def jugar(self, dt):
        ventana.fill(GRIS)
        teclas = pygame.key.get_pressed()
        moved, still = self.jugador.mover(teclas)

        # Gestionar linterna: mantener pulsada la tecla SPACE para encender
        keys = pygame.key.get_pressed()
        linterna_encendida = keys[pygame.K_SPACE] and self.jugador.energia > 0

        # Actualizar energía (consumo / regeneración)
        self.jugador.actualizar_energia(dt, linterna_encendida, moved, still)

        # Mover y dibujar enemigos (detección y persecución)
        for enemigo in self.enemigos:
            enemigo.detectar_y_perseguir(self.jugador, dt)
            enemigo.mover()
            enemigo.dibujar(ventana)

            # Colisión jugador - enemigo
            if self.jugador.rect.colliderect(enemigo.rect):
                self.resultado = "perdiste"
                self.estado = "fin"

        # Dibujar jugador
        self.jugador.dibujar(ventana)

        # Dibujar linterna (visión circular)
        self.dibujar_linterna()

        # Vida
        font = pygame.font.Font(None, 36)
        texto_vida = font.render("Vida:", True, BLANCO)
        ventana.blit(texto_vida, (20, 18))  # posición exacta y centrada verticalmente

        # Coordenadas calculadas para que la barra quede alineada con el texto
        text_width = texto_vida.get_width()
        bar_x = 30 + text_width + 10   # deja 10 píxeles de separación después del texto
        bar_y = 20                     # alineado con el texto
        bar_width = 220
        bar_height = 18

        # Relación vida / vida máxima
        ratio = self.jugador.vida / self.jugador.max_vida if self.jugador.max_vida > 0 else 0

        # Fondo rojo
        pygame.draw.rect(ventana, ROJO, (bar_x, bar_y, bar_width, bar_height))
        # Parte verde proporcional
        pygame.draw.rect(ventana, VERDE, (bar_x, bar_y, bar_width * ratio, bar_height))
        # Borde blanco
        pygame.draw.rect(ventana, BLANCO, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
        
        # Dibujar linterna sólo si está encendida y hay energía
        if linterna_encendida and self.jugador.energia > 0:
            self.dibujar_linterna()

        # Condición de victoria: esquina inferior derecha
        if self.jugador.rect.x > 750 and self.jugador.rect.y > 550:
            self.resultado = "ganaste"
            self.estado = "fin"

        # UI simple (mostrar energía con 0..max)
        energia_mostrar = int(self.jugador.energia)
        self.dibujar_texto(f"Energía: {energia_mostrar}", 30, BLANCO, 10, 10, centrado=False)

    def pantalla_final(self):
        ventana.fill(NEGRO)
        if self.resultado == "ganaste":
            color = VERDE
            mensaje = "¡Escapaste del laberinto!"
            # efecto de victoria
            if 'victory' in self.sounds and self.sounds.get('victory'):
                try:
                    self.sounds['victory'].play()
                except Exception:
                    pass
        else:
            color = ROJO
            mensaje = "Fuiste atrapado en la oscuridad..."
            # efecto de derrota
            if 'lose' in self.sounds and self.sounds.get('lose'):
                try:
                    self.sounds['lose'].play()
                except Exception:
                    pass
        self.dibujar_texto(mensaje, 50, color, ANCHO // 2, 250)
        self.dibujar_texto("ENTER para volver al menú", 30, BLANCO, ANCHO // 2, 350)

    # ----------- UTILIDADES -----------

    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        font = pygame.font.Font(None, tam)
        superficie = font.render(texto, True, color)
        rect = superficie.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        ventana.blit(superficie, rect)

    def dibujar_linterna(self):
        # Crear superficie de sombra (negra semitransparente)
        sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 240))

        # Superficie para dibujar el haz de luz (gradiente)
        luz = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

        # Centro de la linterna (player) y objetivo (mouse)
        cx, cy = self.jugador.rect.center
        mx, my = pygame.mouse.get_pos()

        # Si el mouse coincide con el centro, usar dirección por defecto
        dx, dy = mx - cx, my - cy
        if dx == 0 and dy == 0:
            angle = 0.0
        else:
            angle = math.atan2(dy, dx)

        # Parámetros del cono
        # Hacer que el radio dependa de la energía restante (más realista):
        energia_frac = max(0.0, min(1.0, self.jugador.energia / max(1, self.jugador.max_energia)))
        radius = max(1, int(self.jugador.vision * (0.5 + 0.5 * energia_frac)))
        half_angle = math.radians(35)  # semiancho del haz (ajusta aquí el "amplitud")
        steps = 48  # cuantos anillos/pasos para el degradado (más = más suave)

        # Dibujar el haz como un conjunto de triángulos (fan) con alpha decreciente
        # Dibujamos de fuera hacia dentro para que las capas internas atenúen correctamente
        for i in range(steps, 0, -1):
            r = radius * (i / steps)
            a = half_angle * (i / steps)

            left = (cx + r * math.cos(angle - a), cy + r * math.sin(angle - a))
            right = (cx + r * math.cos(angle + a), cy + r * math.sin(angle + a))

            # Alpha: más oscuro hacia el borde del cono, más claro hacia el centro
            # Normalizamos al rango 0..240 (coincide con la opacidad de la sombra)
            alpha = int(240 * (i / steps))
            alpha = max(0, min(240, alpha))

            # Dibujar triángulo en la superficie de luz usando blanco semi-transparente
            # (al blitearlo sobre la sombra con BLEND_RGBA_SUB reduciremos la opacidad
            #  de la sombra en las zonas donde la luz está presente)
            pygame.draw.polygon(
                luz,
                (255, 255, 255, alpha),
                [(cx, cy), left, right]
            )

        # Restar la superficie de luz de la sombra para crear el efecto de "agujero" iluminado
        sombra.blit(luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Colocar la máscara encima de todo lo dibujado
        ventana.blit(sombra, (0, 0))


    # ----------- LOOP PRINCIPAL -----------

    def ejecutar(self):
        while True:
            # dt en segundos
            dt = clock.tick(60) / 1000.0

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.estado == "menu":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        if e.key == pygame.K_1:
                            self.iniciar_juego(1)
                        if e.key == pygame.K_2:
                            self.iniciar_juego(2)
                        if e.key == pygame.K_3:
                            self.iniciar_juego(3)
                        if e.key == pygame.K_f:
                            # alternar modo pantalla completa en el menú
                            self.fullscreen = not self.fullscreen
                            # aplica inmediatamente la ventana (no cambia estado de juego)
                            global ventana
                            if self.fullscreen:
                                ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
                            else:
                                ventana = pygame.display.set_mode((ANCHO, ALTO))

                elif self.estado == "fin":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                        self.estado = "menu"

            if self.estado == "menu":
                self.menu()
            elif self.estado == "jugando":
                self.jugar(dt)
            elif self.estado == "fin":
                self.pantalla_final()

            pygame.display.flip()


# ------------------------
# Ejecución
# ------------------------
if __name__ == "__main__":
    juego = Game()
    juego.ejecutar()
