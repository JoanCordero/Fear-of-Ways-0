# Sistema de Niveles con Archivos TXT

## 📋 Descripción

Los niveles del juego "Fear of Ways 0" se definen mediante archivos de texto plano (`.txt`) que permiten configurar todos los elementos del mapa de forma simple y legible.

## 📁 Archivos de Niveles

- `mapas_export_nivel_1.txt` - Configuración del Nivel 1
- `mapas_export_nivel_2.txt` - Configuración del Nivel 2  
- `mapas_export_nivel_3.txt` - Configuración del Nivel 3

## 📝 Formato del Archivo TXT

Cada línea define un elemento del mapa usando el siguiente formato:

```
TIPO valor1 valor2 [valor3] [valor4]
```

### Tipos de Elementos

#### 1. MURO (Paredes/Obstáculos)
```
MURO x y ancho alto
```
- **x**: Coordenada X en píxeles
- **y**: Coordenada Y en píxeles
- **ancho**: Ancho del muro en píxeles
- **alto**: Alto del muro en píxeles

**Ejemplo:**
```
MURO 100 200 50 150
```

#### 2. LLAVE (Objetos coleccionables)
```
LLAVE x y ancho alto
```
- **x**: Coordenada X en píxeles
- **y**: Coordenada Y en píxeles
- **ancho**: Ancho (típicamente 20 píxeles)
- **alto**: Alto (típicamente 20 píxeles)

**Ejemplo:**
```
LLAVE 500 600 20 20
```

#### 3. SPAWN (Puntos de aparición de enemigos)
```
SPAWN x y
```
- **x**: Coordenada X en píxeles
- **y**: Coordenada Y en píxeles

**Ejemplo:**
```
SPAWN 300 400
```

#### 4. SALIDA (Puerta de salida del nivel)
```
SALIDA x y
```
- **x**: Coordenada X central en píxeles
- **y**: Coordenada Y central en píxeles

**Ejemplo:**
```
SALIDA 1800 1350
```

## 📐 Especificaciones del Mapa

- **Dimensiones totales:** 2000 x 1500 píxeles
- **Bordes obligatorios:** Muros perimetrales en los 4 lados
- **Llaves mínimas:** 3 por nivel
- **Spawns recomendados:** 8-18 enemigos por nivel
- **Salidas:** 1 por nivel

## 💡 Reglas de Sintaxis

✅ **Permitido:**
- Líneas que comienzan con `#` son comentarios
- Líneas vacías se ignoran
- Espacios entre valores

❌ **No permitido:**
- Valores decimales (solo enteros)
- Valores negativos para ancho/alto
- Múltiples elementos en una línea

## 📄 Ejemplo Completo

```txt
# Nivel de Ejemplo - Configuración Básica

# === BORDES DEL MAPA ===
MURO 0 0 2000 20
MURO 0 1480 2000 20
MURO 0 0 20 1500
MURO 1980 0 20 1500

# === MUROS INTERNOS ===
MURO 400 300 200 30
MURO 800 500 30 400

# === LLAVES A RECOLECTAR ===
LLAVE 450 350 20 20
LLAVE 850 650 20 20
LLAVE 1200 800 20 20

# === PUNTOS DE SPAWN DE ENEMIGOS ===
SPAWN 600 400
SPAWN 1000 700
SPAWN 1400 900

# === SALIDA DEL NIVEL ===
SALIDA 1800 1350
```

## 🔧 Cómo Editar Niveles

### Método 1: Editor de Texto
1. Abrir el archivo `.txt` del nivel con cualquier editor
2. Agregar/modificar líneas siguiendo el formato
3. Guardar el archivo
4. El juego cargará automáticamente los cambios

### Método 2: Editor Visual (mapas.py)
1. Ejecutar: `python mapas.py`
2. Presionar `M` para modo edición
3. Usar herramientas visuales:
   - `W` - Agregar muros
   - `K` - Agregar llaves
   - `S` - Agregar spawns
   - `E` - Colocar salida
4. Presionar `L` para exportar (genera JSON, convertir manualmente a TXT)

## 🧪 Verificar Niveles

Ejecutar el script de prueba para verificar que los niveles se cargan correctamente:

```powershell
python test_niveles_txt.py
```

**Salida esperada:**
```
============================================================
PRUEBA DE CARGA DE NIVELES DESDE ARCHIVOS TXT
============================================================

[Nivel 1]
  ✓ Muros: 43
  ✓ Llaves: 3 (requiere 3)
  ✓ Spawns de enemigos: 18
  ✓ Salida: True

[Nivel 2]
  ✓ Muros: 66
  ✓ Llaves: 4 (requiere 4)
  ✓ Spawns de enemigos: 8
  ✓ Salida: True

[Nivel 3]
  ✓ Muros: 58
  ✓ Llaves: 5 (requiere 5)
  ✓ Spawns de enemigos: 9
  ✓ Salida: True
```

## 🏗️ Arquitectura del Sistema

### Flujo de Carga
```
nivel.py
   └─> crear_nivel_X()
        └─> _cargar_nivel_desde_txt(numero)
             ├─> Lee archivo .txt línea por línea
             ├─> Parsea cada tipo de elemento
             ├─> Crea objetos (pared, llave, spawn, salida)
             └─> Retorna True si exitoso
```

### Código Principal
El método `_cargar_nivel_desde_txt()` en `nivel.py`:
```python
def _cargar_nivel_desde_txt(self, numero_nivel):
    # Lee el archivo correspondiente
    archivo_txt = Path(__file__).parent / f'mapas_export_nivel_{numero_nivel}.txt'
    
    # Procesa cada línea
    for linea in archivo:
        partes = linea.strip().split()
        tipo = partes[0].upper()
        
        # Crea el elemento según el tipo
        if tipo == 'MURO':
            self.muros.append(pared(x, y, w, h))
        elif tipo == 'LLAVE':
            self.llaves.append(pygame.Rect(x, y, w, h))
        # ... etc
```

## ✅ Ventajas del Formato TXT

- ✏️ **Fácil de editar** - Cualquier editor de texto
- 📖 **Legible** - Formato claro y descriptivo
- 📝 **Documentable** - Comentarios integrados
- 🎓 **Académico** - Cumple requisitos educativos
- 🔄 **Versionable** - Git-friendly
- 🛠️ **Simple** - No requiere conocimientos técnicos

## 🐛 Manejo de Errores

El parser es robusto y maneja:
- ✓ Líneas malformadas (las ignora)
- ✓ Valores inválidos (imprime warning)
- ✓ Archivo inexistente (usa generador procedural)
- ✓ Elementos faltantes (usa valores por defecto)

Los errores se imprimen en consola para debugging:
```
Error parseando línea 'MURO 100 abc 50 75': invalid literal for int()
```

## 📚 Referencias

- `nivel.py` - Clase principal de nivel y parser TXT
- `niveles_predeterminados.py` - Documentación detallada del formato
- `test_niveles_txt.py` - Script de validación
- `mapas_export_nivel_*.txt` - Archivos de configuración de niveles

---

**Implementado por:** Sistema de carga basado en texto plano  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
