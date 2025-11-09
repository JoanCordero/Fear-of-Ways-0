# 🎮 Fear of Ways 0
### Juego de Supervivencia en Mazmorras Oscuras

---

## 📖 Descripción

**Fear of Ways 0** es un juego de supervivencia y exploración en mazmorras oscuras. El jugador debe navegar por laberintos peligrosos, recolectar llaves, evitar o combatir enemigos hostiles, y encontrar la salida antes de que se acabe el tiempo. Con un sistema de iluminación dinámico, mecánicas de sigilo y combate, y tres niveles con dificultad progresiva, el juego ofrece una experiencia de tensión y estrategia.

---

## ✨ Características Principales

- 🗝️ **3 Niveles Únicos**: Cada mazmorra tiene un diseño y mecánicas distintas
- 👤 **3 Personajes Jugables**: Cada uno con estadísticas y habilidades únicas
- 🤖 **IA de Enemigos Avanzada**: 3 tipos de enemigos con comportamientos diferentes
- 💡 **Sistema de Iluminación Dinámica**: Linterna cónica que limita la visibilidad
- 🧭 **Exploración Estratégica**: Laberintos con rutas alternativas y secretos
- ⏱️ **Temporizador de Escape**: Presión temporal tras recolectar todas las llaves
- 🎯 **Dificultad Progresiva**: Cada nivel aumenta el desafío
- 🎨 **Animaciones Personalizadas**: Sprites animados para todas las acciones
- 🔊 **Efectos de Sonido**: Música de fondo y efectos de audio inmersivos

---

## 🎯 Requisitos del Sistema

### Software Necesario
- **Python**: Versión 3.9 o superior
- **Pygame**: Versión 2.0 o superior

### Recursos de Hardware Recomendados
- Procesador de doble núcleo
- 2 GB de RAM
- Tarjeta gráfica con soporte OpenGL
- 100 MB de espacio en disco

---

## 📥 Instalación

### Opción 1: Instalación Rápida
```bash
# Clonar o descargar el repositorio
cd "Fear of Ways 0"

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el juego
python main.py
```

### Opción 2: Instalación Manual
```bash
# Instalar Pygame
pip install pygame

# Ejecutar el juego
python main.py
```

---

## 🎮 Cómo Jugar

### Objetivo
Escapa de las 3 mazmorras recolectando todas las llaves y llegando a la salida antes de que se acabe el tiempo.

### Controles

#### Movimiento
- **W**: Mover hacia arriba
- **A**: Mover hacia la izquierda
- **S**: Mover hacia abajo
- **D**: Mover hacia la derecha
- **SHIFT**: Sprint (consume energía)

#### Combate
- **Click Izquierdo**: Ataque cuerpo a cuerpo
- **Click Derecho / ESPACIO**: Disparar proyectil (consume energía)
- **Mouse**: Apuntar linterna y dirección de ataque

#### Interacción
- **P / ESC**: Pausar juego

### Mecánicas del Juego

#### Sistema de Llaves
1. Busca las llaves dispersas por el nivel (color dorado)
2. Recoge todas las llaves del nivel
3. Una vez recolectadas todas, la salida se abre
4. Aparece un temporizador de escape

#### Temporizador de Escape
- **Nivel 1**: 2 minutos para escapar
- **Nivel 2**: 1.5 minutos para escapar
- **Nivel 3**: 1 minuto para escapar
- Si el tiempo se agota, enemigos aparecerán continuamente

#### Sistema de Energía
- La energía se usa para:
  - **Sprint**: Movimiento más rápido
  - **Disparar**: Ataque a distancia
- La energía se regenera automáticamente cuando no se usa

#### Consejos de Supervivencia
- Muévete con la linterna encendida para detectar enemigos a distancia
- Ahorra energía para sprintar en situaciones de peligro
- Escucha los efectos de sonido para anticipar amenazas

---

## 🛠️ Solución de Problemas

- **"Sistema de audio no disponible"**: En entornos sin dispositivo de audio (como servidores o contenedores), Pygame no puede inicializar el mezclador. El juego continuará ejecutándose, pero los efectos de sonido no estarán disponibles.
- **Advertencias al cargar archivos de sonido**: Si ves mensajes como `Advertencia: No se pudo cargar audio/disparo.mp3`, significa que el mezclador no se inicializó correctamente. Para solucionarlo, ejecuta el juego en un entorno con salida de audio o configura un driver de audio virtual.
- **El juego se cierra al presionar `Ctrl+C`**: Esto es normal en la versión de escritorio; el mensaje `Juego interrumpido por el usuario` indica que la salida fue controlada.

