#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_league_filtering():
    print("=== TESTING LEAGUE FILTERING LOGIC ===")
    
    try:
        from ia_bets import filtrar_apuestas_inteligentes
        
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
        
        print("1. Testing all leagues together...")
        predicciones_todas = filtrar_apuestas_inteligentes(partidos_test)
        print(f"   Total predicciones (todas las ligas): {len(predicciones_todas)}")
        for pred in predicciones_todas:
            print(f"   - {pred['liga']}: {pred['prediccion']}")
        
        print("\n2. Testing Liga Colombiana filter...")
        partidos_colombia = [p for p in partidos_test if p["liga"] == "Liga Colombiana"]
        predicciones_colombia = filtrar_apuestas_inteligentes(partidos_colombia)
        print(f"   Partidos Liga Colombiana: {len(partidos_colombia)}")
        print(f"   Predicciones Liga Colombiana: {len(predicciones_colombia)}")
        for pred in predicciones_colombia:
            print(f"   - {pred['liga']}: {pred['prediccion']}")
        
        print("\n3. Testing Liga Argentina filter...")
        partidos_argentina = [p for p in partidos_test if p["liga"] == "Liga Argentina"]
        predicciones_argentina = filtrar_apuestas_inteligentes(partidos_argentina)
        print(f"   Partidos Liga Argentina: {len(partidos_argentina)}")
        print(f"   Predicciones Liga Argentina: {len(predicciones_argentina)}")
        for pred in predicciones_argentina:
            print(f"   - {pred['liga']}: {pred['prediccion']}")
        
        print("\n4. Testing Premier League filter...")
        partidos_premier = [p for p in partidos_test if p["liga"] == "Premier League"]
        predicciones_premier = filtrar_apuestas_inteligentes(partidos_premier)
        print(f"   Partidos Premier League: {len(partidos_premier)}")
        print(f"   Predicciones Premier League: {len(predicciones_premier)}")
        for pred in predicciones_premier:
            print(f"   - {pred['liga']}: {pred['prediccion']}")
        
        print("\n✅ League filtering logic test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in league filtering test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_league_filtering()
    if success:
        print("✅ League filtering test passed")
    else:
        print("❌ League filtering test failed")
