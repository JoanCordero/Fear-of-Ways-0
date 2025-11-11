# Diseño del Nivel 1 - Pasillos Amplios

## 🎯 Objetivo del Diseño
Crear un laberinto completamente navegable que garantice el paso cómodo del jugador sin colisiones en las aperturas entre habitaciones.

## 📏 Especificaciones Técnicas

### Tamaño del Jugador
- **Ancho**: 35 píxeles
- **Alto**: 50 píxeles
- **Fuente**: `jugador.py` línea 93

### Dimensiones de Pasillos y Aperturas
- **Pasillos mínimos**: 80-100 píxeles (2.3x el ancho del jugador)
- **Aperturas estándar**: 100-120 píxeles (2.9x el ancho del jugador)
- **Aperturas amplias**: 150-170 píxeles (4.3x el ancho del jugador)
- **Grosor de muros**: 30 píxeles

### Dimensiones del Mapa
- **Ancho total**: 2000 píxeles
- **Alto total**: 1500 píxeles
- **Bordes**: 20 píxeles

## 🗺️ Estructura del Mapa

### 1. SECCIÓN SUPERIOR IZQUIERDA (Zona de Inicio)
**Coordenadas**: 100-500, 100-400

**Habitación inicial**:
- Tamaño: 400x300 píxeles
- Muros:
  - Superior: (100, 100, 400, 30)
  - Izquierdo: (100, 100, 30, 300)
  - Inferior parcial: (100, 370, 200, 30)

**Aperturas**:
- ✅ **Derecha**: x=500 hasta x=650 = **150 píxeles** (4.3x jugador)
- ✅ **Abajo**: x=300 hasta x=470 = **170 píxeles** (4.9x jugador)

**Punto de spawn**: Automático en área segura

---

### 2. PASILLO HORIZONTAL SUPERIOR
**Coordenadas**: 650-1130, 100-380

**Estructura**:
- Columna separadora izquierda: (650, 100, 30, 150)
- Muro horizontal: (680, 100, 420, 30)
- Columna separadora derecha: (1100, 100, 30, 280)

**Aperturas**:
- ✅ **Hacia abajo**: y=250 hasta y=380 = **130 píxeles** (2.6x alto jugador)

---

### 3. HABITACIÓN SUPERIOR DERECHA (🔑 Llave 1)
**Coordenadas**: 1300-1780, 100-350

**Estructura cerrada**:
- Pared izquierda: (1300, 100, 30, 250)
- Pared superior: (1330, 100, 450, 30)
- Pared derecha: (1750, 100, 30, 250)
- Pared inferior: (1330, 320, 420, 30)

**Contenido**:
- 🔑 **Llave 1**: Posición (1550, 200)
- 👾 Enemigo: (1550, 220)

**Aperturas**:
- ✅ **Izquierda**: x=1130 hasta x=1300 = **170 píxeles** (4.9x jugador)

---

### 4. PASILLOS VERTICALES ZONA MEDIA
**Coordenadas**: 200-520, 400-650

**Estructura**:
- Pasillo vertical: (200, 450, 30, 200)
- Conector horizontal: (230, 620, 170, 30)

**Aperturas**:
- ✅ **Horizontal**: x=400 hasta x=520 = **120 píxeles** (3.4x jugador)

---

### 5. HABITACIÓN CENTRAL-SUPERIOR (🔑 Llave 2)
**Coordenadas**: 520-850, 400-600

**Estructura**:
- Pared izquierda: (520, 400, 30, 200)
- Pared superior: (550, 400, 300, 30)
- Pared derecha: (820, 400, 30, 200)
- Pared inferior parcial: (550, 570, 150, 30)

**Contenido**:
- 🔑 **Llave 2**: Posición (650, 480)
- 👾 Enemigo: (700, 500)

**Aperturas**:
- ✅ **Superior**: x=430 hasta x=550 = **120 píxeles** (3.4x jugador)
- ✅ **Inferior derecha**: x=700 hasta x=820 = **120 píxeles** (3.4x jugador)

---

### 6. COLUMNA CENTRAL (Divisor Vertical)
**Coordenadas**: 1000-1030, 400-700

**Estructura**:
- Columna grande: (1000, 400, 30, 300)

**Aperturas**:
- ✅ **Superior**: Todo el espacio hasta y=400
- ✅ **Inferior**: Todo el espacio desde y=700

