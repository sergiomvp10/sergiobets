#!/usr/bin/env python3
"""Debug test to check why only 1 market is being evaluated"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_market_evaluation():
    print("🧪 DEBUGGING MARKET EVALUATION")
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
    
    print(f"🔍 Testing market evaluation for: {partido_test['local']} vs {partido_test['visitante']}")
    print(f"   Available odds: {len(partido_test['cuotas_disponibles'])} markets")
    
    from ia_bets import analizar_partido_completo, encontrar_mejores_apuestas
    
    print(f"\n📊 Step 1: Complete match analysis")
    analisis = analizar_partido_completo(partido_test)
    print(f"   Analysis keys: {list(analisis.keys())}")
    print(f"   Cuotas disponibles: {len(analisis.get('cuotas_disponibles', {}))}")
    
    print(f"\n📊 Step 2: Finding best bets (bypass=True)")
    mejores_apuestas = encontrar_mejores_apuestas(analisis, num_opciones=20, bypass_filters=True)
    print(f"   Markets found: {len(mejores_apuestas)}")
    
    if mejores_apuestas:
        print(f"\n📋 ALL MARKETS EVALUATED:")
        for i, apuesta in enumerate(mejores_apuestas):
            edge_pct = apuesta.get('edge_percentage', apuesta['valor_esperado'] * 100)
            cumple = "✅" if apuesta.get('cumple_publicacion', False) else "⚠️"
            print(f"   {cumple} {i+1}. {apuesta['descripcion']} @ {apuesta['cuota']:.2f} (Edge: {edge_pct:.1f}%)")
    else:
        print(f"   ❌ No markets found - investigating...")
        
        print(f"\n🔍 Debugging market processing:")
        cuotas_reales = analisis["cuotas_disponibles"]
        print(f"   Cuotas reales keys: {list(cuotas_reales.keys())}")
        print(f"   Sample values: {dict(list(cuotas_reales.items())[:3])}")
        
        from ia_bets import ODDS_RANGE_ANALYZE
        cuota_min, cuota_max = ODDS_RANGE_ANALYZE
        print(f"   Odds range: {cuota_min} - {cuota_max}")
        
        valid_odds = {k: v for k, v in cuotas_reales.items() if isinstance(v, (int, float)) and cuota_min <= v <= cuota_max}
        print(f"   Valid odds in range: {len(valid_odds)}")
        print(f"   Valid odds: {valid_odds}")

if __name__ == "__main__":
    test_market_evaluation()
