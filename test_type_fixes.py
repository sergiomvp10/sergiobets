#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_type_fixes():
    print("=== TESTING TYPE FIXES IN IA_BETS MODULE ===")
    
    try:
        from ia_bets import calcular_probabilidades_1x2, calcular_probabilidades_btts, calcular_probabilidades_over_under
        print("✅ All imports successful")
        
        cuotas = {'local': '1.68', 'empate': '3.1', 'visitante': '5.0'}
        prob_1x2 = calcular_probabilidades_1x2(cuotas)
        print(f"✅ 1X2 probabilities: {prob_1x2}")
        
        prob_btts = calcular_probabilidades_btts()
        print(f"✅ BTTS probabilities: {prob_btts}")
        
        prob_ou = calcular_probabilidades_over_under()
        print(f"✅ Over/Under probabilities: {prob_ou}")
        
        print("✅ All type fixes working correctly")
        
    except Exception as e:
        print(f"❌ Error testing type fixes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_type_fixes()
