"""
Script de prueba para verificar que los niveles se cargan correctamente desde TXT
"""
import sys
sys.path.insert(0, r'c:\Users\chito\OneDrive - Estudiantes ITCR\Escritorio\ProyectoINTRO\Fear of Ways 0')

try:
    from nivel import nivel
    
    print("=" * 60)
    print("PRUEBA DE CARGA DE NIVELES DESDE ARCHIVOS TXT")
    print("=" * 60)
    
    # Probar nivel 1
    print("\n[Nivel 1]")
    n1 = nivel(1)
    print(f"  ✓ Muros: {len(n1.muros)}")
    print(f"  ✓ Llaves: {len(n1.llaves)} (requiere {n1.llaves_requeridas})")
    print(f"  ✓ Spawns de enemigos: {len(n1.spawn_enemigos)}")
    print(f"  ✓ Salida: {n1.salida is not None}")
    
    # Probar nivel 2
    print("\n[Nivel 2]")
    n2 = nivel(2)
    print(f"  ✓ Muros: {len(n2.muros)}")
    print(f"  ✓ Llaves: {len(n2.llaves)} (requiere {n2.llaves_requeridas})")
    print(f"  ✓ Spawns de enemigos: {len(n2.spawn_enemigos)}")
    print(f"  ✓ Salida: {n2.salida is not None}")
    
    # Probar nivel 3
    print("\n[Nivel 3]")
    n3 = nivel(3)
    print(f"  ✓ Muros: {len(n3.muros)}")
    print(f"  ✓ Llaves: {len(n3.llaves)} (requiere {n3.llaves_requeridas})")
    print(f"  ✓ Spawns de enemigos: {len(n3.spawn_enemigos)}")
    print(f"  ✓ Salida: {n3.salida is not None}")
    
    print("\n" + "=" * 60)
    print("TODOS LOS NIVELES SE CARGARON EXITOSAMENTE DESDE TXT")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
