#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import filtrar_apuestas_inteligentes, limpiar_cache_predicciones
from crudo import cargar_partidos_reales
from datetime import datetime

def test_prediction_consistency():
    """Test if predictions are consistent across multiple runs"""
    print("=== TESTING PREDICTION CONSISTENCY ===")
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    partidos = cargar_partidos_reales(fecha)
    
    if not partidos:
        print("No matches found for testing")
        return
    
    print(f"Testing with {len(partidos)} matches for {fecha}")
    
    runs = []
    for i in range(3):
        print(f"\nRun {i+1}:")
        limpiar_cache_predicciones()
        predicciones = filtrar_apuestas_inteligentes(partidos)
        
        run_data = []
        for pred in predicciones:
            run_data.append({
                'partido': pred['partido'],
                'prediccion': pred['prediccion'],
                'cuota': pred['cuota'],
                'confianza': pred['confianza'],
                'valor_esperado': pred['valor_esperado']
            })
            print(f"  {pred['partido']}: {pred['prediccion']} (Cuota: {pred['cuota']}, VE: {pred['valor_esperado']:.3f})")
        
        runs.append(run_data)
    
    print("\n=== CONSISTENCY ANALYSIS ===")
    if len(runs) >= 2:
        consistent = True
        for i in range(len(runs[0])):
            if i < len(runs[1]):
                pred1 = runs[0][i]
                pred2 = runs[1][i]
                
                if (pred1['partido'] == pred2['partido'] and 
                    pred1['prediccion'] == pred2['prediccion'] and
                    abs(pred1['valor_esperado'] - pred2['valor_esperado']) < 0.001):
                    print(f"✅ {pred1['partido']}: CONSISTENT")
                else:
                    print(f"❌ {pred1['partido']}: INCONSISTENT")
                    print(f"   Run 1: {pred1['prediccion']} (VE: {pred1['valor_esperado']:.3f})")
                    print(f"   Run 2: {pred2['prediccion']} (VE: {pred2['valor_esperado']:.3f})")
                    consistent = False
        
        if consistent:
            print("\n✅ ALL PREDICTIONS ARE CONSISTENT")
        else:
            print("\n❌ PREDICTIONS ARE NOT CONSISTENT - RANDOMNESS DETECTED")
    
    return runs

if __name__ == "__main__":
    test_prediction_consistency()
