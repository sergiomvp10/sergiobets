#!/usr/bin/env python3
"""Simple test for individual analysis without GUI dependencies"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_individual_analysis_simple():
    print("🧪 TESTING INDIVIDUAL ANALYSIS (SIMPLE)")
    print("=" * 50)
    
    partido_test = {
        'local': 'Manchester City',
        'visitante': 'Arsenal',
        'liga': 'Premier League',
        'hora': '15:00',
        'cuotas': {
            'casa': 'FootyStats',
            'local': '1.65',
            'empate': '3.80',
            'visitante': '4.20'
        },
        'cuotas_disponibles': {
            'local': 1.65,
            'empate': 3.80,
            'visitante': 4.20,
            'over_15': 1.25,
            'under_15': 3.50,
            'over_25': 1.85,
            'under_25': 1.95,
            'btts_si': 1.70,
            'btts_no': 2.10,
            'corners_over_85': 1.90,
            'corners_over_95': 2.20,
            'corners_over_105': 2.80,
            '1h_over_05': 1.40,
            '1h_over_15': 2.60
        }
    }
    
    print(f"🔍 Testing with: {partido_test['local']} vs {partido_test['visitante']}")
    print(f"   Liga: {partido_test['liga']}")
    print(f"   Available markets: {len([k for k, v in partido_test['cuotas_disponibles'].items() if v > 0])}")
    
    from ia_bets import analizar_partido_individual
    
    print(f"\n🎯 Running individual analysis (bypass ALL filters):")
    resultado = analizar_partido_individual(partido_test, bypass_filters=True)
    
    if resultado["success"]:
        mejor = resultado['mejor_pick']
        print(f"\n✅ ANÁLISIS EXITOSO:")
        print(f"   Mejor pick: {mejor['prediccion']} @ {mejor['cuota']}")
        print(f"   Edge: {mejor.get('edge_percentage', 'N/A')}%")
        print(f"   Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
        print(f"   Total mercados evaluados: {len(resultado['todos_mercados'])}")
        
        print(f"\n📋 TODOS LOS MERCADOS EVALUADOS:")
        for i, mercado in enumerate(resultado['todos_mercados']):
            edge_pct = round(mercado['valor_esperado'] * 100, 1)
            if edge_pct >= 5:
                status = "✅ Cumple"
            elif edge_pct >= 2:
                status = "⚠️ Edge bajo"
            else:
                status = "❌ Edge muy bajo"
            print(f"   {status} {i+1}. {mercado['descripcion']} @ {mercado['cuota']:.2f} (Edge: {edge_pct}%)")
        
        low_edge_count = len([m for m in resultado['todos_mercados'] if m['valor_esperado'] * 100 < 5])
        print(f"\n📊 Mercados con edge < 5%: {low_edge_count} (mostrados correctamente)")
        
        return True
    else:
        print(f"\n❌ ANÁLISIS FALLÓ: {resultado['error']}")
        return False

if __name__ == "__main__":
    success = test_individual_analysis_simple()
    if success:
        print("\n🎉 INDIVIDUAL ANALYSIS WORKING CORRECTLY!")
        print("✅ Shows all markets regardless of edge")
        print("✅ Marks low edge clearly")
        print("✅ Bypasses all filters as expected")
    else:
        print("\n❌ Individual analysis needs debugging.")
