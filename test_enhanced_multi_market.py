#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import (
    analizar_partido_completo, 
    encontrar_mejor_apuesta,
    filtrar_apuestas_inteligentes,
    analizar_rendimiento_equipos,
    calcular_probabilidades_corners,
    calcular_probabilidades_handicap
)
from datetime import datetime

def test_enhanced_multi_market():
    print("=== TESTING ENHANCED MULTI-MARKET IA BETS MODULE ===")
    
    partidos_test = [
        {
            "hora": "15:30",
            "liga": "Liga Colombiana", 
            "local": "Deportivo Cali",
            "visitante": "Llaneros",
            "cuotas": {"casa": "FootyStats", "local": "1.45", "empate": "3.8", "visitante": "6.2"}
        },
        {
            "hora": "18:00",
            "liga": "Liga Argentina",
            "local": "San Lorenzo", 
            "visitante": "Tigre",
            "cuotas": {"casa": "FootyStats", "local": "1.55", "empate": "3.4", "visitante": "5.8"}
        },
        {
            "hora": "20:15",
            "liga": "Premier League",
            "local": "Manchester City", 
            "visitante": "Brighton",
            "cuotas": {"casa": "FootyStats", "local": "1.35", "empate": "4.5", "visitante": "8.0"}
        }
    ]
    
    print("1. Testing team performance analysis...")
    rendimiento = analizar_rendimiento_equipos("Deportivo Cali", "Llaneros")
    print(f"   Forma local: {rendimiento['forma_local']:.2f}")
    print(f"   Forma visitante: {rendimiento['forma_visitante']:.2f}")
    print(f"   Goles promedio: {rendimiento['goles_promedio_local']:.1f} vs {rendimiento['goles_promedio_visitante']:.1f}")
    print(f"   H2H goles total: {rendimiento['h2h_goles_total']:.1f}")
    print()
    
    print("2. Testing new bet types...")
    cuotas_test = {"local": "1.45", "empate": "3.8", "visitante": "6.2"}
    prob_corners = calcular_probabilidades_corners(rendimiento)
    prob_handicap = calcular_probabilidades_handicap(cuotas_test, rendimiento)
    
    print(f"   Corners Over 8.5: {prob_corners['over_85_corners']:.3f}")
    print(f"   Corners Over 10.5: {prob_corners['over_105_corners']:.3f}")
    print(f"   Hándicap Local -0.5: {prob_handicap['handicap_local_05']:.3f}")
    print(f"   Hándicap Visitante +0.5: {prob_handicap['handicap_visitante_05']:.3f}")
    print()
    
    print("3. Testing enhanced predictions with new odds filter (1.30-1.60)...")
    predicciones = filtrar_apuestas_inteligentes(partidos_test)
    
    if predicciones:
        for i, pred in enumerate(predicciones, 1):
            print(f"   🎯 PICK #{i}: {pred['prediccion']}")
            print(f"   📊 Tipo: {pred.get('tipo', 'N/A')} | Cuota: {pred['cuota']} (rango 1.30-1.60)")
            print(f"   💰 VE: {pred['valor_esperado']:.3f} | Confianza: {pred['confianza']:.1f}%")
            print(f"   📝 Justificación: {pred['razon']}")
            print()
    else:
        print("   ❌ No se encontraron value bets en el rango 1.30-1.60")
    
    print("4. Testing complete analysis for single match...")
    if partidos_test:
        analisis = analizar_partido_completo(partidos_test[0])
        print(f"   Partido: {analisis['partido']}")
        print(f"   Mercados analizados: {len([k for k in analisis.keys() if 'probabilidades' in k])}")
        print(f"   Rendimiento incluido: {'rendimiento_equipos' in analisis}")
        
        mejor_apuesta = encontrar_mejor_apuesta(analisis)
        if mejor_apuesta:
            print(f"   Mejor apuesta: {mejor_apuesta['descripcion']}")
            print(f"   Tipo: {mejor_apuesta['tipo']} | VE: {mejor_apuesta['valor_esperado']:.3f}")
            print(f"   Cuota en rango: {1.30 <= mejor_apuesta['cuota'] <= 1.60}")
        else:
            print("   No se encontró value bet en el rango especificado")
    
    print("\n5. Testing odds filter compliance...")
    total_predicciones = 0
    predicciones_en_rango = 0
    
    for partido in partidos_test:
        analisis = analizar_partido_completo(partido)
        mejor = encontrar_mejor_apuesta(analisis)
        if mejor:
            total_predicciones += 1
            if 1.30 <= mejor['cuota'] <= 1.60:
                predicciones_en_rango += 1
    
    print(f"   Total predicciones: {total_predicciones}")
    print(f"   En rango 1.30-1.60: {predicciones_en_rango}")
    print(f"   Cumplimiento filtro: {predicciones_en_rango/total_predicciones*100 if total_predicciones > 0 else 0:.1f}%")
    
    print("\n✅ Enhanced multi-market IA module testing completed")

if __name__ == "__main__":
    test_enhanced_multi_market()
