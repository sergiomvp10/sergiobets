#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import (
    limpiar_cache_predicciones, 
    filtrar_apuestas_inteligentes,
    encontrar_mejores_apuestas,
    analizar_partido_completo
)

def test_multiple_prediction_options():
    """Test that we can generate multiple ranked prediction options"""
    print("=== TESTING MULTIPLE PREDICTION OPTIONS ===")
    
    partido = {
        "local": "Manchester City",
        "visitante": "Arsenal", 
        "liga": "Premier League",
        "hora": "15:00",
        "fecha": "2025-08-03",
        "cuotas": {"local": "1.55", "empate": "4.00", "visitante": "5.50"}
    }
    
    analisis = analizar_partido_completo(partido)
    opciones_2 = encontrar_mejores_apuestas(analisis, num_opciones=2)
    
    if len(opciones_2) >= 2:
        print("✅ Primera opción:")
        print(f"   {opciones_2[0]['descripcion']} - Cuota: {opciones_2[0]['cuota']} - VE: {opciones_2[0]['valor_esperado']:.3f}")
        
        print("✅ Segunda opción:")
        print(f"   {opciones_2[1]['descripcion']} - Cuota: {opciones_2[1]['cuota']} - VE: {opciones_2[1]['valor_esperado']:.3f}")
        
        return opciones_2[0]['descripcion'] != opciones_2[1]['descripcion']
    return False

def test_filtrar_with_options():
    """Test filtrar_apuestas_inteligentes with different option numbers"""
    print("\n=== TESTING FILTRAR WITH OPTION NUMBERS ===")
    
    partidos = [
        {
            "local": "Liverpool",
            "visitante": "Chelsea",
            "liga": "Premier League", 
            "hora": "17:30",
            "cuotas": {"local": "1.60", "empate": "3.60", "visitante": "4.80"}
        }
    ]
    
    limpiar_cache_predicciones()
    pred1 = filtrar_apuestas_inteligentes(partidos, opcion_numero=1)
    pred2 = filtrar_apuestas_inteligentes(partidos, opcion_numero=2)
    
    if len(pred1) > 0 and len(pred2) > 0:
        print(f"Opción 1: {pred1[0]['prediccion']}")
        print(f"Opción 2: {pred2[0]['prediccion']}")
        return pred1[0]['prediccion'] != pred2[0]['prediccion']
    return False

def test_deterministic_regeneration():
    """Test that regenerated predictions are deterministic"""
    print("\n=== TESTING DETERMINISTIC REGENERATION ===")
    
    partidos = [
        {
            "local": "Real Madrid",
            "visitante": "Barcelona",
            "liga": "La Liga", 
            "hora": "20:00",
            "cuotas": {"local": "2.10", "empate": "3.40", "visitante": "3.20"}
        }
    ]
    
    limpiar_cache_predicciones()
    
    pred2_run1 = filtrar_apuestas_inteligentes(partidos, opcion_numero=2)
    pred2_run2 = filtrar_apuestas_inteligentes(partidos, opcion_numero=2)
    pred2_run3 = filtrar_apuestas_inteligentes(partidos, opcion_numero=2)
    
    if len(pred2_run1) > 0 and len(pred2_run2) > 0 and len(pred2_run3) > 0:
        consistent = (
            pred2_run1[0]['prediccion'] == pred2_run2[0]['prediccion'] == pred2_run3[0]['prediccion'] and
            abs(pred2_run1[0]['valor_esperado'] - pred2_run2[0]['valor_esperado']) < 0.001 and
            abs(pred2_run2[0]['valor_esperado'] - pred2_run3[0]['valor_esperado']) < 0.001
        )
        
        if consistent:
            print(f"✅ Regenerated predictions are deterministic: {pred2_run1[0]['prediccion']}")
            return True
        else:
            print("❌ Regenerated predictions are not deterministic")
            print(f"   Run 1: {pred2_run1[0]['prediccion']} (VE: {pred2_run1[0]['valor_esperado']:.3f})")
            print(f"   Run 2: {pred2_run2[0]['prediccion']} (VE: {pred2_run2[0]['valor_esperado']:.3f})")
            print(f"   Run 3: {pred2_run3[0]['prediccion']} (VE: {pred2_run3[0]['valor_esperado']:.3f})")
            return False
    return False

if __name__ == "__main__":
    print("🧪 TESTING REGENERAR FUNCTIONALITY")
    print("=" * 50)
    
    success1 = test_multiple_prediction_options()
    success2 = test_filtrar_with_options()
    success3 = test_deterministic_regeneration()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("✅ ALL REGENERAR TESTS PASSED")
        print("🎯 Ready for UI integration")
    else:
        print("❌ SOME REGENERAR TESTS FAILED")
        if not success1:
            print("   - Multiple prediction options test failed")
        if not success2:
            print("   - Filtrar with options test failed")
        if not success3:
            print("   - Deterministic regeneration test failed")
