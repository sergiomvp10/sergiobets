#!/usr/bin/env python3
"""Comprehensive test for validation fixes"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_validation_fix():
    """Test all validation fixes comprehensively"""
    print("🧪 COMPREHENSIVE VALIDATION FIX TEST")
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
            },
            {
                "name": "Menos de 2.5 goles with 2 goals (should be GANADA)",
                "prediccion": {"prediccion": "Menos de 2.5 goles", "cuota": 1.4, "stake": 10},
                "resultado": {"home_score": 1, "away_score": 1, "total_goals": 2, "status": "complete"},
                "expected": True
            },
            {
                "name": "Menos de 2.5 goles with 3 goals (should be PERDIDA)",
                "prediccion": {"prediccion": "Menos de 2.5 goles", "cuota": 1.4, "stake": 10},
                "resultado": {"home_score": 2, "away_score": 1, "total_goals": 3, "status": "complete"},
                "expected": False
            },
            {
                "name": "Corner bet without data (should be PERDIDA)",
                "prediccion": {"prediccion": "Más de 8.5 corners", "cuota": 1.4, "stake": 10},
                "resultado": {"home_score": 0, "away_score": 0, "total_goals": 0, "total_corners": 0, "corner_data_available": False, "status": "complete"},
                "expected": False
            },
            {
                "name": "Card bet without data (should be PERDIDA)",
                "prediccion": {"prediccion": "Más de 3.5 tarjetas", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 0, "away_score": 0, "total_goals": 0, "total_cards": 0, "cards_data_available": False, "status": "complete"},
                "expected": False
            }
        ]
        
        print("🎯 TESTING VALIDATION LOGIC:")
        all_passed = True
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. {case['name']}")
            print(f"   Predicción: {case['prediccion']['prediccion']}")
            
            acierto, ganancia = tracker.validar_prediccion(case['prediccion'], case['resultado'])
            
            expected_text = "GANADA" if case['expected'] else "PERDIDA"
            actual_text = "GANADA" if acierto else "PERDIDA"
            
            if acierto == case['expected']:
                print(f"   ✅ CORRECTO: {actual_text}")
            else:
                print(f"   ❌ ERROR: Esperado {expected_text}, obtuvo {actual_text}")
                all_passed = False
        
        print(f"\n🔧 TESTING VALIDATION CORRECTION FUNCTION:")
        correction_result = tracker.corregir_validaciones_incorrectas()
        print(f"  Correcciones realizadas: {correction_result.get('correcciones', 0)}")
        print(f"  Total predicciones: {correction_result.get('total_predicciones', 0)}")
        
        print(f"\n📊 CHECKING FOR NULL ACIERTO VALUES:")
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        null_count = 0
        for pred in data:
            if pred.get('acierto') is None and pred.get('resultado_real') is not None:
                null_count += 1
        
        print(f"  Predictions with null acierto: {null_count}")
        
        if null_count == 0:
            print("  ✅ No null acierto values found")
        else:
            print(f"  ⚠️ Found {null_count} predictions with null acierto values")
        
        return all_passed and null_count == 0
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_validation_fix()
    if success:
        print("\n✅ ALL VALIDATION TESTS PASSED")
        print("🎯 Validation logic is working correctly")
    else:
        print("\n❌ VALIDATION TESTS FAILED")
        print("🚨 Validation logic needs further fixing")
