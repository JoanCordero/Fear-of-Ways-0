# 🎬 GUÍA DE DEMOSTRACIÓN
## Fear of Ways 0 - Para Presentación

---

## ⏱️ TIMING SUGERIDO (5-10 minutos)

### Introducción (30 segundos)
"Hola, les presento **Fear of Ways 0**, un juego de supervivencia en mazmorras con mecánicas de sigilo, combate y escape temporal."

---

## 🎮 DEMO PRÁCTICA (3-4 minutos)

### 1. Inicio del Juego (15 segundos)
**Acciones**:
- Ejecutar `python main.py`
- Mostrar la consola con los mensajes de carga
- Señalar: "Implementé manejo robusto de errores"

**Qué decir**:
> "El juego carga todos los recursos con manejo de errores. Si falta algún archivo, usa fallbacks automáticos y no crashea."

---

### 2. Menú Principal (15 segundos)
**Acciones**:
- Mostrar el menú con el fondo
- Seleccionar personaje (tecla 3 - Ingeniero)

**Qué decir**:
> "Hay 3 personajes con estadísticas diferentes: Explorador (equilibrado), Cazador (rápido) e Ingeniero (resistente)."

---

### 3. Tutorial (20 segundos)
**Acciones**:
- Esperar a que aparezca el tutorial
- Señalar los controles
- Presionar ENTER

**Qué decir**:
> "Implementé un tutorial que se muestra automáticamente en el primer nivel para ayudar a nuevos jugadores. Solo aparece una vez."

---

### 4. Gameplay Básico (60 segundos)
**Acciones**:
- Moverse con WASD
- Usar sprint (SHIFT)
- Mostrar cómo la linterna sigue al mouse
- Recoger un bonus
- Disparar a un enemigo (click derecho)
- Derrotar un enemigo

**Qué decir**:
> "La mecánica principal es la **linterna cónica** que limita la visibilidad. El jugador debe equilibrar movimiento, combate y gestión de energía."
> 
> "Noten el **sistema de puntuación**: +100 puntos por cada enemigo. También hay un **contador** de enemigos derrotados."

---

### 5. Mecánicas Avanzadas (40 segundos)
**Acciones**:
- Encontrar y recoger una llave
- Mostrar el mensaje "¡Llave recogida!"
- Encontrar una zona azul (escondite)
- Entrar en ella

**Qué decir**:
> "El nivel tiene **llaves** que deben recogerse. Una vez recogidas todas, se activa un **temporizador de escape** que añade presión temporal."
>
> "Las zonas azules son **escondites** donde los enemigos no pueden detectarte. Es una mecánica de **sigilo**."

---

### 6. Pausa y Estadísticas (20 segundos)
**Acciones**:
- Presionar P para pausar
- Mostrar las estadísticas actuales
- Ajustar volumen con ← y →
- Presionar P para reanudar

**Qué decir**:
> "El menú de pausa muestra **estadísticas en tiempo real**: puntos actuales, enemigos derrotados y nivel."
>
> "También implementé **controles de volumen** independientes para música y efectos."

---

### 7. Completar Nivel (20 segundos)
*Si hay tiempo, puedes hacer trampa y teletransportarte a la salida modificando temporalmente el código, o simplemente explicar:*

**Qué decir**:
> "Al recoger todas las llaves y llegar a la salida, aparece una **pantalla de logro** que muestra:"
> - Puntos base por completar nivel (+500)
> - Bonus de tiempo (si escapaste rápido)
> - Puntos totales acumulados
>
> "Son **3 niveles** con diseños únicos y dificultad progresiva."

---

## 💻 DEMO DE CÓDIGO (3-4 minutos)

### 1. Estructura del Proyecto (30 segundos)
**Mostrar en explorador de archivos**:
```
Fear of Ways 0/
├── main.py           ← Punto de entrada
├── juego.py          ← Lógica principal
├── jugador.py        ← Clase del jugador
├── enemigo.py        ← IA de enemigos
├── nivel.py          ← Generación de niveles
└── assets/           ← Recursos
```

