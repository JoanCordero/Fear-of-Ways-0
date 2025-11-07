# Cambios Realizados en el Sistema de Mazmorras

## Resumen
Se implementó un sistema completo de mazmorras con mecánicas únicas para cada uno de los 3 niveles del juego, asegurando que cada nivel tenga su propia identidad, diseño y desafíos.

---

## 🎮 Mecánicas Implementadas en TODOS los Niveles

### 1. Sistema de Llaves
- **Nivel 1**: 3-4 llaves requeridas (generadas proceduralmente)
- **Nivel 2**: 4 llaves requeridas (posiciones estratégicas en la espiral)
- **Nivel 3**: 5 llaves requeridas (el más desafiante)

### 2. Sistema de Puertas y Palancas
Todos los niveles ahora tienen:
- ✅ Puertas que bloquean el paso
- ✅ Palancas para controlar las puertas
- ✅ Indicador visual "[E] para activar palanca" cuando el jugador está cerca
- ✅ Puertas con animación visual (cerradas = marrón con tablas, abiertas = verde translúcido)

### 3. Temporizador de Escape
- Al recoger todas las llaves, se activa un temporizador
- **Nivel 1**: 2 minutos para escapar
- **Nivel 2**: 1.5 minutos para escapar
- **Nivel 3**: 1 minuto para escapar
- ⚠️ Cuando el tiempo se agota, los enemigos aparecen continuamente

---

## 🗺️ Diseño Único de Cada Nivel

### Nivel 1: Mazmorra Procedural
**Tema**: Laberinto generado proceduralmente estilo caverna
**Características**:
- Generación automática con algoritmo DFS (backtracking)
- Habitaciones amplias de tamaños variables (2×2 a 5×5)
- Pasillos estrechos y laberínticos
- 1 puerta controlada por palanca en cuello de botella
- Llaves distribuidas en callejones sin salida

**Puertas y Palancas**:
- 1 puerta principal (ID: "A1")
- 1 palanca en zona alejada

### Nivel 2: Espiral Concéntrica
**Tema**: Laberinto en forma de espiral hacia el centro
**Características**:
- Diseño en capas concéntricas
- Camino sinuoso que va desde el exterior al centro
- Salida en el centro de la espiral
- 3 puertas estratégicas que controlan el flujo

**Puertas y Palancas**:
- **Puerta 1** (N2_P1): Bloquea paso en espiral exterior
- **Puerta 2** (N2_P2): Bloquea zona intermedia
- **Puerta 3** (N2_P3): Protege acceso al centro
- 3 palancas distribuidas estratégicamente

### Nivel 3: Cámaras Interconectadas
**Tema**: Laberinto caótico con múltiples cámaras y puzzles complejos
**Características**:
- Dividido en 3 zonas principales (izquierda, centro, derecha)
- Zona izquierda: laberinto denso
- Zona central: cámaras conectadas
- Zona derecha: pasajes estrechos
- Sistema complejo de 5 puertas

**Puertas y Palancas**:
- **Puerta 1** (N3_P1): Entrada a zona central
- **Puerta 2** (N3_P2): Paso horizontal en zona central
- **Puerta 3** (N3_P3): Entrada a zona derecha
- **Puerta 4** (N3_P4): Acceso a zona inferior derecha
- **Puerta 5** (N3_P5): Pasaje secreto en zona izquierda
- 5 palancas en ubicaciones estratégicas

---

## 🎨 Mejoras Visuales

### Puertas
- **Cerradas**: Color marrón oscuro con detalles de tablas de madera
- **Abiertas**: Color verde translúcido con líneas diagonales cruzadas
- Borde grueso para mayor visibilidad

### Palancas
- Efecto de brillo pulsante (animación)
- Sombra para profundidad
- Manija vertical con círculo en la punta
- Color azul brillante

### Llaves
- Efecto de brillo pulsante
- Forma de llave detallada (cabeza circular + dientes)
- Color dorado brillante
- Sombra para profundidad

