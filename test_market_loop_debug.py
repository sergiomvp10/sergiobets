#!/usr/bin/env python3
"""Debug the market evaluation loop specifically"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_market_loop():
    print("🧪 DEBUGGING MARKET EVALUATION LOOP")
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
    
    from ia_bets import analizar_partido_completo, ODDS_RANGE_ANALYZE
    
    print(f"🔍 Testing market loop for: {partido_test['local']} vs {partido_test['visitante']}")
    
    analisis = analizar_partido_completo(partido_test)
    cuotas_reales = analisis["cuotas_disponibles"]
    
    print(f"📊 Analysis complete, cuotas_reales: {len(cuotas_reales)} markets")
    
    cuota_min, cuota_max = ODDS_RANGE_ANALYZE
    valor_minimo = 0.0  # bypass mode
    
    print(f"📊 Odds range: {cuota_min} - {cuota_max}")
    print(f"📊 Minimum value: {valor_minimo}")
    
    mercados_disponibles = [
        ("1X2", "local", analisis["probabilidades_1x2"]["local"], cuotas_reales.get("local", "0"), f"Victoria {analisis['partido'].split(' vs ')[0]}"),
        ("1X2", "empate", analisis["probabilidades_1x2"]["empate"], cuotas_reales.get("empate", "0"), "Empate"),
        ("1X2", "visitante", analisis["probabilidades_1x2"]["visitante"], cuotas_reales.get("visitante", "0"), f"Victoria {analisis['partido'].split(' vs ')[1]}"),
        
        ("BTTS", "btts_si", analisis.get("probabilidades_btts", {}).get("btts_si", 0.5), cuotas_reales.get("btts_si", "0"), "Ambos equipos marcan - SÍ"),
        ("BTTS", "btts_no", analisis.get("probabilidades_btts", {}).get("btts_no", 0.5), cuotas_reales.get("btts_no", "0"), "Ambos equipos marcan - NO"),
        
        ("Over/Under", "over_15", analisis.get("probabilidades_over_under", {}).get("over_15", 0.8), cuotas_reales.get("over_15", "0"), "Más de 1.5 goles"),
        ("Over/Under", "under_15", analisis.get("probabilidades_over_under", {}).get("under_15", 0.2), cuotas_reales.get("under_15", "0"), "Menos de 1.5 goles"),
        ("Over/Under", "over_25", analisis.get("probabilidades_over_under", {}).get("over_25", 0.6), cuotas_reales.get("over_25", "0"), "Más de 2.5 goles"),
        ("Over/Under", "under_25", analisis.get("probabilidades_over_under", {}).get("under_25", 0.4), cuotas_reales.get("under_25", "0"), "Menos de 2.5 goles"),
        
        ("Corners", "over_85", analisis.get("probabilidades_corners", {}).get("over_85_corners", 0.6), cuotas_reales.get("corners_over_85", "0"), "Más de 8.5 corners"),
        ("Corners", "over_95", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.5), cuotas_reales.get("corners_over_95", "0"), "Más de 9.5 corners"),
        ("Corners", "over_105", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.4), cuotas_reales.get("corners_over_105", "0"), "Más de 10.5 corners"),
        
        ("1H", "over_05", analisis.get("probabilidades_primera_mitad", {}).get("over_05_1h", 0.6), cuotas_reales.get("1h_over_05", "0"), "Más de 0.5 goles 1H"),
        ("1H", "over_15", analisis.get("probabilidades_primera_mitad", {}).get("over_15_1h", 0.3), cuotas_reales.get("1h_over_15", "0"), "Más de 1.5 goles 1H"),
    ]
    
    print(f"\n📋 TESTING EACH MARKET:")
    processed_count = 0
    valid_count = 0
    
    from ia_bets import calcular_value_bet
    
    for i, (tipo_mercado, mercado, probabilidad, cuota_str, descripcion) in enumerate(mercados_disponibles):
        print(f"\n  Market {i+1}: {descripcion}")
        print(f"    Probability: {probabilidad}")
        print(f"    Odds string: '{cuota_str}' (type: {type(cuota_str)})")
        
        try:
            cuota_real = float(cuota_str)
            print(f"    Odds float: {cuota_real}")
            
            if cuota_real <= 1.0:
                print(f"    ❌ SKIPPED: Invalid odds <= 1.0")
                continue
                
            in_range = cuota_min <= cuota_real <= cuota_max
            print(f"    Odds in range {cuota_min}-{cuota_max}: {in_range}")
            
            ve, es_value = calcular_value_bet(probabilidad, cuota_real)
            edge_pct = ve * 100
            print(f"    Value expected: {ve:.4f} ({edge_pct:.1f}%)")
            print(f"    Is value bet: {es_value}")
            print(f"    Above minimum ({valor_minimo}): {ve >= valor_minimo}")
            
            bypass_condition = True  # bypass_filters = True
            normal_condition = es_value and ve >= valor_minimo
            
            print(f"    Bypass condition: {bypass_condition}")
            print(f"    Normal condition: {normal_condition}")
            
            if bypass_condition or normal_condition:
                print(f"    ✅ WOULD BE INCLUDED")
                valid_count += 1
            else:
                print(f"    ❌ WOULD BE EXCLUDED")
                
            processed_count += 1
            
        except (ValueError, TypeError) as e:
            print(f"    ❌ ERROR: {e}")
            continue
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total markets defined: {len(mercados_disponibles)}")
    print(f"   Successfully processed: {processed_count}")
    print(f"   Would be included: {valid_count}")

if __name__ == "__main__":
    test_market_loop()
