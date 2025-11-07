import pygame
import os
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

        # Carga de recursos gráficos para HUD y menú
        self._dir = os.path.dirname(__file__)
        # Cargar icono del corazón (vida)
        try:
            img = pygame.image.load(os.path.join(self._dir, 'heart.png')).convert_alpha()
            self.heart_img = pygame.transform.scale(img, (32, 32))
        except Exception:
            self.heart_img = None
        # Cargar icono de la llave
        try:
            img = pygame.image.load(os.path.join(self._dir, 'key_icon.png')).convert_alpha()
            # hacer la llave más visible que los corazones
            self.key_img = pygame.transform.scale(img, (44, 44))
        except Exception:
            self.key_img = None
        # Cargar icono del rayo
        try:
            img = pygame.image.load(os.path.join(self._dir, 'lightning.png')).convert_alpha()
            self.lightning_img = pygame.transform.scale(img, (32, 32))
        except Exception:
            self.lightning_img = None
        # Cargar marco para el menú
        try:
            self.menu_frame_img = pygame.image.load(os.path.join(self._dir, 'menu_frame.png')).convert_alpha()
        except Exception:
            self.menu_frame_img = None

        # Seleccionar fuente predeterminada para menús y HUD (por ejemplo, freesansbold)
        # Pygame usa una fuente por defecto si None; sin embargo, definimos explícitamente el nombre para un estilo consistente
        try:
            # match_font devuelve la ruta a una fuente del sistema; fallback a None si no se encuentra
            self.font_path = pygame.font.match_font('freesansbold') or pygame.font.get_default_font()
        except Exception:
            # Fallback a fuente predeterminada de pygame
            self.font_path = pygame.font.get_default_font()

    # -------------------------------------------------------
    # MENÚ PRINCIPAL
    # -------------------------------------------------------
    def menu(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        pantalla.fill(NEGRO)

        # Título principal y subtítulo
        self.dibujar_texto("Fear of Ways", int(alto * 0.1), BLANCO, ancho // 2, int(alto * 0.15))
        self.dibujar_texto("3 Mazmorras Extensas", int(alto * 0.05), AMARILLO, ancho // 2, int(alto * 0.28))

        # Dibujar marco decorativo si existe
        if self.menu_frame_img:
            marco_ancho_dest = int(ancho * 0.5)
            factor = marco_ancho_dest / self.menu_frame_img.get_width()
            marco_alto_dest = int(self.menu_frame_img.get_height() * factor)
            marco = pygame.transform.scale(self.menu_frame_img, (marco_ancho_dest, marco_alto_dest))
            marco_rect = marco.get_rect()
            marco_rect.center = (ancho // 2, int(alto * 0.55))
            pantalla.blit(marco, marco_rect)
            opciones = [
                ("Selecciona tu personaje:", BLANCO, 0.045),
                ("1. Explorador", AMARILLO, 0.04),
                ("2. Cazador", VERDE, 0.04),
                ("3. Ingeniero", AZUL, 0.04),
            ]
            # padding y dimensiones internas para el texto
            pad_x = max(12, int(marco_rect.width * 0.06))
            max_w = marco_rect.width - pad_x * 2
            # calcular tamaños iniciales por línea
            line_count = len(opciones)
            fonts_sizes = []
            surfaces = []
            heights = []
            # tamaño máximo disponible vertical dentro del marco
            avail_h = int(marco_rect.height * 0.75)
            # empezar con tamaños relativos
            for texto, color, rel_size in opciones:
                tam = max(10, int(marco_rect.height * rel_size * 0.9))
                # crear superficie y reducir si excede ancho
                try:
                    f = pygame.font.Font(self.font_path, tam)
                except Exception:
                    f = pygame.font.Font(None, tam)
                surf = f.render(texto, True, color)
                while surf.get_width() > max_w and tam > 8:
                    tam -= 1
                    try:
                        f = pygame.font.Font(self.font_path, tam)
                    except Exception:
                        f = pygame.font.Font(None, tam)
                    surf = f.render(texto, True, color)
                fonts_sizes.append(tam)
                surfaces.append((surf, color, texto))
                heights.append(surf.get_height())

            # calcular spacing y ajustar si la suma excede el alto disponible
            spacing = int(marco_rect.height * 0.11)
            total_h = sum(heights) + spacing * (line_count - 1)
            if total_h > avail_h:
                # reducir todos los tamaños proporcionalmente
                scale = avail_h / total_h
                new_surfaces = []
                heights = []
                for i, (texto, color, rel_size) in enumerate(opciones):
                    tam = max(8, int(fonts_sizes[i] * scale))
                    try:
                        f = pygame.font.Font(self.font_path, tam)
                    except Exception:
                        f = pygame.font.Font(None, tam)
                    surf = f.render(texto, True, color)
                    # asegurar ancho
                    while surf.get_width() > max_w and tam > 6:
                        tam -= 1
                        try:
                            f = pygame.font.Font(self.font_path, tam)
                        except Exception:
                            f = pygame.font.Font(None, tam)
                        surf = f.render(texto, True, color)
                    new_surfaces.append((surf, tam))
                    heights.append(surf.get_height())
                surfaces = [(s, opciones[i][1], opciones[i][0]) for i, (s, _) in enumerate(new_surfaces)]
                fonts_sizes = [t for (_, t) in new_surfaces]
                total_h = sum(heights) + spacing * (line_count - 1)

            # dibujar líneas centradas y distribuidas verticalmente dentro del marco
            top_start = marco_rect.top + (marco_rect.height - total_h) // 2
            for i, (texto, color, rel_size) in enumerate(opciones):
                tam = fonts_sizes[i]
                try:
                    f = pygame.font.Font(self.font_path, tam)
                except Exception:
                    f = pygame.font.Font(None, tam)
                surf = f.render(texto, True, color)
                x_text = marco_rect.centerx
                y_text = top_start + sum(heights[:i]) + i * spacing + surf.get_height() // 2
                rect_final = surf.get_rect(center=(x_text, y_text))
                pantalla.blit(surf, rect_final)
        else:
            rect_ancho = int(ancho * 0.5)
            rect_alto = int(alto * 0.3)
            rect = pygame.Rect(0, 0, rect_ancho, rect_alto)
            rect.center = (ancho // 2, int(alto * 0.55))
            pygame.draw.rect(pantalla, (60, 30, 10), rect)
            pygame.draw.rect(pantalla, (120, 80, 40), rect, 2)
            opciones = [
                ("Selecciona tu personaje:", BLANCO, 0.045),
                ("1. Explorador", AMARILLO, 0.04),
                ("2. Cazador", VERDE, 0.04),
                ("3. Ingeniero", AZUL, 0.04),
            ]
            y_base = rect.top + int(rect.height * 0.15)
            for idx, (texto, color, rel_size) in enumerate(opciones):
                tam_fuente = int(alto * rel_size)
                self.dibujar_texto(texto, tam_fuente, color,
                                   rect.centerx,
                                   y_base + idx * int(alto * 0.06))

        # Mensaje de salida
        self.dibujar_texto("ESC para salir", int(alto * 0.03), GRIS, ancho // 2, int(alto * 0.92))

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
        # Fondo semitransparente y línea inferior
        alto_header = offset
        pygame.draw.rect(pantalla, (20, 20, 30, 230), (0, 0, ancho, alto_header))
        pygame.draw.line(pantalla, (120, 120, 150), (0, alto_header - 2), (ancho, alto_header - 2), 2)

        margen_x = int(ancho * 0.03)
        y_elementos = int(alto_header * 0.25)

        # --- Corazones de vida ---
        if self.heart_img:
            for i in range(self.jugador.vida_max):
                x_corazon = margen_x + i * (self.heart_img.get_width() + 4)
                if i < self.jugador.vida:
                    pantalla.blit(self.heart_img, (x_corazon, y_elementos))
                else:
                    corazon_gray = self.heart_img.copy()
                    corazon_gray.set_alpha(100)
                    pantalla.blit(corazon_gray, (x_corazon, y_elementos))
            ultimo_x = margen_x + self.jugador.vida_max * (self.heart_img.get_width() + 4)
        else:
            ultimo_x = margen_x
            self.dibujar_texto(f"Vida: {self.jugador.vida}/{self.jugador.vida_max}",
                               int(alto * 0.035), (255, 100, 100),
                               ultimo_x, y_elementos, centrado=False)
            ultimo_x += int(ancho * 0.15)

        # --- Llaves recogidas ---
        if hasattr(self.nivel_actual, "llaves_requeridas"):
            obtenidas = self.nivel_actual.llaves_requeridas - len(self.nivel_actual.llaves)
            total = self.nivel_actual.llaves_requeridas
            if self.key_img:
                # Mostrar icono de llave y el conteo a la derecha; alinear verticalmente con los corazones
                x_llave = ultimo_x + 30
                # determinar altura del corazón (fallback a un tamaño estimado)
                if self.heart_img:
                    heart_h = self.heart_img.get_height()
                else:
                    heart_h = int(alto * 0.035)
                # colocar el top de la llave de forma que sus centros coincidan con los corazones
                y_llave = y_elementos + (heart_h - self.key_img.get_height()) // 2
                pantalla.blit(self.key_img, (x_llave, y_llave))
                texto_llaves = f"{obtenidas}/{total}"
                # posición del texto a la derecha del icono con separación mayor
                gap = 36
                x_text = x_llave + self.key_img.get_width() + gap
                y_text_center = y_elementos + heart_h // 2
                # renderizar texto manualmente (control de tamaño y centrado vertical)
                try:
                    fuente_k = pygame.font.Font(self.font_path, int(alto * 0.018))
                except Exception:
                    fuente_k = pygame.font.Font(None, int(alto * 0.018))
                surf_k = fuente_k.render(texto_llaves, True, (255, 220, 140))
                rect_k = surf_k.get_rect(center=(x_text, y_text_center))
                pantalla.blit(surf_k, rect_k)
            else:
                # Si no hay icono, mostrar un texto pequeño y discreto
                self.dibujar_texto(f"Llaves: {obtenidas}/{total}", int(alto * 0.03), (255, 220, 140),
                                   ultimo_x + 20, y_elementos, centrado=False)

        # --- Barra de energía con icono de rayo ---
        # Ajuste visual: barra de energía más compacta
        barra_ancho = int(ancho * 0.12)
        barra_alto = max(6, int(alto_header * 0.18))
        x_barra = ancho - barra_ancho - margen_x
        y_barra = y_elementos
        if self.lightning_img:
            pantalla.blit(self.lightning_img,
                          (x_barra - self.lightning_img.get_width() - 6, y_barra))
        self.dibujar_barra(pantalla, x_barra, y_barra,
                           barra_ancho, barra_alto,
                           self.jugador.energia, self.jugador.energia_max, (80, 200, 255))
        # No mostrar el número de energía junto a la barra (diseño más limpio)

        # --- Nivel al centro ---
        # Muestra solo el número de nivel actual (sin total). Si existe una imagen
        # decorativa (`menu_frame_img`) la usamos como marco ajustado al tamaño del texto.
        center_x = ancho // 2
        center_y = alto_header // 2

        texto_nivel = f"Nivel {self.numero_nivel}"
        tam_texto = int(alto * 0.04)
        try:
            fuente_nivel = pygame.font.Font(self.font_path, tam_texto)
        except Exception:
            fuente_nivel = pygame.font.Font(None, tam_texto)
        surf_texto = fuente_nivel.render(texto_nivel, True, BLANCO)
        text_w, text_h = surf_texto.get_size()

        if self.menu_frame_img:
            try:
                orig_w = self.menu_frame_img.get_width()
                orig_h = self.menu_frame_img.get_height()
                # Padding alrededor del texto dentro del marco
                pad_x = max(12, int(text_w * 0.18))
                pad_y = max(6, int(text_h * 0.4))
                target_w = text_w + pad_x * 2
                target_h = text_h + pad_y * 2
                # Escalar manteniendo la relación de aspecto
                scale = min(target_w / orig_w if orig_w else 1.0, target_h / orig_h if orig_h else 1.0)
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                marco = pygame.transform.scale(self.menu_frame_img, (new_w, new_h))
                marco_rect = marco.get_rect(center=(center_x, center_y))
                pantalla.blit(marco, marco_rect)
            except Exception:
                pass

        # dibujar el texto del nivel encima (siempre)
        rect_texto = surf_texto.get_rect(center=(center_x, center_y))
        pantalla.blit(surf_texto, rect_texto)

    # -------------------------------------------------------
    # DIBUJADO DE ELEMENTOS
    # -------------------------------------------------------
    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        """Renderiza un texto utilizando una fuente predefinida y lo dibuja en pantalla."""
        pantalla = pygame.display.get_surface()
        # Utiliza la fuente configurada en self.font_path; si está indefinida, usa la predeterminada de pygame
        try:
            fuente = pygame.font.Font(self.font_path, tam)
        except Exception:
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
