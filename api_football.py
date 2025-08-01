# api_football.py

import requests
from api_config import API_BASE_URL, HEADERS

# Obtener próximos partidos de un equipo específico
def get_next_games(team_id, season=2025, next_n=5):
    url = f"{API_BASE_URL}fixtures?team={team_id}&season={season}&next={next_n}"
    response = requests.get(url, headers=HEADERS).json()
    return response.get('response', [])

# Obtener estadísticas de un partido específico
def get_match_statistics(fixture_id):
    url = f"{API_BASE_URL}fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS).json()
    return response.get('response', [])

# Obtener cuotas de apuestas de un partido específico
def get_match_odds(fixture_id):
    url = f"{API_BASE_URL}odds?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS).json()
    return response.get('response', [])
