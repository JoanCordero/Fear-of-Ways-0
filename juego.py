import pygame
import random
import math
from nivel import nivel
from camara import camara
from jugador import jugador
from enemigo import enemigo
from proyectil import proyectil

# Colores para UI y dibujo
negro = (0, 0, 0)
blanco = (255, 255, 255)
gris = (40, 40, 40)
rojo = (255, 0, 0)
amarillo = (255, 255, 0)
verde = (0, 255, 0)

class juego:
    def __init__(self):
        # Estado general del juego
        self.estado = "menu"
        # Entidades y mundo
        self.jugador = None
        self.nivel_actual = None
        self.numero_nivel = 1
        self.enemigos = []
        self.proyectiles = []
        self.camara = None
        # UI y resultados
        self.resultado = ""
        self.opcion_pausa = 0
        self.opciones_rects = []

    def menu(self):
        # Dibuja pantalla inicial con instrucciones
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(negro)
        self.dibujar_texto("Fear of Ways", 60, blanco, ancho // 2, 120)
        self.dibujar_texto("3 Niveles de Mazmorras Expandidas", 35, amarillo, ancho // 2, 200)
        self.dibujar_texto("Selecciona tu personaje:", 35, blanco, ancho // 2, 270)
        self.dibujar_texto("1 Explorador  2 Cazador  3 Ingeniero", 28, blanco, ancho // 2, 320)
        self.dibujar_texto("Encuentra la salida verde en cada nivel", 25, verde, ancho // 2, 380)
        self.dibujar_texto("Evita a los enemigos rojos", 25, rojo, ancho // 2, 410)
        self.dibujar_texto("La cámara te seguirá por el mapa", 25, (100, 200, 255), ancho // 2, 440)
        self.dibujar_texto("ESC para salir", 25, blanco, ancho // 2, 480)

    def iniciar_juego(self, tipo_personaje):
        # Crea el jugador según la clase elegida
        if tipo_personaje == 1:
            self.jugador = jugador("Explorador", amarillo, velocidad=4, energia=100, vision=150)
        elif tipo_personaje == 2:
            self.jugador = jugador("Cazador", verde, velocidad=6, energia=70, vision=120)
        elif tipo_personaje == 3:
            self.jugador = jugador("Ingeniero", (0, 150, 255), velocidad=3, energia=120, vision=180)

        # Inicia en el nivel 1 y pasa a jugar
        self.numero_nivel = 1
        self.cargar_nivel(self.numero_nivel)
        self.resultado = ""
        self.estado = "jugando"

    def cargar_nivel(self, numero):
        # Instancia el nivel y la cámara para el tamaño del mapa
        self.numero_nivel = numero
        self.nivel_actual = nivel(numero)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)

        # Genera enemigos (asegura 1 de cada tipo si hay espacio)
        self.enemigos = []
        apariciones = list(self.nivel_actual.spawn_enemigos)
        tipos_forzados = ["veloz", "acechador", "bruto"]
        random.shuffle(apariciones)
        for tipo in tipos_forzados:
            if apariciones:
                x, y = apariciones.pop()
                vel = random.randint(2, 4)
                self.enemigos.append(enemigo(x, y, vel, tipo=tipo))
        # Rellena con tipos aleatorios ponderados
        for x, y in apariciones:
            vel = random.randint(2, 4)
            tipo_aleatorio = random.choices(
                ["veloz", "acechador", "bruto"], weights=[0.45, 0.35, 0.20], k=1
            )[0]
            self.enemigos.append(enemigo(x, y, vel, tipo=tipo_aleatorio))

        # Resetea posición del jugador y su estado de oculto
        self.jugador.resetear_posicion()
        if not hasattr(self.jugador, "oculto"):
            self.jugador.oculto = False

    def jugar(self):
        # Lógica y render del frame de juego
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(gris)

        # Actualiza cámara centrada en el jugador
        self.camara.actualizar(self.jugador.rect)

        # Dibuja mapa (muros, salida, escondites)
        self.nivel_actual.dibujar(pantalla, self.camara)

        # Mueve jugador con colisiones y energía
        teclas = pygame.key.get_pressed()
        self.jugador.mover(teclas, self.nivel_actual.muros, self.nivel_actual.ancho, self.nivel_actual.alto)

        # Actualiza proyectiles del jugador (mover, colisión, dibujar)
        for bala in list(self.proyectiles):
            sigue_activo = bala.mover(self.nivel_actual.muros)
            if not sigue_activo:
                self.proyectiles.remove(bala)
                continue
            bala.dibujar(pantalla, self.camara)

        # Marca si el jugador está dentro de una zona segura
        self.jugador.oculto = any(zona.colliderect(self.jugador.rect) for zona in self.nivel_actual.escondites)

        # Indicador visual de oculto
        if self.jugador.oculto:
            rect_pantalla = self.camara.aplicar(self.jugador.rect)
            pygame.draw.rect(pantalla, (80, 200, 255), rect_pantalla, 3)

        # Mueve y dibuja enemigos (considera zonas seguras y ataques)
        for enemigo_actual in list(self.enemigos):
            enemigo_actual.mover(
                self.nivel_actual.muros,
                self.nivel_actual.ancho,
                self.nivel_actual.alto,
                self.jugador,
                self.nivel_actual.escondites
            )
            enemigo_actual.dibujar(pantalla, self.camara)

            # Daño por contacto al jugador
            if self.jugador.rect.colliderect(enemigo_actual.rect):
                self.jugador.recibir_daño(1)
                # Efecto de choque: empuja al enemigo en la dirección opuesta al jugador
                dx = enemigo_actual.rect.centerx - self.jugador.rect.centerx
                dy = enemigo_actual.rect.centery - self.jugador.rect.centery
                dist = math.hypot(dx, dy)
                # normalizar vector y definir distancia de empuje
                if dist != 0:
                    nx = dx / dist
                    ny = dy / dist
                    push = 20  # píxeles de retroceso
                    old_x, old_y = enemigo_actual.rect.x, enemigo_actual.rect.y
                    enemigo_actual.rect.x += int(nx * push)
                    enemigo_actual.rect.y += int(ny * push)
                    # evita que el empuje meta al enemigo en muros; revierte si colisiona
                    if any(enemigo_actual.rect.colliderect(m.rect) for m in muros_bloq):
                        enemigo_actual.rect.x, enemigo_actual.rect.y = old_x, old_y
                # cambia color para indicar impacto
                enemigo_actual.color = (255, 50, 50)
                # invierte su sentido de patrulla para simular retroceso
                enemigo_actual.sentido *= -1
                # si la vida del jugador llega a cero, termina el juego
                if self.jugador.vida <= 0:
                    self.resultado = "perdiste"
                    self.estado = "fin"

        # Colisión de proyectiles del jugador con enemigos
        for bala in list(self.proyectiles):
            impacto = False
            for enemigo_actual in list(self.enemigos):
                if bala.rect.colliderect(enemigo_actual.rect):
                    enemigo_actual.vida -= 1
                    impacto = True
                    if enemigo_actual.vida <= 0:
                        self.enemigos.remove(enemigo_actual)
                    break
            if impacto:
                self.proyectiles.remove(bala)

        # Dibuja jugador y cono de luz
        self.jugador.dibujar(pantalla, self.camara)
        self.dibujar_linterna()

        # Verifica si llegó a la salida y avanza de nivel
        if self.jugador.rect.colliderect(self.nivel_actual.salida.rect):
            if self.numero_nivel < 3:
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                self.resultado = "ganaste"
                self.estado = "fin"

        # UI básica
        self.dibujar_texto(f"Nivel: {self.numero_nivel}/3", 30, blanco, 10, 10, centrado=False)
        self.dibujar_texto(f"Energía: {int(self.jugador.energia)}", 30, blanco, 10, 40, centrado=False)

        # Barras de vida y energía (HUD)
        self.dibujar_barra(1075, 10, 200, 12, self.jugador.vida, self.jugador.vida_max, (255, 80, 80))
        self.dibujar_barra(1075, 28, 200, 10, self.jugador.energia, self.jugador.energia_max, (80, 200, 255))

    def pantalla_final(self):
        # Pantalla de victoria o derrota
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(negro)

        if self.resultado == "ganaste":
            color_titulo = verde
            titulo = "¡Escapaste de las 3 mazmorras!"
            detalle = f"Completaste todos los niveles con {self.jugador.nombre}"
        else:
            color_titulo = rojo
            titulo = "Fuiste atrapado en la oscuridad..."
            detalle = f"Llegaste hasta el nivel {self.numero_nivel}"

        self.dibujar_texto(titulo, 50, color_titulo, ancho // 2, 220)
        self.dibujar_texto(detalle, 30, blanco, ancho // 2, 290)
        self.dibujar_texto("ENTER para volver al menú", 30, blanco, ancho // 2, 380)

    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        # Dibuja texto y devuelve su rect para detectar clics
        pantalla = pygame.display.get_surface()
        fuente = pygame.font.Font(None, tam)
        imagen = fuente.render(texto, True, color)
        rect = imagen.get_rect()
        if centrado:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        pantalla.blit(imagen, rect)
        return rect

    def dibujar_linterna(self):
        # Cono de luz direccional desde el jugador hacia el mouse
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        capa_sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        capa_sombra.fill((0, 0, 0, 240))
        capa_luz = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - cx, my - cy
        angulo = 0.0 if (dx == 0 and dy == 0) else math.atan2(dy, dx)

        radio = max(1, int(self.jugador.vision))
        semiancho = math.radians(35)
        pasos = 48

        # Gradiente de luz con triángulos solapados
        for i in range(pasos, 0, -1):
            r = radio * (i / pasos)
            a = semiancho * (i / pasos)
            p_izq = (cx + r * math.cos(angulo - a), cy + r * math.sin(angulo - a))
            p_der = (cx + r * math.cos(angulo + a), cy + r * math.sin(angulo + a))
            alpha = max(0, min(240, int(240 * (i / pasos))))
            pygame.draw.polygon(capa_luz, (255, 255, 255, alpha), [(cx, cy), p_izq, p_der])

        capa_sombra.blit(capa_luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        pantalla.blit(capa_sombra, (0, 0))

    def dibujar_barra(self, x, y, ancho, alto, valor, valor_max, color_barra):
        # Barra horizontal con borde blanco
        pantalla = pygame.display.get_surface()
        proporcion = max(0.0, min(1.0, valor / valor_max))
        rect_fondo = pygame.Rect(x, y, ancho, alto)
        rect_barra = pygame.Rect(x, y, int(ancho * proporcion), alto)
        pygame.draw.rect(pantalla, (50, 50, 50), rect_fondo)
        pygame.draw.rect(pantalla, color_barra, rect_barra)
        pygame.draw.rect(pantalla, blanco, rect_fondo, 1)

    def pantalla_pausa(self):
        # Muestra el menú de pausa con dos opciones
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill((10, 10, 20))
        self.dibujar_texto("pausa", 64, (0, 200, 255), ancho // 2, alto // 2 - 140)

        opciones = ["reanudar", "salir al menú"]
        self.opciones_rects = []
        for i, texto in enumerate(opciones):
            y = alto // 2 - 20 + i * 60
            rect = self.dibujar_texto(texto, 40, blanco, ancho // 2 - 100, y, centrado=False)
            self.opciones_rects.append(rect)

    def ejecutar(self):
        # Bucle principal de eventos + render
        reloj = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return

                if self.estado == "menu":
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            pygame.quit()
                            return
                        if evento.key == pygame.K_1:
                            self.iniciar_juego(1)
                        if evento.key == pygame.K_2:
                            self.iniciar_juego(2)
                        if evento.key == pygame.K_3:
                            self.iniciar_juego(3)

                elif self.estado == "pausa":
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            self.estado = "jugando"
                        elif evento.key in (pygame.K_UP, pygame.K_w):
                            self.opcion_pausa = (self.opcion_pausa - 1) % 2
                        elif evento.key in (pygame.K_DOWN, pygame.K_s):
                            self.opcion_pausa = (self.opcion_pausa + 1) % 2
                        elif evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if self.opcion_pausa == 0:
                                self.estado = "jugando"
                            else:
                                self.estado = "menu"
                    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        for i, rect in enumerate(self.opciones_rects):
                            if rect.collidepoint(evento.pos):
                                if i == 0:
                                    self.estado = "jugando"
                                elif i == 1:
                                    self.estado = "menu"

                elif self.estado == "jugando":
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                        self.estado = "pausa"
                        self.opcion_pausa = 0

                    # Disparo del jugador con clic derecho (button 3)
                    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
                        mx, my = pygame.mouse.get_pos()
                        # Convierte la posición del jugador a coords de pantalla para apuntar bien
                        jx, jy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
                        # Crea proyectil hacia el punto del mouse compensando el offset de la cámara
                        nuevo_proyectil = proyectil(
                            jx, jy,
                            self.camara.offset_x + mx,
                            self.camara.offset_y + my,
                            self.jugador.color
                        )
                        self.proyectiles.append(nuevo_proyectil)

                elif self.estado == "fin":
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                        self.estado = "menu"

            # Render según estado
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