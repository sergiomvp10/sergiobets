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
        from daily_counter import reset_daily_counter, get_current_counter, increment_counter_after_send
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
        mensaje1 = generar_mensaje_ia(test_predicciones, fecha)
        print(f"Message formatted (should show #1): {mensaje1[:100]}...")
        print(f"Counter after formatting: {get_current_counter()}")
        
        increment_result1 = increment_counter_after_send(mensaje1)
        print(f"After Telegram send increment: {increment_result1}")
        print(f"Counter after send: {get_current_counter()}")
        
        print("\n🧪 SECOND PREDICTION:")
        mensaje2 = generar_mensaje_ia(test_predicciones, fecha)
        print(f"Message formatted (should show #1 again): {mensaje2[:100]}...")
        print(f"Counter after formatting: {get_current_counter()}")
        
        increment_result2 = increment_counter_after_send(mensaje2)
        print(f"After Telegram send increment: {increment_result2}")
        print(f"Counter after send: {get_current_counter()}")
        
        if get_current_counter() == 2:
            print("✅ SEQUENTIAL COUNTER FIX SUCCESSFUL!")
            print("Counter now increments 1, 2, 3... as expected")
            return True
        else:
            print("❌ Counter fix failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing counter fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sequential_counter_fix()
