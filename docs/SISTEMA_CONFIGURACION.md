# Sistema de Configuración - Fear of Ways 0

## Descripción General
Se ha implementado un menú de configuración completo que permite a los jugadores ajustar las preferencias del juego en tiempo de ejecución, incluyendo el modo de visualización y los niveles de volumen.

## Características Implementadas

### 1. Opción de Menú Principal
- Se agregó "Configuración" como cuarta opción en el menú principal
- Accesible desde el menú principal con un solo clic
- Integrado con el sistema de navegación existente del menú

### 2. Pantalla de Configuración (`pantalla_configuracion()`)

#### Modo de Pantalla
- **Toggle Pantalla Completa/Ventana**
  - Botón interactivo que muestra el modo actual
  - Click para alternar entre:
    - Pantalla completa (resolución nativa del monitor)
    - Modo ventana (1280x720, redimensionable)
  - Estados visuales:
    - Hover: Resaltado dorado con borde
    - Normal: Gris claro con borde sutil

#### Control de Volumen de Música
- **Slider interactivo horizontal**
  - Barra de progreso visual (azul)
  - Indicador circular arrastrable
  - Rango: 0-100%
  - Actualización en tiempo real
  - Muestra porcentaje numérico
- **Funcionalidad:**
  - Click en cualquier punto de la barra para saltar a ese volumen
  - Ajuste inmediato de `pygame.mixer.music.set_volume()`

#### Control de Volumen de Efectos
- **Slider interactivo horizontal**
  - Barra de progreso visual (verde)
  - Indicador circular arrastrable
  - Rango: 0-100%
  - Actualización en tiempo real
  - Muestra porcentaje numérico
- **Funcionalidad:**
  - Click en cualquier punto de la barra para saltar a ese volumen
  - Actualiza todos los efectos de sonido:
    - Disparos
    - Golpes
    - Clicks de menú
    - Corazón
    - Notificaciones
    - Pociones
    - Llaves
    - Rayos

### 3. Método `toggle_fullscreen()`
```python
def toggle_fullscreen(self):
    """Alterna entre modo pantalla completa y ventana"""
```

**Funcionalidad:**
- Detecta el estado actual de la pantalla usando `pygame.FULLSCREEN` flag
- Cambia entre modos sin reiniciar el juego
- Mantiene todo el contexto del juego
- Muestra mensaje de confirmación
- Ventana modo: 1280x720 con flag `pygame.RESIZABLE`
- Pantalla completa: Resolución nativa del monitor

### 4. Integración con el Sistema de Juego

#### Estado "configuracion"
Se agregó un nuevo estado al sistema de estados del juego:
- Manejo de eventos en el loop principal
- Renderizado dedicado
- Navegación fluida (ESC para volver)

#### Event Handlers
```python
elif self.estado == "configuracion":
    # Manejo de teclado
    - ESC: Volver al menú principal
    
    # Manejo de mouse
    - Click en botón de pantalla completa: Toggle display mode
    - Click en slider de música: Ajustar volumen de música
    - Click en slider de efectos: Ajustar volumen de efectos
```

## Diseño Visual

### Estética Consistente
- Usa la misma fuente pixelada del juego
- Fondo: Imagen `menu_background.png` (fallback a negro)
- Título con efecto de sombra (igual que otros menús)
- Colores coherentes con la paleta del juego:
  - Dorado: (255, 215, 0) - Hover y resaltado
  - Gris claro: (235, 225, 210) - Texto normal
  - Azul: (100, 150, 255) - Volumen música
  - Verde: (100, 255, 150) - Volumen efectos

### Layout Responsivo
- Todos los tamaños calculados como porcentaje del alto/ancho de pantalla
- Se adapta automáticamente a diferentes resoluciones
- Spacing proporcional entre elementos

## Instrucciones para el Usuario

**En la Pantalla de Configuración:**
```
"Haz clic en los controles para ajustar"
"ESC para volver al menú"
```

**Ubicación de Elementos:**
- Título: 18% desde arriba
- Modo de pantalla: 35% desde arriba
- Slider música: 50% desde arriba
- Slider efectos: 62% desde arriba
- Instrucciones: 82-90% desde arriba

