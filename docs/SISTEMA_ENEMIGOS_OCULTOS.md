# 🎮 Sistema de Enemigos Ocultos

## Concepto
**"Los peligros permanecen ocultos hasta que están cerca"**

Los enemigos ahora implementan un sistema de ocultamiento que crea tensión y sorpresa en el juego.

---

## ✨ Características Principales

### 1. **Ocultamiento Inicial**
- Todos los enemigos comienzan **completamente invisibles** (`alpha = 0`)
- No son detectables por el jugador hasta que este se acerca
- No atacan mientras están ocultos

### 2. **Revelación Gradual**
```
Distancia > 180px: Enemigo invisible (alpha = 0)
Distancia < 180px: Aparición gradual (alpha aumenta +15 por frame)
Distancia muy cerca: Completamente visible (alpha = 255)
```

### 3. **Revelación Permanente**
- Una vez que un enemigo se revela completamente (alpha = 255)
- Permanece **visible permanentemente**
- Ya no puede volver a ocultarse
- Esto evita confusión y mantiene la dinámica del juego

### 4. **Comportamiento Durante Ocultamiento**
- **Movimiento**: Patrullan normalmente (incluso ocultos)
- **Ataques**: NO atacan hasta estar revelados (alpha > 150)
- **Detección**: Siguen detectando al jugador pero no lo persiguen agresivamente
- **Colisión**: Siguen teniendo colisión física

---

## 🎯 Parámetros Configurables

```python
self.oculto = True                    # Estado inicial: oculto
self.rango_revelacion = 180           # Distancia de revelación (píxeles)
self.alpha_actual = 0                 # Transparencia (0-255)
self.revelado_permanente = False      # Una vez revelado, siempre visible
```

### Ajustar Dificultad

**Más Fácil** (jugador ve enemigos antes):
```python
self.rango_revelacion = 250  # Mayor rango
```

**Más Difícil** (enemigos más sorpresivos):
```python
self.rango_revelacion = 120  # Menor rango
```

---

## 🔧 Generación de Puntos de Spawn

### Método Estático: `generar_punto_spawn_aleatorio()`

Genera puntos de aparición seguros para enemigos:

```python
punto = enemigo.generar_punto_spawn_aleatorio(
    ancho_mapa=2000,
    alto_mapa=2000,
    muros=lista_muros,
    jugador_pos=(100, 100),
    distancia_minima=300,  # Lejos del jugador
    intentos=50
)
```

**Características:**
- ✅ Evita colisiones con muros
- ✅ Mantiene distancia mínima del jugador
- ✅ Área de seguridad de 120x120 píxeles
- ✅ Múltiples intentos de generación

### Método Estático: `generar_multiples_spawns()`

Genera múltiples puntos a la vez:

```python
puntos = enemigo.generar_multiples_spawns(
    cantidad=5,
    ancho_mapa=2000,
    alto_mapa=2000,
    muros=lista_muros,
    jugador_pos=(100, 100),
    distancia_minima=300
)

# Crear enemigos en los puntos generados
for x, y in puntos:
    nuevo_enemigo = enemigo(x, y, velocidad=3)
    enemigos.append(nuevo_enemigo)
```

---

## 📊 Ejemplo de Uso en Juego

### Generar Enemigos con Spawn Aleatorio

```python
# En la inicialización del nivel
def generar_enemigos_nivel(self):
    # Obtener posición del jugador
    jugador_pos = (self.jugador.rect.centerx, self.jugador.rect.centery)
    
    # Generar 5 puntos de spawn seguros
    puntos_spawn = enemigo.generar_multiples_spawns(
        cantidad=5,
        ancho_mapa=self.ancho_mapa,
        alto_mapa=self.alto_mapa,
        muros=self.muros,
        jugador_pos=jugador_pos,
        distancia_minima=350  # Lejos del jugador
    )
    
    # Crear enemigos en esos puntos
    tipos = ["veloz", "acechador", "bruto"]
    for i, (x, y) in enumerate(puntos_spawn):
        tipo = tipos[i % len(tipos)]  # Alternar tipos
        nuevo_enemigo = enemigo(x, y, velocidad=3, tipo=tipo)
        self.enemigos.append(nuevo_enemigo)
```

---

## 🎨 Efectos Visuales

### Transparencia Aplicada a Todo
- ✅ Imagen del enemigo
- ✅ Círculo de advertencia (veloz)
- ✅ Aura del bruto
- ✅ Proyectiles del acechador

### Sin Transparencia
- Los indicadores NO se muestran si `alpha_actual < 100`
- Esto mantiene el ocultamiento completo

---

## 🎮 Experiencia de Juego

### Tensión y Sorpresa
1. **Exploración**: Jugador camina por el mapa sin ver enemigos
2. **Revelación**: Enemigo aparece gradualmente al acercarse
3. **Combate**: Enemigo completamente visible y atacando
4. **Persistencia**: Enemigo permanece visible después de revelarse

### Ventajas del Sistema
- ✅ Aumenta la tensión y el suspenso
- ✅ Previene que el jugador vea todos los enemigos desde lejos
- ✅ Recompensa la exploración cuidadosa
- ✅ Crea momentos de sorpresa
- ✅ Mantiene el desafío constante

---

## 🛠️ Configuración Avanzada

### Desactivar el Sistema (modo clásico)
```python
# En __init__ del enemigo:
self.oculto = False
self.alpha_actual = 255
self.revelado_permanente = True
```

### Enemigos Siempre Ocultos (modo stealth)
```python
# En __init__ del enemigo:
self.rango_revelacion = 50  # Solo se ven muy cerca
self.revelado_permanente = False  # Pueden volver a ocultarse
```

### Modo Boss (siempre visible)
```python
# Crear enemigo especial
boss = enemigo(x, y, velocidad=2, tipo="bruto")
boss.oculto = False
boss.alpha_actual = 255
boss.revelado_permanente = True
```

---

## 📈 Estadísticas Recomendadas

| Tipo | Tamaño | Rango Revelación | Comportamiento |
|------|--------|------------------|----------------|
| Duende (veloz) | 90px | 180px | Ataque rápido al revelarse |
| Esqueleto (acechador) | 100px | 180px | Dispara al aparecer |
| Ogro (bruto) | 120px | 180px | Aura intimidante al revelarse |

---

## 🐛 Notas de Depuración

### Mensajes de Consola
```
Imagen duende.png cargada correctamente - Tamaño: 90x90
Imagen esqueleto.png cargada correctamente - Tamaño: 100x100
Imagen Ogro.png cargada correctamente - Tamaño: 120x120
```

### Verificar Estado de Enemigo
```python
print(f"Oculto: {enemigo.oculto}")
print(f"Alpha: {enemigo.alpha_actual}")
print(f"Revelado permanente: {enemigo.revelado_permanente}")
```

---

## 🎯 Próximas Mejoras Sugeridas

1. **Sonidos de Revelación**: Efecto de sonido cuando un enemigo aparece
2. **Partículas**: Efecto visual de aparición (niebla/sombras)
3. **Indicador de Proximidad**: Sonido ambiental cuando hay enemigos cerca pero ocultos
4. **Niveles de Dificultad**: Ajustar `rango_revelacion` según dificultad
5. **Enemigos Especiales**: Tipos que nunca se ocultan o que parpadean

---

**Creado**: 9 de noviembre de 2025  
**Sistema**: Enemigos Ocultos v1.0  
**Concepto**: "Los peligros permanecen ocultos hasta que están cerca"
