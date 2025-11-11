import pygame
import os
import random
import math
import glob
from nivel import nivel
from camara import camara
from jugador import jugador
from enemigo import enemigo
from proyectil import proyectil
from datetime import datetime
import pared

# -------------------------------------------------------
# COLORES
# -------------------------------------------------------
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
        self.opcion_pausa = 0  # 0: Reanudar, 1: Reiniciar, 2: Configuración, 3: Menú Principal
        self.puntos = 0  # Sistema de puntuación
        self.enemigos_derrotados = 0  # Contador de enemigos
        self.volumen_musica = 0.3  # Volumen de música (0.0 a 1.0)
        self.volumen_efectos = 0.7  # Volumen de efectos (0.0 a 1.0)
        self.estado_previo_config = None  # Para saber si se viene de menú o pausa
        self.mostrar_tutorial = False  # No mostrar tutorial en el juego (ya hay pantalla de controles)
        self.tutorial_mostrado = True  # Marcar como mostrado para que no bloquee controles
        self.menu_index = 0  # Índice de selección en el menú
        self.using_pixel_fonts = False  # Marca si se están usando fuentes pixelizadas personalizadas

        # Sistema de guardado de partidas
        self.nombre_jugador = ""  # Nombre del jugador actual
        self.input_activo = False  # Si el campo de texto está activo
        self.archivo_guardado = "partidas_guardadas.txt"  # Archivo de guardado
        self.archivo_historial = "historial_jugadores.txt"  # Archivo de historial
        self.archivo_campeones = "campeones.txt"  # Archivo de campeones
        self._cargar_hitboxes = []  # Hitboxes para el menú de carga de partidas
        self._borrar_hitboxes = []  # Hitboxes para los botones de borrar partidas
        self._tab_puntuacion = "campeones"  # Tab activa en puntuaciones: "campeones" o "historico"

        # Configuración visual
        self.altura_header = 0.10
        pygame.display.set_caption("Fear of Ways")
        self.fuente_base = pygame.font.Font(None, 30)
        
        # Ocultar cursor del mouse durante el juego
        pygame.mouse.set_visible(True)  # Visible en menú
        
        # Mensajes temporales
        self.mensaje_temporal = ""
        self.mensaje_timer = 0

        # Sistema de temporizador para escape
        self.temporizador_activo = False
        self.tiempo_restante = 0  # En frames (60 fps)
        self.tiempo_agotado = False
        self.spawn_enemigos_extra = 0  # Contador para spawnar enemigos cuando se acaba el tiempo
        
        # Cronómetro de partida (cuenta hacia arriba)
        self.cronometro_frames = 0  # Tiempo en frames (60 fps)
        self.cronometro_activo = False  # Se activa al empezar a jugar
        self.tiempo_total_segundos = 0  # Tiempo total en segundos para guardar
        
        # Control para evitar guardar múltiples veces en historial
        self.historial_guardado = False  # Flag para guardar solo una vez

        # Sistema de spawn progresivo de enemigos
        self.spawn_progresivo_activo = True
        self.contador_spawn_progresivo = 0
        self.intervalo_spawn = 0  # Se configurará según el nivel
        self.cantidad_spawn = 0   # Se configurará según el nivel

        # Sistema de power-ups activables
        self.powerup_activo = None  # Tipo de power-up activo
        self.powerup_duracion = 0   # Duración restante en frames
        self.vision_normal = 0      # Guardar visión normal para restaurar
        self.velocidad_normal = 0   # Guardar velocidad normal para restaurar
        self.disparo_doble = False  # Si está activo el disparo doble
        self.escudo_activo = False  # Si está activo el escudo

        # Sonidos con mejor manejo de errores
        print("\nCargando recursos de audio...")
        self.sonido_disparo = self._cargar_sonido_basico(
            "audio/disparo.mp3",
            "Sonido de disparo",
            volumen_absoluto=0.7
        )
        self.sonido_golpe = self._cargar_sonido_basico(
            "audio/daño.mp3",
            "Sonido de golpe",
            volumen_relativo=0.7
        )

        # Sonidos nuevos
        self.sonidos_click_menu = self._cargar_variantes_click("audio", "click_menu", volumen_relativo=0.5)
        self.sonido_corazon = self._cargar_sonido_opcional("audio", "corazon", "Sonido de corazón", volumen_relativo=0.7)
        self.sonido_notificacion = self._cargar_sonido_opcional(
            "audio",
            "notificaciones_juego",
            "Sonido de notificación",
            volumen_relativo=0.6
        )
        self.sonido_pocion = self._cargar_sonido_opcional("audio", "pociones", "Sonido de pociones", volumen_relativo=0.7)
        self.sonido_recoger_llave = self._cargar_sonido_opcional(
            "audio",
            "recoger_llave",
            "Sonido de llave",
            volumen_relativo=0.7
        )
        self.sonido_rayo = self._cargar_sonido_opcional(
            "audio",
            "rayo",
            "Sonido de rayo",
            volumen_relativo=0.7
        )

        # Música y sonidos de resultado
        # menu_sonido.mp3 debe existir en la carpeta audio/ (si no, se ignora)
        try:
            self.musica_menu_path = self._resolver_archivo_audio("audio", "menu_sonido")
        except Exception:
            self.musica_menu_path = None

        try:
            # Música que se reproduce mientras se juega (solo durante la acción)
            self.musica_nivel_path = self._resolver_archivo_audio("audio", "musica_fondo")
        except Exception:
            self.musica_nivel_path = None

        # Sonidos de victoria/derrota
        self.sonido_victoria = self._cargar_sonido_opcional("audio", "victoria_sonido", "Sonido victoria", volumen_relativo=0.95)
        self.sonido_derrota = self._cargar_sonido_opcional("audio", "derrota", "Sonido derrota", volumen_relativo=0.95)

        # Estado interno para música (ruta actualmente reproducida)
        self._musica_actual = None

        # Usar el sonido de golpe como respaldo cuando falte algún efecto puntual
        print("Audio inicializado\n")

        # Carga de recursos gráficos para HUD y menú
        # Almacenamos el directorio actual para localizar imágenes
        self._dir = os.path.dirname(__file__)

        # Tamaño base de los iconos para el HUD. Al usar un tamaño único se simplifica
        # el diseño y se consigue un aspecto más minimalista. 28 píxeles funciona bien en
        # la mayoría de resoluciones. Si falla la carga, los iconos simplemente no se dibujan.
        icon_size = 28

        # Cargar iconos del HUD con manejo de errores mejorado
        print("Cargando recursos gráficos...")
        
        # Cargar icono del corazón (vida)
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'heart.png')).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("Icono de corazón cargado")
        except (pygame.error, FileNotFoundError):
            self.heart_img = None
            print("Advertencia: images/heart.png no encontrado, se usará fallback")

        # Cargar icono de la llave
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'key_icon.png')).convert_alpha()
            self.key_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("Icono de llave cargado")
        except (pygame.error, FileNotFoundError):
            self.key_img = None
            print(" Advertencia: images/key_icon.png no encontrado, se usará fallback")

        # Cargar icono del rayo
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'lightning.png')).convert_alpha()
            self.lightning_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("Icono de rayo cargado")
        except (pygame.error, FileNotFoundError):
            self.lightning_img = None
            print("Advertencia: images/lightning.png no encontrado, se usará fallback")

        # No usamos un marco externo para el menú, así que desactivamos cualquier intento de cargar menu_frame_img
        self.menu_frame_img = None

        # Cargar textura oscura para el HUD
        try:
            tex = pygame.image.load(os.path.join(self._dir, 'images', 'hud_bar_texture.png')).convert()
            self.hud_texture = tex
            print("Textura de HUD cargada")
        except (pygame.error, FileNotFoundError):
            self.hud_texture = None
            print("Advertencia: images/hud_bar_texture.png no encontrado, se usará color sólido")

        # Cargar icono del corazón para bonus de vida en el mapa
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'heart.png')).convert_alpha()
            self.heart_bonus_img = pygame.transform.scale(img, (15, 15))
            print("Icono de bonus de vida cargado")
        except (pygame.error, FileNotFoundError):
            self.heart_bonus_img = None
            print("Advertencia: Bonus de vida usará fallback")

        # Cargar icono del rayo para bonus de energía en el mapa
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'lightning.png')).convert_alpha()
            self.lightning_bonus_img = pygame.transform.scale(img, (15, 15))
            print("Icono de bonus de energía cargado")
        except (pygame.error, FileNotFoundError):
            self.lightning_bonus_img = None
            print("Advertencia: Bonus de energía usará fallback")
        
        # Cargar icono de poción para power-ups
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'posion.png')).convert_alpha()
            self.posion_img = pygame.transform.scale(img, (15, 15))
            print("Icono de poción cargado")
        except (pygame.error, FileNotFoundError):
            self.posion_img = None
            print(" Advertencia: images/posion.png no encontrado, se usará fallback")
        
        # Cargar icono del cronómetro/reloj para el HUD (más grande que otros iconos)
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'tiempo.png')).convert_alpha()
            tiempo_size = int(icon_size * 1.3)  # 30% más grande que otros iconos
            self.tiempo_img = pygame.transform.smoothscale(img, (tiempo_size, tiempo_size))
            print("Icono de tiempo/cronómetro cargado")
        except (pygame.error, FileNotFoundError):
            self.tiempo_img = None
            print("Advertencia: images/tiempo.png no encontrado, se usará fallback")
        
        print("Recursos gráficos inicializados\n")

        # Cargar textura de muros y asignarla al módulo `pared` para que todos los muros la usen
        try:
            wall_path = os.path.join(self._dir, 'images', 'wall_texture.png')
            if os.path.isfile(wall_path):
                textura = pygame.image.load(wall_path).convert()
                # Guardar la textura sin escalar; `pared.dibujar` la escalará según el rect
                pared.TEXTURA_MURO = textura
                print("Textura de muros cargada: images/wall_texture.png")
            else:
                pared.TEXTURA_MURO = None
                print("Advertencia: images/wall_texture.png no encontrado, se usará fallback para muros")
        except Exception as e:
            pared.TEXTURA_MURO = None
            print(f"Error cargando textura de muros: {e}")

        # Color de la barra de energía (más visible y coherente con la estética)
        self.energy_bar_color = (80, 150, 220)

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
            candidates_title = ["PressStart2P", "Press Start 2P", "VT323", "Pixelify Sans", "Courier New", "Liberation Mono"]
            found_title = None
            for name in candidates_title:
                fp = pygame.font.match_font(name)
                if fp:
                    found_title = fp
                    break
            self.font_path_title = found_title or self.font_path
        except Exception:
            self.font_path_title = self.font_path

        # Detectar fuentes adicionales en assets/fonts (si el usuario colocó alguna)
        try:
            self.detectar_fuentes()
        except Exception:
            # No crítico: si falla la detección, se usan las rutas ya configuradas
            pass

    def ajustar_tamano(self, tam):
        """Ajusta el tamaño de fuente cuando se usan fuentes pixelizadas para evitar que se vean demasiado grandes.
        Devuelve un entero >= 8.
        """
        try:
            factor = 0.90 if getattr(self, 'using_pixel_fonts', False) else 1.0
            return max(8, int(tam * factor))
        except Exception:
            return max(8, int(tam))

    def detectar_fuentes(self):
        """Busca fuentes adicionales en assets/fonts y ajusta rutas de fuente si se encuentran.
        Esto permite que el juego use fuentes provistas por el usuario (por ejemplo fuentes pixeladas).
        """
        try:
            fonts_dir = os.path.join(self._dir, 'assets', 'fonts')
            found_files = []
            if os.path.isdir(fonts_dir):
                # Buscar archivos de fuentes (ttf/otf) con indicios de ser pixeladas o variantes de outline/filled
                found_files = [f for f in os.listdir(fonts_dir)
                               if f.lower().endswith(('.ttf', '.otf')) and
                               ('pixel' in f.lower() or 'outline' in f.lower() or 'filled' in f.lower() or 'typeface' in f.lower())]

            # Buscar candidatos de outline/filled entre los archivos detectados
            preferred_outline = None
            preferred_filled = None
            for f in found_files:
                if 'outline' in f.lower() and preferred_outline is None:
                    preferred_outline = os.path.join(fonts_dir, f)
                if ('filled' in f.lower() or 'pixelfilled' in f.lower()) and preferred_filled is None:
                    preferred_filled = os.path.join(fonts_dir, f)

            if preferred_outline and os.path.isfile(preferred_outline):
                self.font_path_title = preferred_outline
                if preferred_filled and os.path.isfile(preferred_filled):
                    self.font_path = preferred_filled
                else:
                    # fallback to using the outline for body if no filled variant
                    self.font_path = preferred_outline
                self.using_pixel_fonts = True
                print(f"Fuentes detectadas (preferido). Usando: title={self.font_path_title}, body={self.font_path}")
            elif found_files:
                # Fallback to heuristic: outline->title, filled->body
                filled = next((f for f in found_files if 'filled' in f.lower()), found_files[0])
                outline = next((f for f in found_files if 'outline' in f.lower()), None)

                filled_path = os.path.join(fonts_dir, filled)
                outline_path = os.path.join(fonts_dir, outline) if outline else None

                if outline_path and os.path.isfile(outline_path):
                    self.font_path_title = outline_path
                elif os.path.isfile(filled_path):
                    self.font_path_title = filled_path

                if os.path.isfile(filled_path):
                    self.font_path = filled_path

                self.using_pixel_fonts = True
                print(f"Fuentes detectadas. Usando: title={self.font_path_title}, body={self.font_path}")
            else:
                self.using_pixel_fonts = False
        except Exception:
            self.using_pixel_fonts = False

    # MENÚ PRINCIPAL
    def menu(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        """
        Muestra el menú principal del juego. Este método elimina cualquier marco o cuadro
        adicional y utiliza una imagen de fondo especificada por el usuario para
        ambientar el menú. El texto se centra de forma dinámica sobre la imagen
        conservando un aspecto minimalista acorde con el resto del juego.
        """
        # Fondo: intentamos cargar la imagen del fondo de menú 'menu_background.png'.
        # Si no existe o falla la carga, se usa un tono oscuro como fondo.
        fondo_path = os.path.join(self._dir, 'images', 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                # Escalar al tamaño de la ventana para cubrir toda la pantalla.
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))

        # TÍTULO 
        title_size = int(alto * 0.095)
        try:
            font_title = pygame.font.Font(self.font_path_title, self.ajustar_tamano(title_size))
        except Exception:
            font_title = pygame.font.Font(None, self.ajustar_tamano(title_size))

        titulo = "Fear Of Ways"
        base = font_title.render(titulo, True, (240, 235, 220))
        # contorno suave
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.12) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.12)))

        # OPCIONES
        opciones = ["Empezar Aventura", "Continuar", "Tabla de Campeones", "Opciones"]

        # Ajustar área para 4 opciones
        area_y_start = int(alto * 0.40)
        area_y_end   = int(alto * 0.72)
        area_height  = area_y_end - area_y_start

        try:
            menu_size = max(16, int(area_height / 6))
            font_menu = pygame.font.Font(self.font_path, self.ajustar_tamano(menu_size))
        except Exception:
            menu_size = max(16, int(area_height / 6))
            font_menu = pygame.font.Font(None, self.ajustar_tamano(menu_size))

        # Crear superficies con color base
        surfaces = [font_menu.render(txt, True, (235, 225, 210)) for txt in opciones]
        heights  = [s.get_height() for s in surfaces]
        spacing  = int(area_height * 0.12)
        total_h  = sum(heights) + spacing * (len(opciones) - 1)
        y_current = area_y_start + (area_height - total_h) // 2

        mouse_pos = pygame.mouse.get_pos()
        self._menu_hitboxes = []

        for i, txt in enumerate(opciones):
            x = ancho // 2 - surfaces[i].get_width() // 2
            y = y_current

            rect_hit = pygame.Rect(x - 18, y - 8, surfaces[i].get_width() + 36, surfaces[i].get_height() + 16)
            self._menu_hitboxes.append((rect_hit, i))

            hovering = rect_hit.collidepoint(mouse_pos)
            
            # Renderizar texto con color según hover
            if hovering:
                # Color resaltado cuando el mouse está encima
                surf = font_menu.render(txt, True, (255, 215, 0))  # Dorado brillante
                overlay = pygame.Surface((rect_hit.width, rect_hit.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 90))
                pantalla.blit(overlay, rect_hit.topleft)
                pygame.draw.rect(pantalla, (255, 215, 0), rect_hit, 1, border_radius=8)
            else:
                # Color normal
                surf = surfaces[i]

            pantalla.blit(surf, (x, y))
            y_current += surf.get_height() + spacing

        # Pie
        hint_size = int(alto * 0.03)
        self.dibujar_texto("ESC para salir", hint_size, (190, 190, 200), ancho // 2, int(alto * 0.90))
    # -------------------------------------------------------
    # INICIO Y CARGA DE JUEGO
    # -------------------------------------------------------
    def iniciar_juego(self):
        """Inicia una nueva partida usando el personaje por defecto.
        Se ha eliminado la selección de tipo de personaje; ahora siempre se crea
        un único perfil predeterminado (Explorador equilibrado)."""
        self._guardado = False
        self.puntos = 0  # Resetear puntuación
        self.enemigos_derrotados = 0  # Resetear contador
        self.tutorial_mostrado = True  # Mantener como mostrado (ya se muestra en pantalla de controles)
        # Crear un único personaje por defecto (Explorador - equilibrado)
        self.jugador = jugador("Explorador", AMARILLO, velocidad=4, energia=100, vision=150)
        # Resetear frase final y animación de pantalla final para evitar que persistan entre partidas
        self.frase_final = None
        self._pantalla_final_frame = None
        self._pantalla_final_fade_frames = 30  # duración del fade-in en frames

        self.numero_nivel = 1
        self.cargar_nivel(self.numero_nivel)
        self.resultado = ""
        self.estado = "controles"
        pygame.mouse.set_visible(True)   # mostramos el mouse en la pantalla de controles
        
        # Inicializar cronómetro
        self.cronometro_frames = 0
        self.cronometro_activo = False  # Se activará cuando empiece a jugar
        self.tiempo_total_segundos = 0
        
        # Resetear bandera de historial
        self.historial_guardado = False


    def activar_temporizador(self):
        """Activa el temporizador según el nivel actual"""
        self.temporizador_activo = True
        self.tiempo_agotado = False
        self.spawn_enemigos_extra = 0
        
        # Tiempos según el nivel (en frames a 60 FPS)
        if self.numero_nivel == 1:
            self.tiempo_restante = 120 * 60  # 2 minutos
        elif self.numero_nivel == 2:
            self.tiempo_restante = 90 * 60   # 1.5 minutos
        elif self.numero_nivel == 3:
            self.tiempo_restante = 60 * 60   # 1 minuto
        else:
            self.tiempo_restante = 60 * 60   # Por defecto 1 minuto

    def cargar_nivel(self, numero, semilla_mapa=None):
        self.numero_nivel = numero
        # Limpiar nivel anterior completamente
        self.nivel_actual = None
        # Crear nuevo nivel con llaves frescas (usar semilla si se proporciona)
        self.nivel_actual = nivel(numero, semilla=semilla_mapa)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)
        self.enemigos.clear()
        self.proyectiles.clear()
        
        # Resetear el estado de todas las puertas (cerrarlas)
        if hasattr(self.nivel_actual, '_puertas_por_id'):
            for id_puerta, puertas in self.nivel_actual._puertas_por_id.items():
                for puerta in puertas:
                    puerta.abierta = False

        # Generar enemigos con diversidad - REDUCIDOS Y BALANCEADOS
        apariciones = list(self.nivel_actual.spawn_enemigos)
        random.shuffle(apariciones)
        
        # Limitar cantidad de enemigos según el nivel
        max_enemigos = min(4 + numero * 2, len(apariciones))  # 6, 8, 10 enemigos máximo
        apariciones = apariciones[:max_enemigos]
        
        # Asegurar variedad de tipos
        tipos_forzados = ["veloz", "acechador", "bruto"]
        for tipo in tipos_forzados:
            if apariciones:
                x, y = apariciones.pop()
                self.enemigos.append(enemigo(x, y, random.randint(2, 3), tipo=tipo))
        
        # Resto de enemigos con distribución equilibrada
        for x, y in apariciones:
            tipo = random.choices(["veloz", "acechador", "bruto"], [0.4, 0.35, 0.25])[0]
            self.enemigos.append(enemigo(x, y, random.randint(2, 3), tipo=tipo))

        # Generar bonus según el nivel
        self.generar_bonus_nivel(numero)

        # Ajuste de dificultad progresiva MÁS SUAVE
        dificultad = 1 + (numero - 1) * 0.15  # Reducido de 0.25 a 0.15
        for e in self.enemigos:
            e.velocidad = int(e.velocidad * dificultad)
            # NO aumentar rango de detección con dificultad

        # Resetear jugador con posición de spawn aleatoria segura
        spawn_x, spawn_y = self.nivel_actual.obtener_spawn_jugador_seguro(tamaño_jugador=30)
        self.jugador.establecer_posicion_spawn(spawn_x, spawn_y)
        self.jugador.oculto = False
        # Restaurar vida y energía al máximo
        self.jugador.vida = self.jugador.vida_max
        self.jugador.energia = self.jugador.energia_max
        
        # Desactivar cualquier power-up activo (sin mostrar mensaje)
        self.desactivar_powerup(mostrar_mensaje=False)

        # Resetear temporizador
        self.temporizador_activo = False
        self.tiempo_restante = 0
        self.tiempo_agotado = False
        self.spawn_enemigos_extra = 0

        # Configurar spawn progresivo según el nivel
        self.spawn_progresivo_activo = True
        self.contador_spawn_progresivo = 0
        
        if numero == 1:
            self.intervalo_spawn = 20 * 60  # 20 segundos (1200 frames)
            self.cantidad_spawn = 3
        elif numero == 2:
            self.intervalo_spawn = 10 * 60  # 10 segundos (600 frames)
            self.cantidad_spawn = 4
        elif numero == 3:
            self.intervalo_spawn = 5 * 60   # 5 segundos (300 frames)
            self.cantidad_spawn = 5
        else:
            self.intervalo_spawn = 20 * 60
            self.cantidad_spawn = 3

    # GENERACIÓN DE BONUS POR NIVEL
    def posicion_valida_bonus(self, x, y, tamaño):
        """Verifica que una posición no colisione con muros"""
        test_rect = pygame.Rect(x, y, tamaño, tamaño)
        for muro in self.nivel_actual.muros:
            if test_rect.colliderect(muro.rect):
                return False
        return True
    
    def generar_bonus_nivel(self, numero_nivel):
        """Genera bonus de forma controlada según el nivel"""
        self.nivel_actual.bonus = []
        
        # Determinar cantidad máxima de corazones según el nivel
        if numero_nivel == 1:
            max_corazones = 3
        elif numero_nivel == 2:
            max_corazones = 2
        elif numero_nivel == 3:
            max_corazones = 1
        else:
            max_corazones = 2  # Por defecto
        
        # Generar corazones de vida (cantidad aleatoria hasta el máximo)
        num_corazones = random.randint(1, max_corazones)
        intentos_max = 50  # Máximo de intentos para encontrar una posición válida
        
        for _ in range(num_corazones):
            for intento in range(intentos_max):
                bx = random.randint(100, self.nivel_actual.ancho - 100)
                by = random.randint(100, self.nivel_actual.alto - 100)
                if self.posicion_valida_bonus(bx, by, 15):
                    self.nivel_actual.bonus.append({"rect": pygame.Rect(bx, by, 15, 15), "tipo": "vida"})
                    break
        
        # Generar power-ups según el nivel
        if numero_nivel == 1:
            num_powerups = 3
        elif numero_nivel == 2:
            num_powerups = 2
        elif numero_nivel == 3:
            num_powerups = 1
        else:
            num_powerups = 2
        
        # Tipos de power-ups disponibles con sus probabilidades
        powerup_tipos = ["vision_clara", "disparo_doble", "super_velocidad", "escudo"]
        # Pesos de probabilidad: visión clara tiene el doble de probabilidad que los otros
        powerup_pesos = [0.4, 0.2, 0.2, 0.2]  # 40% visión clara, 20% cada uno de los otros
        
        # Generar power-ups en posiciones aleatorias
        for _ in range(num_powerups):
            tipo = random.choices(powerup_tipos, weights=powerup_pesos, k=1)[0]
            tamaño = 15  # Tamaño de los power-ups (igual que corazones y energía)
            
            for intento in range(intentos_max):
                bx = random.randint(100, self.nivel_actual.ancho - 100)
                by = random.randint(100, self.nivel_actual.alto - 100)
                if self.posicion_valida_bonus(bx, by, tamaño):
                    self.nivel_actual.bonus.append({
                        "rect": pygame.Rect(bx, by, tamaño, tamaño), 
                        "tipo": tipo,
                        "activo": False  # Indica si el power-up está activo (para renderizado)
                    })
                    break
        
        # Generar energía adicional
        num_energia = random.randint(1, 2)
        for _ in range(num_energia):
            for intento in range(intentos_max):
                bx = random.randint(100, self.nivel_actual.ancho - 100)
                by = random.randint(100, self.nivel_actual.alto - 100)
                if self.posicion_valida_bonus(bx, by, 15):
                    self.nivel_actual.bonus.append({"rect": pygame.Rect(bx, by, 15, 15), "tipo": "energia"})
                    break

    # BUCLE PRINCIPAL DE JUEGO
    def jugar(self, pausado=False):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        offset_header = int(alto * self.altura_header)
        area_juego = pygame.Surface((ancho, alto - offset_header))
        area_juego.fill(GRIS)

        # Verificar si el tutorial está activo (congela el juego)
        tutorial_activo = (self.numero_nivel == 1 and self.mostrar_tutorial and not self.tutorial_mostrado)
        
        # Actualizar cámara y movimiento del jugador (solo si no está pausado Y el tutorial no está activo)
        if not pausado and not tutorial_activo:
            self.camara.actualizar(self.jugador.rect)
            teclas = pygame.key.get_pressed()
            muros_bloq = [m for m in self.nivel_actual.muros if getattr(m, "bloquea", True)]
            self.jugador.mover(teclas, muros_bloq, self.nivel_actual.ancho, self.nivel_actual.alto)
            
            # Actualizar cronómetro (cuenta hacia arriba)
            if self.cronometro_activo:
                self.cronometro_frames += 1
                self.tiempo_total_segundos = self.cronometro_frames // 60
            
            # Actualizar temporizador si está activo
            if self.temporizador_activo and self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                
                # Advertencia cuando quedan 30 segundos
                if self.tiempo_restante == 30 * 60:
                    self.mostrar_mensaje("¡QUEDAN 30 SEGUNDOS!", 120)
                # Advertencia cuando quedan 10 segundos
                elif self.tiempo_restante == 10 * 60:
                    self.mostrar_mensaje("¡SOLO 10 SEGUNDOS!", 120)
                    
            # Si el tiempo se acaba, spawear enemigos continuamente
            elif self.temporizador_activo and self.tiempo_restante <= 0 and not self.tiempo_agotado:
                self.tiempo_agotado = True
                self.mostrar_mensaje("¡TIEMPO AGOTADO! ¡ENEMIGOS INVADEN!", 180)
            
            # Spawear enemigos extra cuando el tiempo se agota
            if self.tiempo_agotado:
                self.spawn_enemigos_extra += 1
                # Spawear un enemigo cada 2 segundos (120 frames)
                if self.spawn_enemigos_extra >= 120:
                    self.spawn_enemigos_extra = 0
                    self.spawear_enemigo_aleatorio()
            
            # Sistema de spawn progresivo de enemigos
            if self.spawn_progresivo_activo:
                self.contador_spawn_progresivo += 1
                
                # Cuando se cumple el intervalo, spawear enemigos
                if self.contador_spawn_progresivo >= self.intervalo_spawn:
                    self.contador_spawn_progresivo = 0
                    self.spawear_enemigos_progresivos()
        else:
            muros_bloq = [m for m in self.nivel_actual.muros if getattr(m, "bloquea", True)]

        # Sincronizar estado del escudo con el jugador
        self.jugador.escudo_activo = self.escudo_activo
        
        # Dibujar mapa y enemigos
        self.nivel_actual.dibujar(area_juego, self.camara)
        for enemigo_actual in list(self.enemigos):
            if not pausado and not tutorial_activo:
                enemigo_actual.mover(muros_bloq, self.nivel_actual.ancho, self.nivel_actual.alto, self.jugador)
            enemigo_actual.dibujar(area_juego, self.camara)

            # Los enemigos ya NO dañan por contacto directo
            # Cada tipo tiene su propio sistema de ataque con cooldowns
            # Verificar si el jugador murió después de los ataques específicos
            if not pausado and not tutorial_activo and self.jugador.vida <= 0:
                self.resultado = "perdiste"
                self.estado = "fin"
                # Reproducir sonido de derrota cuando el jugador muere
                try:
                    self._reproducir_sonido(self.sonido_derrota)
                except Exception:
                    pass
                # Guardar en historial y eliminar la partida guardada cuando el jugador muere (SOLO UNA VEZ)
                if self.nombre_jugador and not self.historial_guardado:
                    self.guardar_en_historial()
                    self.borrar_partida(self.nombre_jugador)
                    self.historial_guardado = True  # Marcar como guardado
                    print(f"Partida de {self.nombre_jugador} guardada en historial y eliminada")

        # Actualizar duración de power-ups activos
        if not pausado and not tutorial_activo and self.powerup_duracion > 0:
            self.powerup_duracion -= 1
            if self.powerup_duracion <= 0:
                self.desactivar_powerup(mostrar_mensaje=False)
        
        # Dibujar y recoger bonus (solo recoger si no está pausado)
        for bonus in list(getattr(self.nivel_actual, "bonus", [])):
            rect = bonus["rect"]
            tipo = bonus["tipo"]
            # Aplicar transformación de cámara para que se muevan con el mundo
            rect_pantalla = self.camara.aplicar(rect)
            
            # Dibujar según el tipo de bonus
            if tipo == "vida" and self.heart_bonus_img:
                # Usar imagen del corazón para vida
                heart_escalado = pygame.transform.scale(
                    self.heart_bonus_img, 
                    (int(rect_pantalla.width * self.camara.zoom), 
                     int(rect_pantalla.height * self.camara.zoom))
                )
                area_juego.blit(heart_escalado, rect_pantalla)
            elif tipo == "energia" and self.lightning_bonus_img:
                # Usar imagen del rayo para energía
                lightning_escalado = pygame.transform.scale(
                    self.lightning_bonus_img, 
                    (int(rect_pantalla.width * self.camara.zoom), 
                     int(rect_pantalla.height * self.camara.zoom))
                )
                area_juego.blit(lightning_escalado, rect_pantalla)
            elif tipo in ["vision_clara", "disparo_doble", "super_velocidad", "escudo"]:
                # Dibujar power-ups con imagen de poción
                if self.posion_img:
                    # Usar imagen de poción escalada
                    posion_escalado = pygame.transform.scale(
                        self.posion_img, 
                        (int(rect_pantalla.width * self.camara.zoom), 
                         int(rect_pantalla.height * self.camara.zoom))
                    )
                    area_juego.blit(posion_escalado, rect_pantalla)
                else:
                    # Fallback: dibujar círculo de color si no hay imagen
                    tiempo = pygame.time.get_ticks()
                    pulso = 0.8 + 0.2 * math.sin(tiempo / 200)
                    
                    # Colores según tipo
                    if tipo == "vision_clara":
                        color = (255, 255, 100)
                    elif tipo == "disparo_doble":
                        color = (255, 100, 100)
                    elif tipo == "super_velocidad":
                        color = (100, 255, 100)
                    elif tipo == "escudo":
                        color = (100, 200, 255)
                    
                    center = rect_pantalla.center
                    radio = int(rect_pantalla.width / 2 * pulso)
                    pygame.draw.circle(area_juego, color, center, radio)
                    pygame.draw.circle(area_juego, (255, 255, 255), center, radio, 2)
                
                # Dibujar texto indicador si el jugador está cerca
                if self.jugador.rect.inflate(80, 80).colliderect(rect):
                    font = pygame.font.Font(None, 20)
                    texto = font.render("[PRESIONA E]", True, (255, 255, 255))
                    center = rect_pantalla.center
                    texto_rect = texto.get_rect(center=(center[0], center[1] - 15))
                    area_juego.blit(texto, texto_rect)
            
            # Recoger bonus instantáneos (vida, energía)
            if not pausado and not tutorial_activo and self.jugador.rect.colliderect(rect):
                if tipo == "vida":
                    self.jugador.vida = min(self.jugador.vida_max, self.jugador.vida + 1)
                    self.reproducir_corazon()
                    self.nivel_actual.bonus.remove(bonus)
                elif tipo == "energia":
                    self.jugador.energia = min(self.jugador.energia_max, self.jugador.energia + 20)
                    self.reproducir_rayo()
                    self.nivel_actual.bonus.remove(bonus)
        
        # Recoger llaves (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo:
            for llave in list(getattr(self.nivel_actual, "llaves", [])):
                if self.jugador.rect.colliderect(llave):
                    self.nivel_actual.llaves.remove(llave)
                    self.reproducir_llave()
                    # Mensaje visual de llave recogida
                    llaves_restantes = len(self.nivel_actual.llaves)
                    if llaves_restantes == 0:
                        # ¡TODAS LAS LLAVES RECOGIDAS! - ACTIVAR TEMPORIZADOR
                        self.activar_temporizador()
                        tiempo_seg = int(self.tiempo_restante / 60)
                        minutos = tiempo_seg // 60
                        segundos = tiempo_seg % 60
                        self.mostrar_mensaje(
                            f"¡SALIDA ABIERTA! TIENES {minutos}:{segundos:02d} PARA ESCAPAR",
                            180
                        )
                    else:
                        self.mostrar_mensaje(f"¡Llave recogida! Faltan {llaves_restantes}", 90)
        
        # Proyectiles y colisiones (solo mover si no está pausado y tutorial no activo)
        for bala in list(self.proyectiles):
            if not pausado and not tutorial_activo:
                if not bala.mover(muros_bloq):
                    self.proyectiles.remove(bala)
                    continue
            bala.dibujar(area_juego, self.camara)
            if not pausado and not tutorial_activo:
                for enemigo_actual in list(self.enemigos):
                    if bala.rect.colliderect(enemigo_actual.rect):
                        enemigo_actual.vida -= 1
                        if enemigo_actual.vida <= 0:
                            self.enemigos.remove(enemigo_actual)
                            self.enemigos_derrotados += 1
                            self.puntos += 100  # Puntos por enemigo derrotado
                        if bala in self.proyectiles:
                            self.proyectiles.remove(bala)
                        break        # Dibujar jugador y linterna
        self.jugador.dibujar(area_juego, self.camara)
        
        # Dibujar escudo si está activo
        if self.escudo_activo:
            jugador_pantalla = self.camara.aplicar(self.jugador.rect)
            centro = jugador_pantalla.center
            tiempo = pygame.time.get_ticks()
            radio = int(40 * self.camara.zoom + 5 * math.sin(tiempo / 100))
            # Dibujar círculo del escudo con efecto pulsante
            color_escudo = (100, 200, 255, 100)
            superficie_escudo = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(superficie_escudo, color_escudo, (radio, radio), radio)
            pygame.draw.circle(superficie_escudo, (150, 220, 255), (radio, radio), radio, 3)
            area_juego.blit(superficie_escudo, (centro[0] - radio, centro[1] - radio))
        
        self.dibujar_linterna_en_superficie(area_juego)
        pantalla.blit(area_juego, (0, offset_header))
        self.dibujar_header(pantalla, ancho, alto, offset_header)
        
        # Actualizar y mostrar mensaje temporal
        if not pausado and not tutorial_activo and self.mensaje_timer > 0:
            self.mensaje_timer -= 1
            # Dibujar mensaje en el centro de la pantalla
            alpha = min(255, self.mensaje_timer * 3) if self.mensaje_timer < 60 else 255
            color_msg = (0, 255, 0) if "ABIERTA" in self.mensaje_temporal else (255, 255, 100)
            
            # Fondo semi-transparente para el mensaje
            msg_y = int(alto * 0.7)
            overlay = pygame.Surface((ancho, int(alto * 0.1)), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(180, alpha)))
            pantalla.blit(overlay, (0, msg_y))
            
            # Texto del mensaje
            self.dibujar_texto(self.mensaje_temporal, int(alto * 0.05), color_msg, ancho // 2, msg_y + int(alto * 0.05))
        
        # Verificar proximidad a la salida y mostrar mensaje (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo and self.nivel_actual.salida:
            llaves_restantes = len(getattr(self.nivel_actual, "llaves", []))
            cerca, mensaje = self.nivel_actual.salida.verificar_proximidad_jugador(
                self.jugador.rect, llaves_restantes
            )
            if cerca and mensaje:
                indicador_y = int(alto * 0.15)
                color_texto = (255, 100, 100) if llaves_restantes > 0 else (100, 255, 100)
                self.dibujar_texto(mensaje, int(alto * 0.04), color_texto, ancho // 2, indicador_y)
        
        # Dibujar mira personalizada (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo:
            self.dibujar_mira(pantalla)
        
        # Mostrar tutorial en el primer nivel (se muestra aunque el juego esté congelado)
        if self.numero_nivel == 1 and self.mostrar_tutorial and not self.tutorial_mostrado:
            self.dibujar_tutorial(pantalla)

        # Salida del nivel (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo and self.jugador.rect.colliderect(self.nivel_actual.salida.rect) and len(getattr(self.nivel_actual, "llaves", [])) == 0:
            # Bonus por completar nivel
            self.puntos += 500
            # Bonus de tiempo
            tiempo_bonus = 0
            if self.temporizador_activo and self.tiempo_restante > 0:
                tiempo_bonus = (self.tiempo_restante // 60) * 10
                self.puntos += tiempo_bonus
            
            if self.numero_nivel < 3:
                # Mostrar pantalla de transición con estadísticas
                # Reproducir sonido de victoria al completar el nivel
                try:
                    self._reproducir_sonido(self.sonido_victoria)
                except Exception:
                    pass
                self.pantalla_nivel_completado(tiempo_bonus)
                self.cargar_nivel(self.numero_nivel + 1)
                # Guardar progreso automáticamente al pasar de nivel
                if self.nombre_jugador:
                    self.guardar_partida()
            else:
                self.resultado = "ganaste"
                self.estado = "fin"
                # Reproducir sonido de victoria por completar todo el juego
                try:
                    self._reproducir_sonido(self.sonido_victoria)
                except Exception:
                    pass
                # Detener cronómetro y guardar como campeón (SOLO UNA VEZ)
                if self.nombre_jugador and not self.historial_guardado:
                    self.cronometro_activo = False  # Detener cronómetro
                    self.guardar_campeon(self.tiempo_total_segundos)
                    self.guardar_en_historial()
                    self.borrar_partida(self.nombre_jugador)  # Eliminar de partidas guardadas
                    self.historial_guardado = True  # Marcar como guardado
                    print(f"¡{self.nombre_jugador} completó el juego en {self.tiempo_total_segundos}s!")

    # -------------------------------------------------------
    # HEADER (HUD) - Formato Simple Horizontal
    # -------------------------------------------------------
    def dibujar_header(self, pantalla, ancho, alto, offset):
        alto_header = offset
        # Fondo del header: textura oscura si está disponible, de lo contrario un color oscuro uniforme
        if hasattr(self, 'hud_texture') and self.hud_texture:
            header_bg = pygame.transform.scale(self.hud_texture, (ancho, alto_header))
            pantalla.blit(header_bg, (0, 0))
        else:
            pygame.draw.rect(pantalla, (20, 20, 30), (0, 0, ancho, alto_header))
        # Línea inferior de separación
        pygame.draw.line(pantalla, (60, 60, 80), (0, alto_header - 1), (ancho, alto_header - 1), 2)
        y_center = alto_header // 2
        x_cursor = 10
        # Dibujar corazones según la vida
        if self.heart_img:
            h_w, h_h = self.heart_img.get_size()
            for i in range(int(self.jugador.vida_max)):
                if i < self.jugador.vida:
                    img = self.heart_img
                else:
                    img = self.heart_img.copy()
                    img.set_alpha(80)
                pantalla.blit(img, (x_cursor, y_center - h_h // 2))
                x_cursor += h_w + 5
        # Mostrar llaves si el temporizador no está activo
        if not self.temporizador_activo and hasattr(self.nivel_actual, 'llaves_requeridas'):
            llaves_recogidas = self.nivel_actual.llaves_requeridas - len(getattr(self.nivel_actual, 'llaves', []))
            llaves_totales = self.nivel_actual.llaves_requeridas
            x_cursor += 10
            if self.key_img:
                k_w, k_h = self.key_img.get_size()
                pantalla.blit(self.key_img, (x_cursor, y_center - k_h // 2))
                x_cursor += k_w + 5
            font_key_size = max(12, int(alto_header * 0.4))
            try:
                font_key = pygame.font.Font(self.font_path, self.ajustar_tamano(font_key_size))
            except Exception:
                font_key = pygame.font.Font(None, self.ajustar_tamano(font_key_size))
            txt = font_key.render(f"{llaves_recogidas}/{llaves_totales}", True, (240, 220, 100))
            pantalla.blit(txt, (x_cursor, y_center - txt.get_height() // 2))
            x_cursor += txt.get_width() + 5
        
        # Mostrar cronómetro (tiempo jugado)
        if self.cronometro_activo:
            x_cursor += 20  # Espacio adicional
            
            # Dibujar icono del cronómetro si está disponible
            if self.tiempo_img:
                t_w, t_h = self.tiempo_img.get_size()
                pantalla.blit(self.tiempo_img, (x_cursor, y_center - t_h // 2))
                x_cursor += t_w + 5
            
            # Dibujar el tiempo
            minutos = self.tiempo_total_segundos // 60
            segundos = self.tiempo_total_segundos % 60
            font_crono_size = max(12, int(alto_header * 0.35))
            try:
                font_crono = pygame.font.Font(self.font_path, self.ajustar_tamano(font_crono_size))
            except Exception:
                font_crono = pygame.font.Font(None, self.ajustar_tamano(font_crono_size))
            crono_text = f"{minutos:02d}:{segundos:02d}"
            txt_crono = font_crono.render(crono_text, True, (180, 180, 220))
            pantalla.blit(txt_crono, (x_cursor, y_center - txt_crono.get_height() // 2))
            x_cursor += txt_crono.get_width() + 5
        
        # Barra de energía y icono de rayo
        bar_width = int(ancho * 0.15)
        bar_height = int(alto_header * 0.3)
        bar_x = ancho - bar_width - 20
        bar_y = y_center - bar_height // 2
        if self.lightning_img:
            lw, lh = self.lightning_img.get_size()
            pantalla.blit(self.lightning_img, (bar_x - lw - 8, y_center - lh // 2))
        # Fondo de la barra
        pygame.draw.rect(pantalla, (30, 30, 45), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        # Proporción de energía
        propor_e = max(0.0, min(1.0, self.jugador.energia / self.jugador.energia_max))
        fill_w = int(bar_width * propor_e)
        if fill_w > 0:
            color_bar = getattr(self, 'energy_bar_color', (100, 160, 220))
            pygame.draw.rect(pantalla, color_bar, (bar_x, bar_y, fill_w, bar_height), border_radius=5)
        pygame.draw.rect(pantalla, (90, 90, 120), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=5)
        # Mostrar nivel o temporizador en el centro
        center_x = ancho // 2
        if self.temporizador_activo:
            tiempo_seg = max(0, int(self.tiempo_restante / 60))
            minutos = tiempo_seg // 60
            segundos = tiempo_seg % 60
            if self.tiempo_agotado or tiempo_seg == 0:
                color_t = (255, 50, 50)
                display = "¡ESCAPAR!"
            elif tiempo_seg <= 10:
                color_t = (255, 100, 100)
                display = f"{minutos}:{segundos:02d}"
            elif tiempo_seg <= 30:
                color_t = (255, 200, 0)
                display = f"{minutos}:{segundos:02d}"
            else:
                color_t = (100, 255, 100)
                display = f"{minutos}:{segundos:02d}"
            font_size_lvl = max(12, int(alto_header * 0.4))
            try:
                font_t = pygame.font.Font(self.font_path, self.ajustar_tamano(font_size_lvl))
            except Exception:
                font_t = pygame.font.Font(None, self.ajustar_tamano(font_size_lvl))
            surf = font_t.render(display, True, color_t)
            pantalla.blit(surf, (center_x - surf.get_width() // 2, y_center - surf.get_height() // 2))
        else:
            font_size_lvl = max(12, int(alto_header * 0.5))
            try:
                font_t = pygame.font.Font(self.font_path, font_size_lvl)
            except Exception:
                font_t = pygame.font.Font(None, font_size_lvl)
            surf = font_t.render(f"{self.numero_nivel}", True, (240, 220, 150))
            pantalla.blit(surf, (center_x - surf.get_width() // 2, y_center - surf.get_height() // 2))
        
        # Mostrar indicador de power-up activo si existe
        if self.powerup_activo and self.powerup_duracion > 0:
            tiempo_restante_seg = int(self.powerup_duracion / 60)
            
            # Colores y nombres según el tipo
            if self.powerup_activo == "vision_clara":
                color_principal = (255, 255, 150)
                color_fondo = (255, 255, 100)
                icono = "👁"
                nombre = "VISIÓN CLARA"
            elif self.powerup_activo == "disparo_doble":
                color_principal = (255, 120, 120)
                color_fondo = (255, 80, 80)
                icono = "⚡"
                nombre = "DISPARO x2"
            elif self.powerup_activo == "super_velocidad":
                color_principal = (150, 255, 150)
                color_fondo = (100, 255, 100)
                icono = "⚡"
                nombre = "VELOCIDAD"
            elif self.powerup_activo == "escudo":
                color_principal = (150, 220, 255)
                color_fondo = (100, 180, 255)
                icono = "🛡"
                nombre = "ESCUDO"
            
            # Posición a la derecha del nivel (o temporizador)
            powerup_x = center_x + 90
            powerup_width = 140
            powerup_height = int(alto_header * 0.7)
            
            # Fondo con gradiente simulado (múltiples capas)
            bg_rect = pygame.Rect(powerup_x - 5, y_center - powerup_height // 2, 
                                 powerup_width, powerup_height)
            
            # Capa de fondo oscura
            fondo_oscuro = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            fondo_oscuro.fill((20, 20, 30, 200))
            pantalla.blit(fondo_oscuro, (bg_rect.x, bg_rect.y))
            
            # Borde exterior grueso
            pygame.draw.rect(pantalla, (0, 0, 0), bg_rect, 3, border_radius=8)
            
            # Borde interior brillante con el color del power-up
            pygame.draw.rect(pantalla, color_fondo, bg_rect, 2, border_radius=8)
            
            # Barra de progreso del tiempo
            tiempo_max = self.powerup_duracion
            if self.powerup_activo == "vision_clara":
                tiempo_max = 5 * 60
            elif self.powerup_activo in ["disparo_doble", "escudo"]:
                tiempo_max = 30 * 60
            elif self.powerup_activo == "super_velocidad":
                tiempo_max = 10 * 60
            
            progreso = self.powerup_duracion / tiempo_max
            barra_width = int((bg_rect.width - 12) * progreso)
            barra_rect = pygame.Rect(bg_rect.x + 6, bg_rect.bottom - 10, barra_width, 4)
            
            # Fondo de la barra
            pygame.draw.rect(pantalla, (50, 50, 60), 
                           pygame.Rect(bg_rect.x + 6, bg_rect.bottom - 10, bg_rect.width - 12, 4),
                           border_radius=2)
            # Barra de progreso
            if barra_width > 0:
                pygame.draw.rect(pantalla, color_fondo, barra_rect, border_radius=2)
            
            # Nombre del power-up centrado con tamaño ajustado al contenido
            # Tamaño base más pequeño para textos largos
            if len(nombre) > 10:  # "VISIÓN CLARA" y "DISPARO x2" son más largos
                font_size_nombre = max(8, int(alto_header * 0.28))
            else:
                font_size_nombre = max(8, int(alto_header * 0.35))
            
            try:
                font_nombre = pygame.font.Font(self.font_path, self.ajustar_tamano(font_size_nombre))
            except Exception:
                font_nombre = pygame.font.Font(None, font_size_nombre)
            
            surf_nombre = font_nombre.render(nombre, True, color_principal)
            
            # Si el texto es muy ancho, reducir más el tamaño
            if surf_nombre.get_width() > (bg_rect.width - 10):
                font_size_nombre = max(6, int(alto_header * 0.25))
                try:
                    font_nombre = pygame.font.Font(self.font_path, self.ajustar_tamano(font_size_nombre))
                except Exception:
                    font_nombre = pygame.font.Font(None, font_size_nombre)
                surf_nombre = font_nombre.render(nombre, True, color_principal)
            
            texto_x = bg_rect.x + (bg_rect.width - surf_nombre.get_width()) // 2
            texto_y = y_center - surf_nombre.get_height() // 2 - 3
            pantalla.blit(surf_nombre, (texto_x, texto_y))
    
    def dibujar_corazon(self, pantalla, x, y, tamaño):
        """Dibuja un corazón bonito"""
        escala = tamaño / 20
        # Sombra
        puntos_sombra = [
            (x, y - 3 * escala + 2),
            (x - 8 * escala + 2, y - 8 * escala + 2),
            (x - 10 * escala + 2, y - 3 * escala + 2),
            (x, y + 10 * escala + 2),
            (x + 10 * escala + 2, y - 3 * escala + 2),
            (x + 8 * escala + 2, y - 8 * escala + 2)
        ]
        pygame.draw.polygon(pantalla, (100, 20, 20), puntos_sombra)
        
        # Corazón principal
        puntos = [
            (x, y - 3 * escala),
            (x - 8 * escala, y - 8 * escala),
            (x - 10 * escala, y - 3 * escala),
            (x, y + 10 * escala),
            (x + 10 * escala, y - 3 * escala),
            (x + 8 * escala, y - 8 * escala)
        ]
        pygame.draw.polygon(pantalla, (255, 70, 70), puntos)
        
        # Brillo
        puntos_brillo = [
            (x - 4 * escala, y - 5 * escala),
            (x - 6 * escala, y - 4 * escala),
            (x - 5 * escala, y - 2 * escala)
        ]
        pygame.draw.polygon(pantalla, (255, 150, 150), puntos_brillo)
    
    def dibujar_rayo(self, pantalla, x, y, tamaño):
        """Dibuja un rayo de energía"""
        escala = tamaño / 20
        # Sombra
        puntos_sombra = [
            (x - 4 * escala + 2, y - 10 * escala + 2),
            (x + 2 * escala + 2, y - 10 * escala + 2),
            (x - 3 * escala + 2, y - 2 * escala + 2),
            (x + 4 * escala + 2, y - 2 * escala + 2),
            (x - 2 * escala + 2, y + 10 * escala + 2),
            (x - 1 * escala + 2, y + 2 * escala + 2),
            (x - 6 * escala + 2, y + 2 * escala + 2)
        ]
        pygame.draw.polygon(pantalla, (30, 70, 100), puntos_sombra)
        
        # Rayo principal
        puntos = [
            (x - 4 * escala, y - 10 * escala),
            (x + 2 * escala, y - 10 * escala),
            (x - 3 * escala, y - 2 * escala),
            (x + 4 * escala, y - 2 * escala),
            (x - 2 * escala, y + 10 * escala),
            (x - 1 * escala, y + 2 * escala),
            (x - 6 * escala, y + 2 * escala)
        ]
        pygame.draw.polygon(pantalla, (100, 200, 255), puntos)
        
        # Brillos
        pygame.draw.polygon(pantalla, (200, 240, 255), [
            (x - 2 * escala, y - 8 * escala),
            (x, y - 8 * escala),
            (x - 1 * escala, y - 4 * escala)
        ])

    # -------------------------------------------------------
    # UTILIDADES DE DIBUJO
    # -------------------------------------------------------
    def dibujar_texto(self, texto, tam, color, x, y, centrado=True):
        """Renderiza un texto utilizando una fuente predefinida y lo dibuja en pantalla."""
        pantalla = pygame.display.get_surface()
        fuente = pygame.font.Font(None, tam)
        img = fuente.render(texto, True, color)
        rect = img.get_rect()
        rect.center = (x, y) if centrado else (x, y)
        pantalla.blit(img, rect)
        return rect

    def dibujar_barra(self, pantalla, x, y, ancho, alto, valor, valor_max, color_barra):
        propor = max(0.0, min(1.0, valor / valor_max))
        fondo = pygame.Rect(x, y, ancho, alto)
        barra = pygame.Rect(x, y, int(ancho * propor), alto)
        pygame.draw.rect(pantalla, (40, 40, 40), fondo, border_radius=4)
        pygame.draw.rect(pantalla, color_barra, barra, border_radius=4)
        pygame.draw.rect(pantalla, BLANCO, fondo, 1, border_radius=4)
    
    def dibujar_barra_mejorada(self, pantalla, x, y, ancho, alto, valor, valor_max, color_principal, color_oscuro):
        """Dibuja una barra mejorada con gradiente y efectos"""
        propor = max(0.0, min(1.0, valor / valor_max))
        
        # Fondo oscuro con borde
        fondo = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(pantalla, (25, 25, 35), fondo, border_radius=6)
        pygame.draw.rect(pantalla, (60, 60, 80), fondo, 2, border_radius=6)
        
        if propor > 0:
            # Barra de relleno
            ancho_barra = int(ancho * propor)
            barra = pygame.Rect(x, y, ancho_barra, alto)
            
            # Degradado vertical en la barra
            for i in range(alto):
                factor = i / alto
                r = int(color_principal[0] * (1 - factor * 0.3) + color_oscuro[0] * factor * 0.3)
                g = int(color_principal[1] * (1 - factor * 0.3) + color_oscuro[1] * factor * 0.3)
                b = int(color_principal[2] * (1 - factor * 0.3) + color_oscuro[2] * factor * 0.3)
                pygame.draw.line(pantalla, (r, g, b), (x, y + i), (x + ancho_barra, y + i))
            
            # Brillo superior
            brillo_alto = alto // 3
            brillo = pygame.Surface((ancho_barra, brillo_alto), pygame.SRCALPHA)
            brillo.fill((255, 255, 255, 40))
            pantalla.blit(brillo, (x, y))
            
            # Borde de la barra
            pygame.draw.rect(pantalla, color_oscuro, barra, 1, border_radius=6)
        
        # Borde exterior brillante
        pygame.draw.rect(pantalla, (150, 150, 180), fondo, 2, border_radius=6)
    
    def dibujar_mira(self, pantalla):
        """Dibuja una mira personalizada en lugar del cursor del mouse"""
        mx, my = pygame.mouse.get_pos()
        
        # Color de la mira (puede cambiar según el cooldown)
        if self.jugador.cooldown_disparo > 0:
            color_mira = (150, 150, 150)  # Gris cuando está en cooldown
        else:
            color_mira = (0, 255, 0)  # Verde cuando puede disparar
        
        # Tamaño de la mira
        tamaño = 15
        grosor = 2
        espacio = 5  # Espacio central
        
        # Líneas de la mira (cruz)
        # Línea horizontal izquierda
        pygame.draw.line(pantalla, color_mira, (mx - tamaño, my), (mx - espacio, my), grosor)
        # Línea horizontal derecha
        pygame.draw.line(pantalla, color_mira, (mx + espacio, my), (mx + tamaño, my), grosor)
        # Línea vertical arriba
        pygame.draw.line(pantalla, color_mira, (mx, my - tamaño), (mx, my - espacio), grosor)
        # Línea vertical abajo
        pygame.draw.line(pantalla, color_mira, (mx, my + espacio), (mx, my + tamaño), grosor)
        
        # Círculo central
        pygame.draw.circle(pantalla, color_mira, (mx, my), 2)
        
        # Círculo exterior (opcional, para mejor visibilidad)
        pygame.draw.circle(pantalla, color_mira, (mx, my), 8, 1)

    def dibujar_linterna_en_superficie(self, superficie):
        """
        Dibuja una linterna en forma de cono que sale de la mano del jugador.
        Solo ilumina al jugador y lo que está dentro del cono de luz.
        """
        # Si el power-up de visión clara está activo, no dibujar oscuridad
        if self.powerup_activo == "vision_clara":
            return
        
        ancho, alto = superficie.get_size()
        
        # Crear capa oscura (sombra negra semitransparente)
        sombra = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 250))  # Muy oscuro
        
        # Obtener posición del mouse para dirección de la linterna
        pantalla = pygame.display.get_surface()
        pantalla_ancho, pantalla_alto = pantalla.get_size()
        offset_header = int(pantalla_alto * self.altura_header)
        mx, my = pygame.mouse.get_pos()
        my_ajustado = my - offset_header
        
        # Actualizar ángulo de la linterna del jugador
        self.jugador.actualizar_angulo_linterna(mx, my_ajustado, self.camara)
        
        # Posición del centro del jugador en pantalla (origen del cono)
        cx, cy = self.camara.aplicar_pos(self.jugador.rect.centerx, self.jugador.rect.centery)
        
        # Radio de la linterna (alcance máximo)
        radio = int(self.jugador.vision * self.camara.zoom)
        if radio <= 0:
            superficie.blit(sombra, (0, 0))
            return
        
        # Ángulo del cono (semiancho en radianes)
        semiancho_cono = math.radians(40)  # 40 grados de ancho total (20 a cada lado)
        
        # Número de pasos para el gradiente del cono
        pasos = max(30, radio // 4)
        
        # Crear superficie de luz del cono
        luz_cono = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        
        # Dibujar el cono de luz con gradiente radial desde el centro del jugador
        for i in range(pasos, 0, -1):
            fraccion = i / pasos
            r_actual = int(radio * fraccion)
            
            if r_actual <= 0:
                continue
            
            # Calcular ancho del cono a esta distancia (se expande ligeramente con la distancia)
            ancho_actual = semiancho_cono * (0.4 + 0.6 * fraccion)
            
            # Puntos del cono a esta distancia
            angulo_izq = self.jugador.angulo_linterna - ancho_actual
            angulo_der = self.jugador.angulo_linterna + ancho_actual
            
            punto_izq = (
                cx + r_actual * math.cos(angulo_izq),
                cy + r_actual * math.sin(angulo_izq)
            )
            punto_der = (
                cx + r_actual * math.cos(angulo_der),
                cy + r_actual * math.sin(angulo_der)
            )
            
            # Alpha más intenso cerca del jugador, más tenue lejos
            alpha = int(255 * (fraccion ** 1.5))
            alpha = max(0, min(255, alpha))
            
            # Dibujar triángulo del cono desde el centro del jugador
            puntos_triangulo = [
                (int(cx), int(cy)),
                (int(punto_izq[0]), int(punto_izq[1])),
                (int(punto_der[0]), int(punto_der[1]))
            ]
            pygame.draw.polygon(luz_cono, (255, 255, 255, alpha), puntos_triangulo)
        
        # Asegurar que el jugador siempre esté iluminado (círculo alrededor del jugador)
        radio_jugador = max(20, int(35 * self.camara.zoom))
        for i in range(8, 0, -1):
            fraccion = i / 8
            r = int(radio_jugador * fraccion)
            alpha = int(220 * (fraccion ** 1.3))
            pygame.draw.circle(luz_cono, (255, 255, 255, alpha), (int(cx), int(cy)), r)
        
        # Aplicar la luz del cono a la sombra (resta la oscuridad donde hay luz)
        sombra.blit(luz_cono, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Aplicar la sombra final a la superficie del juego
        superficie.blit(sombra, (0, 0))

    # -------------------------------------------------------
    # MENÚ DE PAUSA
    # -------------------------------------------------------
    def menu_pausa(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()

        # Capa oscura
        overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pantalla.blit(overlay, (0, 0))

        # Título de pausa (misma fuente del título)
        title_size = int(alto * 0.075)
        try:
            font_title = pygame.font.Font(self.font_path_title, self.ajustar_tamano(title_size))
        except Exception:
            font_title = pygame.font.Font(None, self.ajustar_tamano(title_size))

        titulo = "PAUSA"
        base = font_title.render(titulo, True, (240, 235, 220))
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.14) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.14)))

        # Opciones
        opciones = ["Continuar", "Reiniciar Partida", "Opciones", "Salir al menu"]

        area_y_start = int(alto * 0.38)
        area_y_end   = int(alto * 0.72)
        area_height  = area_y_end - area_y_start

        try:
            menu_size = max(16, int(area_height / 6))
            font_menu = pygame.font.Font(self.font_path, self.ajustar_tamano(menu_size))
        except Exception:
            menu_size = max(16, int(area_height / 6))
            font_menu = pygame.font.Font(None, self.ajustar_tamano(menu_size))

        # Crear superficies con color base
        surfaces = [font_menu.render(txt, True, (235, 225, 210)) for txt in opciones]
        heights  = [s.get_height() for s in surfaces]
        spacing  = int(area_height * 0.12)
        total_h  = sum(heights) + spacing * (len(opciones) - 1)
        y_current = area_y_start + (area_height - total_h) // 2

        mouse_pos = pygame.mouse.get_pos()
        self._pause_hitboxes = []

        for i, txt in enumerate(opciones):
            x = ancho // 2 - surfaces[i].get_width() // 2
            y = y_current

            rect_hit = pygame.Rect(x - 18, y - 8, surfaces[i].get_width() + 36, surfaces[i].get_height() + 16)
            self._pause_hitboxes.append((rect_hit, i))

            hovering = rect_hit.collidepoint(mouse_pos)
            
            # Renderizar texto con color según hover
            if hovering:
                # Color resaltado cuando el mouse está encima
                surf = font_menu.render(txt, True, (100, 255, 100))  # Verde brillante
                overlay_btn = pygame.Surface((rect_hit.width, rect_hit.height), pygame.SRCALPHA)
                overlay_btn.fill((0, 0, 0, 90))
                pantalla.blit(overlay_btn, rect_hit.topleft)
                pygame.draw.rect(pantalla, (100, 255, 100), rect_hit, 1, border_radius=8)
            else:
                # Color normal
                surf = surfaces[i]

            pantalla.blit(surf, (x, y))
            y_current += surf.get_height() + spacing

        # Pie
        hint_size = int(alto * 0.028)
        self.dibujar_texto("ESC para continuar", hint_size, (190, 190, 200), ancho // 2, int(alto * 0.88))
        
    def controles(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()

        # Fondo (como el menú)
        fondo_path = os.path.join(self._dir, 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))

        # Título con la fuente de título
        title_size = int(alto * 0.085)
        try:
            font_title = pygame.font.Font(self.font_path_title, self.ajustar_tamano(title_size))
        except Exception:
            font_title = pygame.font.Font(None, self.ajustar_tamano(title_size))

        titulo = "Controles Basicos"
        base = font_title.render(titulo, True, (240, 235, 220))
        # Sombra/contorno sutil
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.18) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.18)))

        # Texto de controles (misma fuente del menú)
        try:
            font_body = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.035)))
        except Exception:
            font_body = pygame.font.Font(None, int(alto * 0.035))

        lineas = [
            "Movimiento: W / A / S / D",
            "Disparo: Click Izquierdo",
            "Activar Power-up cercano: E",
            "Pausa: ESC o P",
        ]
        y = int(alto * 0.34)
        for texto in lineas:
            surf = font_body.render(texto, True, (235, 225, 210))
            pantalla.blit(surf, (ancho//2 - surf.get_width()//2, y))
            y += int(surf.get_height() * 1.4)

        # Botón “Continuar” (mismo estilo de botones del menú)
        try:
            font_btn = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
        except Exception:
            font_btn = pygame.font.Font(None, int(alto * 0.04))

        btn_surf = font_btn.render("Continuar", True, (235, 225, 210))
        btn_w, btn_h = btn_surf.get_width() + 36, btn_surf.get_height() + 16
        btn_x = ancho//2 - btn_w//2
        btn_y = int(alto * 0.78)

        self._controles_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        hovering = self._controles_btn_rect.collidepoint(pygame.mouse.get_pos())
        
        # Renderizar texto con color según hover
        if hovering:
            btn_surf = font_btn.render("Continuar", True, (255, 215, 0))  # Dorado brillante
            overlay = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            pantalla.blit(overlay, (btn_x, btn_y))
            pygame.draw.rect(pantalla, (255, 215, 0), self._controles_btn_rect, 1, border_radius=8)

        # Texto del botón
        pantalla.blit(btn_surf, (ancho//2 - btn_surf.get_width()//2, btn_y + (btn_h - btn_surf.get_height())//2))

        # Pie: solo ESC para salir al menú
        hint_size = int(alto * 0.03)
        self.dibujar_texto("ESC para volver al menu", hint_size, (190, 190, 200), ancho // 2, int(alto * 0.92))

    # -------------------------------------------------------
    # TRANSICIÓN Y FINAL
    # -------------------------------------------------------
    def pantalla_nivel_completado(self, tiempo_bonus):
        """Muestra estadísticas al completar un nivel"""
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        reloj = pygame.time.Clock()
        
        # Nombres de niveles
        nombres_niveles = {
            1: "LAS CATACUMBAS",
            2: "LA ESPIRAL DESCENDENTE",
            3: "EL ABISMO PROFUNDO"
        }
        
        esperando = True
        tiempo_minimo = 180  # Mínimo 3 segundos
        contador = 0
        
        while esperando:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    return
                if e.type == pygame.KEYDOWN and contador > tiempo_minimo:
                    if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                        esperando = False
            
            pantalla.fill((5, 5, 10))
            
            # Título
            self.dibujar_texto(f"¡NIVEL {self.numero_nivel} COMPLETADO!", 
                              int(alto * 0.08), VERDE, ancho // 2, alto * 0.2)
            self.dibujar_texto(nombres_niveles[self.numero_nivel], 
                              int(alto * 0.05), AMARILLO, ancho // 2, alto * 0.28)
            
            # Estadísticas
            y_stats = alto * 0.42
            self.dibujar_texto("ESTADÍSTICAS", int(alto * 0.04), BLANCO, 
                              ancho // 2, y_stats)
            
            self.dibujar_texto(f"Puntos base: +500", int(alto * 0.035), BLANCO, 
                              ancho // 2, y_stats + alto * 0.08)
            
            if tiempo_bonus > 0:
                self.dibujar_texto(f"Bonus de tiempo: +{tiempo_bonus}", 
                                  int(alto * 0.035), AMARILLO, 
                                  ancho // 2, y_stats + alto * 0.13)
            
            self.dibujar_texto(f"Puntos totales: {self.puntos}", 
                              int(alto * 0.045), VERDE, 
                              ancho // 2, y_stats + alto * 0.2)
            
            # Mensaje para continuar
            if contador > tiempo_minimo:
                alpha = int(128 + 127 * math.sin(contador / 10))
                color_parpadeante = (255, 255, 255, alpha)
                self.dibujar_texto("Presiona ENTER para continuar", 
                                  int(alto * 0.03), color_parpadeante[:3], 
                                  ancho // 2, alto * 0.75)
            
            # Actualizar música de fondo según el estado actual (menu / jugando / otros)
            try:
                self.actualizar_musica_por_estado()
            except Exception:
                pass

            # Actualizar música de fondo según el estado actual (menu / jugando / otros)
            try:
                self.actualizar_musica_por_estado()
            except Exception:
                pass

            pygame.display.flip()
            reloj.tick(60)
            contador += 1
    
    def transicion_texto(self, texto, subtexto=None):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        for i in range(60):
            overlay = pygame.Surface((ancho, alto))
            overlay.fill((0, 0, 0))
            alpha = int(255 * (i / 60))
            overlay.set_alpha(alpha)
            pantalla.blit(overlay, (0, 0))
            self.dibujar_texto(texto, 50, BLANCO, ancho // 2, alto // 2)
            if subtexto:
                self.dibujar_texto(subtexto, 35, AMARILLO, ancho // 2, alto // 2 + 60)
            pygame.display.flip()
            pygame.time.delay(16)

    def pantalla_final(self):
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        # Fondo base: preferir la textura del menú para coherencia visual
        menu_bg_path = os.path.join(self._dir, 'images', 'menu_background.png')
        win_path = os.path.join(self._dir, 'images', 'pantalla_ganar.png')
        lose_path = os.path.join(self._dir, 'images', 'pantalla_perder.png')

        # Cargar base: si existe menu background, usarlo y luego aplicar overlay; si no, usar las imágenes específicas
        if os.path.isfile(menu_bg_path):
            try:
                bg = pygame.image.load(menu_bg_path).convert()
                bg = pygame.transform.smoothscale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((12, 12, 18))
        else:
            # fallback: usar imagen propia de resultado si existe
            if self.resultado == 'perdiste' and os.path.isfile(lose_path):
                try:
                    bg = pygame.image.load(lose_path).convert()
                    bg = pygame.transform.smoothscale(bg, (ancho, alto))
                    pantalla.blit(bg, (0, 0))
                except Exception:
                    pantalla.fill((8, 8, 12))
            elif self.resultado == 'ganaste' and os.path.isfile(win_path):
                try:
                    bg = pygame.image.load(win_path).convert()
                    bg = pygame.transform.smoothscale(bg, (ancho, alto))
                    pantalla.blit(bg, (0, 0))
                except Exception:
                    pantalla.fill((6, 12, 6))
            else:
                pantalla.fill((10, 10, 18))

        # Paleta coherente con el menú y HUD
        base_text = (240, 235, 220)   # color principal de títulos/menu
        accent_gold = (255, 215, 0)   # dorado usado en menú (hover/ácen)
        success_green = (100, 255, 140)
        fail_red = (220, 90, 90)

        # Tonalidad por nivel (suaves, para no chocar con el fondo)
        if self.numero_nivel == 1:
            overlay_color = (24, 10, 44, 180)
        elif self.numero_nivel == 2:
            overlay_color = (44, 10, 10, 190)
        elif self.numero_nivel == 3:
            overlay_color = (6, 12, 44, 190)
        else:
            overlay_color = (6, 6, 6, 160)

        overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        overlay.fill(overlay_color)
        pantalla.blit(overlay, (0, 0))

        # Título
        titulo = "¡Victoria!" if self.resultado == "ganaste" else "¡Derrota!"
        # Color del título: usar base_text con un matiz según resultado
        color = success_green if self.resultado == "ganaste" else fail_red

        # Fuente para título: preferir la ruta configurada (outline si está presente)
        try:
            font_title = pygame.font.Font(self.font_path_title, self.ajustar_tamano(int(alto * 0.11)))
        except Exception:
            font_title = pygame.font.Font(None, self.ajustar_tamano(int(alto * 0.11)))

        # Dibujar título con halo glow (varias capas con alpha)
        title_surf = font_title.render(titulo, True, color)
        w_title = title_surf.get_width()
        x_title = ancho // 2 - w_title // 2
        y_title = int(alto * 0.18)

        # Glow: capas difusas
        for i, a in enumerate((80, 60, 40, 20), start=1):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            sombra.set_alpha(a)
            pantalla.blit(sombra, (x_title - i*2, y_title - i*2))
            pantalla.blit(sombra, (x_title + i*2, y_title - i*2))
        pantalla.blit(title_surf, (x_title, y_title))

        # Frases finales
        frases_perder = [
            "Fuiste vencido esta vez.",
            "Regresa con mas determinacion.",
            "El laberinto te vencio hoy.",
            "La proxima vez sera."
        ]
        frases_ganar = [
            "Eres imparable!"
        ]

        frases_perder_por_nivel = {
            1: ["Las catacumbas te enseñaron una lección amarga."],
            2: ["La espiral desafió tu temple, aprende sus ritmos."],
            3: ["El abismo exige sacrificios — hoy no fue tu día."],
        }
        frases_ganar_por_puntos = []
        if self.puntos >= 3000:
            frases_ganar_por_puntos.append("Haz brillado en la oscuridad. Puntos sobresalientes.")
        elif self.puntos >= 1500:
            frases_ganar_por_puntos.append("Buen trabajo — tu coraje fue recompensado.")

        if not hasattr(self, 'frase_final') or self.frase_final is None:
            if self.resultado == 'perdiste':
                candidatos = list(frases_perder)
                candidatos += frases_perder_por_nivel.get(self.numero_nivel, [])
                if self.puntos >= 2000:
                    candidatos.append("Ibas bien, pero las sombras ganaron al final.")
                self.frase_final = random.choice(candidatos)
            else:
                # Ganaste: usar la frase fija solicitada
                self.frase_final = "¡Eres imparable!"

        # Fuente de frase: usar la fuente de cuerpo (filled) para mejor legibilidad
        try:
            font_phrase = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.06)))
        except Exception:
            font_phrase = pygame.font.Font(None, self.ajustar_tamano(int(alto * 0.06)))

        # Render con contorno/halo para verse "increíble"
        frase = self.frase_final
        # Draw big outer glow
        for ox, oy, alpha in [(-4,0,40),(4,0,40),(0,-4,40),(0,4,40),(-2,-2,70),(2,2,70)]:
            glow = font_phrase.render(frase, True, (10,10,10))
            glow.set_alpha(alpha)
            pantalla.blit(glow, (ancho//2 - glow.get_width()//2 + ox, int(alto*0.32) + oy))

        # Main colored phrase: usar dorado/acento del menú y base de texto
        frase_surf = font_phrase.render(frase, True, accent_gold)
        pantalla.blit(frase_surf, (ancho//2 - frase_surf.get_width()//2, int(alto*0.32)))

        # Panel de estadísticas: intentar llenar con textura del menú para coherencia
        panel_w = int(ancho * 0.66)
        panel_h = int(alto * 0.26)
        panel_x = ancho // 2 - panel_w // 2
        panel_y = int(alto * 0.46)

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        # Si existe textura de menu, usarla para rellenar el panel (tile una porción)
        if os.path.isfile(menu_bg_path):
            try:
                tex = pygame.image.load(menu_bg_path).convert_alpha()
                tex = pygame.transform.smoothscale(tex, (max(64, panel_w//4), max(64, panel_h//4)))
                # Tile the texture
                for px_t in range(0, panel_w, tex.get_width()):
                    for py_t in range(0, panel_h, tex.get_height()):
                        panel.blit(tex, (px_t, py_t))
                # Overlay dark tint for readability
                tint = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                tint.fill((6, 6, 10, 200))
                panel.blit(tint, (0,0))
            except Exception:
                panel.fill((10,10,12,200))
        else:
            panel.fill((10, 10, 12, 200))

        # Borde decorativo
        pygame.draw.rect(panel, (150, 130, 90, 180), panel.get_rect(), 2, border_radius=10)
        pantalla.blit(panel, (panel_x, panel_y))

        # Estadísticas sobre el panel (usar paleta coherente)
        self.dibujar_texto(f"Puntuación Final: {self.puntos}", int(alto * 0.045), accent_gold, ancho // 2, panel_y + int(panel_h * 0.22))
        self.dibujar_texto(f"Enemigos Derrotados: {self.enemigos_derrotados}", int(alto * 0.035), base_text, ancho // 2, panel_y + int(panel_h * 0.48))

        # Instrucciones
        self.dibujar_texto("ENTER para volver al menú", int(alto * 0.033), (190, 190, 200), ancho // 2, panel_y + panel_h + int(alto * 0.03))

        # Guardado del resultado (único)
        if not getattr(self, '_guardado', False):
            self.guardar_resultado()
            self._guardado = True

        # Fade-in (simple): ejecutar la primera vez que entramos a pantalla final
        if not hasattr(self, '_pantalla_final_frame') or self._pantalla_final_frame is None:
            self._pantalla_final_frame = 0
        frame = self._pantalla_final_frame
        fade_frames = getattr(self, '_pantalla_final_fade_frames', 30)
        if frame < fade_frames:
            alpha = int(255 * (1 - frame / max(1, fade_frames)))
            fade_surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, alpha))
            pantalla.blit(fade_surf, (0, 0))
            self._pantalla_final_frame += 1

    def pantalla_puntuacion(self):
        """Pantalla de puntuaciones - Muestra ranking de jugadores con dos pestañas"""
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        
        # Fondo similar al menú
        fondo_path = os.path.join(self._dir, 'images', 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))
        
        # Título
        title_size = int(alto * 0.085)
        try:
            font_title = pygame.font.Font(self.font_path_title, title_size)
        except Exception:
            font_title = pygame.font.Font(None, title_size)

        titulo = "Puntuaciones"

        # Algunos diseños pixel-outline no incluyen tildes ni signos invertidos (¡ ¿).
        # Si el título contiene caracteres no-ASCII, usar la fuente de cuerpo (filled)
        # que suele tener mejor soporte de glyphs acentuados.
        if any(ord(c) > 127 or c in ('¡', '¿') for c in titulo):
            try:
                font_title = pygame.font.Font(self.font_path, self.ajustar_tamano(title_size))
            except Exception:
                font_title = pygame.font.Font(None, title_size)
        base = font_title.render(titulo, True, (240, 235, 220))
        # Subir ligeramente el título para dar más espacio al panel central
        title_y = int(alto * 0.12)
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, title_y + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, title_y))
        
        # Pestañas
        try:
            font_tab = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
        except Exception:
            font_tab = pygame.font.Font(None, int(alto * 0.04))
        
        tab_y = int(alto * 0.30)
        tab1_text = "Campeones"
        tab2_text = "Historico"
        
        # Calcular posiciones de pestañas
        tab1_surf = font_tab.render(tab1_text, True, (255, 255, 255))
        tab2_surf = font_tab.render(tab2_text, True, (255, 255, 255))
        
        tab1_x = ancho // 2 - tab1_surf.get_width() - 30
        tab2_x = ancho // 2 + 30
        
        # Almacenar hitboxes para las pestañas
        self._tab_campeones_rect = pygame.Rect(tab1_x - 10, tab_y - 5, tab1_surf.get_width() + 20, tab1_surf.get_height() + 10)
        self._tab_historico_rect = pygame.Rect(tab2_x - 10, tab_y - 5, tab2_surf.get_width() + 20, tab2_surf.get_height() + 10)
        
        # Dibujar pestañas
        mouse_pos = pygame.mouse.get_pos()
        
        # Pestaña Campeones
        if self._tab_puntuacion == "campeones":
            pygame.draw.rect(pantalla, (255, 215, 0), self._tab_campeones_rect, 0, border_radius=5)
            tab1_color = (0, 0, 0)
        elif self._tab_campeones_rect.collidepoint(mouse_pos):
            pygame.draw.rect(pantalla, (100, 100, 120), self._tab_campeones_rect, 0, border_radius=5)
            tab1_color = (255, 255, 255)
        else:
            pygame.draw.rect(pantalla, (40, 40, 50), self._tab_campeones_rect, 0, border_radius=5)
            tab1_color = (200, 200, 200)
        
        tab1_render = font_tab.render(tab1_text, True, tab1_color)
        pantalla.blit(tab1_render, (tab1_x, tab_y))
        
        # Pestaña Histórico
        if self._tab_puntuacion == "historico":
            pygame.draw.rect(pantalla, (255, 215, 0), self._tab_historico_rect, 0, border_radius=5)
            tab2_color = (0, 0, 0)
        elif self._tab_historico_rect.collidepoint(mouse_pos):
            pygame.draw.rect(pantalla, (100, 100, 120), self._tab_historico_rect, 0, border_radius=5)
            tab2_color = (255, 255, 255)
        else:
            pygame.draw.rect(pantalla, (40, 40, 50), self._tab_historico_rect, 0, border_radius=5)
            tab2_color = (200, 200, 200)
        
        tab2_render = font_tab.render(tab2_text, True, tab2_color)
        pantalla.blit(tab2_render, (tab2_x, tab_y))
        
        # Contenido según la pestaña activa
        y_inicial = alto * 0.40
        
        if self._tab_puntuacion == "campeones":
            # Mostrar campeones (completaron el juego)
            campeones = self.obtener_campeones()
            
            if not campeones:
                self.dibujar_texto("No hay campeones aun", int(alto * 0.04), (190, 190, 200), ancho // 2, alto * 0.52)
                self.dibujar_texto("Se el primero en completar el juego!", int(alto * 0.03), (150, 150, 160), ancho // 2, alto * 0.60)
            else:
                # Encabezados
                self.dibujar_texto("Pos", int(alto * 0.035), (255, 215, 0), ancho * 0.18, y_inicial)
                self.dibujar_texto("Nombre", int(alto * 0.035), (255, 215, 0), ancho * 0.38, y_inicial)
                self.dibujar_texto("Puntos", int(alto * 0.035), (255, 215, 0), ancho * 0.60, y_inicial)
                self.dibujar_texto("Tiempo", int(alto * 0.035), (255, 215, 0), ancho * 0.82, y_inicial)
                
                # Mostrar hasta 8 campeones
                max_mostrar = min(8, len(campeones))
                y_posicion = y_inicial + alto * 0.07
                
                for i in range(max_mostrar):
                    campeon = campeones[i]
                    
                    # Color especial para podio
                    if i == 0:
                        color = (255, 215, 0)  # Oro
                    elif i == 1:
                        color = (192, 192, 192)  # Plata
                    elif i == 2:
                        color = (205, 127, 50)  # Bronce
                    else:
                        color = (200, 200, 210)
                    
                    # Posición
                    self.dibujar_texto(f"{i+1}°", int(alto * 0.03), color, ancho * 0.18, y_posicion)
                    
                    # Nombre
                    nombre_mostrar = campeon['nombre'] if len(campeon['nombre']) <= 12 else campeon['nombre'][:9] + "..."
                    self.dibujar_texto(nombre_mostrar, int(alto * 0.03), color, ancho * 0.38, y_posicion)
                    
                    # Puntos
                    self.dibujar_texto(str(campeon['puntos']), int(alto * 0.03), color, ancho * 0.60, y_posicion)
                    
                    # Tiempo (formatear como MM:SS)
                    minutos = campeon['tiempo'] // 60
                    segundos = campeon['tiempo'] % 60
                    tiempo_str = f"{minutos:02d}:{segundos:02d}"
                    self.dibujar_texto(tiempo_str, int(alto * 0.03), color, ancho * 0.82, y_posicion)
                    
                    y_posicion += alto * 0.055
        
        else:  # historico
            # Mostrar histórico de todas las partidas
            historial = self.obtener_historial()
            
            if not historial:
                self.dibujar_texto("No hay historial de partidas", int(alto * 0.04), (190, 190, 200), ancho // 2, alto * 0.52)
                self.dibujar_texto("¡Juega para aparecer aquí!", int(alto * 0.03), (150, 150, 160), ancho // 2, alto * 0.60)
            else:
                # Encabezados
                self.dibujar_texto("Nombre", int(alto * 0.032), (255, 215, 0), ancho * 0.22, y_inicial)
                self.dibujar_texto("Nivel", int(alto * 0.032), (255, 215, 0), ancho * 0.42, y_inicial)
                self.dibujar_texto("Puntos", int(alto * 0.032), (255, 215, 0), ancho * 0.58, y_inicial)
                self.dibujar_texto("Tiempo", int(alto * 0.032), (255, 215, 0), ancho * 0.73, y_inicial)
                self.dibujar_texto("Enemigos", int(alto * 0.032), (255, 215, 0), ancho * 0.88, y_inicial)
                
                # Mostrar hasta 8 partidas
                max_mostrar = min(8, len(historial))
                y_posicion = y_inicial + alto * 0.065
                
                for i in range(max_mostrar):
                    partida = historial[i]
                    color = (200, 200, 210)
                    
                    # Nombre
                    nombre_mostrar = partida['nombre'] if len(partida['nombre']) <= 10 else partida['nombre'][:7] + "..."
                    self.dibujar_texto(nombre_mostrar, int(alto * 0.028), color, ancho * 0.22, y_posicion)
                    
                    # Nivel
                    self.dibujar_texto(str(partida['nivel']), int(alto * 0.028), color, ancho * 0.42, y_posicion)
                    
                    # Puntos
                    self.dibujar_texto(str(partida['puntos']), int(alto * 0.028), color, ancho * 0.58, y_posicion)
                    
                    # Tiempo (formatear como MM:SS)
                    minutos = partida['tiempo'] // 60
                    segundos = partida['tiempo'] % 60
                    tiempo_str = f"{minutos:02d}:{segundos:02d}"
                    self.dibujar_texto(tiempo_str, int(alto * 0.028), color, ancho * 0.73, y_posicion)
                    
                    # Enemigos
                    self.dibujar_texto(str(partida['enemigos']), int(alto * 0.028), color, ancho * 0.88, y_posicion)
                    
                    y_posicion += alto * 0.055
        
        # Instrucciones
        self.dibujar_texto("Click en las pestañas para cambiar de vista", int(alto * 0.025), (150, 150, 160), ancho // 2, int(alto * 0.85))
        self.dibujar_texto("ESC para volver al menú", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.90))

    def pantalla_cargar_partida(self):
        """Pantalla para cargar partidas guardadas"""
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        
        # Fondo similar al menú
        fondo_path = os.path.join(self._dir, 'images', 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))
        
        # Título
        title_size = int(alto * 0.085)
        try:
            font_title = pygame.font.Font(self.font_path_title, title_size)
        except Exception:
            font_title = pygame.font.Font(None, title_size)

        titulo = "Cargar Partida"
        base = font_title.render(titulo, True, (240, 235, 220))
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.18) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.18)))
        
        # Obtener partidas guardadas
        partidas = self.obtener_partidas_guardadas()
        
        if not partidas:
            # No hay partidas guardadas
            self.dibujar_texto("No hay partidas guardadas", int(alto * 0.045), (235, 225, 210), ancho // 2, alto * 0.5)
            self.dibujar_texto("ESC para volver", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.90))
        else:
            # Mostrar lista de partidas
            try:
                font_menu = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
            except Exception:
                font_menu = pygame.font.Font(None, int(alto * 0.04))
            
            area_y_start = int(alto * 0.35)
            spacing = int(alto * 0.08)
            
            mouse_pos = pygame.mouse.get_pos()
            self._cargar_hitboxes = []
            self._borrar_hitboxes = []  # Hitboxes para los botones de borrar
            
            try:
                font_delete = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.03)))
            except Exception:
                font_delete = pygame.font.Font(None, int(alto * 0.03))
            
            for i, (nombre, datos) in enumerate(partidas.items()):
                y = area_y_start + i * spacing
                
                # Información de la partida
                texto = f"{nombre} - Nivel {datos['nivel']} - {datos['puntos']} pts"
                surf_normal = font_menu.render(texto, True, (235, 225, 210))
                
                # Calcular posición centrada pero dejando espacio para el botón borrar
                total_width = surf_normal.get_width() + int(ancho * 0.12)  # Espacio para botón
                x = ancho // 2 - total_width // 2
                
                rect_hit = pygame.Rect(x, y - 8, surf_normal.get_width() + 20, surf_normal.get_height() + 16)
                self._cargar_hitboxes.append((rect_hit, nombre))
                
                hovering = rect_hit.collidepoint(mouse_pos)
                
                # Renderizar texto con color según hover
                if hovering:
                    surf = font_menu.render(texto, True, (100, 255, 100))
                    overlay = pygame.Surface((rect_hit.width, rect_hit.height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 90))
                    pantalla.blit(overlay, rect_hit.topleft)
                    pygame.draw.rect(pantalla, (100, 255, 100), rect_hit, 1, border_radius=8)
                else:
                    surf = surf_normal
                
                pantalla.blit(surf, (x, y))
                
                # Botón de borrar - medir el ancho del texto y usar padding en el rect
                delete_text = "[X] Borrar"
                delete_x = x + surf_normal.get_width() + int(ancho * 0.05)

                # Renderizar una vez para medir tamaño (color no relevante para la medida)
                try:
                    delete_surf_normal = font_delete.render(delete_text, True, (200, 150, 150))
                except Exception:
                    delete_surf_normal = pygame.font.Font(None, int(alto * 0.03)).render(delete_text, True, (200, 150, 150))

                pad_x = 12
                pad_y = 8
                delete_w = delete_surf_normal.get_width()
                delete_h = delete_surf_normal.get_height()

                # Ajustar rect para que cubra completamente el texto con padding
                delete_rect = pygame.Rect(delete_x - pad_x, y - pad_y, delete_w + pad_x * 2, delete_h + pad_y * 2)
                self._borrar_hitboxes.append((delete_rect, nombre))

                hovering_delete = delete_rect.collidepoint(mouse_pos)

                if hovering_delete:
                    delete_surf = font_delete.render(delete_text, True, (255, 100, 100))
                    overlay = pygame.Surface((delete_rect.width, delete_rect.height), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 90))
                    pantalla.blit(overlay, delete_rect.topleft)
                    pygame.draw.rect(pantalla, (255, 100, 100), delete_rect, 1, border_radius=8)
                else:
                    delete_surf = delete_surf_normal

                # Blit del texto (ajustar vertical para centrar dentro del rect)
                pantalla.blit(delete_surf, (delete_rect.x + pad_x, delete_rect.y + pad_y))
            
            # Instrucciones
            self.dibujar_texto("Click en una partida para cargarla", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.85))
            self.dibujar_texto("ESC para volver", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.90))

    def pantalla_registro(self):
        """Pantalla para ingresar el nombre del jugador"""
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        
        # Fondo similar al menú
        fondo_path = os.path.join(self._dir, 'images', 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))
        
        # Título
        title_size = int(alto * 0.085)
        try:
            font_title = pygame.font.Font(self.font_path_title, title_size)
        except Exception:
            font_title = pygame.font.Font(None, title_size)

        titulo = "Nueva Partida"
        base = font_title.render(titulo, True, (240, 235, 220))
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.18) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.18)))
        
        # Instrucción
        try:
            font_body = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
        except Exception:
            font_body = pygame.font.Font(None, int(alto * 0.04))
        
        self.dibujar_texto("Ingresa tu nombre:", int(alto * 0.045), (235, 225, 210), ancho // 2, alto * 0.38)
        
        # Campo de texto
        input_width = int(ancho * 0.5)
        input_height = int(alto * 0.08)
        input_x = ancho // 2 - input_width // 2
        input_y = int(alto * 0.48)
        
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        
        # Fondo del campo de texto
        pygame.draw.rect(pantalla, (40, 40, 50), input_rect, border_radius=8)
        pygame.draw.rect(pantalla, (255, 215, 0), input_rect, 2, border_radius=8)
        
        # Texto ingresado
        try:
            font_input = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.045)))
        except Exception:
            font_input = pygame.font.Font(None, int(alto * 0.045))
        
        texto_display = self.nombre_jugador if self.nombre_jugador else ""
        
        # Cursor parpadeante
        tiempo = pygame.time.get_ticks()
        mostrar_cursor = (tiempo // 500) % 2 == 0
        if mostrar_cursor and self.input_activo:
            texto_display += "|"
        
        texto_surf = font_input.render(texto_display, True, (255, 255, 255))
        pantalla.blit(texto_surf, (input_x + 20, input_y + (input_height - texto_surf.get_height()) // 2))
        
        # Botón Continuar (solo si hay texto)
        if len(self.nombre_jugador) > 0:
            try:
                font_btn = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
            except Exception:
                font_btn = pygame.font.Font(None, int(alto * 0.04))

            btn_surf_normal = font_btn.render("Continuar", True, (235, 225, 210))
            btn_w, btn_h = btn_surf_normal.get_width() + 36, btn_surf_normal.get_height() + 16
            btn_x = ancho//2 - btn_w//2
            btn_y = int(alto * 0.68)

            self._registro_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

            hovering = self._registro_btn_rect.collidepoint(pygame.mouse.get_pos())
            
            # Renderizar texto con color según hover
            if hovering:
                btn_surf = font_btn.render("Continuar", True, (255, 215, 0))
                overlay = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 90))
                pantalla.blit(overlay, (btn_x, btn_y))
                pygame.draw.rect(pantalla, (255, 215, 0), self._registro_btn_rect, 1, border_radius=8)
            else:
                btn_surf = btn_surf_normal

            pantalla.blit(btn_surf, (ancho//2 - btn_surf.get_width()//2, btn_y + (btn_h - btn_surf.get_height())//2))
        
        # Instrucciones
        self.dibujar_texto("Escribe tu nombre y presiona ENTER", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.82))
        self.dibujar_texto("ESC para cancelar", int(alto * 0.03), (190, 190, 200), ancho // 2, int(alto * 0.90))

    def pantalla_configuracion(self):
        """Pantalla de configuración con opciones de pantalla completa y volumen"""
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        
        # Fondo similar al menú
        fondo_path = os.path.join(self._dir, 'images', 'menu_background.png')
        if os.path.isfile(fondo_path):
            try:
                bg = pygame.image.load(fondo_path).convert()
                bg = pygame.transform.scale(bg, (ancho, alto))
                pantalla.blit(bg, (0, 0))
            except Exception:
                pantalla.fill((10, 10, 20))
        else:
            pantalla.fill((10, 10, 20))
        
        # Título
        title_size = int(alto * 0.085)
        try:
            font_title = pygame.font.Font(self.font_path_title, title_size)
        except Exception:
            font_title = pygame.font.Font(None, title_size)

        titulo = "Configuracion"

        # Algunos pixel-outline no incluyen tildes o signos invertidos; si el título
        # contiene caracteres no-ASCII, usar la fuente de cuerpo (filled) para mejor soporte.
        if any(ord(c) > 127 or c in ('¡', '¿') for c in titulo):
            try:
                font_title = pygame.font.Font(self.font_path, self.ajustar_tamano(title_size))
            except Exception:
                font_title = pygame.font.Font(None, title_size)
        base = font_title.render(titulo, True, (240, 235, 220))
        for dx, dy in ((-2,0),(2,0),(0,-2),(0,2)):
            sombra = font_title.render(titulo, True, (20, 20, 25))
            pantalla.blit(sombra, (ancho//2 - base.get_width()//2 + dx, int(alto*0.18) + dy))
        pantalla.blit(base, (ancho//2 - base.get_width()//2, int(alto*0.18)))
        
        # Fuentes
        try:
            font_body = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.04)))
            font_small = pygame.font.Font(self.font_path, self.ajustar_tamano(int(alto * 0.032)))
        except Exception:
            font_body = pygame.font.Font(None, int(alto * 0.04))
            font_small = pygame.font.Font(None, int(alto * 0.032))
        
        # ===== MODO DE PANTALLA =====
        y_offset = int(alto * 0.30)
        self.dibujar_texto(" ", int(alto * 0.04), (235, 225, 210), ancho // 2, y_offset)

        # Botón de toggle
        btn_width = int(ancho * 0.30)
        btn_height = int(alto * 0.07)
        btn_x = ancho // 2 - btn_width // 2
        btn_y = y_offset + int(alto * 0.07)
        
        self._config_fullscreen_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
        
        # Detectar estado actual de pantalla completa
        is_fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
        modo_texto = "Pantalla Completa" if is_fullscreen else "Ventana"
        
        hovering = self._config_fullscreen_rect.collidepoint(pygame.mouse.get_pos())
        
        # Dibujar botón
        if hovering:
            pygame.draw.rect(pantalla, (60, 60, 70), self._config_fullscreen_rect, border_radius=8)
            pygame.draw.rect(pantalla, (255, 215, 0), self._config_fullscreen_rect, 2, border_radius=8)
            btn_surf = font_body.render(modo_texto, True, (255, 215, 0))
        else:
            pygame.draw.rect(pantalla, (40, 40, 50), self._config_fullscreen_rect, border_radius=8)
            pygame.draw.rect(pantalla, (200, 200, 200), self._config_fullscreen_rect, 1, border_radius=8)
            btn_surf = font_body.render(modo_texto, True, (235, 225, 210))
        
        pantalla.blit(btn_surf, (ancho // 2 - btn_surf.get_width() // 2, 
                                  btn_y + (btn_height - btn_surf.get_height()) // 2))
        
        # ===== VOLUMEN DE MÚSICA =====
        y_offset = btn_y + int(alto * 0.13)
        self.dibujar_texto("Volumen de música:", int(alto * 0.04), (235, 225, 210), ancho // 2, y_offset)
        
        # Slider de música - Más pequeño
        slider_width = int(ancho * 0.55)
        slider_height = int(alto * 0.018)
        slider_x = ancho // 2 - slider_width // 2
        slider_y = y_offset + int(alto * 0.06)
        
        # Track del slider (fondo) - Borde visible
        self._config_music_track_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(pantalla, (25, 25, 35), self._config_music_track_rect, border_radius=6)
        pygame.draw.rect(pantalla, (80, 80, 90), self._config_music_track_rect, 1, border_radius=6)
        
        # Barra de progreso (indica nivel de volumen) - Color dorado oscuro
        progress_width = int(slider_width * self.volumen_musica)
        if progress_width > 0:
            progress_rect = pygame.Rect(slider_x, slider_y, progress_width, slider_height)
            # Gradiente simulado con rectángulos superpuestos
            pygame.draw.rect(pantalla, (180, 140, 50), progress_rect, border_radius=6)
            # Brillo en la parte superior
            highlight_rect = pygame.Rect(slider_x, slider_y, progress_width, slider_height // 3)
            pygame.draw.rect(pantalla, (210, 170, 80), highlight_rect, border_radius=6)
        
        # Indicador (círculo que se puede arrastrar) - Más pequeño
        indicator_x = slider_x + progress_width
        indicator_y = slider_y + slider_height // 2
        pygame.draw.circle(pantalla, (240, 200, 100), (indicator_x, indicator_y), int(slider_height * 1.3))
        pygame.draw.circle(pantalla, (180, 140, 50), (indicator_x, indicator_y), int(slider_height * 1.3), 2)
        # Centro más claro
        pygame.draw.circle(pantalla, (255, 215, 0), (indicator_x, indicator_y), int(slider_height * 0.7))
        
        # Mostrar porcentaje
        porcentaje_musica = int(self.volumen_musica * 100)
        self.dibujar_texto(f"{porcentaje_musica}%", int(alto * 0.035), (240, 200, 100), 
                          ancho // 2, slider_y + int(alto * 0.05))
        
        self._config_music_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, 
                                                      slider_width + 20, slider_height + 20)
        
        # ===== VOLUMEN DE EFECTOS =====
        y_offset = slider_y + int(alto * 0.11)
        self.dibujar_texto("Volumen de efectos:", int(alto * 0.04), (235, 225, 210), ancho // 2, y_offset)
        
        # Slider de efectos
        slider_y = y_offset + int(alto * 0.06)
        
        # Track del slider (fondo) - Borde visible
        self._config_effects_track_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(pantalla, (25, 25, 35), self._config_effects_track_rect, border_radius=6)
        pygame.draw.rect(pantalla, (80, 80, 90), self._config_effects_track_rect, 1, border_radius=6)
        
        # Barra de progreso - Color rojo/naranja oscuro para efectos
        progress_width = int(slider_width * self.volumen_efectos)
        if progress_width > 0:
            progress_rect = pygame.Rect(slider_x, slider_y, progress_width, slider_height)
            # Gradiente simulado con color rojo/naranja
            pygame.draw.rect(pantalla, (180, 80, 50), progress_rect, border_radius=6)
            # Brillo en la parte superior
            highlight_rect = pygame.Rect(slider_x, slider_y, progress_width, slider_height // 3)
            pygame.draw.rect(pantalla, (210, 110, 70), highlight_rect, border_radius=6)
        
        # Indicador - Más pequeño
        indicator_x = slider_x + progress_width
        indicator_y = slider_y + slider_height // 2
        pygame.draw.circle(pantalla, (240, 140, 100), (indicator_x, indicator_y), int(slider_height * 1.3))
        pygame.draw.circle(pantalla, (180, 80, 50), (indicator_x, indicator_y), int(slider_height * 1.3), 2)
        # Centro más claro
        pygame.draw.circle(pantalla, (255, 160, 100), (indicator_x, indicator_y), int(slider_height * 0.7))
        
        # Mostrar porcentaje
        porcentaje_efectos = int(self.volumen_efectos * 100)
        self.dibujar_texto(f"{porcentaje_efectos}%", int(alto * 0.035), (240, 140, 100), 
                          ancho // 2, slider_y + int(alto * 0.05))
        
        self._config_effects_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, 
                                                        slider_width + 20, slider_height + 20)
        
        # Instrucciones (más abajo para evitar superposición)
        self.dibujar_texto("Haz clic en los controles para ajustar", int(alto * 0.028), 
                          (170, 170, 180), ancho // 2, int(alto * 0.85))
        self.dibujar_texto("ESC para volver", int(alto * 0.028), 
                          (170, 170, 180), ancho // 2, int(alto * 0.92))

    def toggle_fullscreen(self):
        """Alterna entre modo pantalla completa y ventana"""
        pantalla_actual = pygame.display.get_surface()
        is_fullscreen = pantalla_actual.get_flags() & pygame.FULLSCREEN
        
        info = pygame.display.Info()
        
        if is_fullscreen:
            # Cambiar a modo ventana
            nueva_pantalla = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
            self.mostrar_mensaje("Modo ventana activado", 90)
        else:
            # Cambiar a pantalla completa
            nueva_pantalla = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.mostrar_mensaje("Pantalla completa activada", 90)
        
        pygame.display.set_caption("Fear of Ways")

    # -------------------------------------------------------
    # GUARDADO Y CARGA
    # -------------------------------------------------------
    def _serializar_enemigos(self):
        """Convierte la lista de enemigos a formato: tipo:x:y:vida:velocidad,tipo:x:y:vida:velocidad,..."""
        if not self.enemigos:
            return "NONE"
        
        enemigos_data = []
        for e in self.enemigos:
            # Formato: tipo:x:y:vida:velocidad
            tipo = getattr(e, 'tipo', 'normal')
            x = int(e.rect.x)
            y = int(e.rect.y)
            vida = int(e.vida)
            velocidad = int(e.velocidad)
            enemigos_data.append(f"{tipo}:{x}:{y}:{vida}:{velocidad}")
        
        return ",".join(enemigos_data)
    
    def _deserializar_enemigos(self, data):
        """Convierte el string serializado de nuevo a lista de enemigos"""
        if not data or data == "NONE":
            return []
        
        enemigos_restaurados = []
        enemigos_str = data.split(',')
        
        for e_str in enemigos_str:
            partes = e_str.split(':')
            if len(partes) >= 5:
                tipo = partes[0]
                x = int(float(partes[1]))
                y = int(float(partes[2]))
                vida = int(float(partes[3]))
                velocidad = int(float(partes[4]))
                
                # Crear enemigo con los datos guardados
                from enemigo import enemigo as clase_enemigo
                e = clase_enemigo(x, y, vida, tipo=tipo)
                e.velocidad = velocidad
                enemigos_restaurados.append(e)
        
        return enemigos_restaurados
    
    def _serializar_bonus(self):
        """Convierte la lista de bonus (corazones, rayos, power-ups) a formato: tipo:x:y,tipo:x:y,..."""
        if not hasattr(self.nivel_actual, 'bonus') or not self.nivel_actual.bonus:
            return "NONE"
        
        bonus_data = []
        for bonus in self.nivel_actual.bonus:
            # Formato: tipo:x:y
            tipo = bonus.get('tipo', 'vida')
            rect = bonus.get('rect')
            if rect:
                x = int(rect.x)
                y = int(rect.y)
                bonus_data.append(f"{tipo}:{x}:{y}")
        
        return ",".join(bonus_data)
    
    def _deserializar_bonus(self, data):
        """Convierte el string serializado de nuevo a lista de bonus"""
        if not data or data == "NONE":
            return []
        
        bonus_restaurados = []
        bonus_str = data.split(',')
        
        for b_str in bonus_str:
            partes = b_str.split(':')
            if len(partes) >= 3:
                tipo = partes[0]
                x = int(float(partes[1]))
                y = int(float(partes[2]))
                
                # Crear bonus con los datos guardados
                bonus_restaurados.append({
                    "rect": pygame.Rect(x, y, 15, 15),
                    "tipo": tipo
                })
        
        return bonus_restaurados
    
    def guardar_partida(self):
        """Guarda el progreso completo del jugador en formato TXT"""
        try:
            # Leer partidas existentes
            partidas = {}
            if os.path.exists(self.archivo_guardado):
                with open(self.archivo_guardado, 'r', encoding='utf-8') as f:
                    for linea in f:
                        linea = linea.strip()
                        if linea and '|' in linea:
                            partes = linea.split('|')
                            if len(partes) >= 1:
                                nombre = partes[0]
                                partidas[nombre] = linea
            
            # Crear línea con TODOS los datos separados por |
            datos = [
                self.nombre_jugador,                                    # 0: Nombre
                str(self.numero_nivel),                                 # 1: Nivel
                str(self.puntos),                                       # 2: Puntos
                str(self.enemigos_derrotados),                          # 3: Enemigos derrotados
                self.jugador.nombre,                                    # 4: Personaje
                str(self.jugador.vida),                                 # 5: Vida actual
                str(self.jugador.vida_max),                             # 6: Vida máxima
                str(self.jugador.energia),                              # 7: Energía actual
                str(self.jugador.energia_max),                          # 8: Energía máxima
                str(self.jugador.velocidad_base),                       # 9: Velocidad
                str(self.jugador.vision),                               # 10: Visión
                f"{self.jugador.color[0]},{self.jugador.color[1]},{self.jugador.color[2]}",  # 11: Color RGB
                str(self.jugador.rect.x),                               # 12: Posición X
                str(self.jugador.rect.y),                               # 13: Posición Y
                str(len(getattr(self.nivel_actual, "llaves", []))),     # 14: Llaves restantes
                str(getattr(self.nivel_actual, "llaves_requeridas", 3)), # 15: Llaves requeridas
                str(self.temporizador_activo),                          # 16: Temporizador activo
                str(self.tiempo_restante),                              # 17: Tiempo restante
                str(self.tiempo_agotado),                               # 18: Tiempo agotado
                str(self.powerup_activo if self.powerup_activo else "None"),  # 19: Power-up tipo
                str(self.powerup_duracion),                             # 20: Power-up duración
                str(self.vision_normal if hasattr(self, 'vision_normal') else self.jugador.vision),  # 21: Visión normal
                str(self.velocidad_normal if hasattr(self, 'velocidad_normal') else self.jugador.velocidad_base),  # 22: Velocidad normal
                str(self.disparo_doble),                                # 23: Disparo doble
                str(self.escudo_activo),                                # 24: Escudo activo
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),           # 25: Fecha
                str(len(self.enemigos)),                                # 26: Cantidad de enemigos vivos
                str(getattr(self.nivel_actual, 'semilla', 0)),          # 27: Semilla del mapa
                self._serializar_enemigos(),                            # 28: Datos de enemigos (tipo:x:y:vida:velocidad,...)
                self._serializar_bonus(),                               # 29: Datos de bonus (tipo:x:y,tipo:x:y,...)
                str(self.cronometro_frames)                             # 30: Tiempo del cronómetro en frames
            ]
            
            linea_guardado = '|'.join(datos)
            partidas[self.nombre_jugador] = linea_guardado
            
            # Escribir archivo
            with open(self.archivo_guardado, 'w', encoding='utf-8') as f:
                for nombre, linea in partidas.items():
                    f.write(linea + '\n')
            
            semilla_guardada = getattr(self.nivel_actual, 'semilla', 'N/A')
            bonus_count = len(getattr(self.nivel_actual, 'bonus', []))
            print(f"Partida guardada para {self.nombre_jugador} - Nivel {self.numero_nivel}, Vida {self.jugador.vida}, Pos ({self.jugador.rect.x}, {self.jugador.rect.y}), Semilla: {semilla_guardada}, Enemigos: {len(self.enemigos)}, Bonus: {bonus_count}")
            return True
        except Exception as e:
            print(f"Error al guardar partida: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cargar_partida(self, nombre):
        """Carga una partida guardada desde formato TXT con TODOS los datos"""
        try:
            if not os.path.exists(self.archivo_guardado):
                return False
            
            # Buscar la línea del jugador
            linea_encontrada = None
            with open(self.archivo_guardado, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and linea.startswith(nombre + '|'):
                        linea_encontrada = linea
                        break
            
            if not linea_encontrada:
                return False
            
            # Parsear datos
            partes = linea_encontrada.split('|')
            if len(partes) < 26:
                print(f"Error: Formato de guardado incompleto ({len(partes)} partes, se esperan al menos 26)")
                return False
            
            # PASO 1: Extraer TODOS los datos del guardado
            nombre_jugador = partes[0]
            nivel = int(partes[1])
            puntos = int(partes[2])
            enemigos_derrotados = int(partes[3])
            personaje = partes[4]
            vida = int(float(partes[5]))
            vida_max = int(float(partes[6]))
            energia = int(float(partes[7]))
            energia_max = int(float(partes[8]))
            velocidad = int(float(partes[9]))
            vision = int(float(partes[10]))
            
            # Parsear color RGB
            color_rgb = partes[11].split(',')
            color = (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))
            
            pos_x = int(float(partes[12]))
            pos_y = int(float(partes[13]))
            llaves_restantes = int(float(partes[14]))
            llaves_requeridas = int(float(partes[15]))
            temporizador_activo = partes[16] == "True"
            tiempo_restante = int(float(partes[17]))
            tiempo_agotado = partes[18] == "True"
            powerup_tipo = partes[19] if partes[19] != "None" else None
            powerup_duracion = int(float(partes[20]))
            vision_normal = int(float(partes[21]))
            velocidad_normal = int(float(partes[22]))
            disparo_doble = partes[23] == "True"
            escudo_activo = partes[24] == "True"
            
            # Cantidad de enemigos vivos (nuevo campo, compatibilidad con guardados antiguos)
            cantidad_enemigos_guardados = int(float(partes[26])) if len(partes) > 26 else None
            
            # Semilla del mapa (nuevo campo, compatibilidad con guardados antiguos)
            semilla_mapa = int(float(partes[27])) if len(partes) > 27 else None
            
            # Datos de enemigos (nuevo campo, compatibilidad con guardados antiguos)
            enemigos_data = partes[28] if len(partes) > 28 else None
            
            # Datos de bonus (nuevo campo, compatibilidad con guardados antiguos)
            bonus_data = partes[29] if len(partes) > 29 else None
            
            # PASO 2: Crear jugador con los datos guardados
            self.nombre_jugador = nombre_jugador
            self.jugador = jugador(personaje, color, velocidad=velocidad, energia=energia_max, vision=vision)
            
            # PASO 3: Cargar el nivel con la MISMA semilla (esto genera el MISMO mapa)
            print(f"Cargando nivel {nivel} con semilla: {semilla_mapa}")
            self.cargar_nivel(nivel, semilla_mapa=semilla_mapa)
            
            # PASO 3.5: Restaurar enemigos guardados (reemplazar los generados)
            if enemigos_data:
                self.enemigos = self._deserializar_enemigos(enemigos_data)
            
            # PASO 3.6: Restaurar bonus guardados (reemplazar los generados)
            if bonus_data:
                self.nivel_actual.bonus = self._deserializar_bonus(bonus_data)
            
            # PASO 4: RESTAURAR INMEDIATAMENTE todos los valores guardados
            # Restaurar datos básicos
            self.numero_nivel = nivel
            self.puntos = puntos
            self.enemigos_derrotados = enemigos_derrotados
            
            # Restaurar vida y energía EXACTAS (sobrescribir el reset de cargar_nivel)
            self.jugador.vida = vida
            self.jugador.vida_max = vida_max
            self.jugador.energia = energia
            self.jugador.energia_max = energia_max
            self.jugador.velocidad_base = velocidad
            self.jugador.vision = vision
            
            # Restaurar posición EXACTA del jugador (sobrescribir spawn aleatorio)
            self.jugador.rect.x = pos_x
            self.jugador.rect.y = pos_y
            self.jugador.pos_inicial = (pos_x, pos_y)  # También actualizar pos_inicial
            self.jugador.vel_x = 0.0  # Resetear velocidad
            self.jugador.vel_y = 0.0
            
            # Actualizar la cámara para que se centre en la posición restaurada
            if self.camara:
                self.camara.actualizar(self.jugador.rect)
            
            print(f"Posición restaurada: ({pos_x}, {pos_y})")
            
            # Restaurar estado de llaves
            llaves_a_eliminar = llaves_requeridas - llaves_restantes
            if hasattr(self.nivel_actual, "llaves") and llaves_a_eliminar > 0 and llaves_a_eliminar <= len(self.nivel_actual.llaves):
                self.nivel_actual.llaves = self.nivel_actual.llaves[llaves_a_eliminar:]
                print(f"Llaves restauradas: {len(self.nivel_actual.llaves)} restantes")
            
            # Restaurar estado del temporizador
            self.temporizador_activo = temporizador_activo
            self.tiempo_restante = tiempo_restante
            self.tiempo_agotado = tiempo_agotado
            if self.temporizador_activo:
                print(f"Temporizador restaurado: {self.tiempo_restante // 60} segundos restantes")
            
            # Restaurar power-ups activos
            if powerup_tipo:
                self.powerup_activo = powerup_tipo
                self.powerup_duracion = powerup_duracion
                self.vision_normal = vision_normal
                self.velocidad_normal = velocidad_normal
                self.disparo_doble = disparo_doble
                self.escudo_activo = escudo_activo
                
                # Aplicar efectos del power-up activo
                if self.powerup_activo == "vision_clara":
                    self.jugador.vision = 9999
                elif self.powerup_activo == "super_velocidad":
                    self.jugador.velocidad_base = int(self.velocidad_normal * 3.5)
                
                print(f"Power-up restaurado: {self.powerup_activo} ({self.powerup_duracion} frames restantes)")
            else:
                self.powerup_activo = None
                self.powerup_duracion = 0
                self.disparo_doble = False
                self.escudo_activo = False
            
            # Restaurar cronómetro (nuevo campo, compatibilidad con guardados antiguos)
            if len(partes) > 30:
                self.cronometro_frames = int(float(partes[30]))
                self.tiempo_total_segundos = self.cronometro_frames // 60
                self.cronometro_activo = True  # Reactivar cronómetro
                print(f"Cronómetro restaurado: {self.tiempo_total_segundos} segundos")
            else:
                # Guardados antiguos sin cronómetro, inicializar en 0
                self.cronometro_frames = 0
                self.tiempo_total_segundos = 0
                self.cronometro_activo = True
            
            # Resetear bandera de historial para esta partida cargada
            self.historial_guardado = False
            
            bonus_count = len(getattr(self.nivel_actual, 'bonus', []))
            print(f"Partida cargada para {nombre}: Nivel {self.numero_nivel}, Vida {self.jugador.vida}/{self.jugador.vida_max}, Energía {self.jugador.energia}/{self.jugador.energia_max}, Enemigos: {len(self.enemigos)}, Bonus: {bonus_count}, Tiempo: {self.tiempo_total_segundos}s")
            return True
        except Exception as e:
            print(f"Error al cargar partida: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def obtener_partidas_guardadas(self):
        """Obtiene la lista de partidas guardadas desde formato TXT"""
        try:
            if not os.path.exists(self.archivo_guardado):
                return {}
            
            partidas = {}
            with open(self.archivo_guardado, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    partes = linea.split('|')
                    if len(partes) >= 26:
                        nombre = partes[0]
                        partidas[nombre] = {
                            "nivel": int(partes[1]),
                            "puntos": int(partes[2]),
                            "fecha": partes[25]
                        }
            
            return partidas
        except Exception as e:
            print(f"Error al leer partidas: {e}")
            return {}

    def borrar_partida(self, nombre):
        """Borra una partida guardada del archivo TXT"""
        try:
            if not os.path.exists(self.archivo_guardado):
                return False
            
            # Leer todas las líneas excepto la del jugador a borrar
            lineas_conservar = []
            with open(self.archivo_guardado, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea_limpia = linea.strip()
                    if linea_limpia and not linea_limpia.startswith(nombre + '|'):
                        lineas_conservar.append(linea_limpia)
            
            # Reescribir el archivo sin la partida borrada
            with open(self.archivo_guardado, 'w', encoding='utf-8') as f:
                for linea in lineas_conservar:
                    f.write(linea + '\n')
            
            print(f"Partida '{nombre}' borrada exitosamente")
            return True
        except Exception as e:
            print(f"Error al borrar partida: {e}")
            return False

    def guardar_en_historial(self):
        """Guarda la partida actual en el historial de jugadores UNA SOLA VEZ"""
        try:
            # Usar el tiempo del cronómetro
            tiempo_jugado = self.tiempo_total_segundos
            
            # Formato: Nombre|Nivel|Puntos|Tiempo(seg)|Enemigos|Fecha
            datos = [
                self.nombre_jugador,
                str(self.numero_nivel),
                str(self.puntos),
                str(tiempo_jugado),
                str(self.enemigos_derrotados),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            linea = '|'.join(datos) + '\n'
            
            # Agregar al archivo de historial (solo una vez)
            with open(self.archivo_historial, 'a', encoding='utf-8') as f:
                f.write(linea)
            
            print(f"Partida guardada en historial: {self.nombre_jugador} - {tiempo_jugado}s")
            return True
        except Exception as e:
            print(f"Error al guardar en historial: {e}")
            return False
    
    def guardar_campeon(self, tiempo_total):
        """Guarda al jugador como campeón (completó el juego)"""
        try:
            # Formato: Nombre|Puntos|Tiempo(seg)|Fecha
            datos = [
                self.nombre_jugador,
                str(self.puntos),
                str(tiempo_total),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            linea = '|'.join(datos) + '\n'
            
            # Agregar al archivo de campeones
            with open(self.archivo_campeones, 'a', encoding='utf-8') as f:
                f.write(linea)
            
            print(f"¡Campeón registrado!: {self.nombre_jugador}")
            return True
        except Exception as e:
            print(f"Error al guardar campeón: {e}")
            return False
    
    def obtener_campeones(self):
        """Obtiene la lista de campeones ordenada por puntos"""
        try:
            if not os.path.exists(self.archivo_campeones):
                return []
            
            campeones = []
            with open(self.archivo_campeones, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    partes = linea.split('|')
                    if len(partes) >= 4:
                        campeones.append({
                            'nombre': partes[0],
                            'puntos': int(partes[1]),
                            'tiempo': int(partes[2]),
                            'fecha': partes[3]
                        })
            
            # Ordenar por puntos descendente, luego por tiempo ascendente
            campeones.sort(key=lambda x: (-x['puntos'], x['tiempo']))
            return campeones
        except Exception as e:
            print(f"Error al obtener campeones: {e}")
            return []
    
    def obtener_historial(self):
        """Obtiene el historial de todas las partidas jugadas"""
        try:
            if not os.path.exists(self.archivo_historial):
                return []
            
            historial = []
            with open(self.archivo_historial, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    
                    partes = linea.split('|')
                    if len(partes) >= 6:
                        historial.append({
                            'nombre': partes[0],
                            'nivel': int(partes[1]),
                            'puntos': int(partes[2]),
                            'tiempo': int(partes[3]),
                            'enemigos': int(partes[4]),
                            'fecha': partes[5]
                        })
            
            # Ordenar por puntos descendente
            historial.sort(key=lambda x: -x['puntos'])
            return historial
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []

    # -------------------------------------------------------
    # LOOP DE EVENTOS
    # -------------------------------------------------------
    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); return
                if self.estado == "menu":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        pygame.quit(); return
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        if hasattr(self, "_menu_hitboxes"):
                            for rect_hit, idx in self._menu_hitboxes:
                                if rect_hit.collidepoint(pygame.mouse.get_pos()):
                                    self.reproducir_click_menu()
                                    if idx == 0:          # Nueva Partida
                                        self.nombre_jugador = ""
                                        self.input_activo = True
                                        self.estado = "registro"
                                    elif idx == 1:        # Cargar Partida
                                        self.estado = "cargar_partida"
                                    elif idx == 2:        # Puntuación
                                        self.estado = "puntuacion"
                                    elif idx == 3:        # Configuración
                                        self.estado = "configuracion"
                                    break
                
                elif self.estado == "controles":
                        if e.type == pygame.KEYDOWN:
                            if e.key == pygame.K_ESCAPE:
                                self.reproducir_click_menu()
                                self.estado = "menu"
                                pygame.mouse.set_visible(True)
                            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                                self.reproducir_click_menu()
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)
                                # Activar cronómetro cuando empieza a jugar
                                if not self.cronometro_activo:
                                    self.cronometro_activo = True
                                    self.cronometro_frames = 0
                        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                            if hasattr(self, "_controles_btn_rect") and self._controles_btn_rect.collidepoint(pygame.mouse.get_pos()):
                                self.reproducir_click_menu()
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)
                                # Activar cronómetro cuando empieza a jugar
                                if not self.cronometro_activo:
                                    self.cronometro_activo = True
                                    self.cronometro_frames = 0

                # JUGANDO
                elif self.estado == "jugando":
                    # Pausar con ESC o P
                    if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.estado = "pausado"

                    # Tecla 0 -> mostrar pantalla final inmediatamente (útil para pruebas)
                    elif e.type == pygame.KEYDOWN and e.key == pygame.K_0:
                        # Forzar pantalla final como 'perdiste' para testear diseño
                        try:
                            self.reproducir_click_menu()
                        except Exception:
                            pass
                        self.resultado = "perdiste"
                        self._pantalla_final_frame = None
                        self.estado = "fin"
                        pygame.mouse.set_visible(True)
                    elif e.type == pygame.KEYDOWN and e.key == pygame.K_9:
                        # Forzar pantalla final como 'ganaste' (atajo de prueba)
                        try:
                            self.reproducir_click_menu()
                        except Exception:
                            pass
                        self.resultado = "ganaste"
                        self._pantalla_final_frame = None
                        self.estado = "fin"
                        pygame.mouse.set_visible(True)
                    
                    # Disparo con click izquierdo - solo si el tutorial fue cerrado
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and \
                         (self.tutorial_mostrado or self.numero_nivel > 1):
                        if self.jugador.cooldown_disparo == 0:
                            self.disparar_proyectil()

                    # Tecla E - Activar power-up cercano
                    elif e.type == pygame.KEYDOWN and e.key == pygame.K_e and \
                         (self.tutorial_mostrado or self.numero_nivel > 1):
                        # Buscar power-up más cercano al jugador
                        power_up_cercano = None
                        distancia_minima = 80  # Radio de activación
                        
                        for bonus in list(getattr(self.nivel_actual, "bonus", [])):
                            if bonus["tipo"] in ["vision_clara", "disparo_doble", "super_velocidad", "escudo"]:
                                # Calcular distancia entre jugador y power-up
                                dx = bonus["rect"].centerx - self.jugador.rect.centerx
                                dy = bonus["rect"].centery - self.jugador.rect.centery
                                distancia = math.sqrt(dx*dx + dy*dy)
                                
                                if distancia < distancia_minima:
                                    distancia_minima = distancia
                                    power_up_cercano = bonus
                        
                        # Activar el power-up más cercano si se encontró uno
                        if power_up_cercano:
                            self.activar_powerup(power_up_cercano["tipo"])
                            self.nivel_actual.bonus.remove(power_up_cercano)

                # PAUSA 
                elif self.estado == "pausado":
                    # Mostrar cursor en menú de pausa
                    pygame.mouse.set_visible(True)
                    
                    if e.type == pygame.KEYDOWN:
                        if e.key in (pygame.K_ESCAPE, pygame.K_p):
                            self.reproducir_click_menu()
                            self.estado = "jugando"
                            pygame.mouse.set_visible(False)  # Ocultar al reanudar
                        elif e.key == pygame.K_UP:
                            self.opcion_pausa = (self.opcion_pausa - 1) % 3
                        elif e.key == pygame.K_DOWN:
                            self.opcion_pausa = (self.opcion_pausa + 1) % 3
                        # Controles de volumen de música
                        elif e.key == pygame.K_LEFT:
                            self.volumen_musica = max(0.0, self.volumen_musica - 0.25)
                            pygame.mixer.music.set_volume(self.volumen_musica)
                        elif e.key == pygame.K_RIGHT:
                            self.volumen_musica = min(1.0, self.volumen_musica + 0.25)
                            pygame.mixer.music.set_volume(self.volumen_musica)
                        # Controles de volumen de efectos
                        elif e.key == pygame.K_LEFTBRACKET:  # [
                            self.volumen_efectos = max(0.0, self.volumen_efectos - 0.25)
                            self.actualizar_volumen_efectos()
                        elif e.key == pygame.K_RIGHTBRACKET:  # ]
                            self.volumen_efectos = min(1.0, self.volumen_efectos + 0.25)
                            self.actualizar_volumen_efectos()
                        elif e.key == pygame.K_RETURN:
                            if self.opcion_pausa == 0:  # Reanudar
                                self.reproducir_click_menu()
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)  # Ocultar al reanudar
                            elif self.opcion_pausa == 1:  # Reiniciar nivel
                                self.reproducir_click_menu()
                                # Reiniciar el nivel completamente
                                self.cargar_nivel(self.numero_nivel)
                                # Reiniciar cronómetro
                                self.cronometro_frames = 0
                                self.cronometro_activo = True
                                # Resetear temporizador
                                self.temporizador_activo = False
                                self.tiempo_restante = 0
                                self.tiempo_agotado = False
                                self.spawn_enemigos_extra = 0
                                # Limpiar mensajes temporales
                                self.mensaje_temporal = ""
                                self.mensaje_timer = 0
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)  # Ocultar al reanudar
                            elif self.opcion_pausa == 2:  # Menú principal
                                self.reproducir_click_menu()
                                # Guardar antes de salir al menú
                                if self.nombre_jugador:
                                    self.guardar_partida()
                                self.estado = "menu"
                                pygame.mouse.set_visible(True)  # Mostrar cursor en menú
                    
                    # Soporte de mouse en menú de pausa
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        # Usar las hitboxes creadas en menu_pausa() para detección precisa
                        if hasattr(self, "_pause_hitboxes"):
                            for rect_hit, idx in self._pause_hitboxes:
                                if rect_hit.collidepoint(pygame.mouse.get_pos()):
                                    self.reproducir_click_menu()
                                    if idx == 0:  # Reanudar
                                        self.estado = "jugando"
                                        pygame.mouse.set_visible(False)  # Ocultar al reanudar
                                    elif idx == 1:  # Reiniciar nivel
                                        # Reiniciar el nivel completamente
                                        self.cargar_nivel(self.numero_nivel)
                                        # Reiniciar cronómetro
                                        self.cronometro_frames = 0
                                        self.cronometro_activo = True
                                        # Resetear temporizador
                                        self.temporizador_activo = False
                                        self.tiempo_restante = 0
                                        self.tiempo_agotado = False
                                        self.spawn_enemigos_extra = 0
                                        # Limpiar mensajes temporales
                                        self.mensaje_temporal = ""
                                        self.mensaje_timer = 0
                                        self.estado = "jugando"
                                        pygame.mouse.set_visible(False)  # Ocultar al reanudar
                                    elif idx == 2:  # Configuración
                                        self.estado_previo_config = "pausado"  # Guardar de dónde viene
                                        self.estado = "configuracion"
                                    elif idx == 3:  # Menú principal
                                        # Guardar antes de salir al menú
                                        if self.nombre_jugador:
                                            self.guardar_partida()
                                        self.estado = "menu"
                                        pygame.mouse.set_visible(True)
                                    break
                
                elif self.estado == "fin" and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    self.reproducir_click_menu()
                    self.estado = "menu"
                    pygame.mouse.set_visible(True)  # Mostrar cursor en menú

                # PUNTUACIÓN
                elif self.estado == "puntuacion":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        self.reproducir_click_menu()
                        self.estado = "menu"
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        # Click en pestañas
                        if hasattr(self, "_tab_campeones_rect") and self._tab_campeones_rect.collidepoint(mouse_pos):
                            self.reproducir_click_menu()
                            self._tab_puntuacion = "campeones"
                        elif hasattr(self, "_tab_historico_rect") and self._tab_historico_rect.collidepoint(mouse_pos):
                            self.reproducir_click_menu()
                            self._tab_puntuacion = "historico"
                
                # REGISTRO
                elif self.estado == "registro":
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            self.reproducir_click_menu()
                            self.estado = "menu"
                            self.nombre_jugador = ""
                            self.input_activo = False
                        elif e.key == pygame.K_RETURN and len(self.nombre_jugador) > 0:
                            # Iniciar juego con el nombre registrado
                            self.reproducir_click_menu()
                            self.input_activo = False
                            self.iniciar_juego()
                        elif e.key == pygame.K_BACKSPACE:
                            self.nombre_jugador = self.nombre_jugador[:-1]
                        else:
                            # Agregar caracteres (limitar a 20 caracteres)
                            if len(self.nombre_jugador) < 20 and e.unicode.isprintable():
                                self.nombre_jugador += e.unicode
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        # Click en botón continuar
                        if hasattr(self, "_registro_btn_rect") and self._registro_btn_rect.collidepoint(pygame.mouse.get_pos()):
                            if len(self.nombre_jugador) > 0:
                                self.reproducir_click_menu()
                                self.input_activo = False
                                self.iniciar_juego()
                
                # CARGAR PARTIDA
                elif self.estado == "cargar_partida":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        self.reproducir_click_menu()
                        self.estado = "menu"
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Primero verificar si se clickeó un botón de borrar
                        borrado = False
                        if hasattr(self, "_borrar_hitboxes"):
                            for rect_hit, nombre in self._borrar_hitboxes:
                                if rect_hit.collidepoint(mouse_pos):
                                    if self.borrar_partida(nombre):
                                        self.reproducir_click_menu()
                                        self.mostrar_mensaje(f"Partida '{nombre}' borrada", 120)
                                    else:
                                        self.reproducir_click_menu()
                                        self.mostrar_mensaje("Error al borrar la partida", 120)
                                    borrado = True
                                    break
                        
                        # Si no se borró, verificar si se clickeó para cargar
                        if not borrado and hasattr(self, "_cargar_hitboxes"):
                            for rect_hit, nombre in self._cargar_hitboxes:
                                if rect_hit.collidepoint(mouse_pos):
                                    if self.cargar_partida(nombre):
                                        self.reproducir_click_menu()
                                        self.estado = "jugando"
                                        pygame.mouse.set_visible(False)
                                    else:
                                        self.reproducir_click_menu()
                                        self.mostrar_mensaje("Error al cargar la partida", 120)
                                    break
                
                # CONFIGURACIÓN
                elif self.estado == "configuracion":
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                        self.reproducir_click_menu()
                        # Volver al estado anterior (menú o pausa)
                        if hasattr(self, 'estado_previo_config') and self.estado_previo_config == "pausado":
                            self.estado = "pausado"
                            self.estado_previo_config = None
                        else:
                            self.estado = "menu"
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Verificar botón de pantalla completa
                        if hasattr(self, "_config_fullscreen_rect") and self._config_fullscreen_rect.collidepoint(mouse_pos):
                            self.reproducir_click_menu()
                            self.toggle_fullscreen()
                        
                        # Verificar sliders de volumen
                        if hasattr(self, "_config_music_slider_rect") and hasattr(self, "_config_music_track_rect"):
                            if self._config_music_track_rect.collidepoint(mouse_pos):
                                # Calcular nuevo volumen basado en posición del click
                                relative_x = mouse_pos[0] - self._config_music_track_rect.x
                                self.volumen_musica = max(0.0, min(1.0, relative_x / self._config_music_track_rect.width))
                                pygame.mixer.music.set_volume(self.volumen_musica)
                                self.reproducir_click_menu()
                        
                        if hasattr(self, "_config_effects_slider_rect") and hasattr(self, "_config_effects_track_rect"):
                            if self._config_effects_track_rect.collidepoint(mouse_pos):
                                # Calcular nuevo volumen basado en posición del click
                                relative_x = mouse_pos[0] - self._config_effects_track_rect.x
                                self.volumen_efectos = max(0.0, min(1.0, relative_x / self._config_effects_track_rect.width))
                                self.actualizar_volumen_efectos()
                                self.reproducir_click_menu()

            if self.estado == "menu":
                self.menu()
            elif self.estado == "controles":
                self.controles()
            elif self.estado == "jugando":
                self.jugar(pausado=False)
            elif self.estado == "pausado":
                self.jugar(pausado=True)  # Mantener el juego visible pero pausado
                self.menu_pausa()  # Dibujar el menú de pausa encima
            elif self.estado == "fin":
                self.pantalla_final()
            elif self.estado == "puntuacion":
                self.pantalla_puntuacion()
            elif self.estado == "registro":
                self.pantalla_registro()
            elif self.estado == "cargar_partida":
                self.pantalla_cargar_partida()
            elif self.estado == "configuracion":
                self.pantalla_configuracion()

            pygame.display.flip()
            reloj.tick(60)

    # -------------------------------------------------------
    # DISPARO
    # -------------------------------------------------------
    def disparar_proyectil(self):
        """Dispara un proyectil hacia el mouse o en la dirección de movimiento"""
        # Iniciar animación de disparo primero
        if not self.jugador.iniciar_disparo():
            return
        
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        offset_header = int(alto * self.altura_header)
        
        # Obtener posición del mouse
        mx, my = pygame.mouse.get_pos()
        my_ajustado = my - offset_header
        
        # Obtener posición del jugador en pantalla
        jugador_pantalla = self.camara.aplicar(self.jugador.rect)
        px, py = jugador_pantalla.centerx, jugador_pantalla.centery
        
        # Calcular dirección desde el jugador al mouse
        dx = mx - px
        dy = my_ajustado - py
        
        # Si el mouse está muy cerca del jugador, usar la última dirección de movimiento
        distancia_mouse = math.hypot(dx, dy)
        if distancia_mouse < 20:  # Mouse muy cerca del jugador
            dx = self.jugador.ultima_direccion_x * 100
            dy = self.jugador.ultima_direccion_y * 100
        
        # Convertir dirección a coordenadas del mundo
        mundo_destino_x = self.jugador.rect.centerx + dx
        mundo_destino_y = self.jugador.rect.centery + dy
        
        # Crear proyectil principal
        self.proyectiles.append(
            proyectil(
                self.jugador.rect.centerx, 
                self.jugador.rect.centery, 
                mundo_destino_x, 
                mundo_destino_y, 
                self.jugador.color
            )
        )
        
        # Si disparo doble está activo, crear proyectil adicional con un ángulo ligeramente diferente
        if self.disparo_doble:
            # Calcular ángulo del disparo original
            angulo = math.atan2(dy, dx)
            # Crear segundo proyectil con un pequeño offset angular (15 grados)
            offset_angulo = math.radians(15)
            dx2 = math.cos(angulo + offset_angulo) * distancia_mouse
            dy2 = math.sin(angulo + offset_angulo) * distancia_mouse
            
            self.proyectiles.append(
                proyectil(
                    self.jugador.rect.centerx, 
                    self.jugador.rect.centery, 
                    self.jugador.rect.centerx + dx2, 
                    self.jugador.rect.centery + dy2, 
                    self.jugador.color
                )
            )
        
        self.jugador.cooldown_disparo = 8  # Cooldown reducido para disparos más rápidos

        # Reproducir sonido de disparo
        if self.sonido_disparo:
            try:
                self.sonido_disparo.play()
            except Exception as e:
                print(f"Error al reproducir sonido: {e}")

    def _cargar_sonido_basico(self, ruta, descripcion, volumen_absoluto=None, volumen_relativo=None):
        try:
            sonido = pygame.mixer.Sound(ruta)
            if volumen_absoluto is not None:
                sonido.set_volume(volumen_absoluto)
            elif volumen_relativo is not None:
                sonido.set_volume(self.volumen_efectos * volumen_relativo)
            print(f"{descripcion} cargado correctamente")
            return sonido
        except (pygame.error, FileNotFoundError):
            print(f"Advertencia: No se pudo cargar {ruta} ({descripcion})")
            return None

    def _cargar_sonido_opcional(self, carpeta, nombre_base, descripcion, volumen_relativo=1.0):
        ruta = self._resolver_archivo_audio(carpeta, nombre_base)
        if ruta is None:
            print(f"Advertencia: No se encontraron archivos para {descripcion}")
            return None
        try:
            sonido = pygame.mixer.Sound(ruta)
            sonido.set_volume(self.volumen_efectos * volumen_relativo)
            print(f"{descripcion} cargado desde {ruta}")
            return sonido
        except (pygame.error, FileNotFoundError):
            print(f"Advertencia: No se pudo cargar {ruta} ({descripcion})")
            return None

    def _cargar_variantes_click(self, carpeta, prefijo, volumen_relativo=1.0):
        patrones = [f"{prefijo}*.mp3", f"{prefijo}*.wav", f"{prefijo}*.ogg"]
        rutas = []
        for patron in patrones:
            rutas.extend(sorted(glob.glob(os.path.join(carpeta, patron))))

        sonidos = []
        if not rutas:
            print(f"Advertencia: No se encontraron variantes para {prefijo}")
            return sonidos

        for ruta in rutas:
            try:
                sonido = pygame.mixer.Sound(ruta)
                sonido.set_volume(self.volumen_efectos * volumen_relativo)
                sonidos.append(sonido)
                print(f"Sonido de menú cargado: {ruta}")
            except (pygame.error, FileNotFoundError):
                print(f"Advertencia: No se pudo cargar sonido de menú {ruta}")
        return sonidos

    # -------------------------------------------------------
    # Control de música de fondo (menu / nivel)
    # -------------------------------------------------------
    def _play_music(self, ruta, loop=True):
        """Carga y reproduce una pista de música usando pygame.mixer.music.
        Guarda la ruta en self._musica_actual para evitar recargas innecesarias."""
        if not ruta:
            return
        try:
            pygame.mixer.music.load(ruta)
            # Ajustar volumen global de música (usa volumen_musica si existe)
            vol = getattr(self, 'volumen_musica', 0.7)
            pygame.mixer.music.set_volume(vol)
            pygame.mixer.music.play(-1 if loop else 0)
            self._musica_actual = ruta
            print(f"Reproduciendo música: {ruta}")
        except Exception as e:
            print(f"No se pudo reproducir música {ruta}: {e}")

    def _stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._musica_actual = None

    def actualizar_musica_por_estado(self):
        """Decide qué pista reproducir según self.estado.
        - menu/menus -> menu music
        - jugando -> musica de nivel
        - otros estados -> no cambiar (o detener si no hay pista deseada)
        """
        desired = None
        if self.estado == 'jugando':
            desired = self.musica_nivel_path
        elif self.estado in ('menu', 'puntuacion', 'registro', 'cargar_partida', 'configuracion', 'controles'):
            desired = self.musica_menu_path

        # Si la deseada es diferente a la actual, cambiar
        if desired and desired != self._musica_actual:
            # Cambiar pista
            try:
                self._play_music(desired, loop=True)
            except Exception:
                pass
        elif desired is None and self._musica_actual:
            # Si no hay pista deseada (ejemplo: estado de fin) detener la música de fondo
            self._stop_music()

    def _resolver_archivo_audio(self, carpeta, nombre_base):
        extensiones = [".mp3", ".wav", ".ogg"]
        for ext in extensiones:
            ruta = os.path.join(carpeta, f"{nombre_base}{ext}")
            if os.path.exists(ruta):
                return ruta
        return None

    def _reproducir_sonido(self, sonido):
        if sonido:
            try:
                sonido.play()
            except Exception as e:
                print(f"Error al reproducir sonido: {e}")

    def reproducir_click_menu(self):
        if self.sonidos_click_menu:
            sonido = random.choice(self.sonidos_click_menu)
            self._reproducir_sonido(sonido)

    def reproducir_corazon(self):
        self._reproducir_sonido(self.sonido_corazon)

    def reproducir_notificacion(self):
        self._reproducir_sonido(self.sonido_notificacion)

    def reproducir_pocion(self):
        self._reproducir_sonido(self.sonido_pocion)

    def reproducir_llave(self):
        self._reproducir_sonido(self.sonido_recoger_llave)

    def reproducir_rayo(self):
        if self.sonido_rayo:
            self._reproducir_sonido(self.sonido_rayo)
        else:
            self._reproducir_sonido(self.sonido_golpe)

    def mostrar_mensaje(self, texto, duracion, sonido=True):
        self.mensaje_temporal = texto
        self.mensaje_timer = duracion
        if sonido:
            self.reproducir_notificacion()
    
    # -------------------------------------------------------
    # ATAQUE CORTO (melee)
    # -------------------------------------------------------
    def ataque_corto(self):
        """Realiza un ataque cuerpo a cuerpo en la dirección del mouse"""
        # Verificar cooldown del ataque melee (más rápido que disparo)
        if not hasattr(self, 'cooldown_melee'):
            self.cooldown_melee = 0
        
        if self.cooldown_melee > 0:
            return  # Aún en cooldown
        
        # Establecer cooldown (15 frames = 0.25 segundos a 60 FPS)
        self.cooldown_melee = 15
        
        # Obtener posición del mouse ajustada
        pantalla = pygame.display.get_surface()
        ancho, alto = pantalla.get_size()
        offset_header = int(alto * self.altura_header)
        mx, my = pygame.mouse.get_pos()
        my_ajustado = my - offset_header
        
        # Calcular ángulo hacia el mouse
        ang = math.atan2(my_ajustado - self.jugador.rect.centery, 
                         mx - self.jugador.rect.centerx)
        
        # Alcance y área del ataque
        alcance = 50  # Distancia del ataque
        ancho_ataque = 50  # Ancho del área de ataque
        
        # Crear rectángulo de ataque en la dirección del mouse
        ataque_x = self.jugador.rect.centerx + math.cos(ang) * alcance
        ataque_y = self.jugador.rect.centery + math.sin(ang) * alcance
        ataque_rect = pygame.Rect(0, 0, ancho_ataque, ancho_ataque)
        ataque_rect.center = (ataque_x, ataque_y)
        
        # Verificar colisiones con enemigos
        enemigos_golpeados = 0
        for enemigo_actual in list(self.enemigos):
            if ataque_rect.colliderect(enemigo_actual.rect):
                enemigos_golpeados += 1
                enemigo_actual.vida -= 1
                
                # Efecto visual en el enemigo
                enemigo_actual.color = (255, 100, 100)
                
                # Reproducir sonido
                if self.sonido_golpe:
                    self.sonido_golpe.play()
                
                # Verificar si el enemigo murió
                if enemigo_actual.vida <= 0:
                    self.enemigos.remove(enemigo_actual)
                    self.enemigos_derrotados += 1
                    self.puntos += 100  # Puntos por enemigo derrotado

    # -------------------------------------------------------
    # SISTEMA DE POWER-UPS
    # -------------------------------------------------------
    def activar_powerup(self, tipo):
        """Activa un power-up con sus efectos específicos"""
        # Desactivar power-up anterior si existe
        if self.powerup_activo:
            self.desactivar_powerup()
        
        self.powerup_activo = tipo
        self.reproducir_pocion()

        if tipo == "vision_clara":
            # Ver todo claro por 5 segundos
            self.vision_normal = self.jugador.vision
            self.jugador.vision = 9999  # Visión infinita
            self.powerup_duracion = 5 * 60  # 5 segundos a 60 FPS
            self.mostrar_mensaje("👁 ¡VISIÓN CLARA ACTIVADA! (5s)", 120)

        elif tipo == "disparo_doble":
            # Disparar doble por 30 segundos
            self.disparo_doble = True
            self.powerup_duracion = 30 * 60  # 30 segundos
            self.mostrar_mensaje("⚡ ¡DISPARO DOBLE ACTIVADO! (30s)", 120)

        elif tipo == "super_velocidad":
            # Super rápido por 10 segundos
            self.velocidad_normal = self.jugador.velocidad_base
            self.jugador.velocidad_base *= 3.5  # Velocidad aumentada a 3.5x
            self.powerup_duracion = 10 * 60  # 10 segundos
            self.mostrar_mensaje("⚡ ¡SUPER VELOCIDAD ACTIVADA! (10s)", 120)

        elif tipo == "escudo":
            # Escudo por 30 segundos
            self.escudo_activo = True
            self.powerup_duracion = 30 * 60  # 30 segundos
            self.mostrar_mensaje("🛡 ¡ESCUDO ACTIVADO! (30s)", 120)
    
    def desactivar_powerup(self, mostrar_mensaje=True):
        """Desactiva el power-up actual y restaura los valores"""
        if self.powerup_activo == "vision_clara":
            self.jugador.vision = self.vision_normal
        elif self.powerup_activo == "super_velocidad":
            self.jugador.velocidad_base = self.velocidad_normal
        elif self.powerup_activo == "disparo_doble":
            self.disparo_doble = False
        elif self.powerup_activo == "escudo":
            self.escudo_activo = False
        
        self.powerup_activo = None
        self.powerup_duracion = 0
        
        # Solo mostrar mensaje si se especifica
        if mostrar_mensaje:
            self.mostrar_mensaje("⏰ Power-up terminado", 60)

    # -------------------------------------------------------
    # SPAWN DE ENEMIGOS EXTRAS
    # -------------------------------------------------------
    def spawear_enemigo_aleatorio(self):
        """Spawnea un enemigo en una posición aleatoria alejada del jugador"""
        # Intentar spawear lejos del jugador
        max_intentos = 10
        for _ in range(max_intentos):
            x = random.randint(100, self.nivel_actual.ancho - 100)
            y = random.randint(100, self.nivel_actual.alto - 100)
            
            # Calcular distancia al jugador
            dist_jugador = math.hypot(x - self.jugador.rect.centerx, y - self.jugador.rect.centery)
            
            # Solo spawear si está suficientemente lejos (al menos 400 unidades)
            if dist_jugador > 400:
                # Enemigos más peligrosos cuando el tiempo se agota
                tipo = random.choices(["veloz", "acechador", "bruto"], [0.4, 0.4, 0.2])[0]
                velocidad = random.randint(3, 5)  # Más rápidos
                nuevo_enemigo = enemigo(x, y, velocidad, tipo=tipo)
                # Hacerlos más agresivos
                nuevo_enemigo.rango_deteccion = 350
                nuevo_enemigo.velocidad_persecucion = nuevo_enemigo.velocidad + 1.5
                self.enemigos.append(nuevo_enemigo)
                break

    def spawear_enemigos_progresivos(self):
        """Spawnea múltiples enemigos en zonas aleatorias del mapa según el nivel"""
        enemigos_spawneados = 0
        max_intentos_por_enemigo = 15
        
        # Obtener muros para verificación de colisiones
        muros_rects = [m.rect for m in self.nivel_actual.muros]
        
        # Dividir el mapa en zonas para mejor distribución
        ancho_zona = self.nivel_actual.ancho // 3
        alto_zona = self.nivel_actual.alto // 3
        zonas_usadas = set()
        
        for _ in range(self.cantidad_spawn):
            for intento in range(max_intentos_por_enemigo):
                # Seleccionar una zona aleatoria que no se haya usado recientemente
                zona_x = random.randint(0, 2)
                zona_y = random.randint(0, 2)
                zona_id = (zona_x, zona_y)
                
                # Si ya se usó esta zona en este spawn, intentar otra
                if len(zonas_usadas) < 6 and zona_id in zonas_usadas:
                    continue
                
                # Generar posición dentro de la zona seleccionada
                x_min = zona_x * ancho_zona + 80
                x_max = (zona_x + 1) * ancho_zona - 80
                y_min = zona_y * alto_zona + 80
                y_max = (zona_y + 1) * alto_zona - 80
                
                x = random.randint(max(80, x_min), min(self.nivel_actual.ancho - 80, x_max))
                y = random.randint(max(80, y_min), min(self.nivel_actual.alto - 80, y_max))
                
                # Verificar distancia al jugador
                dist_jugador = math.hypot(x - self.jugador.rect.centerx, y - self.jugador.rect.centery)
                
                # Debe estar al menos a 300 unidades del jugador
                if dist_jugador < 300:
                    continue
                
                # Verificar que no esté dentro de un muro
                enemigo_rect = pygame.Rect(x - 25, y - 25, 50, 50)
                colision_muro = False
                for muro_rect in muros_rects:
                    if enemigo_rect.colliderect(muro_rect):
                        colision_muro = True
                        break
                
                if colision_muro:
                    continue
                
                # Verificar que no esté muy cerca de otros enemigos
                muy_cerca_otro = False
                for e in self.enemigos:
                    dist_enemigo = math.hypot(x - e.rect.centerx, y - e.rect.centery)
                    if dist_enemigo < 150:
                        muy_cerca_otro = True
                        break
                
                if muy_cerca_otro:
                    continue
                
                # Posición válida encontrada - Crear enemigo
                tipo = random.choices(["veloz", "acechador", "bruto"], [0.45, 0.35, 0.2])[0]
                velocidad = random.randint(2, 4)
                nuevo_enemigo = enemigo(x, y, velocidad, tipo=tipo)
                
                # Ajustar estadísticas según el nivel
                if self.numero_nivel == 2:
                    nuevo_enemigo.rango_deteccion = 280
                    nuevo_enemigo.velocidad_persecucion = nuevo_enemigo.velocidad + 0.7
                elif self.numero_nivel == 3:
                    nuevo_enemigo.rango_deteccion = 300
                    nuevo_enemigo.velocidad_persecucion = nuevo_enemigo.velocidad + 1.0
                
                self.enemigos.append(nuevo_enemigo)
                zonas_usadas.add(zona_id)
                enemigos_spawneados += 1
                break
        
        # Los enemigos se generan silenciosamente sin mensaje ni sonido

    # -------------------------------------------------------
    # GUARDADO DE RESULTADOS
    # -------------------------------------------------------
    def dibujar_tutorial(self, pantalla):
        """Muestra un tutorial con los controles básicos"""
        ancho, alto = pantalla.get_size()
        
        # Fondo semi-transparente
        overlay = pygame.Surface((ancho, alto // 3))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        y_pos = alto // 3
        pantalla.blit(overlay, (0, y_pos))
        
        # Título
        self.dibujar_texto("CONTROLES BÁSICOS", int(alto * 0.05), AMARILLO, 
                          ancho // 2, y_pos + int(alto * 0.05))
        
        # Controles - Dos columnas
        controles_izq = [
            "WASD - Movimiento",
            "SHIFT - Sprint",
            "Click Izq - Disparar",
            "E - Activar pociones cercanas"
        ]
        
        controles_der = [
            "P/ESC - Pausar",
            "",
            "Recoge llaves para escapar",
            ""
        ]
        
        # Columna izquierda
        x_izq = ancho // 4
        y_start = y_pos + int(alto * 0.12)
        for i, texto in enumerate(controles_izq):
            self.dibujar_texto(texto, int(alto * 0.028), BLANCO, 
                              x_izq, y_start + i * int(alto * 0.04))
        
        # Columna derecha
        x_der = ancho * 3 // 4
        for i, texto in enumerate(controles_der):
            self.dibujar_texto(texto, int(alto * 0.028), BLANCO, 
                              x_der, y_start + i * int(alto * 0.04))
        
        # Mensaje para cerrar
        self.dibujar_texto("Presiona ENTER para comenzar", int(alto * 0.03), VERDE, 
                          ancho // 2, y_pos + int(alto * 0.25))
    
    def actualizar_volumen_efectos(self):
        """Actualiza el volumen de todos los efectos de sonido"""
        if self.sonido_disparo:
            self.sonido_disparo.set_volume(self.volumen_efectos)
        if self.sonido_golpe:
            self.sonido_golpe.set_volume(self.volumen_efectos * 0.7)
        for sonido in getattr(self, "sonidos_click_menu", []):
            sonido.set_volume(self.volumen_efectos * 0.5)
        if self.sonido_corazon:
            self.sonido_corazon.set_volume(self.volumen_efectos * 0.7)
        if self.sonido_notificacion:
            self.sonido_notificacion.set_volume(self.volumen_efectos * 0.6)
        if self.sonido_pocion:
            self.sonido_pocion.set_volume(self.volumen_efectos * 0.7)
        if self.sonido_recoger_llave:
            self.sonido_recoger_llave.set_volume(self.volumen_efectos * 0.7)
        if self.sonido_rayo:
            self.sonido_rayo.set_volume(self.volumen_efectos * 0.7)
    
    def guardar_resultado(self):
        with open("resultados.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {self.jugador.nombre} | Nivel {self.numero_nivel} | {self.resultado} | Puntos: {self.puntos} | Enemigos: {self.enemigos_derrotados}\n")



