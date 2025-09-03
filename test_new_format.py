#!/usr/bin/env python3
"""Test the new BETGENIUX format"""

from ia_bets import generar_mensaje_ia
from daily_counter import reset_daily_counter
from datetime import datetime

def test_new_format():
    print("=== TESTING NEW BETGENIUX FORMAT ===")
    
    reset_daily_counter()
    test_pred = [{
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
    mensaje = generar_mensaje_ia(test_pred, fecha)
    print('=== FORMATO NUEVO ===')
    print(mensaje)
    print('=== FIN ===')
    
    required_elements = [
        "BETGENIUX®",
        "🎯 PRONOSTICO #1",
        "🏆 Brasileirão",
        "⚽️ Criciúma vs Atlético PR",
        "🔮 Más de 1.5 goles",
        "💰 Cuota: 1.55",
        "📊 Confianza: 60.0%",
        "⏰ 15:00",
        "⚠️ Apostar con responsabilidad"
    ]
    
    success = True
    for element in required_elements:
        if element not in mensaje:
            print(f"❌ Missing: {element}")
            success = False
        else:
            print(f"✅ Found: {element}")
    
    if success:
        print("✅ ALL REQUIRED ELEMENTS FOUND!")
    else:
        print("❌ SOME ELEMENTS MISSING!")
    
    return success

if __name__ == "__main__":
    test_new_format()
