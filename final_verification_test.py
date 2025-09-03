#!/usr/bin/env python3
"""Final verification test for BETGENIUX format implementation"""

from ia_bets import generar_mensaje_ia
from daily_counter import reset_daily_counter, get_next_pronostico_numbers
from datetime import datetime
import json

def test_comprehensive_format():
    print("🧪 COMPREHENSIVE BETGENIUX FORMAT VERIFICATION")
    print("=" * 60)
    
    reset_daily_counter()
    
    print("\n1️⃣ TESTING SINGLE PREDICTION (AUTO COUNTER)")
    test_pred_single = [{
        'liga': 'Brasileirão',
        'partido': 'Criciúma vs Atlético PR', 
        'prediccion': 'Más de 1.5 goles',
        'cuota': 1.55,
        'stake_recomendado': 10,
        'confianza': 60.0,
        'valor_esperado': 0.373,
        'hora': '15:00'
    }]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    mensaje_single = generar_mensaje_ia(test_pred_single, fecha)
    print(mensaje_single)
    
    print("\n2️⃣ TESTING MULTIPLE PREDICTIONS (BATCH)")
    test_pred_multiple = [
        {
            'liga': 'Premier League',
            'partido': 'Manchester City vs Arsenal', 
            'prediccion': 'Over 2.5 goles',
            'cuota': 1.85,
            'stake_recomendado': 8,
            'confianza': 75.0,
            'valor_esperado': 0.421,
            'hora': '15:30'
        },
        {
            'liga': 'La Liga',
            'partido': 'Real Madrid vs Barcelona', 
            'prediccion': 'Ambos equipos marcan',
            'cuota': 1.72,
            'stake_recomendado': 12,
            'confianza': 80.0,
            'valor_esperado': 0.512,
            'hora': '18:00'
        }
    ]
    
    mensaje_multiple = generar_mensaje_ia(test_pred_multiple, fecha)
    print(mensaje_multiple)
    
    print("\n3️⃣ TESTING MANUAL COUNTER NUMBERS")
    reset_daily_counter()
    manual_numbers = [5, 6]  # Simulate starting from prediction #5
    mensaje_manual = generar_mensaje_ia(test_pred_multiple, fecha, manual_numbers)
    print(mensaje_manual)
    
    print("\n4️⃣ TESTING EMPTY PREDICTIONS")
    mensaje_empty = generar_mensaje_ia([], fecha)
    print(mensaje_empty)
    
    print("\n✅ VERIFICATION CHECKLIST")
    print("=" * 40)
    
    required_elements = [
        ("BETGENIUX® header", "BETGENIUX®" in mensaje_single),
        ("Date format", f"({fecha})" in mensaje_single),
        ("PRONOSTICO # format", "🎯 PRONOSTICO #" in mensaje_single),
        ("League emoji", "🏆" in mensaje_single),
        ("Match emoji", "⚽️" in mensaje_single),
        ("Prediction emoji", "🔮" in mensaje_single),
        ("Money emoji", "💰" in mensaje_single),
        ("Stats emoji", "📊" in mensaje_single),
        ("Time emoji", "⏰" in mensaje_single),
        ("Responsibility warning", "⚠️ Apostar con responsabilidad" in mensaje_single),
        ("Sequential numbering", "#1" in mensaje_single and "#2" in mensaje_multiple),
        ("Manual numbering works", "#5" in mensaje_manual and "#6" in mensaje_manual),
        ("Empty case handled", "❌ No se encontraron" in mensaje_empty)
    ]
    
    all_passed = True
    for description, passed in required_elements:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ BETGENIUX® format implementation is complete and working correctly")
    else:
        print("❌ SOME VERIFICATION TESTS FAILED!")
        print("🔧 Implementation needs fixes")
    
    return all_passed

if __name__ == "__main__":
    test_comprehensive_format()
