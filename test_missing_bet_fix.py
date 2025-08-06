#!/usr/bin/env python3
"""
Test that the missing corner bet was added and can be processed correctly
"""

import json
from datetime import datetime
from track_record import TrackRecordManager

def test_missing_bet_fix():
    """Test that the Athletic Club vs Atletico GO corner bet is now present and can be updated"""
    print("=" * 70)
    print("TESTING MISSING BET FIX")
    print("=" * 70)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corner_bet = None
    for bet in data:
        if ('Athletic Club' in bet.get('partido', '') and 
            'Atlético GO' in bet.get('partido', '') and 
            'corners' in bet.get('prediccion', '').lower()):
            corner_bet = bet
            break
    
    if corner_bet:
        print(f"✅ Found Athletic Club vs Atletico GO corner bet:")
        print(f"   Date: {corner_bet.get('fecha')}")
        print(f"   Match: {corner_bet.get('partido')}")
        print(f"   Bet: {corner_bet.get('prediccion')}")
        status = 'PENDING' if corner_bet.get('resultado_real') is None else ('WON' if corner_bet.get('acierto') else 'LOST')
        print(f"   Status: {status}")
        
        if corner_bet.get('resultado_real') is None:
            print(f"✅ Bet is PENDING - ready for 'Actualizar Resultados' processing")
            
            api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
            tracker = TrackRecordManager(api_key)
            
            print(f"\n🔍 Testing API call for this match...")
            resultado = tracker.obtener_resultado_partido(
                corner_bet.get('fecha'),
                "Athletic Club", 
                "Atlético GO",
                timeout=15
            )
            
            if resultado:
                print(f"✅ API found match with {resultado.get('total_corners', 0)} corners")
                print(f"   Match ID: {resultado.get('match_id', 'N/A')}")
                
                validation_result = tracker.validar_prediccion(corner_bet, resultado)
                if validation_result != (None, None):
                    acierto, ganancia = validation_result
                    print(f"✅ Bet validation: {'WIN' if acierto else 'LOSS'} (${ganancia:.2f})")
                    
                    if acierto and resultado.get('total_corners', 0) == 9:
                        print(f"🎉 PERFECT! 9 corners > 8.5 = WIN as expected")
                        return True
                else:
                    print(f"❌ Bet validation failed - data pending")
            else:
                print(f"❌ API could not find the match")
        else:
            print(f"⚠️ Bet already processed - status: {status}")
    else:
        print(f"❌ Athletic Club vs Atletico GO corner bet NOT FOUND")
        print(f"   Checking all Athletic Club bets...")
        athletic_bets = [bet for bet in data if 'Athletic Club' in bet.get('partido', '')]
        for bet in athletic_bets:
            print(f"   - {bet.get('partido')} | {bet.get('prediccion')}")
    
    return False

if __name__ == "__main__":
    print(f"🔧 TESTING MISSING BET FIX")
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    success = test_missing_bet_fix()
    
    if success:
        print(f"\n🎉 MISSING BET FIX SUCCESSFUL!")
        print(f"   ✅ Athletic Club vs Atletico GO corner bet found")
        print(f"   ✅ API can find the match (9 corners)")
        print(f"   ✅ Bet validation works correctly (WIN)")
        print(f"   🚀 Ready for 'Actualizar Resultados' button test")
    else:
        print(f"\n⚠️ Missing bet fix needs attention")
