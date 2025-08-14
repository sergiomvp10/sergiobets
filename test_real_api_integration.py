#!/usr/bin/env python3
"""Test script to verify real API integration with diverse bet selection"""

import sys
sys.path.append('/home/ubuntu/repos/sergiobets')

from footystats_api import obtener_partidos_del_dia
from ia_bets import filtrar_apuestas_inteligentes
from datetime import datetime
import json

def test_real_api_integration():
    print("🔍 Testing real API integration with diverse bet selection...")
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    print(f"Testing with real API data for {fecha}")
    
    datos_api = obtener_partidos_del_dia(fecha)
    if not datos_api or len(datos_api) == 0:
        print("❌ No API data available for testing")
        return
    
    print(f"✅ API returned {len(datos_api)} matches")
    
    print("\n📊 Sample API data structure:")
    sample_match = datos_api[0]
    relevant_odds = {
        "odds_ft_1": sample_match.get("odds_ft_1"),
        "odds_ft_x": sample_match.get("odds_ft_x"), 
        "odds_ft_2": sample_match.get("odds_ft_2"),
        "odds_btts_yes": sample_match.get("odds_btts_yes"),
        "odds_btts_no": sample_match.get("odds_btts_no"),
        "odds_ft_over25": sample_match.get("odds_ft_over25"),
        "odds_ft_under25": sample_match.get("odds_ft_under25"),
        "odds_corners_over_85": sample_match.get("odds_corners_over_85"),
        "odds_corners_over_95": sample_match.get("odds_corners_over_95"),
        "odds_1st_half_over05": sample_match.get("odds_1st_half_over05")
    }
    print(json.dumps(relevant_odds, indent=2))
    
    from league_utils import detectar_liga_por_imagen, convertir_timestamp_unix
    
    partidos_procesados = []
    for partido in datos_api[:3]:
        try:
            liga_detectada = detectar_liga_por_imagen(
                partido.get("home_image", ""), 
                partido.get("away_image", "")
            )
            hora_partido = convertir_timestamp_unix(partido.get("date_unix"))
            
            partido_procesado = {
                "hora": hora_partido,
                "liga": liga_detectada,
                "local": partido.get("home_name", f"Team {partido.get('homeID', 'Home')}"),
                "visitante": partido.get("away_name", f"Team {partido.get('awayID', 'Away')}"),
                "cuotas": {
                    "casa": "FootyStats",
                    "local": str(partido.get("odds_ft_1", "2.00")),
                    "empate": str(partido.get("odds_ft_x", "3.00")),
                    "visitante": str(partido.get("odds_ft_2", "4.00")),
                    "btts_si": str(partido.get("odds_btts_yes", "1.80")),
                    "btts_no": str(partido.get("odds_btts_no", "2.00")),
                    "over_15": str(partido.get("odds_ft_over15", "1.30")),
                    "under_15": str(partido.get("odds_ft_under15", "3.50")),
                    "over_25": str(partido.get("odds_ft_over25", "1.70")),
                    "under_25": str(partido.get("odds_ft_under25", "2.10")),
                    "corners_over_85": str(partido.get("odds_corners_over_85", "1.80")),
                    "corners_over_95": str(partido.get("odds_corners_over_95", "2.20")),
                    "corners_over_105": str(partido.get("odds_corners_over_105", "2.80")),
                    "1h_over_05": str(partido.get("odds_1st_half_over05", "1.40")),
                    "1h_over_15": str(partido.get("odds_1st_half_over15", "2.60"))
                }
            }
            partidos_procesados.append(partido_procesado)
            
        except Exception as e:
            print(f"⚠️ Error processing match: {e}")
            continue
    
    print(f"\n🎯 Processed {len(partidos_procesados)} matches for prediction analysis")
    
    predicciones = filtrar_apuestas_inteligentes(partidos_procesados, opcion_numero=1)
    
    print(f"\n🎯 Generated {len(predicciones)} predictions:")
    
    bet_types = set()
    for i, pred in enumerate(predicciones, 1):
        print(f"\n{i}. {pred['partido']}")
        print(f"   Liga: {pred['liga']}")
        print(f"   🎯 SELECTED BET: {pred['prediccion']}")
        print(f"   💰 Cuota: {pred['cuota']}")
        print(f"   📊 Expected Value: {pred['valor_esperado']:.3f}")
        print(f"   🔥 Confidence: {pred['confianza']}%")
        
        if "goles" in pred['prediccion'].lower():
            bet_types.add("Over/Under")
        elif "corners" in pred['prediccion'].lower():
            bet_types.add("Corners")
        elif "marcan" in pred['prediccion'].lower():
            bet_types.add("BTTS")
        elif "victoria" in pred['prediccion'].lower():
            bet_types.add("1X2")
        else:
            bet_types.add("Other")
    
    print(f"\n📈 MARKET DIVERSITY ANALYSIS:")
    print(f"   Market types selected: {bet_types}")
    print(f"   Total unique markets: {len(bet_types)}")
    
    if len(bet_types) > 1:
        print("✅ SUCCESS: Real API integration generates DIVERSE bet types!")
    elif "1X2" not in bet_types:
        print("✅ GOOD: No 'Victoria' predictions - system analyzing all markets!")
    else:
        print("❌ ISSUE: Still limited to basic market types")

if __name__ == "__main__":
    test_real_api_integration()
