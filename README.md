# 🎮 Fear of Ways 0
## Juego de supervivencia y exploración en laberintos oscuros

---

## 📖 Descripción
**Fear of Ways 0** es un juego de supervivencia y exploración desarrollado en Python + Pygame. El jugador debe recorrer laberintos peligrosos, recolectar llaves, activar mecanismos y encontrar la salida antes de que se agote el tiempo. La versión 1.1.0 incorpora un sistema completo de puntuaciones, guardado y carga de partidas, power-ups activables y un menú de configuración que permite ajustar la experiencia en tiempo real.

---

## ✨ Características principales
- 🧭 **Tres laberintos** con texturas temáticas, llaves colocadas manualmente y generación reproducible mediante semillas por nivel.
- 👁️ **Iluminación cónica dinámica** controlada con el mouse y cámara con zoom que mantiene la tensión exploratoria.
- 👾 **IA enemiga variada** (veloz, acechador y bruto) con ataques diferenciados, proyectiles y fases de ocultamiento.
- ⚡ **Power-ups y recursos** (visión clara, doble disparo, super velocidad, escudo, energía y corazones) repartidos aleatoriamente en cada run.
- 🧮 **Sistema de puntuación** con resumen final, tabla de campeones y registro histórico de partidas.
- 💾 **Guardado/carga** desde archivos de texto compatibles entre versiones (posiciones, enemigos, power-ups, semillas y cronómetro).
- 🔉 **Audio y UX** con control de volumen en pausa, variaciones de clicks, notificaciones y efectos específicos para cada evento.
- 🖥️ **Menús completos**: principal, pantalla de controles, pausa interactiva, configuración (pantalla completa/ventana + sliders) y pantalla de puntuaciones.

---

## 🧩 Sistemas complementarios
- 🎯 **Marcadores persistentes**: los resultados terminados se registran automáticamente y pueden consultarse desde el menú de puntuaciones (campeones e histórico).
- 🧪 **Archivos de diseño**: los mapas `.txt` y `.json` permiten modificar rápidamente la disposición de paredes, llaves y puertas.
- 🛡️ **Balance dinámico**: los enemigos ajustan velocidad, alcance y proyectiles en función de su tipo para mantener el desafío.

---

## 🖥️ Requisitos

