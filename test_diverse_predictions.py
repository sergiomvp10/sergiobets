#!/usr/bin/env python3
"""Test script to verify diverse bet type selection"""

import sys
sys.path.append('/home/ubuntu/repos/sergiobets')

from ia_bets import filtrar_apuestas_inteligentes, simular_datos_prueba, analizar_partido_completo, encontrar_mejores_apuestas

def test_diverse_bet_selection():
    print("🔍 Testing diverse bet type selection...")
    
    partidos = simular_datos_prueba()
    print(f"Testing with {len(partidos)} matches")
    
    predicciones = filtrar_apuestas_inteligentes(partidos, opcion_numero=1)
    
    print(f"\n🎯 Generated {len(predicciones)} predictions:")
    
    bet_types = set()
    for i, pred in enumerate(predicciones, 1):
        print(f"\n{i}. {pred['partido']}")
        print(f"   Liga: {pred['liga']}")
        print(f"   Predicción: {pred['prediccion']}")
        print(f"   Cuota: {pred['cuota']}")
        print(f"   VE: {pred['valor_esperado']:.3f}")
        print(f"   Confianza: {pred['confianza']}%")
        
        bet_type = pred['prediccion'].split(' ')[0]
        bet_types.add(bet_type)
    
    print(f"\n📊 Bet types found: {list(bet_types)}")
    
    if len(bet_types) > 1:
        print("✅ SUCCESS: System is selecting diverse bet types!")
    else:
        print("❌ ISSUE: System still defaulting to single bet type")
    
    print("\n🔍 Testing individual match analysis...")
    for i, partido in enumerate(partidos, 1):
        print(f"\nMatch {i}: {partido['local']} vs {partido['visitante']}")
        analisis = analizar_partido_completo(partido)
        mejores = encontrar_mejores_apuestas(analisis, num_opciones=5)
        
        print(f"Available markets analyzed: {len(mejores)}")
        for j, apuesta in enumerate(mejores[:3], 1):
            print(f"  {j}. {apuesta['tipo']} - {apuesta['descripcion']} (VE: {apuesta['valor_esperado']:.3f})")

if __name__ == "__main__":
    test_diverse_bet_selection()
