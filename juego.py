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
        # Almacenamos el directorio actual para localizar imágenes
        self._dir = os.path.dirname(__file__)

        # Tamaño base de los iconos para el HUD. Al usar un tamaño único se simplifica
        # el diseño y se consigue un aspecto más minimalista. 28 píxeles funciona bien en
        # la mayoría de resoluciones. Si falla la carga, los iconos simplemente no se dibujan.
        icon_size = 28

        # Cargar icono del corazón (vida)
        try:
            img = pygame.image.load(os.path.join(self._dir, 'heart.png')).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
        except Exception:
            self.heart_img = None

        # Cargar icono de la llave. Se escala al mismo tamaño para mantener coherencia
        try:
            img = pygame.image.load(os.path.join(self._dir, 'key_icon.png')).convert_alpha()
            self.key_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
        except Exception:
            self.key_img = None

        # Cargar icono del rayo
        try:
            img = pygame.image.load(os.path.join(self._dir, 'lightning.png')).convert_alpha()
            self.lightning_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
        except Exception:
            self.lightning_img = None

        # No usamos un marco externo para el menú, así que desactivamos cualquier intento de cargar menu_frame_img
        self.menu_frame_img = None

        # Cargar textura para la barra de energía del HUD. Si no existe, se usará el color por defecto.
        try:
            tex = pygame.image.load(os.path.join(self._dir, 'hud_bar_texture.png')).convert()
            # La textura se almacenará tal cual; se escalará dinámicamente al dibujar la barra.
            self.energy_texture = tex
        except Exception:
            self.energy_texture = None

        # Seleccionar fuente predeterminada para menús y HUD (por ejemplo, freesansbold)
        # Pygame usa una fuente por defecto si None; sin embargo, definimos explícitamente el nombre para un estilo consistente
        try:
            # match_font devuelve la ruta a una fuente del sistema; fallback a None si no se encuentra
            self.font_path = pygame.font.match_font('freesansbold') or pygame.font.get_default_font()
        except Exception:
            # Fallback a fuente predeterminada de pygame
            self.font_path = pygame.font.get_default_font()

        # Intenta usar una fuente de estilo pixelado (monoespaciada) si está disponible en el sistema. Esto da
        # un aire retro a los menús y al HUD. Si no se encuentra, se mantiene la fuente predeterminada.
        try:
            pixel_candidates = ['LiberationMono-Bold', 'Liberation Mono', 'Courier New']
            pixel_font = None
            for name in pixel_candidates:
                found = pygame.font.match_font(name)
                if found:
                    pixel_font = found
                    break
            # Si encontramos una, reemplazamos font_path por la pixelada
            if pixel_font:
                self.font_path = pixel_font
        except Exception:
            pass

    # -------------------------------------------------------
    # MENÚ PRINCIPAL
    # -------------------------------------------------------
    def menu(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        # Fondo general con color tenue para el menú. Un fondo oscuro ayuda a resaltar los elementos.
        # Intentar cargar una imagen de fondo personalizada para el menú. Si existe un archivo
        # "menu_background.png" en el directorio del juego, se usará como fondo. De lo contrario,
        # se empleará un fondo oscuro con una capa semitransparente para dar profundidad.
        fondo_path = os.path.join(self._dir, 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                fondo = pygame.image.load(fondo_path).convert()
                fondo = pygame.transform.scale(fondo, (ancho, alto))
                pantalla.blit(fondo, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))
            # Dibujar una capa semitransparente para dar profundidad
            overlay = pygame.Surface((ancho, alto))
            overlay.set_alpha(180)
            overlay.fill((20, 20, 30))
            pantalla.blit(overlay, (0, 0))

        # Título principal del juego
        titulo_size = int(alto * 0.10)
        self.dibujar_texto("Fear of Ways", titulo_size, BLANCO, ancho // 2, int(alto * 0.15))
        # Subtítulo motivador. Texto sobrio acorde al estilo de mazmorras
        subtitulo_size = int(alto * 0.035)
        self.dibujar_texto("Explora las mazmorras", subtitulo_size, (200, 200, 200), ancho // 2, int(alto * 0.26))

        # El marco del menú se dibuja como un rectángulo oscuro; no se usa ninguna imagen decorativa.
        marco_rect = pygame.Rect(0, 0, int(ancho * 0.45), int(alto * 0.4))
        marco_rect.center = (ancho // 2, int(alto * 0.55))
        pygame.draw.rect(pantalla, (40, 20, 10), marco_rect)
        pygame.draw.rect(pantalla, (90, 60, 30), marco_rect, 2)

        # Preparar opciones y cabecera
        opciones_texto = [
            "Selecciona tu personaje",
            "1 Explorador",
            "2 Cazador",
            "3 Ingeniero",
        ]

        # Determina tamaños de fuentes de forma proporcional al alto del marco
        # La cabecera (línea 0) será ligeramente más pequeña que las opciones
        disponible_h = marco_rect.height * 0.8
        n_lineas = len(opciones_texto)
        # Factor de escala para las opciones; usamos un tamaño base y se reduce si no cabe
        tam_opcion = max(10, int(marco_rect.height * 0.12))
        tam_cabecera = max(10, int(tam_opcion * 0.7))
        # Calcula el alto real de cada superficie de texto
        alturas = []
        superficies = []
        for i, txt in enumerate(opciones_texto):
            tam = tam_cabecera if i == 0 else tam_opcion
            try:
                fuente = pygame.font.Font(self.font_path, tam)
            except Exception:
                fuente = pygame.font.Font(None, tam)
            surf = fuente.render(txt, True, (230, 220, 200))
            alturas.append(surf.get_height())
            superficies.append((surf, tam))
        # Espacio entre líneas (10 % del alto de marco)
        spacing = int(marco_rect.height * 0.08)
        total_h = sum(alturas) + spacing * (n_lineas - 1)
        if total_h > disponible_h:
            # Reducir tamaño de todas las líneas proporcionalmente
            escala = disponible_h / total_h
            new_surfs = []
            alturas = []
            for i, txt in enumerate(opciones_texto):
                tam_base = tam_cabecera if i == 0 else tam_opcion
                tam_nuevo = max(10, int(tam_base * escala))
                try:
                    fuente = pygame.font.Font(self.font_path, tam_nuevo)
                except Exception:
                    fuente = pygame.font.Font(None, tam_nuevo)
                surf = fuente.render(txt, True, (230, 220, 200))
                alturas.append(surf.get_height())
                new_surfs.append((surf, tam_nuevo))
            superficies = new_surfs
            total_h = sum(alturas) + spacing * (n_lineas - 1)
        # Dibuja cada línea centrada dentro del marco, distribuyendo equidistantemente
        y_inicial = marco_rect.centery - total_h // 2
        acumulado_h = 0
        for i, (surf, tam) in enumerate(superficies):
            x_text = marco_rect.centerx
            y_text = y_inicial + acumulado_h + i * spacing + surf.get_height() // 2
            rect_final = surf.get_rect(center=(x_text, y_text))
            pantalla.blit(surf, rect_final)
            acumulado_h += surf.get_height()

        # Mensaje de salida al pie
        mensaje_size = int(alto * 0.03)
        self.dibujar_texto("ESC para salir", mensaje_size, (150, 150, 160), ancho // 2, int(alto * 0.92))

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
        # Encabezado con textura: si hay una textura definida, se escala para rellenar la banda del HUD.
        # Esto reemplaza el color de fondo uniforme. La textura oscura ayuda a integrar el HUD con la temática.
        if hasattr(self, 'energy_texture') and self.energy_texture:
            try:
                header_tex = pygame.transform.scale(self.energy_texture, (ancho, alto_header))
                pantalla.blit(header_tex, (0, 0))
            except Exception:
                pygame.draw.rect(pantalla, (15, 15, 25, 220), (0, 0, ancho, alto_header))
        else:
            pygame.draw.rect(pantalla, (15, 15, 25, 220), (0, 0, ancho, alto_header))
        # Línea divisoria sutil en la base del encabezado
        pygame.draw.line(pantalla, (80, 80, 110), (0, alto_header - 2), (ancho, alto_header - 2), 2)

        # Márgenes laterales más amplios para airear el contenido
        margen_x = int(ancho * 0.04)
        # Coordenada vertical base para los elementos del HUD dentro del encabezado
        y_elementos = int(alto_header * 0.25)

        # --- Corazones de vida ---
        if self.heart_img:
            # Muestra cada corazón con un espacio mayor entre ellos para un aspecto más limpio
            spacing = 8
            for i in range(self.jugador.vida_max):
                x_corazon = margen_x + i * (self.heart_img.get_width() + spacing)
                # Corazón lleno o atenuado dependiendo de la vida restante
                if i < self.jugador.vida:
                    pantalla.blit(self.heart_img, (x_corazon, y_elementos))
                else:
                    corazon_gray = self.heart_img.copy()
                    corazon_gray.set_alpha(80)
                    pantalla.blit(corazon_gray, (x_corazon, y_elementos))
            # posición horizontal acumulada después de los corazones
            ultimo_x = margen_x + self.jugador.vida_max * (self.heart_img.get_width() + spacing)
        else:
            # Fallback textual si faltan iconos de corazón
            ultimo_x = margen_x
            self.dibujar_texto(f"Vida: {self.jugador.vida}/{self.jugador.vida_max}",
                               int(alto * 0.032), (220, 100, 100),
                               ultimo_x, y_elementos, centrado=False)
            ultimo_x += int(ancho * 0.12)

        # --- Llaves recogidas ---
        if hasattr(self.nivel_actual, "llaves_requeridas"):
            obtenidas = self.nivel_actual.llaves_requeridas - len(self.nivel_actual.llaves)
            total = self.nivel_actual.llaves_requeridas
            if self.key_img:
                # Mostrar icono de llave y el conteo con separación moderada
                x_llave = ultimo_x + 20
                # Altura base para alinear con los corazones
                heart_h = self.heart_img.get_height() if self.heart_img else int(alto * 0.03)
                y_llave = y_elementos + (heart_h - self.key_img.get_height()) // 2
                pantalla.blit(self.key_img, (x_llave, y_llave))
                texto_llaves = f"{obtenidas}/{total}"
                # Posición del texto a la derecha del icono
                gap = 24
                x_text = x_llave + self.key_img.get_width() + gap
                y_text_center = y_elementos + heart_h // 2
                try:
                    fuente_k = pygame.font.Font(self.font_path, int(alto * 0.02))
                except Exception:
                    fuente_k = pygame.font.Font(None, int(alto * 0.02))
                surf_k = fuente_k.render(texto_llaves, True, (230, 210, 150))
                rect_k = surf_k.get_rect(center=(x_text, y_text_center))
                pantalla.blit(surf_k, rect_k)
                # Actualizar ultimo_x para elementos siguientes
                ultimo_x = x_text + surf_k.get_width() // 2
            else:
                # Si no hay icono, mostrar un texto sencillo
                self.dibujar_texto(f"Llaves: {obtenidas}/{total}", int(alto * 0.028), (230, 210, 150),
                                   ultimo_x + 20, y_elementos, centrado=False)
                ultimo_x += int(ancho * 0.12)

        # --- Barra de energía con icono de rayo ---
        # Ajuste visual: barra de energía más compacta
        # --- Barra de energía con icono de rayo ---
        # Se reduce el ancho para que resulte más discreta y la altura para un aspecto estilizado
        barra_ancho = int(ancho * 0.10)
        barra_alto = max(4, int(alto_header * 0.15))
        x_barra = ancho - barra_ancho - margen_x
        y_barra = y_elementos
        if self.lightning_img:
            pantalla.blit(self.lightning_img,
                          (x_barra - self.lightning_img.get_width() - 8, y_barra + (barra_alto - self.lightning_img.get_height()) // 2))
        # Elegir un color de barra acorde a la temática (azul atenuado)
        self.dibujar_barra(pantalla, x_barra, y_barra,
                           barra_ancho, barra_alto,
                           self.jugador.energia, self.jugador.energia_max, (90, 160, 240))

        # --- Nivel al centro ---
        # Muestra solo el número de nivel actual (sin total). Si existe una imagen
        # decorativa (`menu_frame_img`) la usamos como marco ajustado al tamaño del texto.
        center_x = ancho // 2
        center_y = alto_header // 2

        texto_nivel = f"Nivel {self.numero_nivel}"
        # Tamaño ligeramente reducido para que el texto encaje mejor con el marco de nivel
        tam_texto = int(alto * 0.033)
        try:
            fuente_nivel = pygame.font.Font(self.font_path, tam_texto)
        except Exception:
            fuente_nivel = pygame.font.Font(None, tam_texto)
        surf_texto = fuente_nivel.render(texto_nivel, True, (230, 230, 230))
        text_w, text_h = surf_texto.get_size()

        # Dibujar un rectángulo semitransparente detrás del texto del nivel para darle énfasis
        pad_x = max(8, int(text_w * 0.25))
        pad_y = max(4, int(text_h * 0.4))
        bg_rect = pygame.Rect(0, 0, text_w + pad_x, text_h + pad_y)
        bg_rect.center = (center_x, center_y)
        # Fondo y borde del rectángulo
        pygame.draw.rect(pantalla, (30, 30, 45, 180), bg_rect, border_radius=6)
        pygame.draw.rect(pantalla, (70, 70, 100), bg_rect, 1, border_radius=6)
        # Dibujar el texto encima
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
        # Rectángulo de fondo y contorno
        rect_fondo = pygame.Rect(x, y, ancho, alto)
        # Rectángulo de la parte rellena según la proporción de energía
        fill_w = int(ancho * proporcion)
        rect_barra = pygame.Rect(x, y, fill_w, alto)
        # Fondo gris oscuro del indicador
        pygame.draw.rect(pantalla, (40, 40, 50), rect_fondo, border_radius=4)
        # Relleno con textura si está disponible; de lo contrario, usar el color proporcionado
        if fill_w > 0:
            if hasattr(self, 'energy_texture') and self.energy_texture:
                try:
                    # Escala la textura al tamaño del relleno y blitéala
                    tex_scaled = pygame.transform.scale(self.energy_texture, (fill_w, alto))
                    pantalla.blit(tex_scaled, (x, y))
                except Exception:
                    # Fallback a color sólido si falla
                    pygame.draw.rect(pantalla, color_barra, rect_barra, border_radius=4)
            else:
                pygame.draw.rect(pantalla, color_barra, rect_barra, border_radius=4)
        # Borde blanco suave del contorno
        pygame.draw.rect(pantalla, (200, 200, 220), rect_fondo, 1, border_radius=4)

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