---

## 👥 Personajes

### 🔍 Explorador (1)
**Clase Equilibrada**
- ❤️ Vida: 5 corazones
- ⚡ Energía: 100
- 🏃 Velocidad: 4
- 👁️ Visión: 150
- **Ideal para**: Jugadores que buscan un balance entre todas las habilidades

### 🏹 Cazador (2)
**Clase Ágil**
- ❤️ Vida: 5 corazones
- ⚡ Energía: 70
- 🏃 Velocidad: 6
- 👁️ Visión: 120
- **Ideal para**: Jugadores que prefieren movilidad y evasión

### 🔧 Ingeniero (3)
**Clase Resistente**
- ❤️ Vida: 5 corazones
- ⚡ Energía: 120
- 🏃 Velocidad: 3
- 👁️ Visión: 180
- **Ideal para**: Jugadores que prefieren visibilidad y más tiempo de sprint

---

## 👾 Enemigos

### ⚡ Veloz (Amarillo)
- **Vida**: 2
- **Velocidad**: Alta
- **Ataque**: Cuerpo a cuerpo rápido
- **Estrategia**: Persigue agresivamente, ataca con advertencia visual

### 🔵 Acechador (Cian)
- **Vida**: 3
- **Velocidad**: Media
- **Ataque**: Proyectiles a distancia
- **Estrategia**: Mantiene distancia, dispara desde lejos

### 💪 Bruto (Rojo)
- **Vida**: 5
- **Velocidad**: Baja
- **Ataque**: Aura de ralentización + contacto
- **Estrategia**: Tanque lento con área de efecto

---

## 🗺️ Niveles

### Nivel 1: Las Catacumbas
- **Diseño**: Laberinto procedural con habitaciones tipo cueva
- **Mecánicas**: Búsqueda de llaves y rutas alternas
- **Dificultad**: Introducción, enemigos moderados
- **Llaves**: 3-4 llaves requeridas

### Nivel 2: La Espiral Descendente
- **Diseño**: Laberinto en espiral hacia el centro
- **Mecánicas**: Secciones estrechas y emboscadas
- **Dificultad**: Intermedia, más enemigos y spawn más rápido
- **Llaves**: Distribuidas estratégicamente

### Nivel 3: El Abismo Profundo
- **Diseño**: Laberinto caótico con múltiples rutas
- **Mecánicas**: Enemigos agresivos y gestión del tiempo
- **Dificultad**: Alta, spawn muy rápido y tiempo limitado
- **Llaves**: Búsqueda desafiante

---

## 📊 Sistema de Progresión

### Aumento de Dificultad por Nivel

| Aspecto | Nivel 1 | Nivel 2 | Nivel 3 |
|---------|---------|---------|---------|
| **Enemigos Iniciales** | 6 | 8 | 10 |
| **Velocidad Enemigos** | 100% | 115% | 130% |
| **Intervalo de Spawn** | 20s | 10s | 5s |
| **Tiempo de Escape** | 2:00 | 1:30 | 1:00 |
| **Bonus de Vida** | 3 | 2 | 1 |

---

## 🎨 Recursos Visuales

### Assets Incluidos (en carpeta `images/`)
- `ingeniero_sheet.png`: Sprite sheet del personaje (1080x1080)
- `wall_texture.png`: Textura de muros
- `floor_texture.png`: Textura de suelo
- `key_icon.png`: Icono de llave
- `heart.png`: Icono de vida
- `lightning.png`: Icono de energía
- `menu_background.png`: Fondo del menú
- `hud_bar_texture.png`: Textura del HUD
- `posion.png`: Icono de poción

### Assets de Audio (en carpeta `audio/`)
- `musica_fondo.mp3`: Música ambiente
- `disparo.mp3`: Efecto de disparo
- `daño.mp3`: Efecto de daño

---

## 🏆 Consejos y Estrategias

### Para Principiantes
1. 🗝️ **Explora sistemáticamente**: Cubre todo el mapa metódicamente
2. 💡 **Usa la linterna**: Apunta hacia donde quieres ir
3. 🛡️ **Controla la distancia**: Mantén a los enemigos al borde de la luz de la linterna
4. ⚡ **Gestiona la energía**: No uses sprint constantemente
5. 🎯 **Prioriza objetivos**: Llaves primero, enemigos si es necesario

### Estrategias Avanzadas
1. 🏃 **Kiting**: Atrae enemigos y elimínalos uno por uno
2. 🔦 **Gestiona la iluminación**: Alterna la linterna para confundir a los enemigos
3. ⏱️ **Gestión del tiempo**: Memoriza rutas para el escape final
4. 🎯 **Disparo selectivo**: Guarda energía para situaciones críticas
5. 👂 **Presta atención al sonido**: Reconoce a cada enemigo por su audio característico

