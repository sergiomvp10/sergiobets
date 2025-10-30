#!/usr/bin/env python3
"""Test comprehensive market analysis with all market types"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_markets():
    print("🧪 TESTING COMPREHENSIVE MARKET ANALYSIS")
    print("=" * 60)
    
    from footystats_api import obtener_partidos_del_dia
    from ia_bets import analizar_partido_individual
    from league_utils import detectar_liga_por_imagen
    
    partidos_api = obtener_partidos_del_dia('2025-09-04')
    if not partidos_api:
        print("❌ No matches found from API")
        return False
    
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
    
    resultado = analizar_partido_individual(partido_procesado, bypass_filters=True)
    
    if resultado["success"]:
        market_categories = {}
        for mercado in resultado['todos_mercados']:
            desc = mercado['descripcion']
            if 'goles 1H' in desc or '1H' in desc:
                category = 'Primera Mitad'
            elif 'goles 2H' in desc or '2H' in desc:
                category = 'Segunda Mitad'
            elif 'corners' in desc:
                category = 'Corners'
            elif 'tarjetas' in desc:
                category = 'Tarjetas'
            elif 'Handicap' in desc or '+0.5' in desc or '-0.5' in desc:
                category = 'Handicap'
            elif 'marcan' in desc:
                category = 'BTTS'
            elif 'Empate o' in desc or 'o Empate' in desc:
                category = 'Doble Oportunidad'
            elif 'goles' in desc:
                category = 'Goles Totales'
            elif 'Victoria' in desc or 'Empate' == desc:
                category = '1X2'
            else:
                category = 'Otros'
            
            if category not in market_categories:
                market_categories[category] = []
            market_categories[category].append(mercado)
        
        print(f"📋 MARKETS BY CATEGORY:")
        for category, markets in market_categories.items():
            print(f"   {category}: {len(markets)} markets")
        
        required_categories = ['Primera Mitad', 'Corners', 'Tarjetas', 'Handicap']
        missing_categories = [cat for cat in required_categories if cat not in market_categories]
        
        if missing_categories:
            print(f"⚠️ Missing market categories: {missing_categories}")
        else:
            print(f"✅ All required market categories present!")
        
        print(f"\n📊 TOTAL MARKETS ANALYZED: {len(resultado['todos_mercados'])}")
        
        print(f"\n🏆 TOP 5 MARKETS:")
        for i, mercado in enumerate(resultado['todos_mercados'][:5]):
            edge_pct = mercado.get('edge_percentage', mercado['valor_esperado'] * 100)
            source = mercado.get('source', 'api')
            source_mark = "" if source == "api" else " *Sin cuota API*"
            cumple = "✅" if mercado.get('cumple_publicacion', False) else "⚠️"
            print(f"   {cumple} {i+1}. {mercado['descripcion']} @ {mercado['cuota']:.2f} (Edge: {edge_pct:.1f}%){source_mark}")
        
        return len(market_categories) >= 6 and len(resultado['todos_mercados']) >= 30
    else:
        print(f"❌ Individual analysis failed: {resultado['error']}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_markets()
    if success:
        print("\n🎉 COMPREHENSIVE MARKET ANALYSIS WORKING!")
    else:
        print("\n❌ Comprehensive market analysis needs improvement.")
