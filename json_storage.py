import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

_file_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, datetime] = {}
CACHE_DURATION = timedelta(minutes=5)

def _is_cache_valid(filename: str) -> bool:
    """Check if cached data is still valid"""
    if filename not in _cache_timestamps:
        return False
    return datetime.now() - _cache_timestamps[filename] < CACHE_DURATION

def _update_cache(filename: str, data: Any) -> None:
    """Update cache with new data"""
    _file_cache[filename] = data
    _cache_timestamps[filename] = datetime.now()

def _clear_cache(filename: str) -> None:
    """Clear cache for a specific file"""
    _file_cache.pop(filename, None)
    _cache_timestamps.pop(filename, None)

def guardar_json(nombre_archivo, data):
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Guardado: {nombre_archivo}")
        _update_cache(nombre_archivo, data)
    except Exception as e:
        print(f"❌ Error al guardar {nombre_archivo}: {e}")

def cargar_json(nombre_archivo):
    try:
        if _is_cache_valid(nombre_archivo) and nombre_archivo in _file_cache:
            print(f"📋 Cache hit: {nombre_archivo}")
            return _file_cache[nombre_archivo]
        
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        _update_cache(nombre_archivo, data)
        print(f"📁 Loaded from file: {nombre_archivo}")
        return data
        
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {nombre_archivo}. Se devolverá None.")
        return None
    except Exception as e:
        print(f"❌ Error al cargar {nombre_archivo}: {e}")
        return None

def clear_json_cache(nombre_archivo: Optional[str] = None):
    """Clear cache for specific file or all files"""
    if nombre_archivo:
        _clear_cache(nombre_archivo)
        print(f"🗑️ Cache cleared for: {nombre_archivo}")
    else:
        _file_cache.clear()
        _cache_timestamps.clear()
        print("🗑️ All cache cleared")
