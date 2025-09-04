#!/usr/bin/env python3
"""Debug why only 10 markets are being evaluated instead of 50+"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_market_evaluation():
    print("🔍 DEBUGGING MARKET EVALUATION LOGIC")
    print("=" * 60)
    
    from footystats_api import obtener_partidos_del_dia
    from ia_bets import analizar_partido_completo, encontrar_mejores_apuestas
    from league_utils import detectar_liga_por_imagen
    
    partidos_api = obtener_partidos_del_dia('2025-09-04')
    if not partidos_api:
        print("❌ No API data available")
        return
    
    primer_partido = partidos_api[0]
    partido_procesado = {
        "hora": "15:00",
        "liga": detectar_liga_por_imagen(primer_partido.get("home_image", ""), primer_partido.get("away_image", "")),
        "local": primer_partido.get("home_name", "Local"),
        "visitante": primer_partido.get("away_name", "Visitante"),
        "cuotas": {"casa": "FootyStats", "local": str(primer_partido.get("odds_ft_1", "2.00")), "empate": str(primer_partido.get("odds_ft_x", "3.00")), "visitante": str(primer_partido.get("odds_ft_2", "4.00"))},
        "cuotas_disponibles": {
            "local": primer_partido.get("odds_ft_1", 0),
            "empate": primer_partido.get("odds_ft_x", 0),
            "visitante": primer_partido.get("odds_ft_2", 0),
            "over_05": primer_partido.get("odds_ft_over05", 0),
            "under_05": primer_partido.get("odds_ft_under05", 0),
            "over_15": primer_partido.get("odds_ft_over15", 0),
            "under_15": primer_partido.get("odds_ft_under15", 0),
            "over_25": primer_partido.get("odds_ft_over25", 0),
            "under_25": primer_partido.get("odds_ft_under25", 0),
            "over_35": primer_partido.get("odds_ft_over35", 0),
            "under_35": primer_partido.get("odds_ft_under35", 0),
            "over_45": primer_partido.get("odds_ft_over45", 0),
            "under_45": primer_partido.get("odds_ft_under45", 0),
            "over_55": primer_partido.get("odds_ft_over55", 0),
            "under_55": primer_partido.get("odds_ft_under55", 0),
            "btts_si": primer_partido.get("odds_btts_yes", 0),
            "btts_no": primer_partido.get("odds_btts_no", 0),
            "1h_over_05": primer_partido.get("odds_1st_half_over05", 0),
            "1h_under_05": primer_partido.get("odds_1st_half_under05", 0),
            "1h_over_15": primer_partido.get("odds_1st_half_over15", 0),
            "1h_under_15": primer_partido.get("odds_1st_half_under15", 0),
            "1h_over_25": primer_partido.get("odds_1st_half_over25", 0),
            "1h_under_25": primer_partido.get("odds_1st_half_under25", 0),
            "1h_result_1": primer_partido.get("odds_1st_half_result_1", 0),
            "1h_result_x": primer_partido.get("odds_1st_half_result_x", 0),
            "1h_result_2": primer_partido.get("odds_1st_half_result_2", 0),
            "2h_over_05": primer_partido.get("odds_2nd_half_over05", 0),
            "2h_under_05": primer_partido.get("odds_2nd_half_under05", 0),
            "2h_over_15": primer_partido.get("odds_2nd_half_over15", 0),
            "2h_under_15": primer_partido.get("odds_2nd_half_under15", 0),
            "2h_over_25": primer_partido.get("odds_2nd_half_over25", 0),
            "2h_under_25": primer_partido.get("odds_2nd_half_under25", 0),
            "dc_1x": primer_partido.get("odds_doublechance_1x", 0),
            "dc_12": primer_partido.get("odds_doublechance_12", 0),
            "dc_x2": primer_partido.get("odds_doublechance_x2", 0),
            "corners_over_85": primer_partido.get("odds_corners_over_85", 0),
            "corners_over_95": primer_partido.get("odds_corners_over_95", 0),
            "corners_over_105": primer_partido.get("odds_corners_over_105", 0)
        }
    }
    
    print(f"🎯 Testing: {partido_procesado['local']} vs {partido_procesado['visitante']}")
    
    analisis = analizar_partido_completo(partido_procesado)
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"   Probabilidades 1X2: {len(analisis.get('probabilidades_1x2', {}))}")
    print(f"   Probabilidades BTTS: {len(analisis.get('probabilidades_btts', {}))}")
    print(f"   Probabilidades Over/Under: {len(analisis.get('probabilidades_over_under', {}))}")
    print(f"   Probabilidades Primera Mitad: {len(analisis.get('probabilidades_primera_mitad', {}))}")
    print(f"   Probabilidades Segunda Mitad: {len(analisis.get('probabilidades_segunda_mitad', {}))}")
    print(f"   Probabilidades Tarjetas: {len(analisis.get('probabilidades_tarjetas', {}))}")
    print(f"   Probabilidades Corners: {len(analisis.get('probabilidades_corners', {}))}")
    print(f"   Probabilidades Handicap: {len(analisis.get('probabilidades_handicap', {}))}")
    print(f"   Cuotas disponibles: {len(analisis.get('cuotas_disponibles', {}))}")
    
    mejores_apuestas = encontrar_mejores_apuestas(analisis, num_opciones=50, bypass_filters=True)
    
    print(f"\n🎯 MARKET EVALUATION RESULTS:")
    print(f"   Total markets processed: {len(mejores_apuestas)}")
    
    if mejores_apuestas:
        print(f"\n📋 MARKETS BY TYPE:")
        market_types = {}
        for apuesta in mejores_apuestas:
            tipo = apuesta.get('tipo', 'Unknown')
            if tipo not in market_types:
                market_types[tipo] = []
            market_types[tipo].append(apuesta)
        
        for tipo, markets in market_types.items():
            print(f"   {tipo}: {len(markets)} markets")
            for market in markets[:2]:  # Show first 2 of each type
                source = market.get('source', 'api')
                source_mark = "" if source == "api" else " *Calculado*"
                print(f"     - {market['descripcion']} @ {market['cuota']:.2f}{source_mark}")
    
    return len(mejores_apuestas) >= 30

if __name__ == "__main__":
    success = debug_market_evaluation()
    if success:
        print("\n✅ Market evaluation working correctly!")
    else:
        print("\n❌ Market evaluation needs debugging.")
