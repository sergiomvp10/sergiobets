#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import (
    analizar_partido_completo, 
    encontrar_mejor_apuesta,
    calcular_value_bet,
    filtrar_apuestas_inteligentes,
    guardar_prediccion_historica,
    generar_reporte_rendimiento
)
from datetime import datetime

def test_enhanced_ia_complete():
    print("=== TESTING COMPLETE ENHANCED IA BETS MODULE ===")
    
    partidos_test = [
        {
            "hora": "12:00",
            "liga": "Liga Colombiana", 
            "local": "Deportivo Cali",
            "visitante": "Llaneros",
            "cuotas": {"casa": "FootyStats", "local": "1.68", "empate": "3.1", "visitante": "5.0"}
        },
        {
            "hora": "12:15",
            "liga": "Liga Argentina",
            "local": "San Lorenzo", 
            "visitante": "Tigre",
            "cuotas": {"casa": "FootyStats", "local": "2.41", "empate": "2.9", "visitante": "2.85"}
        }
    ]
    
    print("1. Testing enhanced predictions...")
    predicciones = filtrar_apuestas_inteligentes(partidos_test)
    
    for i, pred in enumerate(predicciones, 1):
        print(f"   Pick {i}: {pred['prediccion']}")
        print(f"   Partido: {pred['partido']}")
        print(f"   Cuota: {pred['cuota']} | VE: {pred['valor_esperado']:.3f}")
        print(f"   Justificación: {pred['razon']}")
        print()
    
    print("2. Testing historical tracking...")
    reporte = generar_reporte_rendimiento()
    print(f"   Total predicciones históricas: {reporte.get('total_predicciones', 0)}")
    
    print("3. Testing individual analysis...")
    if partidos_test:
        analisis = analizar_partido_completo(partidos_test[0])
        print(f"   Análisis completo: {analisis['partido']}")
        print(f"   Probabilidades 1X2: {analisis['probabilidades_1x2']}")
        
        mejor_apuesta = encontrar_mejor_apuesta(analisis)
        if mejor_apuesta:
            print(f"   Mejor apuesta: {mejor_apuesta['descripcion']}")
            print(f"   Valor esperado: {mejor_apuesta['valor_esperado']:.3f}")
    
    print("4. Testing value bet calculation...")
    ve, is_value = calcular_value_bet(0.6, 1.68)
    print(f"   Value bet test (60% prob, 1.68 odds): VE={ve:.3f}, Is Value={is_value}")
    
    print("✅ Enhanced IA module testing completed")

if __name__ == "__main__":
    test_enhanced_ia_complete()
