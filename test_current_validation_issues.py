#!/usr/bin/env python3
"""Test current validation issues to understand what's still broken"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_current_validation_issues():
    """Test current validation issues in the track record"""
    print("🔍 TESTING CURRENT VALIDATION ISSUES")
    print("=" * 60)
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Total predictions in historial: {len(data)}")
        
        issues = {
            "null_acierto": 0,
            "mas_de_1_5_goles_issues": [],
            "validation_inconsistencies": [],
            "missing_resultado_real": 0
        }
        
        for i, pred in enumerate(data):
            if pred.get('acierto') is None and pred.get('resultado_real') is not None:
                issues["null_acierto"] += 1
            
            if pred.get('resultado_real') is None:
                issues["missing_resultado_real"] += 1
            
            if "más de 1.5 goles" in pred.get('prediccion', '').lower():
                resultado = pred.get('resultado_real')
                if resultado:
                    total_goals = resultado.get('total_goals', 0)
                    acierto = pred.get('acierto')
                    expected_acierto = total_goals > 1.5
                    
                    if acierto != expected_acierto:
                        issues["mas_de_1_5_goles_issues"].append({
                            "index": i,
                            "partido": pred.get('partido', 'unknown'),
                            "fecha": pred.get('fecha', 'unknown'),
                            "total_goals": total_goals,
                            "current_acierto": acierto,
                            "expected_acierto": expected_acierto,
                            "score": f"{resultado.get('home_score', 0)}-{resultado.get('away_score', 0)}"
                        })
        
        print(f"\n🚨 ISSUES FOUND:")
        print(f"  • Predictions with null acierto: {issues['null_acierto']}")
        print(f"  • Predictions missing resultado_real: {issues['missing_resultado_real']}")
        print(f"  • 'Más de 1.5 goles' validation issues: {len(issues['mas_de_1_5_goles_issues'])}")
        
        if issues["mas_de_1_5_goles_issues"]:
            print(f"\n📋 'MÁS DE 1.5 GOLES' VALIDATION ISSUES:")
            for issue in issues["mas_de_1_5_goles_issues"][:10]:  # Show first 10
                expected_text = "GANADA" if issue['expected_acierto'] else "PERDIDA"
                current_text = "GANADA" if issue['current_acierto'] else "PERDIDA" if issue['current_acierto'] is not None else "NULL"
                print(f"  • {issue['partido']} ({issue['fecha']}) - Score: {issue['score']} ({issue['total_goals']} goals)")
                print(f"    Current: {current_text} | Expected: {expected_text}")
        
        print(f"\n🧪 TESTING VALIDATION LOGIC DIRECTLY:")
        from track_record import TrackRecordManager
        
        api_key = os.getenv('FOOTYSTATS_API_KEY', 'test_key')
        tracker = TrackRecordManager(api_key)
        
        test_cases = [
            {
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 0, "away_score": 0, "total_goals": 0, "status": "complete"},
                "expected": False,
                "description": "0-0 (0 goals) should be PERDIDA"
            },
            {
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 1, "away_score": 0, "total_goals": 1, "status": "complete"},
                "expected": False,
                "description": "1-0 (1 goal) should be PERDIDA"
            },
            {
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 1, "away_score": 1, "total_goals": 2, "status": "complete"},
                "expected": True,
                "description": "1-1 (2 goals) should be GANADA"
            },
            {
                "prediccion": {"prediccion": "Más de 1.5 goles", "cuota": 1.5, "stake": 10},
                "resultado": {"home_score": 2, "away_score": 1, "total_goals": 3, "status": "complete"},
                "expected": True,
                "description": "2-1 (3 goals) should be GANADA"
            }
        ]
        
        validation_working = True
        for case in test_cases:
            acierto, ganancia = tracker.validar_prediccion(case['prediccion'], case['resultado'])
            expected_text = "GANADA" if case['expected'] else "PERDIDA"
            actual_text = "GANADA" if acierto else "PERDIDA"
            
            if acierto == case['expected']:
                print(f"  ✅ {case['description']}: {actual_text}")
            else:
                print(f"  ❌ {case['description']}: Expected {expected_text}, got {actual_text}")
                validation_working = False
        
        return {
            "validation_logic_working": validation_working,
            "data_issues": issues,
            "needs_manual_correction": len(issues["mas_de_1_5_goles_issues"]) > 0 or issues["null_acierto"] > 0
        }
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    result = test_current_validation_issues()
    if result.get("validation_logic_working", False):
        print("\n✅ VALIDATION LOGIC IS WORKING CORRECTLY")
        if result.get("needs_manual_correction", False):
            print("🔧 BUT HISTORICAL DATA NEEDS MANUAL CORRECTION")
        else:
            print("🎯 ALL DATA IS CORRECT")
    else:
        print("\n❌ VALIDATION LOGIC STILL HAS ISSUES")
        print("🚨 NEEDS IMMEDIATE FIXING")
