# footystats_api.py

import requests
from datetime import datetime
from api_cache import APICache
from error_handler import safe_api_call

API_KEY = "1d19b51cc6be6520d3b96a60c3d0fb862b120d9826886671c28dd796989048ee"
BASE_URL = "https://api.football-data-api.com"

api_cache = APICache(cache_duration_minutes=30)

@safe_api_call
def obtener_partidos_del_dia(fecha=None, use_cache=True):
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")
    
    cache_key = f"partidos_{fecha}"
    
    if use_cache:
        cached_data = api_cache.get(cache_key)
        if cached_data is not None:
            print(f"📦 Using cached data for {fecha}")
            return cached_data
    
    endpoint = f"{BASE_URL}/todays-matches"
    params = {
        "key": API_KEY,
        "date": fecha,
        "timezone": "America/Bogota"
    }

    try:
        print(f"🌐 Making API call for {fecha}")
        response = requests.get(endpoint, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            partidos = data.get("data", [])
            
            if use_cache:
                api_cache.set(cache_key, partidos)
            
            return partidos
        else:
            print("Error al obtener partidos:", response.status_code, response.text)
            return []
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout getting matches for {fecha}")
        return []
    except Exception as e:
        print("Excepción:", e)
        return []

def clear_api_cache():
    """Clear expired API cache entries"""
    cleared = api_cache.clear_expired()
    print(f"🧹 Cleared {cleared} expired cache entries")
    return cleared
