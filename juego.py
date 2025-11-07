import pygame
import random
import math
from nivel import nivel
from camara import camara
from jugador import jugador
from enemigo import enemigo
from proyectil import proyectil
from datetime import datetime

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (40, 40, 40)
ROJO = (255, 80, 80)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)
AZUL = (100, 180, 255)

class juego:
    def __init__(self):
        self.estado = "menu"
        self.jugador = None
        self.nivel_actual = None
        self.numero_nivel = 1
        self.enemigos = []
        self.proyectiles = []
        self.camara = None
        self.resultado = ""
        self._guardado = False

        # Configuración visual
        self.altura_header = 0.10
        pygame.display.set_caption("Fear of Ways")
        self.fuente_base = pygame.font.Font(None, 30)

        # Sonidos
        try:
            self.sonido_disparo = pygame.mixer.Sound("disparo.mp3")
        except Exception:
            self.sonido_disparo = None

    # -------------------------------------------------------
    # MENÚ PRINCIPAL
    # -------------------------------------------------------
    def menu(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(NEGRO)
        self.dibujar_texto("Fear of Ways", int(alto * 0.1), BLANCO, ancho // 2, alto * 0.2)
        self.dibujar_texto("3 Mazmorras Extensas", int(alto * 0.05), AMARILLO, ancho // 2, alto * 0.35)
        self.dibujar_texto("Selecciona tu personaje:", int(alto * 0.045), BLANCO, ancho // 2, alto * 0.45)
        self.dibujar_texto("1. Explorador   2. Cazador   3. Ingeniero", int(alto * 0.04), BLANCO, ancho // 2, alto * 0.52)
        self.dibujar_texto("ESC para salir", int(alto * 0.03), GRIS, ancho // 2, alto * 0.9)

    # -------------------------------------------------------
    # INICIO Y CARGA DE JUEGO
    # -------------------------------------------------------
    def iniciar_juego(self, tipo_personaje):
        self._guardado = False
        if tipo_personaje == 1:
            self.jugador = jugador("Explorador", AMARILLO, velocidad=4, energia=100, vision=150)
        elif tipo_personaje == 2:
            self.jugador = jugador("Cazador", VERDE, velocidad=6, energia=70, vision=120)
        else:
            self.jugador = jugador("Ingeniero", AZUL, velocidad=3, energia=120, vision=180)

        self.numero_nivel = 1
        self.cargar_nivel(self.numero_nivel)
        self.resultado = ""
        self.estado = "jugando"

    def cargar_nivel(self, numero):
        self.numero_nivel = numero
        self.nivel_actual = nivel(numero)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)
        self.enemigos.clear()
        self.proyectiles.clear()

        # Generar enemigos
        apariciones = list(self.nivel_actual.spawn_enemigos)
        tipos_forzados = ["veloz", "acechador", "bruto"]
        random.shuffle(apariciones)
        for tipo in tipos_forzados:
            if apariciones:
                x, y = apariciones.pop()
                self.enemigos.append(enemigo(x, y, random.randint(2, 4), tipo=tipo))
        for x, y in apariciones:
            tipo = random.choices(["veloz", "acechador", "bruto"], [0.5, 0.3, 0.2])[0]
            self.enemigos.append(enemigo(x, y, random.randint(2, 4), tipo=tipo))

        self.jugador.resetear_posicion()
        self.jugador.oculto = False

        # Incremento progresivo de dificultad
        dificultad = 1 + (numero - 1) * 0.25
        for e in self.enemigos:
            e.velocidad = int(e.velocidad * dificultad)
            e.rango_deteccion = int(e.rango_deteccion * dificultad)

    # -------------------------------------------------------
    # BUCLE PRINCIPAL DE JUEGO
    # -------------------------------------------------------
    def jugar(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        offset_header = int(alto * self.altura_header)

        # Área de juego bajo el header
        area_juego = pygame.Surface((ancho, alto - offset_header))
        area_juego.fill(GRIS)

        # Actualizar cámara y jugador
        self.camara.actualizar(self.jugador.rect)
        teclas = pygame.key.get_pressed()
        muros_bloq = [m for m in self.nivel_actual.muros if getattr(m, "bloquea", True)]
        self.jugador.mover(teclas, muros_bloq, self.nivel_actual.ancho, self.nivel_actual.alto)

        # Dibujar mapa, enemigos, proyectiles y jugador
        self.nivel_actual.dibujar(area_juego, self.camara)
        for enemigo_actual in list(self.enemigos):
            enemigo_actual.mover(muros_bloq, self.nivel_actual.ancho, self.nivel_actual.alto, self.jugador, self.nivel_actual.escondites)
            enemigo_actual.dibujar(area_juego, self.camara)

            if self.jugador.rect.colliderect(enemigo_actual.rect):
                self.jugador.recibir_daño(1)
                if self.jugador.vida <= 0:
                    self.resultado = "perdiste"
                    self.estado = "fin"

        for bala in list(self.proyectiles):
            if not bala.mover(muros_bloq):
                self.proyectiles.remove(bala)
                continue
            bala.dibujar(area_juego, self.camara)
            for enemigo_actual in list(self.enemigos):
                if bala.rect.colliderect(enemigo_actual.rect):
                    enemigo_actual.vida -= 1
                    if enemigo_actual.vida <= 0:
                        self.enemigos.remove(enemigo_actual)
                    if bala in self.proyectiles:
                        self.proyectiles.remove(bala)
                    break

        self.jugador.dibujar(area_juego, self.camara)
        self.dibujar_linterna_en_superficie(area_juego)
        pantalla.blit(area_juego, (0, offset_header))

        # --- Header superior ---
        self.dibujar_header(pantalla, ancho, alto, offset_header)

        # Salida de nivel
        llaves_restantes = len(getattr(self.nivel_actual, "llaves", []))
        if self.jugador.rect.colliderect(self.nivel_actual.salida.rect) and llaves_restantes == 0:
            if self.numero_nivel < 3:
                self.transicion_texto(f"Mazmorra {self.numero_nivel+1}")
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                self.resultado = "ganaste"
                self.estado = "fin"

    # -------------------------------------------------------
    # DIBUJAR HEADER (HUD)
    # -------------------------------------------------------
    def dibujar_header(self, pantalla, ancho, alto, offset):
        alto_header = offset
        pygame.draw.rect(pantalla, (20, 20, 30, 230), (0, 0, ancho, alto_header))
        pygame.draw.line(pantalla, (120, 120, 150), (0, alto_header - 2), (ancho, alto_header - 2), 2)

        margen_x = int(ancho * 0.03)
        margen_y = int(alto_header * 0.25)
        barra_ancho = int(ancho * 0.25)
        barra_alto = int(alto_header * 0.25)

        # Vida izquierda
        self.dibujar_texto("❤️ VIDA", int(alto * 0.035), (255, 100, 100),
                           margen_x, margen_y - 5, centrado=False)
        self.dibujar_barra(pantalla, margen_x, margen_y + int(alto_header * 0.35),
                           barra_ancho, barra_alto,
                           self.jugador.vida, self.jugador.vida_max, (255, 80, 80))

        # Energía derecha
        self.dibujar_texto("⚡ ENERGÍA", int(alto * 0.035), (120, 200, 255),
                           ancho - barra_ancho - margen_x, margen_y - 5, centrado=False)
        self.dibujar_barra(pantalla, ancho - barra_ancho - margen_x, margen_y + int(alto_header * 0.35),
                           barra_ancho, barra_alto,
                           self.jugador.energia, self.jugador.energia_max, (80, 200, 255))

        # Nivel al centro
        self.dibujar_texto(f"Nivel {self.numero_nivel}/3",
                           int(alto * 0.045), BLANCO, ancho // 2, alto_header // 2, centrado=True)

    # -------------------------------------------------------
    # DIBUJADO DE ELEMENTOS
    # -------------------------------------------------------
    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        pantalla = pygame.display.get_surface()
        fuente = pygame.font.Font(None, tam)
        imagen = fuente.render(texto, True, color)
        rect = imagen.get_rect()
        rect.center = (x, y) if centrado else (x, y)
        pantalla.blit(imagen, rect)
        return rect

    def dibujar_barra(self, pantalla, x, y, ancho, alto, valor, valor_max, color_barra):
        proporcion = max(0.0, min(1.0, valor / valor_max))
        rect_fondo = pygame.Rect(x, y, ancho, alto)
        rect_barra = pygame.Rect(x, y, int(ancho * proporcion), alto)
        pygame.draw.rect(pantalla, (40, 40, 40), rect_fondo, border_radius=4)
        pygame.draw.rect(pantalla, color_barra, rect_barra, border_radius=4)
        pygame.draw.rect(pantalla, BLANCO, rect_fondo, 1, border_radius=4)

    def dibujar_linterna_en_superficie(self, superficie):
        ancho, alto = superficie.get_size()
        sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 240))
        luz = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        mx, my = pygame.mouse.get_pos()
        dy_ajustado = my - cy - int(pygame.display.get_surface().get_height() * self.altura_header)
        dx, dy = mx - cx, dy_ajustado
        angulo = math.atan2(dy, dx) if (dx or dy) else 0.0

        base_radio = self.jugador.vision
        if self.jugador.energia < 20:
            base_radio *= 0.8 + 0.2 * random.random()
        radio = int(base_radio)
        semiancho = math.radians(35)
        pasos = 48

        for i in range(pasos, 0, -1):
            r = radio * (i / pasos)
            a = semiancho * (i / pasos)
            p_izq = (cx + r * math.cos(angulo - a), cy + r * math.sin(angulo - a))
            p_der = (cx + r * math.cos(angulo + a), cy + r * math.sin(angulo + a))
            alpha = int(240 * (i / pasos))
            pygame.draw.polygon(luz, (255, 255, 255, alpha), [(cx, cy), p_izq, p_der])

        sombra.blit(luz, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        superficie.blit(sombra, (0, 0))

    # -------------------------------------------------------
    # TRANSICIÓN ENTRE NIVELES
    # -------------------------------------------------------
    def transicion_texto(self, texto):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        for i in range(60):
            overlay = pygame.Surface((ancho, alto))
            overlay.fill((0, 0, 0))
            alpha = int(255 * (i / 60))
            overlay.set_alpha(alpha)
            pantalla.blit(overlay, (0, 0))
            self.dibujar_texto(texto, 50, BLANCO, ancho // 2, alto // 2)
            pygame.display.flip()
            pygame.time.delay(16)

    # -------------------------------------------------------
    # PANTALLA FINAL
    # -------------------------------------------------------
    def pantalla_final(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(NEGRO)
        titulo = "¡Escapaste de las 3 mazmorras!" if self.resultado == "ganaste" else "Fuiste atrapado..."
        color = VERDE if self.resultado == "ganaste" else ROJO
        self.dibujar_texto(titulo, int(alto * 0.08), color, ancho // 2, alto * 0.4)
        self.dibujar_texto("ENTER para volver al menú", int(alto * 0.04), BLANCO, ancho // 2, alto * 0.55)
        if not self._guardado:
            self.guardar_resultado()
            self._guardado = True

    # -------------------------------------------------------
    # BUCLE DE EVENTOS PRINCIPAL
    # -------------------------------------------------------
    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if self.estado == "menu" and e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit(); return
                    if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        self.iniciar_juego(int(e.key - pygame.K_0))
                elif self.estado == "jugando":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        self.estado = "menu"
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3 and self.jugador.cooldown_disparo == 0:
                        mx, my = pygame.mouse.get_pos()
                        jx, jy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
                        self.proyectiles.append(proyectil(jx, jy, self.camara.offset_x + mx, self.camara.offset_y + my, self.jugador.color))
                        self.jugador.cooldown_disparo = 15
                        if self.sonido_disparo:
                            self.sonido_disparo.play()
                elif self.estado == "fin" and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    self.estado = "menu"

            if self.estado == "menu":
                self.menu()
            elif self.estado == "jugando":
                self.jugar()
            elif self.estado == "fin":
                self.pantalla_final()

            pygame.display.flip()
            reloj.tick(60)

    # -------------------------------------------------------
    # GUARDADO DE RESULTADOS
    # -------------------------------------------------------
    def guardar_resultado(self):
        with open("resultados.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {self.jugador.nombre} | Nivel {self.numero_nivel} | {self.resultado}\n")