### Software necesario
- Python 3.9 o superior.
- [Pygame 2.x](https://www.pygame.org/wiki/GettingStarted).

### Hardware recomendado
- CPU de doble núcleo.
- 2 GB de RAM.
- GPU con soporte OpenGL.
- 200 MB de espacio libre para recursos y archivos generados.

---

## 📥 Instalación
```bash
# Clonar el repositorio
git clone https://github.com/JoanCordero/Fear-of-Ways-0.git
cd Fear-of-Ways-0

# (Opcional) Crear un entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias principales
python -m pip install --upgrade pip
python -m pip install pygame
```

---

## ▶️ Ejecución
```bash
python main.py
```
Durante el arranque el juego intentará inicializar la pantalla en modo **pantalla completa** y reproducir música de fondo. Si la inicialización de audio falla (por ejemplo, en entornos sin dispositivo de sonido) el juego continúa con los efectos silenciados.

---

## 🧭 Flujo de menús
- **Empezar Laberinto**: registra un nombre y muestra una pantalla de controles antes de iniciar el nivel 1.
- **Continuar**: carga cualquier guardado disponible en `partidas_guardadas.txt`.
- **Tabla de Campeones**: muestra la tabla de ganadores y el historial completo, con pestañas seleccionables mediante mouse.
- **Opciones**: abre el menú de configuración (cambiar pantalla completa/ventana y ajustar volúmenes con sliders).

El menú de pausa (ESC o P) permite reanudar, reiniciar nivel, abrir configuración o volver al menú principal. También ofrece atajos de teclado para ajustar volumen de música (←/→) y efectos (`[` / `]`).

---

## 🎮 Cómo jugar

### Objetivo
Recolecta todas las llaves del nivel, abre la salida y escapa antes de que el temporizador llegue a cero. Cada laberinto completado otorga puntos adicionales y desbloquea el siguiente mapa.

### Controles
| Acción | Tecla / Botón |
|--------|---------------|
| Moverse | W, A, S, D |
| Sprint | Shift izquierdo o derecho (consume energía) |
| Disparo | Click izquierdo del mouse |
| Activar power-up cercano | E |
| Pausa / Menú de pausa | ESC o P |
| Navegar menús | Mouse y teclado |

El apuntado de la linterna y los disparos siguen al cursor. Si mantienes pulsado Shift, el jugador acelera a costa de energía que se regenera automáticamente al detenerse.

### Power-ups y recursos
- **Visión clara**: elimina temporalmente la oscuridad cónica.
- **Doble disparo**: lanza un proyectil extra con ángulo diferente.
- **Super velocidad**: incrementa velocidad/aceleración.
- **Escudo**: reduce daño durante su duración.
- **Corazones**: restauran vida.
- **Rayos**: restauran energía.

Los power-ups aparecen en cada nivel con probabilidades distintas y deben activarse manualmente con `E`.

### Temporizador y dificultad
- Laberinto 1: 1 minuto 30 segundos.
- Laberinto 2: 1 minuto.
- Laberinto 3: 1 minuto (con generación agresiva de enemigos extra si se agota el tiempo).

Cuando el tiempo termina los enemigos comienzan a aparecer continuamente hasta que encuentres la salida o pierdas la partida.

### Puntuaciones y archivos
- Al completar un nivel se muestran puntos por enemigos derrotados, bonus de tiempo y estado del jugador.
- Las partidas terminadas se registran en `resultados.txt` y el historial consolidado en `historial_jugadores.txt`.
- Si completas el juego se añade una entrada en `campeones.txt` (se crea automáticamente si no existe) y la tabla puede consultarse desde el menú principal.

---

## 🧑‍🚀 Personaje disponible
El juego crea un único perfil predeterminado equilibrado.

### 🔍 Explorador (predeterminado)
- ❤️ Vida: 5 corazones.
- ⚡ Energía: 100 (usada para sprint y disparos).
- 🏃 Velocidad base: 4.
- 👁️ Visión: 150 (radio de la linterna).
- 🎯 Equipamiento: linterna direccional, disparo básico y animaciones completas (idle, caminar, disparar, morir).

---

## 👾 Enemigos

### ⚡ Veloz (amarillo)
- **Vida**: 2.
- **Velocidad**: alta, con persecución agresiva.
- **Ataque**: cuerpo a cuerpo telegráfico de corto alcance.

### 🔵 Acechador (cian)
- **Vida**: 3.
- **Velocidad**: media.
- **Ataque**: proyectiles a distancia con tiempos de recarga altos.

### 💪 Bruto (rojo)
- **Vida**: 5.
- **Velocidad**: baja.
- **Ataque**: aura de ralentización y empujes a corta distancia.

Todos los enemigos inician ocultos y se revelan cuando el jugador se aproxima, reforzando la sensación de peligro en los laberintos.

---

## 🗺️ Laberintos

### Laberinto 1: Procedural
- Diseño modular con habitaciones conectadas por pasillos estrechos.
- Llaves en callejones y palancas que desbloquean puertas principales.
- Dificultad introductoria, ideal para familiarizarse con la linterna y el sprint.

### Laberinto 2: Espiral Concéntrica
- Pasillos en espiral que obligan a recorrer el mapa de afuera hacia adentro.
- Múltiples puertas y palancas que controlan el ritmo del avance.
- Tiempo más ajustado y mayor densidad de enemigos.

### Laberinto 3: Cámaras Interconectadas
- Zonas laterales y central conectadas mediante puertas escalonadas.
- Cinco palancas y llaves distribuidas para recorridos estratégicos.
- Aparición acelerada de enemigos cuando el tiempo está por expirar.

---

## 🎨 Recursos incluidos

### Imágenes (`images/`)
`ingeniero_sheet.png`, `duende.png`, `esqueleto.png`, `Ogro.png`, `key_icon.png`, `heart.png`, `lightning.png`, `menu_background.png`, `hud_bar_texture.png`, `floor_texture.png`, `wall_texture.png`, `pared_hojas.png`, `pared_lava.png`, `pared_pasto.png`, `texture_tierra.png`, `texture_piedra.png`, `tiempo.png`, `siguiente_nivel.png`, `pantalla_ganar.png`, `pantalla_perder.png`, `puerta.png`, `puerta_abierta.png`, `posion.png`.

### Audio (`audio/`)
`musica_fondo.mp3`, `menu_sonido.mp3`, `disparo.mp3`, `daño.mp3`, `click_menu.mp3`, `corazon.mp3`, `notificaciones_juego.mp3`, `pociones.mp3`, `recojer_llave.mp3`, `rayo.mp3`, `derrota.mp3`, `victoria_sonido.mp3`.

Todos los recursos tienen carga tolerante a fallos: si falta un archivo el juego registra una advertencia y continúa ejecutándose con alternativas visuales o silencios controlados.

---

## 📂 Archivos generados
- `partidas_guardadas.txt`: partidas en progreso (un registro por jugador).
- `historial_jugadores.txt`: partidas completadas con puntuación, nivel alcanzado y fecha.
- `campeones.txt`: jugadores que finalizaron el juego (creado al registrar el primer campeón).
- `resultados.txt`: log crudo de resultados para depuración.

Puedes eliminar cualquiera de estos archivos para reiniciar los registros.

---

## 🏗️ Estructura del proyecto
```
Fear of Ways 0/
├── main.py
├── juego.py
├── jugador.py
├── enemigo.py
├── nivel.py
├── camara.py
├── pared.py
├── proyectil.py
├── salida.py
├── mapas_export_nivel_1.txt
├── mapas_export_nivel_2.txt
├── mapas_export_nivel_3.txt
├── audio/
│   └── … (efectos y música)
├── images/
│   └── … (sprites, texturas y HUD)
├── docs/
│   └── … (documentación técnica y de diseño)
├── partidas_guardadas.txt
├── historial_jugadores.txt
├── resultados.txt
└── README.md
```

---

## 🛠️ Solución de problemas
- **El audio no se reproduce**: algunos sistemas necesitan `pygame.mixer.init()` con un dispositivo de sonido válido. Si falla, el juego continúa sin música ni efectos.
- **Ventana negra al iniciar**: verifica que la carpeta `images/` esté completa y que tu GPU soporte OpenGL.
- **Errores al cargar guardados**: borra la entrada correspondiente en `partidas_guardadas.txt` si cambiaste el nombre del archivo o moviste recursos.
- **Controles congelados al empezar**: asegúrate de cerrar la pantalla de controles (ENTER o click en "Comenzar") para habilitar el movimiento.

---

## 📞 Contacto
- Repositorio: [GitHub - Fear-of-Ways-0](https://github.com/JoanCordero/Fear-of-Ways-0)
- Issues: usa la sección de *Issues* en GitHub para reportar errores o solicitar mejoras.

---

## 📝 Créditos y licencia
Proyecto creado para el curso **Introducción a la Programación (ITCR)**, II Semestre 2025.

Los recursos incluidos se distribuyen con fines educativos. Si reutilizas el proyecto en otro contexto, verifica las licencias de los assets gráficos y de audio antes de publicar.

**¡Disfruta escapando de los laberintos!** 👾🗝️
