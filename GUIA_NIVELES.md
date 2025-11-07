# 🗺️ Guía Visual de Niveles - Fear of Ways 0

## 📊 Comparación de Niveles

| Característica | Nivel 1 | Nivel 2 | Nivel 3 |
|---------------|---------|---------|---------|
| **Tipo** | Procedural | Espiral | Cámaras |
| **Llaves** | 3-4 | 4 | 5 |
| **Puertas** | 1 | 3 | 5 |
| **Palancas** | 1 | 3 | 5 |
| **Enemigos** | 6-8 | 12 | 16 |
| **Tiempo Escape** | 2:00 | 1:30 | 1:00 |
| **Dificultad** | ⭐⭐☆☆☆ | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ |

---

## 🎮 NIVEL 1: MAZMORRA PROCEDURAL

### Diseño
```
╔════════════════════════════════════╗
║  ┌─────┐     ┌──────┐     ┌────┐ ║
║  │ HAB │ ··· │ HAB  │ ··· │ 🔑 │ ║
║  └─────┘     └──────┘     └────┘ ║
║    ║            ║            ║    ║
║  ┌─────┐     ┌──────┐     ┌────┐ ║
║  │ 🗝️  │ ··· │ 🚪P1 │ ··· │ 🔑 │ ║
║  └─────┘     └──────┘     └────┘ ║
║    ║            ║            ║    ║
║  ┌─────┐     ┌──────┐     ┌────┐ ║
║  │ 🔑  │ ··· │ HAB  │ ··· │ 🚪  │ ║
║  └─────┘     └──────┘     └────┘ ║
╚════════════════════════════════════╝
```

### Leyenda
- `HAB` = Habitación amplia (2x2 a 5x5 celdas)
- `🔑` = Llave (en callejones sin salida)
- `🚪` = Salida
- `🚪P1` = Puerta 1 (controlada por palanca)
- `🗝️` = Palanca
- `···` = Pasillos conectores

### Estrategia
1. Explorar el laberinto procedural
2. Encontrar llaves en callejones sin salida
3. Localizar la palanca (zona alejada)
4. Activar palanca para abrir puerta principal
5. Recoger todas las llaves
6. Escapar en 2 minutos

---

## 🌀 NIVEL 2: ESPIRAL CONCÉNTRICA

### Diseño
```
╔════════════════════════════════════╗
║ ┌──────────────────────────────┐  ║
║ │ 🗝️P1                      🔑 │  ║
║ │  ┌────────────────────────┐  │  ║
║ │  │ 🔑                 🚪P1│  │  ║
║ │  │  ┌──────────────────┐  │  │  ║
║ │  │  │ 🗝️P2      🚪P2  │  │  │  ║
║ │  │  │  ┌────────────┐  │  │  │  ║
║ │  │  │  │ 🔑   🚪P3 │  │  │  │  ║
║ │  │  │  │  ┌──────┐  │  │  │  │  ║
║ │  │  │  │  │  🚪  │  │  │  │  │  ║
║ │  │  │  │  └──────┘  │  │  │  │  ║
║ │  │  │  │      🗝️P3  │  │  │  │  ║
║ │  │  │  └────────────┘  │  │  │  ║
║ │  │  │          🔑       │  │  │  ║
║ │  │  └──────────────────┘  │  │  ║
║ │  └────────────────────────┘  │  ║
║ │ 🔑                            │  ║
║ └──────────────────────────────┘  ║
╚════════════════════════════════════╝
```

### Elementos
- **Puerta P1**: Bloquea espiral exterior (zona derecha)
- **Puerta P2**: Bloquea zona intermedia (horizontal)
- **Puerta P3**: Protege acceso al centro
- **Palanca P1**: Esquina superior derecha
- **Palanca P2**: Zona izquierda intermedia
- **Palanca P3**: Zona inferior del mapa

### Estrategia
1. Recorrer la espiral desde afuera hacia adentro
2. Activar palancas para abrir paso
3. Recoger las 4 llaves distribuidas
4. Llegar al centro donde está la salida
5. Escapar en 1:30 minutos

---

## 🏰 NIVEL 3: CÁMARAS INTERCONECTADAS

### Diseño
```
╔════════════════════════════════════╗
║ ZONA IZQUIERDA │ CENTRAL │ DERECHA║
║ ┌────────┐     │         │  ┌────┐║
║ │ 🗝️P1  │     │ 🚪P1   │  │🔑  │║
║ │ 🔑    │     │         │  │🗝️P3│║
║ │       │═════╪═════════╪══│    │║
║ └───────┘     │ 🗝️P2   │  │🚪P3│║
║ ┌───────┐     │         │  └────┘║
║ │ 🗝️P5  │     │ 🚪P2   │  ┌────┐║
║ │ 🔑    │     │         │  │🚪P4│║
║ │ 🚪P5  │     │ 🔑      │  │🗝️P4│║
║ └───────┘     │         │  │    │║
║               │         │  │🔑  │║
║               │         │  │🚪  │║
║               │         │  └────┘║
╚════════════════════════════════════╝
```

