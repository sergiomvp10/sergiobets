#!/usr/bin/env python3
"""Test the updated prediction message format"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prediction_format():
    """Test that prediction format matches user requirements"""
    print("🧪 TESTING PREDICTION MESSAGE FORMAT")
    print("=" * 50)
    
    try:
        from ia_bets import generar_mensaje_ia
        from datetime import datetime
        
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
        mensaje = generar_mensaje_ia(test_predicciones, fecha)
        
        print("✅ Generated prediction message:")
        print(mensaje)
        print()
        
        expected_elements = [
            "BETGENIUX®",
            "🎯 PRONOSTICO #1",
            "🏆 Champions League", 
            "⚽️ Shakhtar Donetsk vs Panathinaikos",
            "🔮 Más de 8.5 corners",
            "💰 Cuota: 1.63 | Stake: 10u",
            "📊 Confianza: 60% | VE: +0.543",
            "⏰ 11:00",
            "⚠️ Apostar con responsabilidad"
        ]
        
        all_present = True
        for element in expected_elements:
            if element not in mensaje:
                print(f"❌ Missing element: {element}")
                all_present = False
            else:
                print(f"✅ Found: {element}")
        
        if all_present:
            print("\n🎉 Prediction format test PASSED!")
            print("Format matches user specification exactly.")
            return True
        else:
            print("\n❌ Prediction format test FAILED!")
            return False
        
    except Exception as e:
        print(f"❌ Error testing prediction format: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_prediction_format()
