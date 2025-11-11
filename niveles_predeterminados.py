"""
NIVELES PREDETERMINADOS - FORMATO TXT
======================================

Este archivo documenta el formato de los archivos TXT utilizados para definir
los niveles del juego "Fear of Ways 0".

ARCHIVOS DE NIVELES:
-------------------
- mapas_export_nivel_1.txt
- mapas_export_nivel_2.txt
- mapas_export_nivel_3.txt

FORMATO DEL ARCHIVO:
-------------------
Cada línea del archivo representa un elemento del mapa. El formato es:

TIPO valor1 valor2 [valor3] [valor4]

Donde TIPO puede ser:
- MURO: Define un muro rectangular
- LLAVE: Define una llave recolectable
- SPAWN: Define un punto de aparición de enemigos
- SALIDA: Define la salida del nivel

SINTAXIS DETALLADA:
------------------

1. MURO x y w h
   - x: coordenada X (píxeles)
   - y: coordenada Y (píxeles)
   - w: ancho (píxeles)
   - h: alto (píxeles)
   
   Ejemplo: MURO 100 200 50 150

2. LLAVE x y w h
   - x: coordenada X (píxeles)
   - y: coordenada Y (píxeles)
   - w: ancho (píxeles, típicamente 20)
   - h: alto (píxeles, típicamente 20)
   
   Ejemplo: LLAVE 500 600 20 20

3. SPAWN x y
   - x: coordenada X (píxeles)
   - y: coordenada Y (píxeles)
   
   Ejemplo: SPAWN 300 400

4. SALIDA x y
   - x: coordenada X central (píxeles)
   - y: coordenada Y central (píxeles)
   
   Ejemplo: SALIDA 1800 1350

REGLAS:
-------
- Las líneas que comienzan con # son comentarios y se ignoran
- Las líneas vacías se ignoran
- Los valores deben estar separados por espacios
- Todos los valores numéricos deben ser enteros
- El orden de las líneas no importa (excepto que es recomendable agrupar por tipo)

ESTRUCTURA DEL MAPA:
-------------------
- Dimensiones totales: 2000 x 1500 píxeles
- Los muros perimetrales (bordes del mapa) son obligatorios
- Cada nivel requiere al menos 3 llaves
- Se recomienda entre 8-18 spawns de enemigos por nivel
- Solo debe haber una salida por nivel

EJEMPLO COMPLETO:
----------------
# Nivel de ejemplo
# Bordes del mapa
MURO 0 0 2000 20
MURO 0 1480 2000 20
MURO 0 0 20 1500
MURO 1980 0 20 1500

# Muros internos
MURO 400 300 200 30
MURO 800 500 30 400

# Llaves
LLAVE 450 350 20 20
LLAVE 850 650 20 20
LLAVE 1200 800 20 20

# Spawns de enemigos
SPAWN 600 400
SPAWN 1000 700
SPAWN 1400 900

# Salida
SALIDA 1800 1350

CÓMO EDITAR LOS NIVELES:
------------------------
1. Abrir el archivo .txt del nivel a editar
2. Agregar/modificar líneas siguiendo el formato especificado
3. Guardar el archivo
4. El juego cargará automáticamente los cambios al iniciar el nivel

HERRAMIENTA DE EDICIÓN:
-----------------------
Puedes usar mapas.py para editar visualmente los niveles:
- Ejecutar: python mapas.py
- Presionar 'M' para entrar en modo edición
- Usar las herramientas para agregar/eliminar elementos
- Presionar 'L' para exportar los cambios a JSON (luego convertir a TXT si necesario)

VALIDACIÓN:
----------
El parser de nivel (_cargar_nivel_desde_txt en nivel.py) hace lo siguiente:
- Ignora líneas malformadas y continúa con las siguientes
- Imprime errores en consola si hay problemas de parseo
- Usa valores por defecto si falta información crítica (como la salida)
- Retorna False si el archivo no existe o hay error fatal

VENTAJAS DEL FORMATO TXT:
-------------------------
✓ Fácil de leer y editar con cualquier editor de texto
✓ Formato simple y directo
✓ Comentarios para documentar secciones
✓ No requiere conocimientos de JSON o programación
✓ Fácil de versionar en sistemas de control de versiones
✓ Compatible con requisitos académicos

CONVERSIÓN JSON A TXT:
---------------------
Si tienes archivos JSON existentes, puedes convertirlos manualmente:
- JSON: {"x": 100, "y": 200, "w": 50, "h": 75}
- TXT: MURO 100 200 50 75

Para spawns:
- JSON: {"x": 300, "y": 400}
- TXT: SPAWN 300 400

Para salida:
- JSON: {"x": 1800, "y": 1350}
- TXT: SALIDA 1800 1350
"""

# Este archivo es solo documentación y no contiene código ejecutable
# Los niveles se cargan directamente desde los archivos .txt