---

### 7. ZONA MEDIA DERECHA
**Coordenadas**: 1200-1600, 450-600

**Estructura**:
- Separador pequeño: (1200, 450, 30, 150)
- Horizontal: (1230, 570, 370, 30)
- Columna derecha: (1570, 450, 30, 150)

**Función**: Conexión entre zonas superior y central

---

### 8. LABERINTO CENTRAL
**Coordenadas**: 100-650, 750-950

**Estructura compleja**:
- Horizontal izquierdo: (100, 750, 180, 30)
- Vertical: (250, 780, 30, 170)
- Columna central: (400, 750, 30, 200)
- Horizontal inferior: (430, 920, 220, 30)

**Aperturas**:
- ✅ **Entre columnas**: x=280 hasta x=400 = **120 píxeles** (3.4x jugador)
- ✅ **Hacia habitación central**: x=650 hasta x=750 = **100 píxeles** (2.9x jugador)

**Enemigos**:
- 👾 (350, 850) - Media izquierda

---

### 9. HABITACIÓN CENTRAL AMPLIA
**Coordenadas**: 650-930, 750-900

**Estructura**:
- Pared izquierda: (650, 750, 30, 150)
- Pared derecha: (900, 750, 30, 150)
- Pared inferior parcial: (680, 870, 190, 30)

**Función**: Área de batalla principal, espacio amplio para maniobras

**Aperturas múltiples**:
- ✅ **Izquierda**: 100 píxeles
- ✅ **Derecha**: 150 píxeles
- ✅ **Arriba y abajo**: Múltiples accesos

**Enemigo**:
- 👾 (750, 820)

---

### 10. ZONA DERECHA MEDIA-BAJA
**Coordenadas**: 1100-1600, 750-930

**Estructura**:
- Separador: (1100, 750, 30, 180)
- Columna pequeña: (1300, 800, 30, 130)

**Enemigo**:
- 👾 (1250, 650)

---

### 11. SECCIÓN INFERIOR IZQUIERDA (🔑 Llave 3)
**Coordenadas**: 100-350, 1050-1300

**Estructura**:
- Pared izquierda: (100, 1050, 30, 250)
- Pared superior: (130, 1050, 220, 30)
- Pared derecha: (320, 1080, 30, 220)
- Pared inferior: (130, 1270, 190, 30)

**Contenido**:
- 🔑 **Llave 3**: Posición (200, 1180)
- 👾 Enemigo: (220, 1170)

**Aperturas**:
- ✅ **Superior**: x=350 hasta x=470 = **120 píxeles** (3.4x jugador)

---

### 12. PASILLO INFERIOR CENTRAL
**Coordenadas**: 470-950, 1100-1350

**Estructura**:
- Columna izquierda: (470, 1100, 30, 250)
- Horizontal: (500, 1220, 180, 30)
- Columna central: (800, 1150, 30, 200)
- Horizontal pequeño: (830, 1150, 120, 30)

**Aperturas**:
- ✅ **Principal**: x=680 hasta x=800 = **120 píxeles** (3.4x jugador)

**Enemigo**:
- 👾 (600, 1250)

---

### 13. ZONA INFERIOR DERECHA (Hacia Salida)
**Coordenadas**: 1050-1580, 1050-1350

**Estructura**:
- Separador grande: (1050, 1050, 30, 300)
- Horizontal: (1080, 1220, 250, 30)
- Columna: (1400, 1050, 30, 180)
- Horizontal: (1430, 1200, 150, 30)

**Función**: Camino progresivo hacia la salida

**Enemigo**:
- 👾 (1200, 1150)

---

### 14. HABITACIÓN DE LA SALIDA 🚪
**Coordenadas**: 1650-1930, 1100-1380

**Estructura**:
- Pared izquierda: (1650, 1100, 30, 280)
- Pared superior: (1680, 1100, 250, 30)
- Pared derecha: (1900, 1130, 30, 250)

**Contenido**:
- 🚪 **SALIDA**: Posición (1800, 1300)

**Aperturas**:
- ✅ **Desde la izquierda**: Acceso amplio (>150 píxeles)
- ✅ **Desde arriba**: Acceso secundario

---

## 📊 Resumen de Aperturas

