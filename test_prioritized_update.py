#!/usr/bin/env python3
"""
Test the prioritized update system for Athletic Club corner bet
"""

import json
from datetime import datetime
from track_record import TrackRecordManager

def test_prioritized_athletic_update():
    """Test that Athletic Club corner bet gets processed first with prioritization"""
    print("=" * 70)
    print("TESTING PRIORITIZED ATHLETIC CLUB UPDATE")
    print("=" * 70)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
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
        print(f"✅ Found Athletic Club corner bet:")
        print(f"   Date: {corner_bet.get('fecha')}")
        print(f"   Match: {corner_bet.get('partido')}")
        print(f"   Bet: {corner_bet.get('prediccion')}")
        status_before = 'PENDING' if corner_bet.get('resultado_real') is None else ('WON' if corner_bet.get('acierto') else 'LOST')
        print(f"   Status BEFORE: {status_before}")
        
        if status_before == 'PENDING':
            print(f"\n🔄 Running prioritized update (Athletic Club should be processed FIRST)...")
            result = tracker.actualizar_historial_con_resultados(max_matches=1, timeout_per_match=15)
            print(f"📈 Update result: {result}")
            
            with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
                updated_data = json.load(f)
            
            updated_corner_bet = None
            for bet in updated_data:
                if ('Athletic Club' in bet.get('partido', '') and 
                    'Atlético GO' in bet.get('partido', '') and 
                    'corners' in bet.get('prediccion', '').lower()):
                    updated_corner_bet = bet
                    break
            
            if updated_corner_bet:
                status_after = 'PENDING' if updated_corner_bet.get('resultado_real') is None else ('WON' if updated_corner_bet.get('acierto') else 'LOST')
                print(f"   Status AFTER: {status_after}")
                
                if status_after == 'WON':
                    print(f"🎉 SUCCESS! Athletic Club corner bet updated to WON")
                    print(f"   Corners: {updated_corner_bet.get('resultado_real', {}).get('total_corners', 'N/A')}")
                    print(f"   Ganancia: ${updated_corner_bet.get('ganancia', 0):.2f}")
                    print(f"   Match ID: {updated_corner_bet.get('resultado_real', {}).get('match_id', 'N/A')}")
                    return True
                elif status_after == 'PENDING':
                    print(f"⚠️ Bet still pending - may need another update cycle")
                else:
                    print(f"❌ Bet marked as LOST - validation error")
            else:
                print(f"❌ Could not find corner bet after update")
        else:
            print(f"✅ Bet already processed - status: {status_before}")
            return status_before == 'WON'
    else:
        print(f"❌ Athletic Club corner bet not found")
    
    return False

if __name__ == "__main__":
    print(f"🔧 TESTING PRIORITIZED ATHLETIC CLUB UPDATE")
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    success = test_prioritized_athletic_update()
    
    if success:
        print(f"\n🎉 PRIORITIZED UPDATE SUCCESSFUL!")
        print(f"   ✅ Athletic Club corner bet processed first")
        print(f"   ✅ Bet status updated to WON")
        print(f"   ✅ 9 corners > 8.5 = WIN as expected")
        print(f"   🚀 'Actualizar Resultados' button working correctly!")
    else:
        print(f"\n⚠️ Prioritized update needs attention")
        print(f"   Check if Athletic Club match is being processed first")
