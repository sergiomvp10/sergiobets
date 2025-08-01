import json

def guardar_json(nombre_archivo, data):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Guardado: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar {nombre_archivo}: {e}")

def cargar_json(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {nombre_archivo}. Se devolverá None.")
        return None
    except Exception as e:
        print(f"❌ Error al cargar {nombre_archivo}: {e}")
        return None