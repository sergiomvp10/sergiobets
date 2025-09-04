#!/usr/bin/env python3
"""Test script to verify prediction system fixes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from footystats_api import obtener_partidos_del_dia
from ia_bets import filtrar_apuestas_inteligentes, analizar_partido_individual, es_liga_conocida, ODDS_RANGE_ANALYZE, ODDS_RANGE_PUBLISH
from league_utils import detectar_liga_por_imagen

def test_prediction_fixes():
    print("🧪 TESTING PREDICTION SYSTEM FIXES")
    print("=" * 50)
    
    print(f"📊 Odds ranges configured:")
    print(f"   ANALYZE: {ODDS_RANGE_ANALYZE}")
    print(f"   PUBLISH: {ODDS_RANGE_PUBLISH}")
    
    partidos = obtener_partidos_del_dia('2025-09-04')
    print(f"\n🔍 Found {len(partidos)} matches")
    
    if partidos:
        print("\n🏆 Testing league detection:")
        for i, partido in enumerate(partidos[:3]):
            liga = detectar_liga_por_imagen(partido.get('home_image', ''), partido.get('away_image', ''))
            conocida = es_liga_conocida(liga)
            print(f"  Match {i+1}: {partido.get('home_name')} vs {partido.get('away_name')}")
            print(f"    League: {liga} (Known: {conocida})")
        
        print("\n🎯 Testing general prediction system:")
        predicciones = filtrar_apuestas_inteligentes(partidos, 1)
        print(f"Generated {len(predicciones)} predictions")
        
        if predicciones:
            for pred in predicciones:
                print(f"  ✅ {pred['partido']}: {pred['prediccion']} @ {pred['cuota']}")
        else:
            print("  ⚠️ No predictions generated - checking first match individually...")
            
        print("\n🔍 Testing individual analysis:")
        if partidos:
            resultado = analizar_partido_individual(partidos[0], bypass_filters=True)
            if resultado["success"]:
                mejor = resultado['mejor_pick']
                print(f"✅ Individual analysis successful:")
                print(f"   Match: {resultado['partido']}")
                print(f"   Best pick: {mejor['prediccion']} @ {mejor['cuota']}")
                print(f"   Meets publication criteria: {'Yes' if mejor.get('cumple_publicacion', False) else 'No'}")
                print(f"   Markets analyzed: {len(resultado['todos_mercados'])}")
                
                print(f"\n📋 All markets found:")
                for i, mercado in enumerate(resultado['todos_mercados'][:3]):
                    print(f"   {i+1}. {mercado['descripcion']} @ {mercado['cuota']:.2f} (VE: +{mercado['valor_esperado']:.3f})")
                if len(resultado['todos_mercados']) > 3:
                    print(f"   ... and {len(resultado['todos_mercados']) - 3} more markets")
            else:
                print(f"❌ Individual analysis failed: {resultado['error']}")
    else:
        print("❌ No matches found for testing")

if __name__ == "__main__":
    test_prediction_fixes()
