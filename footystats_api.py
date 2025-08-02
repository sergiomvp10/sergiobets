# footystats_api.py

import requests
from datetime import datetime

API_KEY = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
BASE_URL = "https://api.footystats.org"

def obtener_partidos_del_dia():
    hoy = datetime.now().strftime("%Y-%m-%d")
    endpoint = f"{BASE_URL}/league-matches"
    params = {
        "key": API_KEY,
        "date": hoy,
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