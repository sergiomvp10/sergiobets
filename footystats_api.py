# footystats_api.py

import requests
from datetime import datetime

API_KEY = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
BASE_URL = "https://api.football-data-api.com"

def obtener_partidos_del_dia(fecha=None):
    if fecha is None:
        fecha = datetime.now().strftime("%Y-%m-%d")
    endpoint = f"{BASE_URL}/todays-matches"
    params = {
        "key": API_KEY,
        "date": fecha,
        "timezone": "America/Bogota"
    }

    try:
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            partidos = data.get("data", [])
            return partidos
        else:
            print("Error al obtener partidos:", response.status_code, response.text)
            return []
    except Exception as e:
        print("Excepción:", e)
        return []
