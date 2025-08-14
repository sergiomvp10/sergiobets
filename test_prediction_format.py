#!/usr/bin/env python3
"""Test the updated prediction message format with daily counter"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prediction_format_with_telegram_integration():
    """Test that prediction format works with Telegram sending integration"""
    print("🧪 TESTING PREDICTION FORMAT WITH TELEGRAM INTEGRATION")
    print("=" * 50)
    
    try:
        from ia_bets import generar_mensaje_ia
        from daily_counter import reset_daily_counter, get_current_counter, count_predictions_in_message
        from datetime import datetime
        
        reset_daily_counter()
        
        test_predicciones = [
            {
                'liga': 'Champions League',
                'partido': 'Shakhtar Donetsk vs Panathinaikos',
                'prediccion': 'Más de 8.5 corners',
                'cuota': 1.63,
                'stake_recomendado': 10,
                'confianza': 60.0,
                'valor_esperado': 0.543,
                'hora': '11:00'
            }
        ]
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Testing date: {fecha}")
        print(f"🔢 Counter before: {get_current_counter()}")
        
        mensaje = generar_mensaje_ia(test_predicciones, fecha)
        print(f"\n✅ Generated message:\n{mensaje}")
        
        prediction_count = count_predictions_in_message(mensaje)
        print(f"\n📊 Predictions detected in message: {prediction_count}")
        
        if "🎯 PRONOSTICO #1" in mensaje:
            print("✅ Sequential numbering works correctly")
            return True
        else:
            print("❌ Sequential numbering failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_format():
    """Test that prediction format matches user requirements with daily counter"""
    print("🧪 TESTING PREDICTION MESSAGE FORMAT WITH DAILY COUNTER")
    print("=" * 50)
    
    try:
        from ia_bets import generar_mensaje_ia
        from daily_counter import get_current_counter, reset_daily_counter
        from datetime import datetime
        
        reset_daily_counter()
        
        test_predicciones = [
            {
                'liga': 'Champions League',
                'partido': 'Shakhtar Donetsk vs Panathinaikos',
                'prediccion': 'Más de 8.5 corners',
                'cuota': 1.63,
                'stake_recomendado': 10,
                'confianza': 60.0,
                'valor_esperado': 0.543,
                'hora': '11:00'
            },
            {
                'liga': 'Premier League',
                'partido': 'Manchester City vs Arsenal',
                'prediccion': 'Over 2.5 goles',
                'cuota': 1.85,
                'stake_recomendado': 8,
                'confianza': 75.0,
                'valor_esperado': 0.421,
                'hora': '15:30'
            }
        ]
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Testing date: {fecha}")
        print(f"🔢 Counter before: {get_current_counter()}")
        
        mensaje1 = generar_mensaje_ia([test_predicciones[0]], fecha)
        print("\n✅ First prediction message:")
        print(mensaje1)
        print(f"🔢 Counter after first: {get_current_counter()}")
        
        mensaje2 = generar_mensaje_ia([test_predicciones[1]], fecha)
        print("\n✅ Second prediction message:")
        print(mensaje2)
        print(f"🔢 Counter after second: {get_current_counter()}")
        
        mensaje3 = generar_mensaje_ia(test_predicciones, fecha)
        print("\n✅ Batch prediction message:")
        print(mensaje3)
        print(f"🔢 Counter after batch: {get_current_counter()}")
        
        expected_elements_first = ["🎯 PRONOSTICO #1"]
        expected_elements_second = ["🎯 PRONOSTICO #2"]
        expected_elements_batch = ["🎯 PRONOSTICO #3", "🎯 PRONOSTICO #4"]
        
        tests_passed = 0
        total_tests = 4
        
        if all(elem in mensaje1 for elem in expected_elements_first):
            print("✅ First message numbering correct")
            tests_passed += 1
        else:
            print("❌ First message numbering incorrect")
            
        if all(elem in mensaje2 for elem in expected_elements_second):
            print("✅ Second message numbering correct")
            tests_passed += 1
        else:
            print("❌ Second message numbering incorrect")
            
        if all(elem in mensaje3 for elem in expected_elements_batch):
            print("✅ Batch message numbering correct")
            tests_passed += 1
        else:
            print("❌ Batch message numbering incorrect")
            
        if "⚠️ Apostar con responsabilidad" in mensaje3:
            print("✅ Responsibility warning present")
            tests_passed += 1
        else:
            print("❌ Responsibility warning missing")
        
        if tests_passed == total_tests:
            print(f"\n🎉 Daily counter prediction format test PASSED! ({tests_passed}/{total_tests})")
            print("Sequential numbering works correctly throughout the day.")
            return True
        else:
            print(f"\n❌ Daily counter prediction format test FAILED! ({tests_passed}/{total_tests})")
            return False
        
    except Exception as e:
        print(f"❌ Error testing prediction format: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running both test functions...\n")
    test_prediction_format_with_telegram_integration()
    print("\n" + "="*50 + "\n")
    test_prediction_format()
