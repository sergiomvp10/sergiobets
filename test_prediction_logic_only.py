#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import (
    limpiar_cache_predicciones, 
    filtrar_apuestas_inteligentes,
    generar_semilla_partido,
    analizar_partido_completo
)

def test_seeding_deterministic():
    """Test that seeding produces consistent results"""
    print("=== TESTING DETERMINISTIC SEEDING ===")
    
    local = "Real Madrid"
    visitante = "Barcelona"
    fecha = "2025-08-03"
    cuotas = {"local": "1.65", "empate": "3.80", "visitante": "4.20"}
    
    seed1 = generar_semilla_partido(local, visitante, fecha, cuotas)
    seed2 = generar_semilla_partido(local, visitante, fecha, cuotas)
    seed3 = generar_semilla_partido(local, visitante, fecha, cuotas)
    
    print(f"Seed 1: {seed1}")
    print(f"Seed 2: {seed2}")
    print(f"Seed 3: {seed3}")
    
    if seed1 == seed2 == seed3:
        print("✅ Seeding is deterministic")
        return True
    else:
        print("❌ Seeding is not deterministic")
        return False

def test_partido_analysis_deterministic():
    """Test that match analysis produces consistent results"""
    print("\n=== TESTING DETERMINISTIC MATCH ANALYSIS ===")
    
    partido = {
        "local": "Manchester City",
        "visitante": "Arsenal", 
        "liga": "Premier League",
        "hora": "15:00",
        "fecha": "2025-08-03",
        "cuotas": {"local": "1.55", "empate": "4.00", "visitante": "5.50"}
    }
    
    analysis1 = analizar_partido_completo(partido)
    analysis2 = analizar_partido_completo(partido)
    analysis3 = analizar_partido_completo(partido)
    
    consistent = True
    
    btts1 = analysis1["probabilidades_btts"]["btts_si"]
    btts2 = analysis2["probabilidades_btts"]["btts_si"]
    btts3 = analysis3["probabilidades_btts"]["btts_si"]
    
    print(f"BTTS probabilities: {btts1:.4f}, {btts2:.4f}, {btts3:.4f}")
    
    if abs(btts1 - btts2) < 0.0001 and abs(btts2 - btts3) < 0.0001:
        print("✅ BTTS analysis is deterministic")
    else:
        print("❌ BTTS analysis is not deterministic")
        consistent = False
    
    over1 = analysis1["probabilidades_over_under"]["over_25"]
    over2 = analysis2["probabilidades_over_under"]["over_25"]
    over3 = analysis3["probabilidades_over_under"]["over_25"]
    
    print(f"Over 2.5 probabilities: {over1:.4f}, {over2:.4f}, {over3:.4f}")
    
    if abs(over1 - over2) < 0.0001 and abs(over2 - over3) < 0.0001:
        print("✅ Over/Under analysis is deterministic")
    else:
        print("❌ Over/Under analysis is not deterministic")
        consistent = False
    
    return consistent

def test_cache_functionality():
    """Test that caching works correctly"""
    print("\n=== TESTING CACHE FUNCTIONALITY ===")
    
    partidos = [
        {
            "local": "Liverpool",
            "visitante": "Chelsea",
            "liga": "Premier League", 
            "hora": "17:30",
            "cuotas": {"local": "1.60", "empate": "3.60", "visitante": "4.80"}
        },
        {
            "local": "Juventus",
            "visitante": "Inter Milan",
            "liga": "Serie A",
            "hora": "20:00", 
            "cuotas": {"local": "1.45", "empate": "4.20", "visitante": "6.00"}
        }
    ]
    
    limpiar_cache_predicciones()
    pred1 = filtrar_apuestas_inteligentes(partidos)
    
    pred2 = filtrar_apuestas_inteligentes(partidos)
    
    limpiar_cache_predicciones()
    pred3 = filtrar_apuestas_inteligentes(partidos)
    
    print(f"Run 1: {len(pred1)} predictions")
    print(f"Run 2: {len(pred2)} predictions") 
    print(f"Run 3: {len(pred3)} predictions")
    
    if len(pred1) > 0 and len(pred2) > 0 and len(pred3) > 0:
        consistent = True
        
        p1, p2, p3 = pred1[0], pred2[0], pred3[0]
        
        if (p1['partido'] == p2['partido'] == p3['partido'] and
            p1['prediccion'] == p2['prediccion'] == p3['prediccion'] and
            abs(p1['valor_esperado'] - p2['valor_esperado']) < 0.001 and
            abs(p2['valor_esperado'] - p3['valor_esperado']) < 0.001):
            print("✅ Cache functionality works correctly")
            print(f"   Consistent prediction: {p1['partido']} - {p1['prediccion']}")
            return True
        else:
            print("❌ Cache functionality failed")
            print(f"   P1: {p1['partido']} - {p1['prediccion']} (VE: {p1['valor_esperado']:.3f})")
            print(f"   P2: {p2['partido']} - {p2['prediccion']} (VE: {p2['valor_esperado']:.3f})")
            print(f"   P3: {p3['partido']} - {p3['prediccion']} (VE: {p3['valor_esperado']:.3f})")
            return False
    else:
        print("❌ No predictions generated for cache testing")
        return False

if __name__ == "__main__":
    print("🧪 TESTING DETERMINISTIC PREDICTION SYSTEM")
    print("=" * 50)
    
    success1 = test_seeding_deterministic()
    success2 = test_partido_analysis_deterministic()
    success3 = test_cache_functionality()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("✅ ALL TESTS PASSED - PREDICTION SYSTEM IS DETERMINISTIC")
    else:
        print("❌ SOME TESTS FAILED - PREDICTION SYSTEM NEEDS FIXES")
        
    print("🎯 Ready for integration with main application")