**Qué decir**:
> "El proyecto usa **arquitectura modular** con separación clara de responsabilidades."

---

### 2. Código Destacado 1: Generación Procedural (45 segundos)
**Abrir**: `nivel.py`, método `_generar_laberinto_por_celdas`

**Qué decir**:
> "Este es el **algoritmo DFS** para generar laberintos procedurales. Cada partida del nivel 1 tiene un laberinto diferente."

**Mostrar líneas clave**:
```python
def _generar_laberinto_por_celdas(self, cols, filas):
    visit = set()
    stack = [(0, 0)]
    # ... algoritmo de backtracking
```

---

### 3. Código Destacado 2: Sistema de Puntuación (30 segundos)
**Abrir**: `juego.py`, buscar "puntos +="

**Qué decir**:
> "Implementé un **sistema de puntuación completo** con bonificaciones:"

**Mostrar**:
```python
# Por enemigo
self.puntos += 100

# Por completar nivel
self.puntos += 500

# Bonus de tiempo
tiempo_bonus = (self.tiempo_restante // 60) * 10
self.puntos += tiempo_bonus
```

---

### 4. Código Destacado 3: IA de Enemigos (45 segundos)
**Abrir**: `enemigo.py`, método `mover`

**Qué decir**:
> "Los enemigos tienen **IA con estados**: patrullaje y persecución. Hay 3 tipos con comportamientos únicos:"
> - **Veloz**: Ataque cuerpo a cuerpo rápido
> - **Acechador**: Dispara proyectiles
> - **Bruto**: Aura que ralentiza

**Mostrar**:
```python
if self.objetivo_visible:
    # Persecución
    dirx, diry = dx / dist, dy / dist
else:
    # Patrulla aleatoria
    dirx, diry = math.cos(self.ang_pat), math.sin(self.ang_pat)
```

---

### 5. Código Destacado 4: Manejo de Errores (30 segundos)
**Abrir**: `main.py` o `juego.py`, mostrar try-catch

**Qué decir**:
> "Implementé **manejo robusto de errores** para todos los recursos. Si falta un archivo, el juego continúa con fallbacks."

**Mostrar**:
```python
try:
    self.sonido_disparo = pygame.mixer.Sound("disparo.mp3")
    print("✓ Sonido de disparo cargado")
except (pygame.error, FileNotFoundError):
    self.sonido_disparo = None
    print("⚠ Advertencia: disparo.mp3 no encontrado")
```

---

## 📊 DESTACAR CARACTERÍSTICAS (1 minuto)

### Lista Rápida de Logros
**Decir en orden rápido**:

1. ✅ **3 niveles únicos** con mecánicas diferentes
2. ✅ **3 personajes** con estadísticas distintas
3. ✅ **3 tipos de enemigos** con IA diferente
4. ✅ **Sistema de iluminación** con linterna cónica
5. ✅ **Generación procedural** de laberintos
6. ✅ **Sistema de puntuación** completo
7. ✅ **Tutorial integrado** para nuevos jugadores
8. ✅ **Control de volumen** en tiempo real
9. ✅ **Estadísticas detalladas** en pantallas de logro
10. ✅ **Manejo de errores** robusto

**Cerrar con**:
> "Además de cumplir el 100% de los requisitos, implementé **10 mejoras adicionales** que mejoran significativamente la experiencia del usuario."

---

## ❓ PREGUNTAS FRECUENTES Y RESPUESTAS

### P1: "¿Cómo funciona la generación procedural?"
**R**: "Uso un algoritmo DFS (Depth-First Search) con backtracking para crear laberintos perfectos. Luego deribo muros aleatorios para crear ciclos y habitaciones tipo cueva."

### P2: "¿Por qué elegiste ese sistema de iluminación?"
**R**: "La linterna cónica refuerza el tema de 'miedo' y 'caminos oscuros'. Limita la visibilidad y obliga al jugador a explorar cuidadosamente, creando tensión."

