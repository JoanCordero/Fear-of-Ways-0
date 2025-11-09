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
        self.opcion_pausa = 0  # 0: Reanudar, 1: Reiniciar, 2: Menú Principal, 3: Volumen
        self.puntos = 0  # Sistema de puntuación
        self.enemigos_derrotados = 0  # Contador de enemigos
        self.volumen_musica = 0.3  # Volumen de música (0.0 a 1.0)
        self.volumen_efectos = 0.7  # Volumen de efectos (0.0 a 1.0)
        self.mostrar_tutorial = True  # Mostrar tutorial en el primer nivel
        self.tutorial_mostrado = False  # Controlar si ya se mostró

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
        print("\n🔊 Cargando recursos de audio...")
        try:
            self.sonido_disparo = pygame.mixer.Sound("audio/disparo.mp3")
            self.sonido_disparo.set_volume(0.7)
            print("  ✓ Sonido de disparo cargado correctamente")
        except (pygame.error, FileNotFoundError) as e:
            self.sonido_disparo = None
            print(f"  ⚠ Advertencia: No se pudo cargar audio/disparo.mp3")
        
        try:
            self.sonido_golpe = pygame.mixer.Sound("audio/daño.mp3")
            self.sonido_golpe.set_volume(0.5)
            print("  ✓ Sonido de golpe cargado correctamente")
        except (pygame.error, FileNotFoundError) as e:
            self.sonido_golpe = None
            print(f"  ⚠ Advertencia: No se pudo cargar audio/daño.mp3")
        
        # Usar el sonido de golpe para bonus (alternativa)
        self.sonido_bonus = self.sonido_golpe
        print("  ✓ Audio inicializado\n")

        # Carga de recursos gráficos para HUD y menú
        # Almacenamos el directorio actual para localizar imágenes
        self._dir = os.path.dirname(__file__)

        # Tamaño base de los iconos para el HUD. Al usar un tamaño único se simplifica
        # el diseño y se consigue un aspecto más minimalista. 28 píxeles funciona bien en
        # la mayoría de resoluciones. Si falla la carga, los iconos simplemente no se dibujan.
        icon_size = 28

        # Cargar iconos del HUD con manejo de errores mejorado
        print("🎨 Cargando recursos gráficos...")
        
        # Cargar icono del corazón (vida)
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'heart.png')).convert_alpha()
            self.heart_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("  ✓ Icono de corazón cargado")
        except (pygame.error, FileNotFoundError):
            self.heart_img = None
            print("  ⚠ Advertencia: images/heart.png no encontrado, se usará fallback")

        # Cargar icono de la llave
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'key_icon.png')).convert_alpha()
            self.key_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("  ✓ Icono de llave cargado")
        except (pygame.error, FileNotFoundError):
            self.key_img = None
            print("  ⚠ Advertencia: images/key_icon.png no encontrado, se usará fallback")

        # Cargar icono del rayo
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'lightning.png')).convert_alpha()
            self.lightning_img = pygame.transform.smoothscale(img, (icon_size, icon_size))
            print("  ✓ Icono de rayo cargado")
        except (pygame.error, FileNotFoundError):
            self.lightning_img = None
            print("  ⚠ Advertencia: images/lightning.png no encontrado, se usará fallback")

        # No usamos un marco externo para el menú, así que desactivamos cualquier intento de cargar menu_frame_img
        self.menu_frame_img = None

        # Cargar textura oscura para el HUD
        try:
            tex = pygame.image.load(os.path.join(self._dir, 'images', 'hud_bar_texture.png')).convert()
            self.hud_texture = tex
            print("  ✓ Textura de HUD cargada")
        except (pygame.error, FileNotFoundError):
            self.hud_texture = None
            print("  ⚠ Advertencia: images/hud_bar_texture.png no encontrado, se usará color sólido")

        # Cargar icono del corazón para bonus de vida en el mapa
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'heart.png')).convert_alpha()
            self.heart_bonus_img = pygame.transform.scale(img, (15, 15))
            print("  ✓ Icono de bonus de vida cargado")
        except (pygame.error, FileNotFoundError):
            self.heart_bonus_img = None
            print("  ⚠ Advertencia: Bonus de vida usará fallback")

        # Cargar icono del rayo para bonus de energía en el mapa
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'lightning.png')).convert_alpha()
            self.lightning_bonus_img = pygame.transform.scale(img, (15, 15))
            print("  ✓ Icono de bonus de energía cargado")
        except (pygame.error, FileNotFoundError):
            self.lightning_bonus_img = None
            print("  ⚠ Advertencia: Bonus de energía usará fallback")
        
        # Cargar icono de poción para power-ups
        try:
            img = pygame.image.load(os.path.join(self._dir, 'images', 'posion.png')).convert_alpha()
            self.posion_img = pygame.transform.scale(img, (15, 15))
            print("  ✓ Icono de poción cargado")
        except (pygame.error, FileNotFoundError):
            self.posion_img = None
            print("  ⚠ Advertencia: images/posion.png no encontrado, se usará fallback")
        
        print("  ✓ Recursos gráficos inicializados\n")

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

        # Ya no dibujamos un marco ni un cuadro; el fondo se muestra completamente.
        # Título y subtítulo del menú. Se posicionan en la parte superior de la pantalla.
        title_size = int(alto * 0.09)
        self.dibujar_texto("Fear of Ways", title_size, BLANCO, ancho // 2, int(alto * 0.18))
        subtitle_size = int(alto * 0.035)
        self.dibujar_texto("Explora las mazmorras", subtitle_size, (210, 200, 190), ancho // 2, int(alto * 0.26))

        # Definición de las opciones del menú. Se eliminan los dos puntos y los puntos finales
        # para lograr un aspecto más limpio. Estas cadenas pueden ser adaptadas según el juego.
        opciones = [
            "Selecciona tu personaje",
            "1 Explorador",
            "2 Cazador",
            "3 Ingeniero",
        ]

        # Obtener posición del mouse para hover
        mx, my = pygame.mouse.get_pos()
        
        # Calculamos el área vertical donde se dibujarán las opciones. Ajustamos el rango
        # para que el texto quede más cerca del centro de la pantalla y armonice con el fondo.
        area_y_start = int(alto * 0.45)
        area_y_end = int(alto * 0.72)
        area_height = area_y_end - area_y_start
        num_lines = len(opciones)
        
        # Determinar el tamaño base de la fuente en función del espacio disponible.
        base_size = int(area_height / (num_lines + 2))
        spacing = int(alto * 0.09)  # Espaciado más amplio
        
        # Dibujar el título "Selecciona tu personaje" con estilo especial
        title_opciones = int(base_size * 1.1)
        try:
            font_title = pygame.font.Font(self.font_path, title_opciones)
        except Exception:
            font_title = pygame.font.Font(None, title_opciones)
        
        surf_title = font_title.render(opciones[0], True, (255, 215, 100))
        x_title = ancho // 2 - surf_title.get_width() // 2
        y_title = area_y_start
        pantalla.blit(surf_title, (x_title, y_title))
        
        # Dibujar línea decorativa debajo del título
        line_y = y_title + surf_title.get_height() + 10
        line_start = ancho // 2 - 150
        line_end = ancho // 2 + 150
        pygame.draw.line(pantalla, (255, 215, 100), (line_start, line_y), (line_end, line_y), 2)
        
        # Dibujar opciones de personaje con hover mejorado
        y_opciones_start = line_y + int(alto * 0.06)
        
        for i in range(1, len(opciones)):
            text = opciones[i]
            y_pos = y_opciones_start + (i - 1) * spacing
            
            # Tamaño base de la fuente
            size = int(base_size * 1.2)
            
            try:
                font = pygame.font.Font(self.font_path, size)
            except Exception:
                font = pygame.font.Font(None, size)
            
            # Renderizar texto para obtener dimensiones
            surf_temp = font.render(text, True, (235, 225, 210))
            x_base = ancho // 2 - surf_temp.get_width() // 2
            
            # Área expandida para detección de hover (más generosa)
            padding = 20
            rect_opcion = pygame.Rect(x_base - padding, y_pos - padding, 
                                     surf_temp.get_width() + padding * 2, 
                                     surf_temp.get_height() + padding * 2)
            is_hover = rect_opcion.collidepoint(mx, my)
            
            if is_hover:
                # Efecto de hover más sutil: solo cambio de color y tamaño ligero
                size_hover = int(size * 1.05)  # Crecimiento más sutil (5% en vez de 15%)
                try:
                    font_hover = pygame.font.Font(self.font_path, size_hover)
                except Exception:
                    font_hover = pygame.font.Font(None, size_hover)
                
                # Texto resaltado en amarillo sin efectos exagerados
                surf_main = font_hover.render(text, True, (255, 230, 100))
                x_text = ancho // 2 - surf_main.get_width() // 2
                pantalla.blit(surf_main, (x_text, y_pos))
                
            else:
                # Estado normal: color beige suave
                surf = font.render(text, True, (210, 200, 190))
                x = ancho // 2 - surf.get_width() // 2
                pantalla.blit(surf, (x, y_pos))

        # Mensaje para salir del menú al pie de la pantalla
        exit_size = int(alto * 0.028)
        self.dibujar_texto("ESC para salir", exit_size, (180, 180, 190), ancho // 2, int(alto * 0.92))

    # -------------------------------------------------------
    # INICIO Y CARGA DE JUEGO
    # -------------------------------------------------------
    def iniciar_juego(self, tipo_personaje):
        self._guardado = False
        self.puntos = 0  # Resetear puntuación
        self.enemigos_derrotados = 0  # Resetear contador
        self.tutorial_mostrado = False  # Resetear tutorial
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
        pygame.mouse.set_visible(False)  # Ocultar cursor durante el juego

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

    def cargar_nivel(self, numero):
        self.numero_nivel = numero
        # Limpiar nivel anterior completamente
        self.nivel_actual = None
        # Crear nuevo nivel con llaves frescas
        self.nivel_actual = nivel(numero)
        self.camara = camara(self.nivel_actual.ancho, self.nivel_actual.alto)
        self.enemigos.clear()
        self.proyectiles.clear()

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

    # -------------------------------------------------------
    # GENERACIÓN DE BONUS POR NIVEL
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # BUCLE PRINCIPAL DE JUEGO
    # -------------------------------------------------------
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
            
            # Actualizar temporizador si está activo
            if self.temporizador_activo and self.tiempo_restante > 0:
                self.tiempo_restante -= 1
                
                # Advertencia cuando quedan 30 segundos
                if self.tiempo_restante == 30 * 60:
                    self.mensaje_temporal = "⚠️ ¡QUEDAN 30 SEGUNDOS! ⚠️"
                    self.mensaje_timer = 120
                # Advertencia cuando quedan 10 segundos
                elif self.tiempo_restante == 10 * 60:
                    self.mensaje_temporal = "⚠️ ¡SOLO 10 SEGUNDOS! ⚠️"
                    self.mensaje_timer = 120
                    
            # Si el tiempo se acaba, spawear enemigos continuamente
            elif self.temporizador_activo and self.tiempo_restante <= 0 and not self.tiempo_agotado:
                self.tiempo_agotado = True
                self.mensaje_temporal = "💀 ¡TIEMPO AGOTADO! ¡ENEMIGOS INVADEN! 💀"
                self.mensaje_timer = 180
            
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
                enemigo_actual.mover(muros_bloq, self.nivel_actual.ancho, self.nivel_actual.alto, self.jugador, self.nivel_actual.escondites)
            enemigo_actual.dibujar(area_juego, self.camara)

            # Los enemigos ya NO dañan por contacto directo
            # Cada tipo tiene su propio sistema de ataque con cooldowns
            # Verificar si el jugador murió después de los ataques específicos
            if not pausado and not tutorial_activo and self.jugador.vida <= 0:
                self.resultado = "perdiste"
                self.estado = "fin"

        # Actualizar duración de power-ups activos
        if not pausado and not tutorial_activo and self.powerup_duracion > 0:
            self.powerup_duracion -= 1
            if self.powerup_duracion <= 0:
                self.desactivar_powerup()
        
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
                    texto = font.render("[CLICK IZQ]", True, (255, 255, 255))
                    center = rect_pantalla.center
                    texto_rect = texto.get_rect(center=(center[0], center[1] - 15))
                    area_juego.blit(texto, texto_rect)
            
            # Recoger bonus instantáneos (vida, energía)
            if not pausado and not tutorial_activo and self.jugador.rect.colliderect(rect):
                if tipo == "vida":
                    self.jugador.vida = min(self.jugador.vida_max, self.jugador.vida + 1)
                    if self.sonido_bonus:
                        self.sonido_bonus.play()
                    self.nivel_actual.bonus.remove(bonus)
                elif tipo == "energia":
                    self.jugador.energia = min(self.jugador.energia_max, self.jugador.energia + 20)
                    if self.sonido_bonus:
                        self.sonido_bonus.play()
                    self.nivel_actual.bonus.remove(bonus)
        
        # Recoger llaves (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo:
            for llave in list(getattr(self.nivel_actual, "llaves", [])):
                if self.jugador.rect.colliderect(llave):
                    self.nivel_actual.llaves.remove(llave)
                    if self.sonido_bonus:
                        self.sonido_bonus.play()
                    # Mensaje visual de llave recogida
                    llaves_restantes = len(self.nivel_actual.llaves)
                    if llaves_restantes == 0:
                        # ¡TODAS LAS LLAVES RECOGIDAS! - ACTIVAR TEMPORIZADOR
                        self.activar_temporizador()
                        tiempo_seg = int(self.tiempo_restante / 60)
                        minutos = tiempo_seg // 60
                        segundos = tiempo_seg % 60
                        self.mensaje_temporal = f"¡SALIDA ABIERTA! TIENES {minutos}:{segundos:02d} PARA ESCAPAR"
                        self.mensaje_timer = 180  # 3 segundos a 60 FPS
                    else:
                        self.mensaje_temporal = f"¡Llave recogida! Faltan {llaves_restantes}"
                        self.mensaje_timer = 90  # 1.5 segundos
        
        # Interactuar con palancas (presionar E cerca de una palanca)
        if not pausado and not tutorial_activo:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_e]:
                for i, palanca_rect in enumerate(getattr(self.nivel_actual, "palancas", [])):
                    # Verificar si el jugador está cerca de la palanca
                    if self.jugador.rect.inflate(40, 40).colliderect(palanca_rect):
                        # Activar/desactivar la puerta correspondiente
                        id_puerta = self.obtener_id_puerta_por_indice(i)
                        if id_puerta and id_puerta in self.nivel_actual._puertas_por_id:
                            puertas = self.nivel_actual._puertas_por_id[id_puerta]
                            for puerta in puertas:
                                puerta.abierta = not puerta.abierta
                                # No necesitamos establecer bloquea, es una propiedad calculada automáticamente
                            
                            estado = "abierta" if puertas[0].abierta else "cerrada"
                            self.mensaje_temporal = f"¡Puerta {estado}!"
                            self.mensaje_timer = 60
                            if self.sonido_bonus:
                                self.sonido_bonus.play()
                            break

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
        
        # Verificar proximidad a la puerta de salida y mostrar mensaje (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo and self.nivel_actual.salida:
            llaves_restantes = len(getattr(self.nivel_actual, "llaves", []))
            cerca, mensaje = self.nivel_actual.salida.verificar_proximidad_jugador(
                self.jugador.rect, llaves_restantes
            )
            if cerca and mensaje:
                indicador_y = int(alto * 0.15)
                color_texto = (255, 100, 100) if llaves_restantes > 0 else (100, 255, 100)
                self.dibujar_texto(mensaje, int(alto * 0.04), color_texto, ancho // 2, indicador_y)
        
        # Indicador de interacción con palancas (solo si no está pausado y tutorial no activo)
        if not pausado and not tutorial_activo:
            for palanca_rect in getattr(self.nivel_actual, "palancas", []):
                if self.jugador.rect.inflate(40, 40).colliderect(palanca_rect):
                    # Mostrar indicador de "Presiona E"
                    indicador_y = int(alto * 0.15)
                    self.dibujar_texto("[E] para activar palanca", int(alto * 0.04), 
                                      (255, 255, 100), ancho // 2, indicador_y)
                    break
        
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
                self.pantalla_nivel_completado(tiempo_bonus)
                self.cargar_nivel(self.numero_nivel + 1)
            else:
                self.resultado = "ganaste"
                self.estado = "fin"

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
                font_key = pygame.font.Font(self.font_path, font_key_size)
            except Exception:
                font_key = pygame.font.Font(None, font_key_size)
            txt = font_key.render(f"{llaves_recogidas}/{llaves_totales}", True, (240, 220, 100))
            pantalla.blit(txt, (x_cursor, y_center - txt.get_height() // 2))
            x_cursor += txt.get_width() + 5
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
                font_t = pygame.font.Font(self.font_path, font_size_lvl)
            except Exception:
                font_t = pygame.font.Font(None, font_size_lvl)
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
                font_nombre = pygame.font.Font(self.font_path, font_size_nombre)
            except Exception:
                font_nombre = pygame.font.Font(None, font_size_nombre)
            
            surf_nombre = font_nombre.render(nombre, True, color_principal)
            
            # Si el texto es muy ancho, reducir más el tamaño
            if surf_nombre.get_width() > (bg_rect.width - 10):
                font_size_nombre = max(6, int(alto_header * 0.25))
                try:
                    font_nombre = pygame.font.Font(self.font_path, font_size_nombre)
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
        
        # Oscurecer la pantalla
        overlay = pygame.Surface((ancho, alto))
        overlay.set_alpha(180)
        overlay.fill(NEGRO)
        pantalla.blit(overlay, (0, 0))
        
        # Título
        self.dibujar_texto("PAUSA", int(alto * 0.1), AMARILLO, ancho // 2, alto * 0.15)
        
        # Estadísticas de la partida actual
        stats_y = alto * 0.28
        self.dibujar_texto(f"Puntos: {self.puntos}", int(alto * 0.035), BLANCO, ancho // 2, stats_y)
        self.dibujar_texto(f"Enemigos Derrotados: {self.enemigos_derrotados}", int(alto * 0.035), BLANCO, ancho // 2, stats_y + alto * 0.05)
        self.dibujar_texto(f"Nivel: {self.numero_nivel}/3", int(alto * 0.035), BLANCO, ancho // 2, stats_y + alto * 0.1)
        
        # Obtener posición del mouse para hover
        mx, my = pygame.mouse.get_pos()
        
        # Opciones del menú
        opciones = ["Reanudar", "Reiniciar Nivel", "Menú Principal"]
        y_inicial = alto * 0.5
        espaciado = alto * 0.08
        
        for i, opcion in enumerate(opciones):
            y_opcion = y_inicial + i * espaciado
            
            # Verificar si el mouse está sobre esta opción
            tam = int(alto * 0.05) if i == self.opcion_pausa else int(alto * 0.045)
            try:
                font = pygame.font.Font(self.font_path, tam)
            except Exception:
                font = pygame.font.Font(None, tam)
            
            text_surface = font.render(f"  {opcion}", True, BLANCO)
            text_rect = text_surface.get_rect(center=(ancho // 2, y_opcion))
            is_hover = text_rect.collidepoint(mx, my)
            
            # Determinar color y tamaño según selección con teclado o hover con mouse
            if is_hover:
                color = AMARILLO
                tam = int(alto * 0.05)
            elif i == self.opcion_pausa:
                color = BLANCO
                tam = int(alto * 0.05)
            else:
                color = GRIS
                tam = int(alto * 0.045)
            
            prefijo = "> " if i == self.opcion_pausa else "  "
            self.dibujar_texto(f"{prefijo}{opcion}", tam, color, ancho // 2, y_opcion)
        
        # Controles de volumen
        vol_y = alto * 0.75
        self.dibujar_texto("VOLUMEN", int(alto * 0.04), AMARILLO, ancho // 2, vol_y)
        
        # Barra de volumen música
        vol_musica_porcentaje = int(self.volumen_musica * 100)
        self.dibujar_texto(f"Música: {vol_musica_porcentaje}%", int(alto * 0.03), BLANCO, 
                          ancho // 2 - int(ancho * 0.15), vol_y + alto * 0.05)
        
        # Barra de volumen efectos
        vol_efectos_porcentaje = int(self.volumen_efectos * 100)
        self.dibujar_texto(f"Efectos: {vol_efectos_porcentaje}%", int(alto * 0.03), BLANCO, 
                          ancho // 2 + int(ancho * 0.15), vol_y + alto * 0.05)
        
        # Controles
        self.dibujar_texto("↑↓ para navegar | ENTER para seleccionar | P/ESC para reanudar", 
                          int(alto * 0.025), GRIS, ancho // 2, alto * 0.88)
        self.dibujar_texto("←→ para ajustar volumen de música | [ ] para ajustar efectos", 
                          int(alto * 0.025), GRIS, ancho // 2, alto * 0.92)
    
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
        pantalla.fill(NEGRO)
        titulo = "¡Escapaste de las 3 mazmorras!" if self.resultado == "ganaste" else "Fuiste atrapado..."
        color = VERDE if self.resultado == "ganaste" else ROJO
        self.dibujar_texto(titulo, int(alto * 0.08), color, ancho // 2, alto * 0.3)
        
        # Mostrar estadísticas
        self.dibujar_texto(f"Puntuación Final: {self.puntos}", int(alto * 0.05), AMARILLO, ancho // 2, alto * 0.42)
        self.dibujar_texto(f"Enemigos Derrotados: {self.enemigos_derrotados}", int(alto * 0.04), BLANCO, ancho // 2, alto * 0.5)
        self.dibujar_texto(f"Personaje: {self.jugador.nombre}", int(alto * 0.04), self.jugador.color, ancho // 2, alto * 0.56)
        
        self.dibujar_texto("ENTER para volver al menú", int(alto * 0.035), GRIS, ancho // 2, alto * 0.7)
        if not self._guardado:
            self.guardar_resultado()
            self._guardado = True

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
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_ESCAPE:
                            pygame.quit(); return
                        if e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            self.iniciar_juego(int(e.key - pygame.K_0))
                    # Soporte de mouse en el menú principal
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        pantalla = pygame.display.get_surface()
                        ancho, alto = pantalla.get_size()
                        
                        # Verificar clicks en las opciones de personaje
                        # Áreas aproximadas donde aparecen las opciones
                        area_y_start = int(alto * 0.45)
                        area_y_end = int(alto * 0.70)
                        
                        # Opción 1 - Explorador
                        if area_y_start + int(alto * 0.08) < my < area_y_start + int(alto * 0.16):
                            self.iniciar_juego(1)
                        # Opción 2 - Cazador
                        elif area_y_start + int(alto * 0.16) < my < area_y_start + int(alto * 0.24):
                            self.iniciar_juego(2)
                        # Opción 3 - Ingeniero
                        elif area_y_start + int(alto * 0.24) < my < area_y_start + int(alto * 0.32):
                            self.iniciar_juego(3)

                elif self.estado == "jugando":
                    # Cerrar tutorial con ENTER
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and not self.tutorial_mostrado:
                        self.tutorial_mostrado = True
                    
                    # Solo permitir pausar si el tutorial ya fue cerrado
                    elif e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_p):
                        if self.tutorial_mostrado or self.numero_nivel > 1:
                            self.estado = "pausado"
                            self.opcion_pausa = 0

                    # Ataque a distancia (click derecho o tecla ESPACIO) - solo si el tutorial fue cerrado
                    elif ((e.type == pygame.MOUSEBUTTONDOWN and e.button == 3) or \
                         (e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE)) and \
                         (self.tutorial_mostrado or self.numero_nivel > 1):
                        if self.jugador.cooldown_disparo == 0:
                            self.disparar_proyectil()

                    # Click izquierdo - verificar si es para activar power-up o ataque
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and \
                         (self.tutorial_mostrado or self.numero_nivel > 1):
                        # Obtener posición del mouse en el mundo
                        pantalla = pygame.display.get_surface()
                        ancho, alto = pantalla.get_size()
                        offset_header = int(alto * self.altura_header)
                        mx, my = pygame.mouse.get_pos()
                        my_ajustado = my - offset_header
                        
                        # Convertir posición de pantalla a mundo
                        mundo_x = mx / self.camara.zoom + self.camara.offset_x
                        mundo_y = my_ajustado / self.camara.zoom + self.camara.offset_y
                        punto_mouse = pygame.Rect(mundo_x - 5, mundo_y - 5, 10, 10)
                        
                        # Verificar si se clickeó un power-up
                        powerup_activado = False
                        for bonus in list(getattr(self.nivel_actual, "bonus", [])):
                            if bonus["tipo"] in ["vision_clara", "disparo_doble", "super_velocidad", "escudo"]:
                                if punto_mouse.colliderect(bonus["rect"]):
                                    # Activar power-up y removerlo
                                    self.activar_powerup(bonus["tipo"])
                                    self.nivel_actual.bonus.remove(bonus)
                                    powerup_activado = True
                                    break
                        
                        # Si no activó power-up, hacer ataque cuerpo a cuerpo
                        if not powerup_activado:
                            self.ataque_corto()

                elif self.estado == "pausado":
                    # Mostrar cursor en menú de pausa
                    pygame.mouse.set_visible(True)
                    
                    if e.type == pygame.KEYDOWN:
                        if e.key in (pygame.K_ESCAPE, pygame.K_p):
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
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)  # Ocultar al reanudar
                            elif self.opcion_pausa == 1:  # Reiniciar nivel
                                self.cargar_nivel(self.numero_nivel)
                                self.estado = "jugando"
                                pygame.mouse.set_visible(False)  # Ocultar al reanudar
                            elif self.opcion_pausa == 2:  # Menú principal
                                self.estado = "menu"
                                pygame.mouse.set_visible(True)  # Mostrar cursor en menú
                    
                    # Soporte de mouse en menú de pausa
                    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        pantalla = pygame.display.get_surface()
                        ancho, alto = pantalla.get_size()
                        
                        y_inicial = alto * 0.5
                        espaciado = alto * 0.08
                        
                        # Verificar clicks en las opciones del menú
                        for i in range(3):
                            y_opcion = y_inicial + i * espaciado
                            # Área clickeable aproximada (altura de cada opción)
                            if y_opcion - alto * 0.03 < my < y_opcion + alto * 0.03:
                                if i == 0:  # Reanudar
                                    self.estado = "jugando"
                                    pygame.mouse.set_visible(False)  # Ocultar al reanudar
                                elif i == 1:  # Reiniciar nivel
                                    self.cargar_nivel(self.numero_nivel)
                                    self.estado = "jugando"
                                    pygame.mouse.set_visible(False)  # Ocultar al reanudar
                                elif i == 2:  # Menú principal
                                    self.estado = "menu"
                                    pygame.mouse.set_visible(True)
                                break
                        
                        # Verificar clicks en controles de volumen
                        vol_y = alto * 0.75
                        
                        # Música (izquierda)
                        musica_x = ancho // 2 - int(ancho * 0.15)
                        if vol_y + alto * 0.03 < my < vol_y + alto * 0.07:
                            # Click en área de música
                            if mx < musica_x - 50:  # Zona izquierda - disminuir
                                self.volumen_musica = max(0.0, self.volumen_musica - 0.25)
                                pygame.mixer.music.set_volume(self.volumen_musica)
                            elif mx > musica_x + 50:  # Zona derecha - aumentar
                                self.volumen_musica = min(1.0, self.volumen_musica + 0.25)
                                pygame.mixer.music.set_volume(self.volumen_musica)
                        
                        # Efectos (derecha)
                        efectos_x = ancho // 2 + int(ancho * 0.15)
                        if vol_y + alto * 0.03 < my < vol_y + alto * 0.07:
                            # Click en área de efectos
                            if mx > efectos_x - 150 and mx < efectos_x - 50:  # Zona izquierda - disminuir
                                self.volumen_efectos = max(0.0, self.volumen_efectos - 0.25)
                                self.actualizar_volumen_efectos()
                            elif mx > efectos_x + 50:  # Zona derecha - aumentar
                                self.volumen_efectos = min(1.0, self.volumen_efectos + 0.25)
                                self.actualizar_volumen_efectos()
                
                elif self.estado == "fin" and e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                    self.estado = "menu"
                    pygame.mouse.set_visible(True)  # Mostrar cursor en menú

            if self.estado == "menu":
                self.menu()
            elif self.estado == "jugando":
                self.jugar(pausado=False)
            elif self.estado == "pausado":
                self.jugar(pausado=True)  # Mantener el juego visible pero pausado
                self.menu_pausa()  # Dibujar el menú de pausa encima
            elif self.estado == "fin":
                self.pantalla_final()

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
        
        self.jugador.cooldown_disparo = 20
        
        # Reproducir sonido de disparo
        if self.sonido_disparo:
            try:
                self.sonido_disparo.play()
            except Exception as e:
                print(f"Error al reproducir sonido: {e}")
    
    # -------------------------------------------------------
    # ATAQUE CORTO (melee)
    # -------------------------------------------------------
    def ataque_corto(self):
        alcance = 60
        ang = math.atan2(pygame.mouse.get_pos()[1] - self.jugador.rect.centery,
                         pygame.mouse.get_pos()[0] - self.jugador.rect.centerx)
        ataque_rect = pygame.Rect(0, 0, 40, 40)
        ataque_rect.center = (self.jugador.rect.centerx + math.cos(ang) * alcance,
                              self.jugador.rect.centery + math.sin(ang) * alcance)
        for enemigo_actual in list(self.enemigos):
            if ataque_rect.colliderect(enemigo_actual.rect):
                enemigo_actual.vida -= 1
                enemigo_actual.color = (255, 100, 100)
                if self.sonido_golpe:
                    self.sonido_golpe.play()
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
        
        if tipo == "vision_clara":
            # Ver todo claro por 5 segundos
            self.vision_normal = self.jugador.vision
            self.jugador.vision = 9999  # Visión infinita
            self.powerup_duracion = 5 * 60  # 5 segundos a 60 FPS
            self.mensaje_temporal = "👁 ¡VISIÓN CLARA ACTIVADA! (5s)"
            self.mensaje_timer = 120
            
        elif tipo == "disparo_doble":
            # Disparar doble por 30 segundos
            self.disparo_doble = True
            self.powerup_duracion = 30 * 60  # 30 segundos
            self.mensaje_temporal = "⚡ ¡DISPARO DOBLE ACTIVADO! (30s)"
            self.mensaje_timer = 120
            
        elif tipo == "super_velocidad":
            # Super rápido por 10 segundos
            self.velocidad_normal = self.jugador.velocidad_base
            self.jugador.velocidad_base *= 3.5  # Velocidad aumentada a 3.5x
            self.powerup_duracion = 10 * 60  # 10 segundos
            self.mensaje_temporal = "⚡ ¡SUPER VELOCIDAD ACTIVADA! (10s)"
            self.mensaje_timer = 120
            
        elif tipo == "escudo":
            # Escudo por 30 segundos
            self.escudo_activo = True
            self.powerup_duracion = 30 * 60  # 30 segundos
            self.mensaje_temporal = "🛡 ¡ESCUDO ACTIVADO! (30s)"
            self.mensaje_timer = 120
        
        if self.sonido_bonus:
            self.sonido_bonus.play()
    
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
            self.mensaje_temporal = "⏰ Power-up terminado"
            self.mensaje_timer = 60

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
        
        # Mostrar mensaje si se spawnearon enemigos
        if enemigos_spawneados > 0:
            self.mensaje_temporal = f"⚠️ ¡{enemigos_spawneados} nuevos enemigos han aparecido! ⚠️"
            self.mensaje_timer = 90  # 1.5 segundos

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
            "ESPACIO/Click Der - Disparar",
            "Click Izq - Ataque / Activar pociones"
        ]
        
        controles_der = [
            "E - Activar palancas",
            "P/ESC - Pausar",
            "",
            "Recoge llaves para escapar"
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
        if self.sonido_bonus:
            self.sonido_bonus.set_volume(self.volumen_efectos * 0.7)
    
    def obtener_id_puerta_por_indice(self, indice):
        """Devuelve el ID de la puerta correspondiente al índice de la palanca según el nivel"""
        if self.numero_nivel == 1:
            return "A1" if indice == 0 else None
        elif self.numero_nivel == 2:
            mapeo = {0: "N2_P1", 1: "N2_P2", 2: "N2_P3"}
            return mapeo.get(indice)
        elif self.numero_nivel == 3:
            mapeo = {0: "N3_P1", 1: "N3_P2", 2: "N3_P3", 3: "N3_P4", 4: "N3_P5"}
            return mapeo.get(indice)
        return None
    
    def guardar_resultado(self):
        with open("resultados.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {self.jugador.nombre} | Nivel {self.numero_nivel} | {self.resultado} | Puntos: {self.puntos} | Enemigos: {self.enemigos_derrotados}\n")



