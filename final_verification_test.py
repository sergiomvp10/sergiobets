#!/usr/bin/env python3
"""Final verification that diverse bet selection is working correctly"""

import sys
sys.path.append('/home/ubuntu/repos/sergiobets')

from ia_bets import filtrar_apuestas_inteligentes, simular_datos_prueba

def final_verification():
    print("🎯 FINAL VERIFICATION: Diverse Bet Type Selection")
    print("=" * 60)
    
    partidos = simular_datos_prueba()
    predicciones = filtrar_apuestas_inteligentes(partidos, opcion_numero=1)
    
    print(f"✅ Generated {len(predicciones)} predictions from {len(partidos)} matches")
    print()
    
    market_types = []
    for i, pred in enumerate(predicciones, 1):
        print(f"🏆 MATCH {i}: {pred['partido']}")
        print(f"   Liga: {pred['liga']}")
        print(f"   🎯 SELECTED BET: {pred['prediccion']}")
        print(f"   💰 Cuota: {pred['cuota']}")
        print(f"   📊 Expected Value: {pred['valor_esperado']:.3f}")
        print(f"   🔥 Confidence: {pred['confianza']}%")
        print(f"   📝 Reason: {pred['razon']}")
        print()
        
        if "goles" in pred['prediccion'].lower():
            market_types.append("Over/Under")
        elif "corners" in pred['prediccion'].lower():
            market_types.append("Corners")
        elif "marcan" in pred['prediccion'].lower():
            market_types.append("BTTS")
        elif "victoria" in pred['prediccion'].lower():
            market_types.append("1X2")
        else:
            market_types.append("Other")
    
    print("📈 MARKET DIVERSITY ANALYSIS:")
    print(f"   Market types selected: {set(market_types)}")
    print(f"   Total unique markets: {len(set(market_types))}")
    
    if len(set(market_types)) > 1:
        print("✅ SUCCESS: System is selecting DIVERSE bet types!")
        print("✅ FIXED: No longer defaulting to only 'Victoria' predictions")
    else:
        print("❌ ISSUE: Still limited market diversity")
    
    print()
    print("🔍 COMPARISON WITH USER'S ISSUE:")
    print("   Before: ALL predictions were 'Victoria' (home wins)")
    print(f"   After: {market_types}")
    print()
    
    if "1X2" not in market_types:
        print("✅ EXCELLENT: Zero 'Victoria' predictions - system analyzing all markets!")
    elif market_types.count("1X2") < len(market_types):
        print("✅ GOOD: Mixed market selection with some non-1X2 bets")
    else:
        print("❌ PROBLEM: Still defaulting to 1X2 markets")

if __name__ == "__main__":
    final_verification()
