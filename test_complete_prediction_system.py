#!/usr/bin/env python3
"""Complete test of the prediction system with real data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_system():
    print("🧪 TESTING COMPLETE PREDICTION SYSTEM")
    print("=" * 60)
    
    from footystats_api import obtener_partidos_del_dia
    from ia_bets import filtrar_apuestas_inteligentes, analizar_partido_individual, ODDS_RANGE_PUBLISH, ODDS_RANGE_ANALYZE
    from league_utils import detectar_liga_por_imagen
    
    print(f"📊 Configured odds ranges:")
    print(f"   PUBLISH: {ODDS_RANGE_PUBLISH}")
    print(f"   ANALYZE: {ODDS_RANGE_ANALYZE}")
    
    partidos_api = obtener_partidos_del_dia('2025-09-04')
    print(f"\n🔍 Found {len(partidos_api)} matches from API")
    
    if not partidos_api:
        print("❌ No matches found from API")
        return False
    
    partidos_procesados = []
    for partido in partidos_api:
        liga_detectada = detectar_liga_por_imagen(
            partido.get("home_image", ""), 
            partido.get("away_image", "")
        )
        
        partido_procesado = {
            "hora": "15:00",
            "liga": liga_detectada,
            "local": partido.get("home_name", f"Team {partido.get('homeID', 'Home')}"),
            "visitante": partido.get("away_name", f"Team {partido.get('awayID', 'Away')}"),
            "cuotas": {
                "casa": "FootyStats",
                "local": str(partido.get("odds_ft_1", "2.00")),
                "empate": str(partido.get("odds_ft_x", "3.00")),
                "visitante": str(partido.get("odds_ft_2", "4.00")),
            },
            "cuotas_disponibles": {
                "local": partido.get("odds_ft_1", 0),
                "empate": partido.get("odds_ft_x", 0),
                "visitante": partido.get("odds_ft_2", 0),
                "over_15": partido.get("odds_ft_over15", 0),
                "under_15": partido.get("odds_ft_under15", 0),
                "over_25": partido.get("odds_ft_over25", 0),
                "under_25": partido.get("odds_ft_under25", 0),
                "btts_si": partido.get("odds_btts_yes", 0),
                "btts_no": partido.get("odds_btts_no", 0),
                "corners_over_85": partido.get("odds_corners_over_85", 0),
                "corners_over_95": partido.get("odds_corners_over_95", 0),
                "corners_over_105": partido.get("odds_corners_over_105", 0),
                "1h_over_05": partido.get("odds_1st_half_over05", 0),
                "1h_over_15": partido.get("odds_1st_half_over15", 0)
            }
        }
        partidos_procesados.append(partido_procesado)
    
    print(f"✅ Processed {len(partidos_procesados)} matches")
    
    print(f"\n🎯 Testing general prediction system (PUBLISH range):")
    predicciones = filtrar_apuestas_inteligentes(partidos_procesados, 5)
    print(f"Generated {len(predicciones)} predictions")
    
    if predicciones:
        for i, pred in enumerate(predicciones):
            print(f"  ✅ {i+1}. {pred['partido']}: {pred['prediccion']} @ {pred['cuota']}")
        general_success = True
    else:
        print(f"  ❌ No predictions generated")
        general_success = False
    
    print(f"\n🔍 Testing individual analysis (ANALYZE range, bypass filters):")
    if partidos_procesados:
        resultado = analizar_partido_individual(partidos_procesados[0], bypass_filters=True)
        if resultado["success"]:
            mejor = resultado['mejor_pick']
            edge_pct = mejor.get('edge_percentage', mejor['valor_esperado'] * 100)
            print(f"✅ Individual analysis successful:")
            print(f"   Match: {resultado['partido']}")
            print(f"   Best pick: {mejor['prediccion']} @ {mejor['cuota']}")
            print(f"   Edge: {edge_pct:.1f}% | Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
            print(f"   Total markets: {len(resultado['todos_mercados'])}")
            individual_success = True
        else:
            print(f"❌ Individual analysis failed: {resultado['error']}")
            individual_success = False
    else:
        individual_success = False
    
    print(f"\n📊 SYSTEM TEST SUMMARY:")
    print(f"   General predictions: {'✅ Working' if general_success else '❌ Failed'}")
    print(f"   Individual analysis: {'✅ Working' if individual_success else '❌ Failed'}")
    
    return general_success and individual_success

if __name__ == "__main__":
    success = test_complete_system()
    if success:
        print("\n🎉 COMPLETE SYSTEM WORKING!")
    else:
        print("\n❌ System needs debugging.")
