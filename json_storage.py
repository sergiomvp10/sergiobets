import json
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import contextmanager

@contextmanager
def batch_json_operations():
    """Context manager for batching multiple JSON operations"""
    operations = []
    yield operations
    for operation in operations:
        operation()

def guardar_json(nombre_archivo, data):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Guardado: {nombre_archivo}")
    except Exception as e:
        print(f"❌ Error al guardar {nombre_archivo}: {e}")

def guardar_json_batch(operations: List[Tuple[str, Union[Dict[str, Any], List[Any]]]]):
    """Batch multiple JSON save operations for efficiency"""
    try:
        for nombre_archivo, data in operations:
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Guardado en lote: {len(operations)} archivos")
    except Exception as e:
        print(f"❌ Error en guardado en lote: {e}")

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

def cargar_json_cached(nombre_archivo, cache: Dict[str, Any] = {}):
    """Load JSON with simple caching to avoid repeated file reads"""
    if nombre_archivo in cache:
        return cache[nombre_archivo]
    
    data = cargar_json(nombre_archivo)
    if data is not None:
        cache[nombre_archivo] = data
    return data
