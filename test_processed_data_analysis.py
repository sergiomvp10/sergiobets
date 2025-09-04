#!/usr/bin/env python3
"""Test individual analysis with processed data from GUI"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_processed_data_analysis():
    print("🧪 TESTING INDIVIDUAL ANALYSIS WITH PROCESSED DATA")
    print("=" * 60)
    
    from sergiobets_unified import SergioBetsUnified
    from ia_bets import analizar_partido_individual
    
    app = SergioBetsUnified()
    partidos_procesados = app.cargar_partidos_reales('2025-09-04')
    
    if not partidos_procesados:
        print("❌ No se encontraron partidos procesados para probar")
        return False
    
    print(f"🔍 Found {len(partidos_procesados)} processed matches, testing first one:")
    
    primer_partido = partidos_procesados[0]
    print(f"   Match: {primer_partido['local']} vs {primer_partido['visitante']}")
    print(f"   Liga: {primer_partido['liga']}")
    print(f"   Cuotas: {primer_partido['cuotas']['local']}-{primer_partido['cuotas']['empate']}-{primer_partido['cuotas']['visitante']}")
    
    if 'cuotas_disponibles' in primer_partido:
        available_markets = len([k for k, v in primer_partido['cuotas_disponibles'].items() if v > 0])
        print(f"   ✅ Cuotas disponibles: {available_markets} markets")
        
        print(f"   📊 Sample markets:")
        for k, v in list(primer_partido['cuotas_disponibles'].items())[:5]:
            if v > 0:
                print(f"      {k}: {v}")
    else:
        print(f"   ❌ Missing cuotas_disponibles")
        return False
    
    print(f"\n🔍 Testing individual analysis (bypass all filters):")
    resultado = analizar_partido_individual(primer_partido, bypass_filters=True)
    
    if resultado["success"]:
        mejor = resultado['mejor_pick']
        print(f"\n✅ ANÁLISIS EXITOSO:")
        print(f"   Mejor pick: {mejor['prediccion']} @ {mejor['cuota']}")
        print(f"   Edge: {mejor.get('edge_percentage', 'N/A')}%")
        print(f"   Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
        print(f"   Total mercados: {len(resultado['todos_mercados'])}")
        
        print(f"\n📋 PRIMEROS 5 MERCADOS:")
        for i, mercado in enumerate(resultado['todos_mercados'][:5]):
            edge_pct = round(mercado['valor_esperado'] * 100, 1)
            cumple = "✅" if edge_pct >= 5 else "⚠️"
            print(f"   {cumple} {i+1}. {mercado['descripcion']} @ {mercado['cuota']:.2f} (Edge: {edge_pct}%)")
            
        return True
    else:
        print(f"\n❌ ANÁLISIS FALLÓ: {resultado['error']}")
        return False

if __name__ == "__main__":
    success = test_processed_data_analysis()
    if success:
        print("\n🎉 INDIVIDUAL ANALYSIS WORKING WITH PROCESSED DATA!")
    else:
        print("\n❌ Individual analysis still needs debugging.")
