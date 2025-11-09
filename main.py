import pygame
import sys
import os
from juego import juego

print("=" * 60)
print("FEAR OF WAYS 0 - Inicializando...")
print("=" * 60)

# Inicializar Pygame
try:
    pygame.init()
    print("Pygame inicializado correctamente")
except Exception as e:
    print(f"Error al inicializar Pygame: {e}")
    sys.exit(1)

# Configurar ventana
try:
    info = pygame.display.Info()
    ventana = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    print(f"Ventana creada: {info.current_w}x{info.current_h} (Pantalla completa)")
except Exception as e:
    print(f" No se pudo crear ventana en pantalla completa, usando 1280x720")
    ventana = pygame.display.set_mode((1280, 720))

# Inicializar sistema de audio
try:
    pygame.mixer.init()
    print("Sistema de audio inicializado")
    
    # Cargar música de fondo
    try:
        pygame.mixer.music.load("audio/musica_fondo.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)
        print("Música de fondo cargada y reproduciendo")
    except (pygame.error, FileNotFoundError):
        print(" Advertencia: No se pudo cargar audio/musica_fondo.mp3")
        print("  El juego continuará sin música de fondo")
except Exception as e:
    print(f"Sistema de audio no disponible: {e}")


# cargar texturas después de iniciar pygame
def cargar_texturas():
    ruta_muro = os.path.join(os.path.dirname(__file__), 'images', 'wall_texture.png')
    ruta_suelo = os.path.join(os.path.dirname(__file__), 'images', 'floor_texture.png')
    try:
        textura_muro = pygame.image.load(ruta_muro).convert()
        textura_suelo = pygame.image.load(ruta_suelo).convert()
    except:
        textura_muro = None
        textura_suelo = None
    return textura_muro, textura_suelo

if __name__ == "__main__":
    try:
        # Cargar texturas y crear juego
        textura_muro, textura_suelo = cargar_texturas()
        import pared
        import nivel
        pared.TEXTURA_MURO = textura_muro
        nivel.TEXTURA_SUELO = textura_suelo
        
        # Cargar icono de llave para usar tanto en el HUD como en el mapa
        ruta_llave = os.path.join(os.path.dirname(__file__), 'images', 'key_icon.png')
        try:
            icono_llave = pygame.image.load(ruta_llave).convert_alpha()
            print("Icono de llave cargado para el mapa")
        except (pygame.error, FileNotFoundError):
            icono_llave = None
            print("Advertencia: images/key_icon.png no encontrado para el mapa")
        
        nivel.ICONO_LLAVE = icono_llave
        
        print("\n" + "=" * 60)
        print("INICIANDO JUEGO...")
        print("=" * 60 + "\n")
        
        # Crear instancia del juego y ejecutar
        juego_inst = juego()
        juego_inst.ejecutar()
        
    except KeyboardInterrupt:
        print("\n\nJuego interrumpido por el usuario")
    except Exception as e:
        print(f"\n\nError crítico durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("Cerrando Fear of Ways 0...")
        print("=" * 60)
        pygame.quit()
        sys.exit(0)
