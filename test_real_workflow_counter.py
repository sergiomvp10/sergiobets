#!/usr/bin/env python3
"""Test to verify counter works in real user workflow"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_counter import reset_daily_counter, get_current_counter, get_next_pronostico_numbers
from ia_bets import generar_mensaje_ia
from datetime import datetime

def test_real_workflow():
    print("🧪 TESTING REAL USER WORKFLOW")
    print("=" * 50)
    
    reset_daily_counter()
    print(f"✅ Counter reset. Starting at: {get_current_counter()}")
    
    test_predicciones = [
        {
            'liga': 'Liga Argentina',
            'partido': 'Platense vs Godoy Cruz',
            'prediccion': 'Más de 8.5 corners',
            'cuota': 1.99,
            'stake_recomendado': 10,
            'confianza': 65.7,
            'valor_esperado': 0.308,
            'hora': '15:15'
        }
    ]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    print("\n📊 SIMULATING SEARCH/PREVIEW (should not consume counter):")
    preview_counter_numbers = list(range(1, len(test_predicciones) + 1))
    preview_mensaje = generar_mensaje_ia(test_predicciones, fecha, preview_counter_numbers)
    print(f"Counter after preview: {get_current_counter()}")
    
    print("\n📤 SIMULATING FIRST SEND:")
    counter_numbers_1 = get_next_pronostico_numbers(len(test_predicciones))
    mensaje_1 = generar_mensaje_ia(test_predicciones, fecha, counter_numbers_1)
    print(f"Counter after first send: {get_current_counter()}")
    print(f"First message contains: PRONOSTICO #{counter_numbers_1[0]}")
    
    print("\n📤 SIMULATING SECOND SEND:")
    counter_numbers_2 = get_next_pronostico_numbers(len(test_predicciones))
    mensaje_2 = generar_mensaje_ia(test_predicciones, fecha, counter_numbers_2)
    print(f"Counter after second send: {get_current_counter()}")
    print(f"Second message contains: PRONOSTICO #{counter_numbers_2[0]}")
    
    if counter_numbers_1[0] == 1 and counter_numbers_2[0] == 2:
        print("✅ REAL WORKFLOW TEST PASSED!")
        print("✅ Sequential numbering: #1, #2 as expected")
        return True
    else:
        print("❌ Real workflow test failed")
        return False

if __name__ == "__main__":
    success = test_real_workflow()
    if success:
        print("\n🎉 COUNTER FIX VERIFIED FOR REAL WORKFLOW!")
    else:
        print("\n❌ Counter fix needs more work.")