---

## ⚙️ Archivos Modificados

### 1. `nivel.py`
- ✅ Método `crear_nivel_2()`: Añadidas 3 puertas y palancas
- ✅ Método `crear_nivel_3()`: Añadidas 5 puertas y palancas con diseño complejo
- ✅ Mejorado el dibujo de palancas con efectos visuales
- ✅ Sistema de ID de puertas para control individual

### 2. `juego.py`
- ✅ Añadida lógica de interacción con palancas (tecla E)
- ✅ Método `obtener_id_puerta_por_indice()`: Mapeo de palancas a puertas por nivel
- ✅ Indicador visual "[E] para activar palanca"
- ✅ Mensajes de feedback al activar palancas
- ✅ Sistema de temporizador funcional en todos los niveles

### 3. `pared.py`
- ✅ Mejorado el método `dibujar()` para puertas
- ✅ Puertas cerradas: Detalles de tablas de madera
- ✅ Puertas abiertas: Efecto translúcido con líneas cruzadas
- ✅ Propiedad `bloquea` respeta el estado de las puertas

---

## 🎯 Flujo de Juego Mejorado

1. **Inicio del nivel**: Jugador aparece en posición segura
2. **Exploración**: Buscar llaves mientras evita enemigos
3. **Puzzles**: Activar palancas para abrir puertas bloqueadas
4. **Recolección**: Encontrar y recoger todas las llaves requeridas
5. **Activación**: Al recoger la última llave, se abre la salida y comienza el temporizador
6. **Escape**: Llegar a la salida antes de que se acabe el tiempo
7. **Penalización**: Si el tiempo se agota, enemigos aparecen constantemente

---

## 🎮 Controles

- **WASD / Flechas**: Movimiento
- **Click izquierdo**: Ataque cuerpo a cuerpo
- **Click derecho / ESPACIO**: Disparar proyectil
- **E**: Activar palanca (cuando está cerca)
- **P / ESC**: Pausar juego

---

## ✨ Características Destacadas

1. **Progresión de Dificultad**:
   - Nivel 1: 3-4 llaves, 1 puerta, 2 minutos
   - Nivel 2: 4 llaves, 3 puertas, 1.5 minutos
   - Nivel 3: 5 llaves, 5 puertas, 1 minuto

2. **Diseños Únicos**:
   - Cada nivel tiene arquitectura distintiva
   - Diferentes estrategias de navegación
   - Complejidad creciente

3. **Feedback Visual Claro**:
   - Indicadores de interacción
   - Mensajes de progreso
   - Animaciones y efectos

4. **Sistema de Recompensa**:
   - Llaves necesarias para desbloquear salida
   - Palancas abren rutas alternativas
   - Temporizador añade tensión

---

## 🐛 Correcciones y Optimizaciones

- ✅ Spawn del jugador en posiciones seguras
- ✅ Cooldowns balanceados para enemigos
- ✅ Sistema de puertas no interfiere con muros normales
- ✅ Palancas solo afectan sus puertas asignadas
- ✅ Mensajes temporales no interfieren con el HUD

---

## 📝 Notas Técnicas

- Las puertas usan la propiedad `bloquea` para controlar colisiones
- Cada nivel tiene su propio diccionario `_puertas_por_id`
- Las palancas son objetos `pygame.Rect` almacenados en una lista
- El mapeo de palancas a puertas se hace mediante el método `obtener_id_puerta_por_indice()`
- El temporizador se activa automáticamente al recoger la última llave

---

## 🚀 Resultado Final

El juego ahora ofrece una experiencia completa de mazmorra con:
- ✅ 3 niveles completamente diferentes
- ✅ Mecánicas de exploración y puzzle
- ✅ Sistema de progresión satisfactorio
- ✅ Feedback visual claro
- ✅ Tensión creciente con el temporizador
- ✅ Desafíos únicos en cada nivel
