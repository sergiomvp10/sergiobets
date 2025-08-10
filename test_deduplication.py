#!/usr/bin/env python3

from footystats_api import obtener_partidos_del_dia
from datetime import datetime

def test_deduplication():
    """Test deduplication with current API data"""
    fecha = datetime.now().strftime('%Y-%m-%d')
    partidos = obtener_partidos_del_dia(fecha)
    
    print(f'Before deduplication: {len(partidos)} matches')
    
    partidos_unicos = {}
    for partido in partidos:
        home_name = partido.get("home_name", "")
        away_name = partido.get("away_name", "")
        date_unix = partido.get("date_unix", 0)
        match_key = f"{home_name}|{away_name}|{date_unix}"
        
        if match_key not in partidos_unicos:
            partidos_unicos[match_key] = partido
        else:
            print(f"DUPLICATE REMOVED: {home_name} vs {away_name}")
    
    print(f'After deduplication: {len(partidos_unicos)} unique matches')
    
    print("\nUnique matches:")
    for i, partido in enumerate(partidos_unicos.values(), 1):
        print(f"{i}. {partido.get('home_name', 'N/A')} vs {partido.get('away_name', 'N/A')}")

if __name__ == "__main__":
    test_deduplication()