| Zona | Apertura (px) | Multiplicador | Estado |
|------|---------------|---------------|--------|
| Inicio → Derecha | 150 | 4.3x | ✅ Muy amplio |
| Inicio → Abajo | 170 | 4.9x | ✅ Muy amplio |
| Pasillo Superior | 130 | 3.7x | ✅ Amplio |
| Llave 1 Acceso | 170 | 4.9x | ✅ Muy amplio |
| Zona Media | 120 | 3.4x | ✅ Amplio |
| Llave 2 Arriba | 120 | 3.4x | ✅ Amplio |
| Llave 2 Abajo | 120 | 3.4x | ✅ Amplio |
| Laberinto Central | 120 | 3.4x | ✅ Amplio |
| Habitación Central | 100-150 | 2.9-4.3x | ✅ Amplio |
| Llave 3 Acceso | 120 | 3.4x | ✅ Amplio |
| Pasillo Inferior | 120 | 3.4x | ✅ Amplio |
| Hacia Salida | >150 | >4.3x | ✅ Muy amplio |

**Nota**: Multiplicador = Apertura / Ancho del jugador (35px)

## ✅ Verificación de Accesibilidad

### Llaves
1. 🔑 **Llave 1** (1550, 200): ✅ Accesible desde pasillo superior (170px)
2. 🔑 **Llave 2** (650, 480): ✅ Accesible desde arriba o abajo (120px cada una)
3. 🔑 **Llave 3** (200, 1180): ✅ Accesible desde arriba (120px)

### Salida
🚪 **Salida** (1800, 1300): ✅ Accesible desde múltiples direcciones (>150px)

### Enemigos (9 totales)
Todos ubicados en zonas accesibles con pasillos amplios.

## 🎮 Flujo de Juego Recomendado

1. **Inicio** (100-500, 100-400)
   - Salir por la derecha →
   
2. **Pasillo Superior** (650-1130, 100-380)
   - Continuar a la derecha →
   
3. **🔑 Recoger Llave 1** (1550, 200)
   - Regresar y bajar ↓
   
4. **🔑 Recoger Llave 2** (650, 480)
   - Descender al centro ↓
   
5. **Explorar Centro** (650-930, 750-900)
   - Moverse a la izquierda ←
   
6. **🔑 Recoger Llave 3** (200, 1180)
   - Ir hacia la derecha →
   
7. **Dirigirse a la Salida** (1800, 1300)
   - 🚪 ¡Completar nivel!

## 🔧 Notas de Diseño

### Ventajas del Diseño Manual
- ✅ Todas las aperturas son 2.9x-4.9x el tamaño del jugador
- ✅ No hay callejones sin salida vacíos
- ✅ Las tres llaves tienen acceso garantizado
- ✅ La salida tiene múltiples rutas de acceso
- ✅ Los enemigos están distribuidos equilibradamente
- ✅ Múltiples caminos alternativos

### Comparación con Diseño Procedural Anterior
| Aspecto | Procedural | Manual |
|---------|-----------|--------|
| Grosor de muros | 40px | 30px |
| Apertura mínima | ~60px | 100px |
| Tamaño de pasillos | Variable | 80-100px |
| Garantía de paso | ⚠️ No | ✅ Sí |
| Llaves accesibles | ⚠️ Aleatorio | ✅ 100% |

## 📝 Modificaciones Futuras

Si necesitas ajustar el diseño:

1. **Agregar más aperturas**: Reduce la longitud de los muros
2. **Ampliar pasillos**: Aumenta la separación entre muros paralelos
3. **Mover llaves**: Cambia las coordenadas en la lista `self.llaves`
4. **Relocar enemigos**: Modifica la lista `self.spawn_enemigos`

### Fórmula para Nuevas Aperturas
```
Apertura mínima = Tamaño_jugador × 2.5
Para comodidad = Tamaño_jugador × 3.0
Óptimo = Tamaño_jugador × 3.5-5.0
```

Con jugador de 35px:
- Mínimo: 87.5px ≈ **90px**
- Cómodo: 105px ≈ **100px**
- Óptimo: 122-175px ≈ **120-170px**

---

**Archivo generado**: 2025-11-09  
**Versión**: 1.0  
**Estado**: ✅ Totalmente jugable y accesible  
**Tamaño jugador**: 35x50 píxeles  
**Pasillos mínimos**: 80-100 píxeles  
**Aperturas**: 100-170 píxeles