---

## 🛠️ Estructura del Proyecto

```
Fear of Ways 0/
├── main.py                 # Punto de entrada, inicialización
├── juego.py               # Lógica principal del juego
├── jugador.py             # Clase del jugador, controles
├── enemigo.py             # IA y comportamiento de enemigos
├── nivel.py               # Generación de niveles
├── camara.py              # Sistema de cámara con zoom
├── pared.py               # Muros del laberinto
├── proyectil.py           # Proyectiles
├── salida.py              # Salidas de niveles
├── images/                # Recursos gráficos
│   ├── ingeniero_sheet.png
│   ├── wall_texture.png
│   ├── floor_texture.png
│   ├── key_icon.png
│   ├── heart.png
│   ├── lightning.png
│   ├── menu_background.png
│   ├── hud_bar_texture.png
│   ├── posion.png
├── audio/                 # Archivos de audio
│   ├── musica_fondo.mp3
│   ├── disparo.mp3
│   └── daño.mp3
├── docs/                  # Documentación
│   ├── CAMBIOS_MAZMORRAS.md
│   ├── EVALUACION_REQUISITOS.md
│   ├── GUIA_DEMO.md
│   ├── GUIA_NIVELES.md
│   ├── INDICE.md
│   ├── MEJORAS_APLICADAS.md
│   ├── RECOMENDACIONES.md
│   └── RESUMEN_EJECUTIVO.md
├── copiagame/             # Versiones anteriores
├── resultados.txt         # Registro de partidas
├── requirements.txt       # Dependencias Python
└── README.md              # Este archivo
```

---

## 🔧 Características Técnicas

### Arquitectura
- **Patrón**: Orientado a Objetos con separación de responsabilidades
- **Rendering**: Sistema de cámara 2D con zoom dinámico
- **Física**: Sistema de colisiones AABB optimizado
- **IA**: Máquina de estados finitos para enemigos

### Algoritmos Destacados
- **Generación Procedural**: Algoritmo DFS para laberintos perfectos
- **Pathfinding**: Búsqueda BFS para distancias
- **Visibilidad**: Ray casting para línea de visión
- **Iluminación**: Rendering cónico con gradiente radial

### Optimizaciones
- Pre-renderizado de suelos para evitar artefactos de zoom
- Culling de entidades fuera de cámara
- Pooling de proyectiles
- Cache de cálculos de distancia

---

## 📝 Créditos

### Desarrollado por
- **Estudiante**: [Tu Nombre]
- **Curso**: Introducción a la Programación
- **Institución**: ITCR (Instituto Tecnológico de Costa Rica)
- **Profesor**: Alejandro Alfaro
- **Semestre**: II - 2025

### Tecnologías Utilizadas
- **Python 3.9+**: Lenguaje de programación
- **Pygame 2.x**: Motor de juego 2D
- **Assets**: Creados/recopilados para el proyecto

---

## 📄 Licencia

Este proyecto fue creado con fines educativos para el curso de Introducción a la Programación del ITCR.

---

## 🐛 Solución de Problemas

### El juego no inicia
- Verifica que Python 3.9+ esté instalado: `python --version`
- Verifica que Pygame esté instalado: `pip list | findstr pygame`
- Reinstala Pygame: `pip install --upgrade pygame`

### No se escucha el audio
- Verifica que los archivos `.mp3` existen en la carpeta `audio/`
- Comprueba el volumen del sistema
- Algunos sistemas necesitan codecs adicionales para MP3

### El juego va lento
- Cierra otros programas que consuman recursos
- Reduce la resolución de pantalla si es posible
- El zoom alto puede afectar rendimiento en PCs antiguos

### Los sprites no se ven
- Verifica que `images/ingeniero_sheet.png` existe
- Verifica que todas las imágenes `.png` están en la carpeta `images/`
- Los fallbacks dibujarán figuras geométricas si faltan imágenes

---

## 📞 Contacto y Soporte

Para preguntas sobre el proyecto:
- **Repositorio**: [GitHub - Fear-of-Ways-0](https://github.com/JoanCordero/Fear-of-Ways-0)
- **Issues**: Reporta bugs en el repositorio de GitHub

---

## 🎉 Agradecimientos

Gracias al profesor Alejandro Alfaro por la guía durante el desarrollo del proyecto y a todos los compañeros que probaron el juego y dieron feedback.


**¡Disfruta escapando de las mazmorras!** 🎮👾🗝️