### P3: "¿Cómo implementaste la IA de los enemigos?"
**R**: "Cada enemigo tiene una máquina de estados finitos con dos estados: patrullaje (movimiento aleatorio) y persecución (cuando detecta al jugador). También implementé detección de línea de visión para que no vean a través de muros."

### P4: "¿Qué fue lo más difícil de implementar?"
**R**: "El sistema de cámara con zoom fue desafiante. Tuve que convertir coordenadas del mundo a pantalla constantemente, y evitar artefactos visuales con texturas repetidas."

### P5: "¿Cómo balanceaste la dificultad?"
**R**: "Implementé dificultad progresiva: cada nivel tiene más enemigos, spawns más rápidos, menos tiempo de escape y menos recursos. Los enemigos también se vuelven más rápidos."

---

## 🎯 PUNTOS CLAVE PARA ÉNFASIS

### Técnicos
- ✅ "Arquitectura orientada a objetos modular"
- ✅ "Algoritmos complejos (DFS, BFS, ray casting)"
- ✅ "Manejo robusto de excepciones"
- ✅ "Sistema de cámara con transformación de coordenadas"

### Creativos
- ✅ "Mecánica única de linterna cónica"
- ✅ "Sistema de sigilo con escondites"
- ✅ "Temporizador dinámico que activa presión temporal"
- ✅ "Generación procedural para rejugabilidad"

### Experiencia de Usuario
- ✅ "Tutorial integrado naturalmente"
- ✅ "Feedback constante (visual y sonoro)"
- ✅ "Sistema de progresión (puntuación)"
- ✅ "Controles intuitivos y personalizables"

---

## 🎬 CIERRE (30 segundos)

**Resumen Final**:
> "**Fear of Ways 0** es un juego completo que cumple todos los requisitos del proyecto y va más allá con características adicionales. Demuestra conocimientos en:"
> - Programación orientada a objetos
> - Algoritmos y estructuras de datos
> - Manejo de eventos y estados
> - Diseño de juegos y UX
> - Manejo de errores y robustez
>
> "Está **completamente funcional, sin bugs, y listo para jugar**. Gracias por su atención. ¿Hay alguna pregunta?"

---

## 📝 NOTAS IMPORTANTES

### Antes de la Demo
- [ ] Cerrar todas las aplicaciones innecesarias
- [ ] Tener el código abierto en VS Code
- [ ] Tener el explorador de archivos abierto en la carpeta
- [ ] Probar que el juego se ejecuta correctamente
- [ ] Tener un cronómetro visible

### Durante la Demo
- ✅ Hablar con confianza y claridad
- ✅ No apresurarse en las partes importantes
- ✅ Hacer pausas para que asimilen información
- ✅ Señalar características destacadas
- ✅ Estar preparado para improvisar si algo falla

### Si Algo Sale Mal
- 🔴 **Crasheo**: "Como dije, implementé manejo de errores, pero siempre puede haber casos límite. Permítanme reiniciar..."
- 🔴 **Lag**: "En este equipo puede ir un poco lento, pero funciona perfectamente en hardware estándar."
- 🔴 **Error de código**: "Interesante, esto me ayudará a mejorar el código. La lógica principal está correcta como pueden ver en..."

---

## ✅ CHECKLIST PRE-DEMO

### Técnico
- [ ] Juego ejecuta sin errores
- [ ] Todos los recursos están presentes
- [ ] Volumen del sistema configurado
- [ ] Resolución de pantalla apropiada

### Presentación
- [ ] Puntos clave memorizados
- [ ] Código destacado marcado
- [ ] Respuestas a preguntas preparadas
- [ ] Timing practicado

### Backup
- [ ] Copia del proyecto en USB
- [ ] Screenshots del juego funcionando
- [ ] Video de gameplay (opcional)
- [ ] Presentación PDF (opcional)

---

## 🏆 MENSAJE FINAL

**Recuerda**:
- Tu proyecto está **excelente** ✅
- Cumple **todos los requisitos** ✅
- Tiene **características extra** ✅
- El código está **limpio y funciona** ✅

**¡Confía en tu trabajo y disfruta la presentación! 🚀🎮**

---

**Buena suerte! 🍀**
