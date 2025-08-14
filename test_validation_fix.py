#!/usr/bin/env python3
"""Test the validation fix for Over/Under bets specifically"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_validation_fix():
    """Test that 'Más de 1.5 goles' with 3-1 result is correctly marked as won"""
    print("🧪 TESTING VALIDATION FIX FOR OVER/UNDER BETS")
    print("=" * 60)
    
    try:
        from track_record import TrackRecordManager
        import json
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        test_prediction = {
            "prediccion": "Más de 1.5 goles",
            "cuota": 1.5,
            "stake": 10
        }
        
        test_result = {
            "home_score": 3,
            "away_score": 1,
            "total_goals": 4,
            "status": "complete"
        }
        
        print(f"🎯 TEST CASE:")
        print(f"  Predicción: {test_prediction['prediccion']}")
        print(f"  Resultado: 3-1 (4 goles totales)")
        print(f"  Umbral: 1.5 goles")
        print(f"  Esperado: GANADA (4 > 1.5)")
        
        acierto, ganancia = tracker.validar_prediccion(test_prediction, test_result)
        
        print(f"\n📊 RESULTADO DE VALIDACIÓN:")
        print(f"  Acierto: {acierto}")
        print(f"  Ganancia: {ganancia}")
        
        if acierto:
            print("✅ CORRECTO: La predicción se marca como GANADA")
        else:
            print("❌ ERROR: La predicción se marca como PERDIDA (incorrecto)")
            return False
        
        test_cases = [
            {
                "prediccion": "Más de 2.5 goles",
                "result": {"home_score": 2, "away_score": 1, "total_goals": 3, "status": "complete"},
                "expected": True,
                "description": "3 goles > 2.5"
            },
            {
                "prediccion": "Menos de 2.5 goles", 
                "result": {"home_score": 1, "away_score": 0, "total_goals": 1, "status": "complete"},
                "expected": True,
                "description": "1 gol < 2.5"
            },
            {
                "prediccion": "Más de 3.5 goles",
                "result": {"home_score": 2, "away_score": 1, "total_goals": 3, "status": "complete"},
                "expected": False,
                "description": "3 goles < 3.5"
            }
        ]
        
        print(f"\n🔍 TESTING ADDITIONAL OVER/UNDER CASES:")
        all_passed = True
        
        for i, case in enumerate(test_cases, 1):
            test_pred = {"prediccion": case["prediccion"], "cuota": 1.5, "stake": 10}
            acierto, ganancia = tracker.validar_prediccion(test_pred, case["result"])
            
            status = "✅ PASS" if acierto == case["expected"] else "❌ FAIL"
            print(f"  {i}. {case['prediccion']} - {case['description']} - {status}")
            
            if acierto != case["expected"]:
                all_passed = False
        
        print(f"\n🔧 TESTING VALIDATION CORRECTION FUNCTION:")
        correction_result = tracker.corregir_validaciones_incorrectas()
        print(f"  Correcciones realizadas: {correction_result.get('correcciones', 0)}")
        print(f"  Total predicciones: {correction_result.get('total_predicciones', 0)}")
        
        if correction_result.get('correcciones', 0) > 0:
            print("✅ Validation correction function is working")
        else:
            print("ℹ️ No validation corrections needed (data already correct)")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_validation_fix()
    if success:
        print("\n✅ ALL VALIDATION TESTS PASSED")
        print("🎯 'Más de 1.5 goles' with 3-1 result correctly marked as GANADA")
    else:
        print("\n❌ VALIDATION TESTS FAILED")
        print("🚨 Over/Under validation logic needs fixing")
