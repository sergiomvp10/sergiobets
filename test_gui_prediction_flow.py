#!/usr/bin/env python3
"""Test the actual GUI prediction flow with real API data"""

import sys
sys.path.append('/home/ubuntu/repos/sergiobets')

from datetime import datetime
from sergiobets_unified import SergioBetsUnified

def test_gui_prediction_flow():
    print("🔍 Testing actual GUI prediction flow...")
    
    app = SergioBetsUnified()
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    print(f"Testing cargar_partidos_reales() for {fecha}")
    
    partidos = app.cargar_partidos_reales(fecha)
    
    if not partidos or len(partidos) == 0:
        print("❌ No matches loaded from real API")
        return
    
    print(f"✅ Loaded {len(partidos)} matches from real API")
    
    print("\n📊 Sample processed match data:")
    sample_match = partidos[0]
    print(f"Match: {sample_match['local']} vs {sample_match['visitante']}")
    print(f"Liga: {sample_match['liga']}")
    print("Available odds:")
    for market, odds in sample_match['cuotas'].items():
        print(f"  {market}: {odds}")
    
    from ia_bets import filtrar_apuestas_inteligentes
    
    print(f"\n🎯 Testing prediction generation with {len(partidos)} real matches...")
    predicciones = filtrar_apuestas_inteligentes(partidos, opcion_numero=1)
    
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
    
    print(f"\n📈 FINAL RESULT - MARKET DIVERSITY:")
    print(f"   Market types selected: {bet_types}")
    print(f"   Total unique markets: {len(bet_types)}")
    
    if len(bet_types) > 1:
        print("✅ SUCCESS: GUI prediction flow generates DIVERSE bet types!")
        print("✅ FIXED: System no longer defaults to only 'Victoria' predictions")
    elif "1X2" not in bet_types:
        print("✅ EXCELLENT: Zero 'Victoria' predictions - analyzing all markets!")
    else:
        print("❌ ISSUE: Still generating only basic market types")
        print("❌ User's issue NOT resolved - system still defaulting to 'Victoria'")

if __name__ == "__main__":
    test_gui_prediction_flow()