### Sistema de Puertas
1. **P1** (Verde): Entrada a zona central desde izquierda
2. **P2** (Azul): Paso horizontal en zona central
3. **P3** (Amarillo): Entrada a zona derecha
4. **P4** (Rojo): Acceso final (zona inferior derecha)
5. **P5** (Morado): Pasaje secreto en zona izquierda

### Distribución de Palancas
- **🗝️P1**: Zona izquierda superior
- **🗝️P2**: Zona central inferior
- **🗝️P3**: Zona derecha superior
- **🗝️P4**: Zona derecha inferior
- **🗝️P5**: Zona izquierda inferior (secreto)

### Estrategia Recomendada
1. **Fase 1 - Exploración Inicial**:
   - Recoger llave en zona inicial
   - Activar palanca P1 para acceder a zona central

2. **Fase 2 - Zona Central**:
   - Navegar por la zona central
   - Activar palanca P2 para abrir paso horizontal
   - Recoger llave en zona central

3. **Fase 3 - Expansión Derecha**:
   - Activar palanca P3 para acceder a zona derecha
   - Explorar zona derecha superior
   - Recoger llave en zona derecha

4. **Fase 4 - Zona Final**:
   - Activar palanca P4 para acceso final
   - Recoger llave en zona inferior derecha
   - Prepararse para activar escape

5. **Fase 5 - Secreto (Opcional)**:
   - Regresar a zona izquierda inferior
   - Activar palanca P5 para pasaje secreto
   - Recoger última llave si falta

6. **Fase 6 - Escape**:
   - Con todas las 5 llaves, se abre la salida
   - Tienes 1 minuto para escapar
   - Evitar enemigos o eliminarlos

---

## 🎯 Consejos por Nivel

### Nivel 1: Mazmorra Procedural
- ✅ Explora sistemáticamente cada pasillo
- ✅ Los callejones sin salida tienen llaves
- ✅ Memoriza la ubicación de la palanca
- ✅ Usa los escondites para evitar enemigos
- ⚠️ El laberinto cambia cada vez que juegas

### Nivel 2: Espiral
- ✅ Sigue el patrón de la espiral
- ✅ Activa las palancas en orden (P1 → P2 → P3)
- ✅ Las llaves están en las curvas de la espiral
- ✅ El centro tiene la salida, planea tu ruta de escape
- ⚠️ Los enemigos patrullan las capas

### Nivel 3: Cámaras
- ✅ Mapea mentalmente las 3 zonas
- ✅ Cada zona tiene su propia llave
- ✅ Las palancas controlan el flujo entre zonas
- ✅ Prioriza llaves sobre combate
- ✅ Usa las puertas para dividir enemigos
- ⚠️ No te quedes sin tiempo en zonas alejadas

---

## ⏱️ Gestión del Tiempo

### Fase de Exploración (Sin Límite)
- Recoge llaves
- Activa palancas
- Elimina enemigos estratégicamente
- Usa escondites

### Fase de Escape (Con Temporizador)
- **Nivel 1**: 2:00 minutos
- **Nivel 2**: 1:30 minutos
- **Nivel 3**: 1:00 minuto

### Advertencias
- **30 segundos restantes**: ⚠️ Mensaje de alerta
- **10 segundos restantes**: 🚨 Alerta crítica
- **0 segundos**: 💀 Enemigos infinitos aparecen

---

## 🏆 Consejos de Maestro

1. **Prioriza la Exploración**: Encuentra todas las llaves antes de activar el escape
2. **Memoriza Rutas**: Planea tu ruta de escape mientras exploras
3. **Gestiona Energía**: No gastes toda tu energía antes del escape
4. **Usa las Puertas**: Las puertas abiertas son atajos, las cerradas son puzzles
5. **Evita Combates Innecesarios**: Esquiva enemigos cuando sea posible
6. **Escóndete Estratégicamente**: Las zonas de escondite rompen la persecución
7. **Practica Cada Nivel**: Cada nivel requiere estrategias diferentes

---

## 📈 Progresión de Dificultad

```
Complejidad del Laberinto
    ^
    │     ┌────────────────
    │     │ NIVEL 3
    │   ┌─┘ (Cámaras + Puzzles)
    │   │
    │ ┌─┘ NIVEL 2
    │ │   (Espiral)
    │┌┘
    ││ NIVEL 1
    └┴────────────────────> Tiempo
     (Procedural)
```

¡Buena suerte en tu escape! 🏃‍♂️💨
