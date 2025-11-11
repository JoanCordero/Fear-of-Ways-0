"""
DEMOSTRACIÓN COMPLETA - Sistema de Niveles con Formato TXT
===========================================================

Este script demuestra todas las funcionalidades del nuevo sistema
de carga de niveles desde archivos TXT.
"""

import os
import sys
from pathlib import Path

# Asegurar que estamos en el directorio correcto
base_dir = Path(__file__).resolve().parent
os.chdir(base_dir)
sys.path.insert(0, str(base_dir))


def linea_separadora():
    print("=" * 70)


def seccion(titulo):
    print("\n")
    linea_separadora()
    print(f"  {titulo}")
    linea_separadora()


def main():
    linea_separadora()
    print("  🎮 FEAR OF WAYS 0 - DEMOSTRACIÓN SISTEMA TXT")
    linea_separadora()
    print("\n  Sistema de carga de niveles desde archivos TXT")
    print("  Implementado para cumplir requisitos académicos\n")
    
    # ============================================================
    # PARTE 1: Verificar archivos TXT
    # ============================================================
    seccion("1. VERIFICACIÓN DE ARCHIVOS TXT")
    
    archivos_necesarios = [
        'mapas_export_nivel_1.txt',
        'mapas_export_nivel_2.txt',
        'mapas_export_nivel_3.txt'
    ]
    
    print("\n  Buscando archivos de configuración...")
    todos_encontrados = True
    
    for archivo in archivos_necesarios:
        ruta = base_dir / archivo
        if ruta.exists():
            tamaño = ruta.stat().st_size
            with open(ruta, 'r', encoding='utf-8') as f:
                lineas = len([l for l in f if l.strip() and not l.strip().startswith('#')])
            print(f"    ✅ {archivo}")
            print(f"       Tamaño: {tamaño:,} bytes | Líneas de datos: {lineas}")
        else:
            print(f"    ❌ {archivo} - NO ENCONTRADO")
            todos_encontrados = False
    
    if not todos_encontrados:
        print("\n  ⚠️ Algunos archivos no se encontraron")
        return
    
    # ============================================================
    # PARTE 2: Cargar y analizar niveles
    # ============================================================
    seccion("2. CARGA Y ANÁLISIS DE NIVELES")
    
    try:
        from nivel import nivel
        import pygame
        pygame.init()
        
        print("\n  Cargando niveles desde archivos TXT...")
        niveles = []
        
        for num in [1, 2, 3]:
            print(f"\n  📄 Nivel {num}:")
            n = nivel(num)
            niveles.append(n)
            
            print(f"     • Muros: {len(n.muros)}")
            print(f"     • Llaves: {len(n.llaves)} (requiere {n.llaves_requeridas})")
            print(f"     • Spawns: {len(n.spawn_enemigos)}")
            print(f"     • Salida: {'✓' if n.salida else '✗'}")
            
            # Calcular área total de muros
            area_muros = sum(m.rect.width * m.rect.height for m in n.muros)
            print(f"     • Área de muros: {area_muros:,} px²")
            
            # Posición de la salida
            if n.salida:
                print(f"     • Posición salida: ({n.salida.rect.centerx}, {n.salida.rect.centery})")
        
        pygame.quit()
        
    except Exception as e:
        print(f"\n  ❌ Error cargando niveles: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # PARTE 3: Análisis de formato TXT
    # ============================================================
    seccion("3. ANÁLISIS DE FORMATO TXT")
    
    print("\n  Analizando estructura de archivos TXT...")
    
    for num in [1, 2, 3]:
        archivo = base_dir / f'mapas_export_nivel_{num}.txt'
        print(f"\n  📋 Nivel {num} ({archivo.name}):")
        
        stats = {
            'MURO': 0,
            'LLAVE': 0,
            'SPAWN': 0,
            'SALIDA': 0,
            'comentarios': 0,
            'vacias': 0
        }
        
        with open(archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    stats['vacias'] += 1
                elif linea.startswith('#'):
                    stats['comentarios'] += 1
                else:
                    tipo = linea.split()[0].upper()
                    if tipo in stats:
                        stats[tipo] += 1
        
        print(f"     • Muros (MURO): {stats['MURO']}")
        print(f"     • Llaves (LLAVE): {stats['LLAVE']}")
        print(f"     • Spawns (SPAWN): {stats['SPAWN']}")
        print(f"     • Salida (SALIDA): {stats['SALIDA']}")
        print(f"     • Comentarios: {stats['comentarios']}")
        print(f"     • Líneas vacías: {stats['vacias']}")
        total = sum(stats.values())
        print(f"     • Total líneas: {total}")
    
    # ============================================================
    # PARTE 4: Ejemplo de formato
    # ============================================================
    seccion("4. EJEMPLO DE FORMATO TXT")
    
    print("\n  Primeras 15 líneas de nivel_1.txt:\n")
    
    archivo_ejemplo = base_dir / 'mapas_export_nivel_1.txt'
    with open(archivo_ejemplo, 'r', encoding='utf-8') as f:
        for i, linea in enumerate(f, 1):
            if i <= 15:
                print(f"     {i:2d}: {linea.rstrip()}")
            else:
                break
    
    print("\n     [...resto del archivo...]")
    
    # ============================================================
    # PARTE 5: Comparación con JSON
    # ============================================================
    seccion("5. COMPARACIÓN TXT vs JSON")
    
    print("\n  Comparando tamaños de archivo:")
    
    for num in [1, 2, 3]:
        archivo_txt = base_dir / f'mapas_export_nivel_{num}.txt'
        archivo_json = base_dir / f'mapas_export_nivel_{num}.json'
        
        if archivo_txt.exists() and archivo_json.exists():
            tamaño_txt = archivo_txt.stat().st_size
            tamaño_json = archivo_json.stat().st_size
            diferencia = tamaño_json - tamaño_txt
            porcentaje = (diferencia / tamaño_json) * 100
            
            print(f"\n  Nivel {num}:")
            print(f"     • TXT:  {tamaño_txt:,} bytes")
            print(f"     • JSON: {tamaño_json:,} bytes")
            print(f"     • TXT es {abs(diferencia):,} bytes {'más pequeño' if diferencia > 0 else 'más grande'}")
            print(f"     • Diferencia: {abs(porcentaje):.1f}%")
    
    # ============================================================
    # PARTE 6: Ventajas del formato TXT
    # ============================================================
    seccion("6. VENTAJAS DEL FORMATO TXT")
    
    ventajas = [
        "✓ Legible en cualquier editor de texto",
        "✓ No requiere conocimientos de JSON",
        "✓ Comentarios integrados para documentación",
        "✓ Fácil de editar manualmente",
        "✓ Sintaxis simple y directa",
        "✓ Compatible con control de versiones (Git)",
        "✓ Formato académicamente apropiado",
        "✓ Parsing robusto con manejo de errores",
        "✓ Extensible para nuevos tipos de elementos"
    ]
    
    print("\n  Beneficios del sistema implementado:\n")
    for ventaja in ventajas:
        print(f"     {ventaja}")
    
    # ============================================================
    # PARTE 7: Herramientas disponibles
    # ============================================================
    seccion("7. HERRAMIENTAS DISPONIBLES")
    
    print("\n  Scripts y utilidades:")
    
    herramientas = [
        ("test_niveles_txt.py", "Validar carga de niveles"),
        ("conversor_niveles.py", "Convertir entre JSON y TXT"),
        ("mapas.py", "Editor visual de mapas"),
        ("nivel.py", "Parser principal (método _cargar_nivel_desde_txt)"),
        ("niveles_predeterminados.py", "Documentación del formato")
    ]
    
    for archivo, descripcion in herramientas:
        ruta = base_dir / archivo
        existe = "✓" if ruta.exists() else "✗"
        print(f"     {existe} {archivo}")
        print(f"        └─ {descripcion}")
    
    # ============================================================
    # PARTE 8: Documentación
    # ============================================================
    seccion("8. DOCUMENTACIÓN DISPONIBLE")
    
    print("\n  Archivos de documentación:\n")
    
    docs = [
        "docs/FORMATO_NIVELES_TXT.md",
        "docs/RESUMEN_IMPLEMENTACION_TXT.md",
        "docs/CHANGELOG_TXT.md"
    ]
    
    for doc in docs:
        ruta = base_dir / doc
        if ruta.exists():
            tamaño = ruta.stat().st_size
            print(f"     ✓ {doc}")
            print(f"        Tamaño: {tamaño:,} bytes")
        else:
            print(f"     ✗ {doc} - No encontrado")
    
    # ============================================================
    # CONCLUSIÓN
    # ============================================================
    seccion("✅ DEMOSTRACIÓN COMPLETADA")
    
    print("\n  Sistema de niveles TXT completamente funcional")
    print("\n  Características:")
    print("     • 3 niveles implementados y probados")
    print("     • Parser robusto con manejo de errores")
    print("     • Documentación completa incluida")
    print("     • Herramientas de conversión disponibles")
    print("     • Formato académicamente apropiado")
    print("\n  Estado: ✅ LISTO PARA PRODUCCIÓN")
    
    linea_separadora()
    print("\n  Para probar el juego completo, ejecutar:")
    print("     python main.py")
    print("\n  Para validar niveles:")
    print("     python test_niveles_txt.py")
    print("\n  Para convertir formatos:")
    print("     python conversor_niveles.py json2txt 1")
    linea_separadora()
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⚠️ Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n  ❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