## Código Modificado

### Archivos Afectados
1. **juego.py**
   - Línea ~293: Agregada opción "Configuración" al array de opciones
   - Línea ~2434: Agregado handler para opción de configuración en menú
   - Línea ~2660: Agregado handler de eventos para estado "configuracion"
   - Línea ~2750: Agregado renderizado de pantalla de configuración
   - Línea ~1928: Método `pantalla_configuracion()` (150+ líneas)
   - Línea ~2079: Método `toggle_fullscreen()` (20 líneas)

### Nuevos Atributos (ya existían)
- `self.volumen_musica`: Float (0.0-1.0) - Volumen actual de música
- `self.volumen_efectos`: Float (0.0-1.0) - Volumen actual de efectos

### Nuevos Hitboxes Temporales
- `_config_fullscreen_rect`: Área del botón de pantalla completa
- `_config_music_slider_rect`: Área interactiva del slider de música
- `_config_music_track_rect`: Track (barra) del slider de música
- `_config_effects_slider_rect`: Área interactiva del slider de efectos
- `_config_effects_track_rect`: Track (barra) del slider de efectos

## Flujo de Usuario

```
Menú Principal
    ↓
[Click en "Configuración"]
    ↓
Pantalla de Configuración
    ├─→ [Click en "Pantalla Completa/Ventana"] → Toggle display mode
    ├─→ [Click en slider música] → Ajustar volumen música
    ├─→ [Click en slider efectos] → Ajustar volumen efectos
    └─→ [Presionar ESC] → Volver al Menú Principal
```

## Características Técnicas

### Persistencia
**Nota:** Actualmente los cambios NO se guardan entre sesiones. Los valores regresan a:
- `volumen_musica = 0.3` (30%)
- `volumen_efectos = 0.7` (70%)
- Modo: Pantalla completa por defecto

**Mejora Futura:** Implementar sistema de guardado de configuración en archivo `.ini` o `.json`

### Compatibilidad
- ✅ Probado en Windows 10/11
- ✅ Compatible con monitores múltiples
- ✅ Funciona con diferentes resoluciones
- ✅ Modo ventana es redimensionable manualmente

## Testing Realizado

### Pruebas Funcionales
1. ✅ Navegación al menú de configuración
2. ✅ Toggle entre pantalla completa y ventana
3. ✅ Ajuste de volumen de música (0-100%)
4. ✅ Ajuste de volumen de efectos (0-100%)
5. ✅ Cambios se aplican inmediatamente
6. ✅ ESC regresa al menú principal
7. ✅ Interfaz responde a hover del mouse
8. ✅ Click de sonido al interactuar

### Pruebas de Integración
1. ✅ No interfiere con otros menús
2. ✅ Estados del juego se mantienen
3. ✅ No hay errores de consola
4. ✅ Fuentes y estilos consistentes
5. ✅ Sonidos se actualizan correctamente

## Uso del Sistema

### Para Cambiar a Ventana:
1. Abrir el juego (inicia en pantalla completa)
2. Menú principal → "Configuración"
3. Click en botón "Pantalla Completa"
4. Ahora muestra "Ventana" y el juego está en modo ventana

### Para Ajustar Volumen:
1. Menú principal → "Configuración"
2. Click en cualquier punto de la barra azul (música) o verde (efectos)
3. El volumen cambia inmediatamente
4. El porcentaje se actualiza en tiempo real

### Para Volver a Pantalla Completa:
1. En "Configuración"
2. Click en botón "Ventana"
3. Cambia a "Pantalla Completa" y el juego ocupa toda la pantalla

## Conclusión

El sistema de configuración ha sido implementado exitosamente con:
- ✅ Interfaz intuitiva y visual
- ✅ Controles responsivos con feedback inmediato
- ✅ Toggle de pantalla completa/ventana sin reiniciar
- ✅ Control granular de volúmenes (música y efectos por separado)
- ✅ Diseño coherente con el resto del juego
- ✅ Código limpio y bien integrado

El jugador ahora tiene control completo sobre la experiencia audiovisual del juego.
