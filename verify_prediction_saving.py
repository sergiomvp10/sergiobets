#!/usr/bin/env python3

import json
from datetime import datetime
from ia_bets import guardar_prediccion_historica

def test_prediction_saving():
    """Test that predictions are saved correctly when sent to Telegram"""
    print("=== TESTING PREDICTION SAVING LOGIC ===")
    
    test_prediction = {
        "partido": "Test Team A vs Test Team B",
        "liga": "Test League",
        "prediccion": "Más de 2.5 goles",
        "cuota": 1.65,
        "stake_recomendado": 10,
        "valor_esperado": 0.25,
        "confianza": 85.5
    }
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial_before = json.load(f)
    except:
        historial_before = []
    
    count_before = len(historial_before)
    print(f"Predictions before test: {count_before}")
    
    fecha = "2025-08-03"
    guardar_prediccion_historica(test_prediction, fecha)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        historial_after = json.load(f)
    
    count_after = len(historial_after)
    print(f"Predictions after test: {count_after}")
    
    if count_after > count_before:
        print("✅ Prediction saving works correctly")
        
        last_prediction = historial_after[-1]
        print(f"📝 Saved prediction: {last_prediction['partido']} - {last_prediction['prediccion']}")
        print(f"📅 Date: {last_prediction['fecha']}")
        print(f"💰 Stake: {last_prediction['stake']}")
        print(f"🎯 Confidence: {last_prediction['confianza']}%")
        
        historial_after.pop()
        with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
            json.dump(historial_after, f, ensure_ascii=False, indent=4)
        print("🧹 Test prediction removed to keep data clean")
        
        return True
    else:
        print("❌ Prediction saving failed")
        return False

if __name__ == "__main__":
    success = test_prediction_saving()
    if success:
        print("\n✅ Prediction saving test PASSED")
    else:
        print("\n❌ Prediction saving test FAILED")
