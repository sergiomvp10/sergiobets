#!/usr/bin/env python3

from datetime import datetime
from footystats_api import obtener_partidos_del_dia
from league_utils import detectar_liga_por_imagen

def test_field_mappings():
    print("=== TESTING CORRECTED FIELD MAPPINGS ===")
    
    fecha = datetime.now().strftime("%Y-%m-%d")
    partidos_api = obtener_partidos_del_dia(fecha)
    
    if partidos_api:
        print(f"API returned {len(partidos_api)} matches for {fecha}")
        print()
        
        for i, partido in enumerate(partidos_api[:3], 1):
            liga = detectar_liga_por_imagen(
                partido.get("home_image", ""), 
                partido.get("away_image", "")
            )
            print(f"Match {i}:")
            print(f"  Teams: {partido.get('home_name')} vs {partido.get('away_name')}")
            print(f"  Detected League: {liga}")
            print(f"  Time: Por confirmar")
            print(f"  Odds: {partido.get('odds_ft_1')} / {partido.get('odds_ft_x')} / {partido.get('odds_ft_2')}")
            print(f"  Home Image: {partido.get('home_image', 'N/A')}")
            print()
        
        print("=== TESTING LEAGUE DIVERSITY ===")
        ligas_encontradas = set()
        for partido in partidos_api:
            liga = detectar_liga_por_imagen(
                partido.get("home_image", ""), 
                partido.get("away_image", "")
            )
            ligas_encontradas.add(liga)
        
        print(f"Unique leagues found: {sorted(ligas_encontradas)}")
        print("✅ League dropdown should now populate with these leagues")
        
    else:
        print("No API data available for testing")

if __name__ == "__main__":
    test_field_mappings()
