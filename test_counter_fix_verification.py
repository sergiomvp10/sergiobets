#!/usr/bin/env python3
"""Test to verify the counter jumping bug is fixed"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_counter import reset_daily_counter, get_current_counter, get_next_pronostico_numbers
from ia_bets import generar_mensaje_ia
from datetime import datetime

def test_sequential_counter_fix():
    print("🧪 TESTING SEQUENTIAL COUNTER FIX")
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
        },
        {
            'liga': 'Liga Argentina', 
            'partido': 'Belgrano vs San Martín San Juan',
            'prediccion': 'Más de 1.5 goles',
            'cuota': 1.67,
            'stake_recomendado': 10,
            'confianza': 83.6,
            'valor_esperado': 0.395,
            'hora': '16:00'
        }
    ]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    print("\n📊 SIMULATING FIXED WORKFLOW:")
    counter_numbers = get_next_pronostico_numbers(len(test_predicciones))
    print(f"Reserved numbers: {counter_numbers}")
    print(f"Counter after reservation: {get_current_counter()}")
    
    mensaje = generar_mensaje_ia(test_predicciones, fecha, counter_numbers)
    print(f"Counter after message generation: {get_current_counter()}")
    
    print("\n📱 GENERATED MESSAGE:")
    print(mensaje)
    print()
    
    expected_numbers = [1, 2]
    for i, expected_num in enumerate(expected_numbers):
        if f"PRONOSTICO #{expected_num}" not in mensaje:
            print(f"❌ Missing PRONOSTICO #{expected_num} in message")
            return False
    
    if get_current_counter() == len(test_predicciones):
        print("✅ COUNTER FIX SUCCESSFUL!")
        print(f"✅ Counter correctly shows {get_current_counter()} for {len(test_predicciones)} predictions")
        print("✅ Sequential numbering: #1, #2 as expected")
        return True
    else:
        print("❌ Counter fix failed")
        return False

def test_multiple_sends():
    print("\n🔄 TESTING MULTIPLE SENDS (SIMULATING REAL USAGE)")
    print("=" * 50)
    
    reset_daily_counter()
    
    single_pred = [{
        'liga': 'Premier League',
        'partido': 'Manchester City vs Arsenal',
        'prediccion': 'Over 2.5 goles',
        'cuota': 1.85,
        'stake_recomendado': 8,
        'confianza': 75.0,
        'valor_esperado': 0.421,
        'hora': '15:30'
    }]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    print("First send:")
    counter_numbers_1 = get_next_pronostico_numbers(len(single_pred))
    mensaje_1 = generar_mensaje_ia(single_pred, fecha, counter_numbers_1)
    print(f"Counter after first send: {get_current_counter()}")
    
    print("Second send:")
    counter_numbers_2 = get_next_pronostico_numbers(len(single_pred))
    mensaje_2 = generar_mensaje_ia(single_pred, fecha, counter_numbers_2)
    print(f"Counter after second send: {get_current_counter()}")
    
    print("Third send:")
    counter_numbers_3 = get_next_pronostico_numbers(len(single_pred))
    mensaje_3 = generar_mensaje_ia(single_pred, fecha, counter_numbers_3)
    print(f"Counter after third send: {get_current_counter()}")
    
    if "#1" in mensaje_1 and "#2" in mensaje_2 and "#3" in mensaje_3:
        print("✅ MULTIPLE SENDS WORKING CORRECTLY!")
        print("✅ Sequential numbering maintained across multiple sends")
        return True
    else:
        print("❌ Multiple sends failed")
        return False

if __name__ == "__main__":
    success1 = test_sequential_counter_fix()
    success2 = test_multiple_sends()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! Counter fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Counter fix needs more work.")
