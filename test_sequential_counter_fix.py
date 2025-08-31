#!/usr/bin/env python3
"""Test that the sequential counter fix works correctly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sequential_counter_fix():
    """Test that counter now counts sequentially 1, 2, 3..."""
    print("🧪 TESTING SEQUENTIAL COUNTER FIX")
    print("=" * 50)
    
    try:
        from daily_counter import reset_daily_counter, get_current_counter, get_next_pronostico_numbers
        from ia_bets import generar_mensaje_ia
        from datetime import datetime
        
        reset_daily_counter()
        print(f"✅ Counter reset. Current: {get_current_counter()}")
        
        test_predicciones = [
            {
                'liga': 'Liga Argentina',
                'partido': 'Test vs Test',
                'prediccion': 'Test prediction',
                'cuota': 1.58,
                'stake_recomendado': 10,
                'confianza': 56.0,
                'valor_esperado': 0.299,
                'hora': '15:30'
            }
        ]
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print("\n🧪 FIRST PREDICTION:")
        numbers1 = get_next_pronostico_numbers(1)
        print(f"Got numbers for send: {numbers1}")
        print(f"Counter after getting numbers: {get_current_counter()}")
        
        mensaje1 = generar_mensaje_ia(test_predicciones, fecha, numbers1)
        print(f"Message formatted with reserved numbers: PRONOSTICO #{numbers1[0]}")
        
        print("\n🧪 SECOND PREDICTION:")
        numbers2 = get_next_pronostico_numbers(1)
        print(f"Got numbers for send: {numbers2}")
        print(f"Counter after getting numbers: {get_current_counter()}")
        
        mensaje2 = generar_mensaje_ia(test_predicciones, fecha, numbers2)
        print(f"Message formatted with reserved numbers: PRONOSTICO #{numbers2[0]}")
        
        if get_current_counter() == 2 and numbers1 == [1] and numbers2 == [2]:
            print("✅ SEQUENTIAL COUNTER FIX SUCCESSFUL!")
            print("Counter now increments 1, 2, 3... as expected")
            return True
        else:
            print("❌ Counter fix failed")
            print(f"Expected counter=2, numbers1=[1], numbers2=[2]")
            print(f"Got counter={get_current_counter()}, numbers1={numbers1}, numbers2={numbers2}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing counter fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sequential_counter_fix()
