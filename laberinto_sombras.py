import pygame
import sys

# Inicialización
pygame.init()
ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El Laberinto de las Sombras")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (40, 40, 40)

# Fuente
fuente = pygame.font.Font(None, 60)
fuente_peq = pygame.font.Font(None, 36)

# Control de estados
ESTADO = "menu"  # "menu", "jugando", "fin"
resultado = ""   # "ganaste" o "perdiste"

# Jugador
jugador = pygame.Rect(380, 280, 40, 40)
velocidad = 5

# Reloj
clock = pygame.time.Clock()


# --- Funciones ---

def dibujar_texto(texto, tam, color, x, y, centrado=True):
    font = pygame.font.Font(None, tam)
    superficie = font.render(texto, True, color)
    rect = superficie.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    ventana.blit(superficie, rect)


def menu():
    ventana.fill(NEGRO)
    dibujar_texto("El Laberinto de las Sombras", 60, BLANCO, ANCHO // 2, 150)
    dibujar_texto("Presiona ENTER para jugar", 36, BLANCO, ANCHO // 2, 300)
    dibujar_texto("Presiona ESC para salir", 36, BLANCO, ANCHO // 2, 350)


def juego():
    ventana.fill(GRIS)
    pygame.draw.rect(ventana, (200, 200, 0), jugador)  # Jugador amarillo temporal

    # Aquí luego se agregará el efecto de linterna, enemigos, colisiones, etc.
    dibujar_texto("Movete con las flechas o WASD", 30, BLANCO, 10, 10, centrado=False)


def pantalla_final():
    ventana.fill(NEGRO)
    if resultado == "ganaste":
        color = (0, 255, 0)
        mensaje = "¡Escapaste del laberinto!"
    else:
        color = (255, 0, 0)
        mensaje = "Fuiste atrapado en la oscuridad..."
    dibujar_texto(mensaje, 50, color, ANCHO // 2, 250)
    dibujar_texto("Presiona ENTER para volver al menú", 36, BLANCO, ANCHO // 2, 350)


# --- Bucle principal ---
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Controles generales
        if ESTADO == "menu":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    ESTADO = "jugando"
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        elif ESTADO == "fin":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    ESTADO = "menu"

    # Lógica del juego
    if ESTADO == "jugando":
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            jugador.x -= velocidad
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            jugador.x += velocidad
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            jugador.y -= velocidad
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            jugador.y += velocidad

        # Límites del mapa
        if jugador.left < 0: jugador.left = 0
        if jugador.right > ANCHO: jugador.right = ANCHO
        if jugador.top < 0: jugador.top = 0
        if jugador.bottom > ALTO: jugador.bottom = ALTO

        # Ejemplo de condición de victoria temporal
        if jugador.x > 750 and jugador.y > 550:
            resultado = "ganaste"
            ESTADO = "fin"

    # Render según estado
    if ESTADO == "menu":
        menu()
    elif ESTADO == "jugando":
        juego()
    elif ESTADO == "fin":
        pantalla_final()

    pygame.display.flip()
    clock.tick(60)
