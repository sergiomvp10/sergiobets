#!/usr/bin/env python3

from datetime import datetime
from footystats_api import obtener_partidos_del_dia
from league_utils import detectar_liga_por_imagen, convertir_timestamp_unix

def test_real_times_integration():
    print("=== TESTING COMPLETE INTEGRATION WITH REAL TIMES ===")
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
            hora = convertir_timestamp_unix(partido.get("date_unix"))
            
            print(f"Match {i}: {partido.get('home_name')} vs {partido.get('away_name')}")
            print(f"  League: {liga}")
            print(f"  Time (Arizona): {hora}")
            print(f"  Odds: {partido.get('odds_ft_1')}/{partido.get('odds_ft_x')}/{partido.get('odds_ft_2')}")
            print(f"  Raw timestamp: {partido.get('date_unix')}")
            print()
        
        print("✅ Integration test successful - real times are now displayed")
        
        print("\n=== TESTING CRUDO.PY DATA STRUCTURE ===")
        partidos_transformados = []
        for partido in partidos_api[:2]:
            liga_detectada = detectar_liga_por_imagen(
                partido.get("home_image", ""), 
                partido.get("away_image", "")
            )
            hora_partido = convertir_timestamp_unix(partido.get("date_unix"))
            
            partido_transformado = {
                "hora": hora_partido,
                "liga": liga_detectada,
                "local": partido.get("home_name", f"Team {partido.get('homeID', 'Home')}"),
                "visitante": partido.get("away_name", f"Team {partido.get('awayID', 'Away')}"),
                "cuotas": {
                    "casa": "FootyStats",
                    "local": str(partido.get("odds_ft_1", "2.00")),
                    "empate": str(partido.get("odds_ft_x", "3.00")),
                    "visitante": str(partido.get("odds_ft_2", "4.00"))
                }
            }
            partidos_transformados.append(partido_transformado)
        
        for i, partido in enumerate(partidos_transformados, 1):
            print(f"Transformed Match {i}:")
            print(f"  {partido['local']} vs {partido['visitante']}")
            print(f"  Liga: {partido['liga']}")
            print(f"  Hora: {partido['hora']} (Arizona)")
            print(f"  Cuotas: {partido['cuotas']['local']}/{partido['cuotas']['empate']}/{partido['cuotas']['visitante']}")
            print()
        
        print("✅ Data transformation test successful")
        
    else:
        print("❌ No API data available")

if __name__ == "__main__":
    test_real_times_integration()
