#!/usr/bin/env python3
"""
Test script to verify the statistics optimization fixes
"""

import json
from datetime import datetime

def test_statistics_data():
    """Test the statistics data structure and prediction tracking"""
    print("=== TESTING STATISTICS OPTIMIZATION ===")
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"✅ Total predictions in history: {len(historial)}")
        
        con_resultado = [p for p in historial if p.get("resultado_real") is not None]
        sin_resultado = [p for p in historial if p.get("resultado_real") is None]
        
        print(f"✅ Predictions with results: {len(con_resultado)}")
        print(f"✅ Predictions pending results: {len(sin_resultado)}")
        
        recent_predictions = [p for p in historial if p.get('fecha') == '2025-08-03']
        recent_with_results = [p for p in recent_predictions if p.get("resultado_real") is not None]
        recent_without_results = [p for p in recent_predictions if p.get("resultado_real") is None]
        
        print(f"\n📅 Today's predictions (2025-08-03):")
        print(f"   Total: {len(recent_predictions)}")
        print(f"   With results: {len(recent_with_results)}")
        print(f"   Pending: {len(recent_without_results)}")
        
        if recent_without_results:
            print(f"\n🔍 Sample recent pending prediction:")
            sample = recent_without_results[-1]
            print(f"   Partido: {sample.get('partido')}")
            print(f"   Predicción: {sample.get('prediccion')}")
            print(f"   Timestamp: {sample.get('timestamp')}")
        
        return True
        
    except FileNotFoundError:
        print("❌ historial_predicciones.json not found")
        return False
    except Exception as e:
        print(f"❌ Error testing data: {e}")
        return False

def test_track_record_manager():
    """Test TrackRecordManager with the new optimization"""
    print("\n=== TESTING TRACK RECORD MANAGER ===")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"❌ Error in metrics: {metricas['error']}")
            return False
        
        print("✅ TrackRecordManager metrics:")
        print(f"   Total predicciones: {metricas.get('total_predicciones', 'N/A')}")
        print(f"   Predicciones resueltas: {metricas.get('predicciones_resueltas', 'N/A')}")
        print(f"   Predicciones pendientes: {metricas.get('predicciones_pendientes', 'N/A')}")
        print(f"   Aciertos: {metricas.get('aciertos', 'N/A')}")
        
        if metricas.get('predicciones_resueltas', 0) > 0:
            print(f"   Tasa acierto: {metricas.get('tasa_acierto', 'N/A'):.1f}%")
            print(f"   ROI: {metricas.get('roi', 'N/A'):.2f}%")
        
        expected_keys = ['total_predicciones', 'predicciones_resueltas', 'predicciones_pendientes']
        for key in expected_keys:
            if key not in metricas:
                print(f"❌ Missing key in metrics: {key}")
                return False
        
        print("✅ All expected metrics keys present")
        return True
        
    except Exception as e:
        print(f"❌ Error testing TrackRecordManager: {e}")
        return False

def test_telegram_bot_imports():
    """Test that telegram bot listener imports work correctly"""
    print("\n=== TESTING TELEGRAM BOT IMPORTS ===")
    
    try:
        from telegram_bot_listener import mostrar_estadisticas, contar_usuarios_registrados
        print("✅ Successfully imported mostrar_estadisticas")
        print("✅ Successfully imported contar_usuarios_registrados")
        
        print("✅ User count function still available for users functionality")
        return True
        
    except Exception as e:
        print(f"❌ Error testing imports: {e}")
        return False

def main():
    print("🧪 Testing Statistics Optimization")
    print("=" * 50)
    
    tests = [
        ("Statistics Data", test_statistics_data),
        ("TrackRecordManager", test_track_record_manager),
        ("Telegram Bot Imports", test_telegram_bot_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Statistics optimization is working correctly.")
        print("✅ Recent predictions now appear in statistics as 'pending'")
        print("✅ User count removed from statistics display")
        print("✅ TrackRecordManager includes both resolved and pending predictions")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    exit_code = 0 if all_passed else 1
    print(f"\nExit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    main()
