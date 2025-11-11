"""
Conversor entre formatos JSON y TXT para niveles del juego
Uso:
    python conversor_niveles.py json2txt nivel_1  # Convierte JSON a TXT
    python conversor_niveles.py txt2json nivel_1  # Convierte TXT a JSON
"""
import json
import sys
from pathlib import Path


def json_a_txt(numero_nivel):
    """Convierte un archivo JSON a formato TXT"""
    base = Path(__file__).resolve().parent
    archivo_json = base / f'mapas_export_nivel_{numero_nivel}.json'
    archivo_txt = base / f'mapas_export_nivel_{numero_nivel}.txt'
    
    if not archivo_json.exists():
        print(f"❌ Error: No se encuentra {archivo_json}")
        return False
    
    try:
        # Leer JSON
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Escribir TXT
        with open(archivo_txt, 'w', encoding='utf-8') as f:
            f.write(f"# Nivel {numero_nivel} - Configuración del Mapa\n")
            f.write("# Formato: TIPO x y w h (para muros y llaves)\n")
            f.write("#          SPAWN x y (para spawns de enemigos)\n")
            f.write("#          SALIDA x y (para la salida)\n\n")
            
            # Muros
            f.write("# Muros del mapa\n")
            for muro in data.get('muros', []):
                f.write(f"MURO {muro['x']} {muro['y']} {muro['w']} {muro['h']}\n")
            f.write("\n")
            
            # Llaves
            f.write("# Llaves a recolectar\n")
            for llave in data.get('llaves', []):
                w = llave.get('w', 20)
                h = llave.get('h', 20)
                f.write(f"LLAVE {llave['x']} {llave['y']} {w} {h}\n")
            f.write("\n")
            
            # Spawns
            f.write("# Puntos de spawn de enemigos\n")
            for spawn in data.get('spawns', []):
                f.write(f"SPAWN {spawn['x']} {spawn['y']}\n")
            f.write("\n")
            
            # Salida
            salida = data.get('salida')
            if salida:
                f.write("# Salida del nivel\n")
                f.write(f"SALIDA {salida['x']} {salida['y']}\n")
        
        print(f"✅ Convertido: {archivo_json} → {archivo_txt}")
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir: {e}")
        return False


def txt_a_json(numero_nivel):
    """Convierte un archivo TXT a formato JSON"""
    base = Path(__file__).resolve().parent
    archivo_txt = base / f'mapas_export_nivel_{numero_nivel}.txt'
    archivo_json = base / f'mapas_export_nivel_{numero_nivel}.json'
    
    if not archivo_txt.exists():
        print(f"❌ Error: No se encuentra {archivo_txt}")
        return False
    
    try:
        data = {
            'nivel': numero_nivel,
            'muros': [],
            'llaves': [],
            'spawns': [],
            'salida': None
        }
        
        # Leer TXT
        with open(archivo_txt, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                
                # Ignorar comentarios y líneas vacías
                if not linea or linea.startswith('#'):
                    continue
                
                partes = linea.split()
                if not partes:
                    continue
                
                tipo = partes[0].upper()
                
                try:
                    if tipo == 'MURO' and len(partes) >= 5:
                        data['muros'].append({
                            'x': int(partes[1]),
                            'y': int(partes[2]),
                            'w': int(partes[3]),
                            'h': int(partes[4])
                        })
                    
                    elif tipo == 'LLAVE' and len(partes) >= 5:
                        data['llaves'].append({
                            'x': int(partes[1]),
                            'y': int(partes[2]),
                            'w': int(partes[3]),
                            'h': int(partes[4])
                        })
                    
                    elif tipo == 'SPAWN' and len(partes) >= 3:
                        data['spawns'].append({
                            'x': int(partes[1]),
                            'y': int(partes[2])
                        })
                    
                    elif tipo == 'SALIDA' and len(partes) >= 3:
                        data['salida'] = {
                            'x': int(partes[1]),
                            'y': int(partes[2])
                        }
                
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Línea ignorada '{linea}': {e}")
                    continue
        
        # Escribir JSON
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Convertido: {archivo_txt} → {archivo_json}")
        print(f"   Muros: {len(data['muros'])}")
        print(f"   Llaves: {len(data['llaves'])}")
        print(f"   Spawns: {len(data['spawns'])}")
        print(f"   Salida: {'Sí' if data['salida'] else 'No'}")
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir: {e}")
        return False


def mostrar_ayuda():
    """Muestra información de uso"""
    print("=" * 60)
    print("CONVERSOR DE FORMATOS DE NIVELES")
    print("=" * 60)
    print("\nUso:")
    print("  python conversor_niveles.py json2txt <numero>")
    print("  python conversor_niveles.py txt2json <numero>")
    print("\nEjemplos:")
    print("  python conversor_niveles.py json2txt 1")
    print("  python conversor_niveles.py txt2json 2")
    print("\nFormatos:")
    print("  JSON → TXT: Convierte archivo JSON a formato texto plano")
    print("  TXT → JSON: Convierte archivo texto a formato JSON")
    print("\nArchivos:")
    print("  Input:  mapas_export_nivel_<numero>.{json|txt}")
    print("  Output: mapas_export_nivel_<numero>.{txt|json}")
    print("=" * 60)


def main():
    """Función principal"""
    if len(sys.argv) != 3:
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    numero = sys.argv[2]
    
    print("=" * 60)
    print("CONVERSOR DE FORMATOS DE NIVELES")
    print("=" * 60)
    
    if comando == 'json2txt':
        print(f"\n📄 Convirtiendo JSON → TXT (Nivel {numero})")
        json_a_txt(numero)
    
    elif comando == 'txt2json':
        print(f"\n📄 Convirtiendo TXT → JSON (Nivel {numero})")
        txt_a_json(numero)
    
    else:
        print(f"\n❌ Comando desconocido: {comando}")
        print("Comandos válidos: json2txt, txt2json")
        mostrar_ayuda()


if __name__ == '__main__':
    main()
