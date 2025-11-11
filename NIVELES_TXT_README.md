# 🎮 Sistema de Niveles - Formato TXT

## 📋 Resumen Rápido

Los niveles del juego están definidos en archivos **`.txt`** con formato simple y legible.

## 📁 Archivos Principales

```
mapas_export_nivel_1.txt  → Nivel 1 (43 muros, 3 llaves, 18 spawns)
mapas_export_nivel_2.txt  → Nivel 2 (66 muros, 4 llaves, 8 spawns)
mapas_export_nivel_3.txt  → Nivel 3 (58 muros, 5 llaves, 9 spawns)
```

## 📝 Formato del Archivo

Cada línea define un elemento:

```txt
# Comentarios comienzan con #

MURO x y ancho alto      # Paredes/obstáculos
LLAVE x y ancho alto     # Objetos coleccionables
SPAWN x y                # Puntos de aparición de enemigos
SALIDA x y               # Salida del nivel
```

## 💡 Ejemplo Práctico

```txt
# Nivel 1 - Ejemplo

# Bordes del mapa
MURO 0 0 2000 20
MURO 0 0 20 1500

# Muro interno
MURO 560 1190 360 30

# Llaves a recolectar
LLAVE 1267 1116 20 20
LLAVE 248 987 20 20

# Spawns de enemigos
SPAWN 1080 750
SPAWN 920 750

# Salida
SALIDA 793 549
```

## 🔧 Cómo Editar Niveles

1. **Abrir archivo** `mapas_export_nivel_X.txt` con cualquier editor
2. **Agregar/modificar** líneas según formato
3. **Guardar** archivo
4. **Ejecutar** juego - cambios se cargan automáticamente

## 🧪 Validar Cambios

Ejecutar el script de prueba:

```bash
python test_niveles_txt.py
```

**Salida esperada:**
```
[Nivel 1] ✓ 43 muros, 3 llaves, 18 spawns
[Nivel 2] ✓ 66 muros, 4 llaves, 8 spawns
[Nivel 3] ✓ 58 muros, 5 llaves, 9 spawns
```

## 🎯 Ventajas

- ✅ **Simple** - Sintaxis clara y directa
- ✅ **Editable** - Cualquier editor de texto
- ✅ **Documentable** - Comentarios integrados
- ✅ **Académico** - Cumple requisitos educativos
- ✅ **Ligero** - ~70% más pequeño que JSON

## 🛠️ Herramientas Disponibles

| Script | Función |
|--------|---------|
| `test_niveles_txt.py` | Validar carga de niveles |
| `conversor_niveles.py` | Convertir JSON ↔ TXT |
| `demo_sistema_txt.py` | Demostración completa |
| `mapas.py` | Editor visual de mapas |

## 📚 Documentación Completa

- **`docs/FORMATO_NIVELES_TXT.md`** - Guía detallada
- **`docs/RESUMEN_IMPLEMENTACION_TXT.md`** - Resumen técnico
- **`docs/CHANGELOG_TXT.md`** - Historial de cambios
- **`niveles_predeterminados.py`** - Especificación del formato

## 🚀 Comandos Útiles

```bash
# Ejecutar el juego
python main.py

# Validar niveles
python test_niveles_txt.py

# Ver demostración completa
python demo_sistema_txt.py

# Convertir JSON a TXT
python conversor_niveles.py json2txt 1

# Convertir TXT a JSON
python conversor_niveles.py txt2json 1

# Editor visual
python mapas.py
```

## 📐 Especificaciones

- **Dimensiones del mapa:** 2000 × 1500 píxeles
- **Llaves mínimas:** 3 por nivel
- **Spawns recomendados:** 8-18 por nivel
- **Formato:** TXT con encoding UTF-8
- **Valores:** Solo enteros

## ✅ Estado

**Sistema completamente funcional y probado**

- ✓ 3 niveles implementados
- ✓ Parser robusto
- ✓ Documentación completa
- ✓ Herramientas incluidas
- ✓ Listo para producción

---

**Versión:** 1.0.0  
**Fecha:** Noviembre 2025  
**Implementado por:** Sistema Fear of Ways 0
