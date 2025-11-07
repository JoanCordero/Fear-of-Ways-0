import pygame
import random
import math
from nivel import nivel
from camara import camara
from jugador import jugador
from enemigo import enemigo
from proyectil import proyectil

# Colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
gris = (40, 40, 40)
rojo = (255, 0, 0)
amarillo = (255, 255, 0)
verde = (0, 255, 0)

class juego:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.nivel_actual = None
        self.numero_nivel = 1
        self.enemigos = []
        self.resultado = ""
        self.camara = None
        self.opcion_pausa = 0
        self.rects_pausa = []  
        self.proyectiles = []

    # Pantallas
    def menu(self):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        ventana.fill(negro)
        self.dibujar_texto("Fear of Ways", 60, blanco, ancho//2, 120)
        self.dibujar_texto("3 Niveles de Mazmorras Expandidas", 35, amarillo, ancho//2, 200)
        self.dibujar_texto("Selecciona tu personaje:", 35, blanco, ancho//2, 270)
        self.dibujar_texto("1 Explorador  2 Cazador  3 Ingeniero", 28, blanco, ancho//2, 320)
        self.dibujar_texto("Encuentra la salida verde en cada nivel", 25, verde, ancho//2, 380)
        self.dibujar_texto("Evita a los enemigos rojos", 25, rojo, ancho//2, 410)
        self.dibujar_texto("La cámara te seguirá por el mapa", 25, (100, 200, 255), ancho//2, 440)
        self.dibujar_texto("ESC para salir", 25, blanco, ancho//2, 480)

    def iniciar_juego(self, tipo):
        if tipo == 1:
            self.jugador = jugador("Explorador", amarillo, velocidad=4, energia=100, vision=150)
        elif tipo == 2:
            self.jugador = jugador("Cazador", verde, velocidad=6, energia=70, vision=120)
        elif tipo == 3:
            self.jugador = jugador("Ingeniero", (0, 150, 255), velocidad=3, energia=120, vision=180)

        self.numero_nivel = 1
        self.cargar_nivel(1)
        self.resultado = ""
        self.estado = "jugando"
    
    def cargar_nivel(self, numero):
        """Carga un nivel específico"""
        self.numero_nivel = numero
        self.nivel_actual = nivel(numero)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)
        
        # Crear enemigos
        self.enemigos = []
        spawns = list(self.nivel_actual.spawn_enemigos)

        # forzar al menos 1 de cada tipo (si hay >=3 spawns)
        tipos_base = ["veloz", "acechador", "bruto"]
        random.shuffle(spawns)
        for t in tipos_base:
            if spawns:
                sx, sy = spawns.pop()
                vel = random.randint(2, 4)
                self.enemigos.append(enemigo(sx, sy, vel, tipo=t))

        # el resto, aleatorios con pesos
        for sx, sy in spawns:
            vel = random.randint(2, 4)
            tipo = random.choices(["veloz","acechador","bruto"], weights=[0.45,0.35,0.20], k=1)[0]
            self.enemigos.append(enemigo(sx, sy, vel, tipo=tipo))

        
        # Resetear posición del jugador
        self.jugador.resetear_posicion()

    def jugar(self):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        ventana.fill(gris)
        
        # Actualizar cámara
        self.camara.actualizar(self.jugador.rect)
        
        # Dibujar nivel
        self.nivel_actual.dibujar(ventana, self.camara)
        
        # Mover jugador
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas, self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto)

        # Mover y dibujar proyectiles
        for p in list(self.proyectiles):
            activo = p.mover(self.nivel_actual.muros)
            if not activo:
                self.proyectiles.remove(p)
                continue
            p.dibujar(ventana, self.camara)
        
        # ¿Está dentro de un escondite?
        self.jugador.oculto = any(
            esc.colliderect(self.jugador.rect) for esc in self.nivel_actual.escondites)

        # Opcional: marco visual si está oculto
        if self.jugador.oculto:
            r = self.camara.aplicar(self.jugador.rect)
            pygame.draw.rect(pygame.display.get_surface(), (80, 200, 255), r, 3)
        
        # Mover y dibujar enemigos
        for enemigo_actual in self.enemigos:
            enemigo_actual.mover(
                self.nivel_actual.muros,
                self.nivel_actual.ancho,
                self.nivel_actual.alto,
                self.jugador,
                self.nivel_actual.escondites
            )
            enemigo_actual.dibujar(ventana, self.camara)

            # Colisión jugador - enemigo
            if self.jugador.rect.colliderect(enemigo_actual.rect):
                self.jugador.recibir_daño(1)
                # flash visual opcional (enemigo rojo si hizo daño)
                enemigo_actual.color_base = (255, 50, 50)
                if self.jugador.vida <= 0:    
                    self.resultado = "perdiste"
                    self.estado = "fin"
        # Detectar impactos de proyectiles con enemigos
        for p in list(self.proyectiles):
            for enemigo_actual in list(self.enemigos):
                if p.rect.colliderect(enemigo_actual.rect):
                    enemigo_actual.vida -= 1
                    self.proyectiles.remove(p)
                    if enemigo_actual.vida <= 0:
                        self.enemigos.remove(enemigo_actual)
                    break
        # Dibujar jugador
        self.jugador.dibujar(ventana, self.camara)

        # Dibujar linterna
        self.dibujar_linterna()

        # Verificar salida
        if self.jugador.rect.colliderect(self.nivel_actual.salida.rect):
            if self.numero_nivel < 3:
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                self.resultado = "ganaste"
                self.estado = "fin"

        # UI
        self.dibujar_texto(f"Nivel: {self.numero_nivel}/3", 30, blanco, 10, 10, centrado=False)
        self.dibujar_texto(f"Energía: {int(self.jugador.energia)}", 30, blanco, 10, 40, centrado=False)

        #HUD: vida y energia
        self.dibujar_barra(1075, 10, 200, 12, self.jugador.vida, self.jugador.vida_max, (255, 80, 80))
        self.dibujar_barra(1075, 28, 200, 10, self.jugador.energia, self.jugador.energia_max, (80, 200, 255))
        
    def pantalla_final(self):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        ventana.fill(negro)
        if self.resultado == "ganaste":
            color = verde
            mensaje = "¡Escapaste de las 3 mazmorras!"
            submensaje = f"Completaste todos los niveles con {self.jugador.nombre}"
        else:
            color = rojo
            mensaje = "Fuiste atrapado en la oscuridad..."
            submensaje = f"Llegaste hasta el nivel {self.numero_nivel}"
        
        self.dibujar_texto(mensaje, 50, color, ancho // 2, 220)
        self.dibujar_texto(submensaje, 30, blanco, ancho // 2, 290)
        self.dibujar_texto("ENTER para volver al menú", 30, blanco, ancho // 2, 380)

    # Utilidades

    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        fuente_local = pygame.font.Font(None, tam)
        superficie = fuente_local.render(texto, True, color)
        rect = superficie.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        ventana.blit(superficie, rect)
        return rect  # Devolver el rectángulo del texto para detección de clics

    def dibujar_linterna(self):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 240))

        luz = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        mx, my = pygame.mouse.get_pos()

        dx, dy = mx - cx, my - cy
        if dx == 0 and dy == 0:
            angulo = 0.0
        else:
            angulo = math.atan2(dy, dx)

        radio = max(1, int(self.jugador.vision))
        semiancho = math.radians(35)
        pasos = 48

        for i in range(pasos, 0, -1):
            r = radio * (i / pasos)
            a = semiancho * (i / pasos)

            izquierdo = (cx + r * math.cos(angulo - a), cy + r * math.sin(angulo - a))
            derecho = (cx + r * math.cos(angulo + a), cy + r * math.sin(angulo + a))

            alpha = int(240 * (i / pasos))
            alpha = max(0, min(240, alpha))

            pygame.draw.polygon(
                luz,
                (255, 255, 255, alpha),
                [(cx, cy), izquierdo, derecho]
            )

        sombra.blit(luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        ventana.blit(sombra, (0, 0))
    
    def dibujar_barra(self, x, y, ancho, alto, valor, valor_max, color):
        ventana = pygame.display.get_surface()
        ratio = valor / valor_max
        if ratio < 0:
            ratio = 0
        if ratio > 1:
            ratio = 1
        fondo = pygame.Rect(x, y, ancho, alto)
        barra = pygame.Rect(x, y, int(ancho * ratio), alto)
        pygame.draw.rect(ventana, (50, 50, 50), fondo)
        pygame.draw.rect(ventana, color, barra)
        pygame.draw.rect(ventana, (255, 255, 255), fondo, 1)
    def pantalla_pausa(self):
        ventana = pygame.display.get_surface()
        ancho, alto = ventana.get_size()
        ventana.fill((10, 10, 20))

        self.dibujar_texto("pausa", 64, (0, 200, 255), ancho//2, alto//2 - 140)
        opciones = ["reanudar", "salir al menú"]
        self.opciones_rects = []  # Guardar rectángulos de las opciones para detección de clics

        for i, texto in enumerate(opciones):
            y = alto//2 - 20 + i*60
            color = blanco  # Eliminar el efecto amarillo
            rect = self.dibujar_texto(texto, 40, color, ancho//2 - 100, y, centrado=False)
            self.opciones_rects.append(rect)  # Guardar el rectángulo de la opción



    # LOOP PRINCIPAL
    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return

                # menú principal
                if self.estado == "menu":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                        if e.key == pygame.K_1:
                            self.iniciar_juego(1)
                        if e.key == pygame.K_2:
                            self.iniciar_juego(2)
                        if e.key == pygame.K_3:
                            self.iniciar_juego(3)

                # pausa
                elif self.estado == "pausa":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            self.estado = "jugando"  # volver al juego
                        elif e.key in (pygame.K_UP, pygame.K_w):
                            self.opcion_pausa = (self.opcion_pausa - 1) % 2
                        elif e.key in (pygame.K_DOWN, pygame.K_s):
                            self.opcion_pausa = (self.opcion_pausa + 1) % 2
                        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.opcion_pausa == 0:
                                self.estado = "jugando"  # reanudar
                            else:
                                self.estado = "menu"  # salir al menú
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # Clic izquierdo
                        for i, rect in enumerate(self.opciones_rects):
                            if rect.collidepoint(e.pos):
                                if i == 0:
                                    self.estado = "jugando"  # reanudar
                                elif i == 1:
                                    self.estado = "menu"  # salir al menú

                # jugando
                elif self.estado == "jugando":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        self.estado = "pausa"
                        self.opcion_pausa = 0
                    
                    # lanzar proyectil con clik derecho
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                        mx, my = pygame.mouse.get_pos()
                        px, py = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
                        nuevo = proyectil(px, py, self.camara.offset_x + mx, self.camara.offset_y + my, self.jugador.color)
                        self.proyectiles.append(nuevo)

                # pantalla final
                elif self.estado == "fin":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                        self.estado = "menu"

            # render según el estado
            if self.estado == "menu":
                self.menu()
            elif self.estado == "jugando":
                self.jugar()
            elif self.estado == "pausa":
                self.pantalla_pausa()
            elif self.estado == "fin":
                self.pantalla_final()

            pygame.display.flip()
            reloj.tick(60)
