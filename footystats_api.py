# footystats_api.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from api_cache import APICache
from error_handler import safe_api_call

load_dotenv()

API_KEY = os.getenv("FOOTYSTATS_API_KEY", "")
BASE_URL = "https://api.football-data-api.com"

api_cache = APICache(cache_duration_minutes=30)

COMPETITION_ID_TO_NAME = {
    14968: "Bundesliga",
    14956: "La Liga",
    15746: "Primera División Argentina",
    14957: "Premier League",
    14958: "Serie A",
    14959: "Ligue 1",
    14960: "Eredivisie",
    14961: "Primeira Liga",
    14962: "Süper Lig",
    14963: "Russian Premier League",
    14964: "Belgian First Division A",
    14965: "Austrian Bundesliga",
    14966: "Swiss Super League",
    14967: "Scottish Premiership",
    14969: "2. Bundesliga",
    14970: "Championship",
    14971: "Serie B",
    14972: "La Liga 2",
    15747: "Primera B Nacional",
    15748: "Copa de la Liga Profesional",
}

def get_league_name(competition_id: int, fallback: str = "Liga desconocida") -> str:
    """Obtiene el nombre de la liga desde el competition_id"""
    return COMPETITION_ID_TO_NAME.get(competition_id, fallback)

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
            
            for partido in partidos:
                comp_id = partido.get('competition_id')
                if comp_id and 'competition_name' not in partido:
                    partido['competition_name'] = get_league_name(comp_id)
            
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
