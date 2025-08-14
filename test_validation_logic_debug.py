#!/usr/bin/env python3
"""Debug the validation logic for Over/Under bets"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_validation_logic():
    """Test the exact validation logic for Over/Under bets"""
    print("🧪 DEBUGGING VALIDATION LOGIC FOR OVER/UNDER BETS")
    print("=" * 60)
    
    try:
        from track_record import TrackRecordManager
        
        api_key = os.getenv('FOOTYSTATS_API_KEY', 'test_key')
        tracker = TrackRecordManager(api_key)
        
        test_cases = [
            {
                "name": "Más de 1.5 goles with 2 goals (should be GANADA)",
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 1, "away_score": 1, "total_goals": 2, "status": "complete"},
                "expected": True
            },
            {
                "name": "Más de 1.5 goles with 3 goals (should be GANADA)", 
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 2, "away_score": 1, "total_goals": 3, "status": "complete"},
                "expected": True
            },
            {
                "name": "Más de 1.5 goles with 1 goal (should be PERDIDA)",
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 1, "away_score": 0, "total_goals": 1, "status": "complete"},
                "expected": False
            },
            {
                "name": "Más de 1.5 goles with 0 goals (should be PERDIDA)",
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 0, "away_score": 0, "total_goals": 0, "status": "complete"},
                "expected": False
            }
        ]
        
        print("🎯 TESTING VALIDATION LOGIC:")
        all_passed = True
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. {case['name']}")
            print(f"   Predicción: {case['prediccion']['prediccion']}")
            print(f"   Resultado: {case['resultado']['home_score']}-{case['resultado']['away_score']} ({case['resultado']['total_goals']} goles)")
            
            acierto, ganancia = tracker.validar_prediccion(case['prediccion'], case['resultado'])
            
            expected_text = "GANADA" if case['expected'] else "PERDIDA"
            actual_text = "GANADA" if acierto else "PERDIDA"
            
            if acierto == case['expected']:
                print(f"   ✅ CORRECTO: {actual_text}")
            else:
                print(f"   ❌ ERROR: Esperado {expected_text}, obtuvo {actual_text}")
                all_passed = False
        
        print(f"\n🔍 DEBUGGING VALIDATION LOGIC:")
        prediccion_text = "Más de 1.5 goles"
        total_goals = 2
        
        if "más de" in prediccion_text.lower() and "goles" in prediccion_text.lower():
            try:
                umbral = float(prediccion_text.split("más de ")[1].split(" goles")[0])
                result = total_goals > umbral
                print(f"   Umbral extraído: {umbral}")
                print(f"   Goles totales: {total_goals}")
                print(f"   Comparación: {total_goals} > {umbral} = {result}")
                print(f"   Lógica: {'CORRECTA' if result else 'INCORRECTA'}")
            except Exception as e:
                print(f"   ❌ Error en extracción de umbral: {e}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_validation_logic()
    if success:
        print("\n✅ ALL VALIDATION TESTS PASSED")
    else:
        print("\n❌ VALIDATION TESTS FAILED - Logic needs fixing")
