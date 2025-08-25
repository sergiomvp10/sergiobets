#!/usr/bin/env python3
"""
Final investigation to find the missing corner bet and fix API issues
"""

import json
from track_record import TrackRecordManager

def debug_final_investigation():
    """Final comprehensive debug to solve the corner bet issue"""
    print("=== FINAL INVESTIGATION: CORNER BET AND API ISSUES ===")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n1. SEARCHING FOR ALL CORNER BETS THAT COULD BE THE ONE IN GUI:")
    all_corner_bets = []
    for i, pred in enumerate(data):
        if 'corner' in pred.get('prediccion', '').lower():
            all_corner_bets.append((i, pred))
    
    print(f"Found {len(all_corner_bets)} total corner bets in historical data")
    
    potential_matches = []
    for i, (idx, bet) in enumerate(all_corner_bets):
        partido = bet.get('partido', '').lower()
        if ('athletic' in partido and 'atlético' in partido) or \
           ('athletic' in partido and 'atletico' in partido) or \
           ('atlético go' in partido) or ('atletico go' in partido):
            potential_matches.append((idx, bet))
    
    print(f"\nPotential matches for Athletic/Atlético GO corner bets: {len(potential_matches)}")
    for i, (idx, bet) in enumerate(potential_matches):
        print(f"  {i+1}. Index {idx}: {bet.get('partido')} - {bet.get('prediccion')} ({bet.get('fecha')})")
        if bet.get('resultado_real'):
            corners = bet['resultado_real'].get('total_corners', 'N/A')
            print(f"      Current corners: {corners}, Status: {bet.get('acierto')}")
    
    print("\n2. TESTING API WITH CORRECT PARAMETER ORDER:")
    api_key = 'ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd'
    tracker = TrackRecordManager(api_key)
    
    try:
        print("   Testing 2025-08-04 (Flashscore date):")
        resultado_04 = tracker.obtener_resultado_partido(
            "2025-08-04",  # fecha first
            "Athletic Club",  # equipo_local second
            "Atlético GO"  # equipo_visitante third
        )
        
        if resultado_04:
            print(f"   ✅ API found match for 2025-08-04:")
            print(f"      Score: {resultado_04.get('home_score')}-{resultado_04.get('away_score')}")
            print(f"      Total corners: {resultado_04.get('total_corners')}")
            print(f"      Corners home: {resultado_04.get('corners_home')}")
            print(f"      Corners away: {resultado_04.get('corners_away')}")
            print(f"      Status: {resultado_04.get('status')}")
            
            test_corner_bet = {
                'prediccion': 'Más de 8.5 corners',
                'stake': 10,
                'cuota': 1.4
            }
            
            validation_result = tracker.validar_prediccion(test_corner_bet, resultado_04)
            print(f"\n      Corner bet validation result: {validation_result}")
            
            if validation_result != (None, None):
                acierto, ganancia = validation_result
                print(f"      Result: {'WIN' if acierto else 'LOSS'} with gain/loss: {ganancia}")
                
                if resultado_04.get('total_corners', 0) > 8.5:
                    print(f"      ✅ CONFIRMED: {resultado_04.get('total_corners')} corners > 8.5, bet should WIN")
                else:
                    print(f"      ❌ {resultado_04.get('total_corners')} corners <= 8.5, bet should lose")
        else:
            print(f"   ❌ No API result found for 2025-08-04")
            
        print("\n   Testing 2025-08-03 (historical data date):")
        resultado_03 = tracker.obtener_resultado_partido(
            "2025-08-03",  # fecha first
            "Athletic Club",  # equipo_local second
            "Atlético GO"  # equipo_visitante third
        )
        
        if resultado_03:
            print(f"   ✅ API found match for 2025-08-03:")
            print(f"      Score: {resultado_03.get('home_score')}-{resultado_03.get('away_score')}")
            print(f"      Total corners: {resultado_03.get('total_corners')}")
            print(f"      Status: {resultado_03.get('status')}")
        else:
            print(f"   ❌ No API result found for 2025-08-03")
            
    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. CHECKING FOR CORNER BETS ON 2025-08-04:")
    corner_bets_04 = []
    for i, pred in enumerate(data):
        if ('corner' in pred.get('prediccion', '').lower() and 
            '2025-08-04' in pred.get('fecha', '')):
            corner_bets_04.append((i, pred))
    
    print(f"Found {len(corner_bets_04)} corner bets on 2025-08-04:")
    for i, (idx, bet) in enumerate(corner_bets_04):
        print(f"  {i+1}. Index {idx}: {bet.get('partido')} - {bet.get('prediccion')}")
    
    print(f"\n4. SUMMARY AND NEXT STEPS:")
    print(f"   - Historical data has {len(all_corner_bets)} corner bets total")
    print(f"   - Found {len(potential_matches)} potential Athletic/Atlético GO corner matches")
    print(f"   - Found {len(corner_bets_04)} corner bets on 2025-08-04")
    print(f"   - API parameter order issue identified and tested")
    
    if 'resultado_04' in locals() and resultado_04 and resultado_04.get('total_corners', 0) > 8.5:
        print(f"   ✅ CONFIRMED: Match had {resultado_04.get('total_corners')} corners, 'Más de 8.5 corners' should WIN")
    
    return potential_matches, locals().get('resultado_04')

if __name__ == "__main__":
    debug_final_investigation()
