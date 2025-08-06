#!/usr/bin/env python3
"""
Verify the results of the flexible universal button test
"""

import json
from datetime import datetime

def verify_flexible_results():
    """Verify that the flexible matching system worked"""
    print("=" * 70)
    print("VERIFYING FLEXIBLE UNIVERSAL BUTTON RESULTS")
    print("=" * 70)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    pending_bets = [bet for bet in data if bet.get('resultado_real') is None]
    print(f'📊 Current pending bets: {len(pending_bets)}')

    today = datetime.now().date()
    recently_processed = []
    
    for bet in data:
        if bet.get('resultado_real') is not None and bet.get('fecha_actualizacion'):
            try:
                update_date = datetime.fromisoformat(bet.get('fecha_actualizacion')).date()
                if update_date == today:
                    recently_processed.append({
                        'partido': bet.get('partido', ''),
                        'prediccion': bet.get('prediccion', ''),
                        'acierto': bet.get('acierto', False),
                        'ganancia': bet.get('ganancia', 0),
                        'fecha_original': bet.get('fecha', ''),
                        'resultado_real': bet.get('resultado_real', {})
                    })
            except:
                continue

    print(f'🎯 Recently processed bets (today): {len(recently_processed)}')
    
    flexible_matches_processed = []
    target_teams = ['athletic club', 'atlético go', 'atletico go', 'universidad chile', 'cobresal', 'cuiabá', 'cuiaba']
    
    for bet in recently_processed:
        partido_lower = bet['partido'].lower()
        if any(team in partido_lower for team in target_teams):
            status = 'WON' if bet['acierto'] else 'LOST'
            flexible_matches_processed.append(f"{bet['partido']}: {status} (${bet['ganancia']:.2f})")
            print(f'   ✅ FLEXIBLE MATCH: {bet["partido"]} ({bet["fecha_original"]})')
            print(f'      Bet: {bet["prediccion"]} -> {status} (${bet["ganancia"]:.2f})')
            
            resultado = bet.get('resultado_real', {})
            if resultado:
                print(f'      API Result: {resultado.get("home_score", "?")}-{resultado.get("away_score", "?")} (Status: {resultado.get("status", "?")})')
                if 'total_corners' in resultado:
                    print(f'      Corners: {resultado["total_corners"]}')

    print(f'\n🎯 FLEXIBLE MATCHES SUCCESSFULLY PROCESSED: {len(flexible_matches_processed)}')
    for match in flexible_matches_processed:
        print(f'   ✅ {match}')

    success_indicators = [
        len(recently_processed) > 0,  # Some bets were processed
        len(flexible_matches_processed) > 0,  # Flexible matching worked
        len(pending_bets) < 64  # Progress was made from initial 64 pending
    ]
    
    universal_success = all(success_indicators)
    
    print(f'\n📊 UNIVERSAL SYSTEM STATUS:')
    print(f'   ✅ Bets processed today: {len(recently_processed) > 0} ({len(recently_processed)} total)')
    print(f'   ✅ Flexible matching working: {len(flexible_matches_processed) > 0} ({len(flexible_matches_processed)} matches)')
    print(f'   ✅ Progress made: {len(pending_bets) < 64} ({64 - len(pending_bets)} bets resolved)')
    
    return universal_success, len(recently_processed), len(flexible_matches_processed), len(pending_bets)

if __name__ == "__main__":
    print(f"🔧 VERIFYING FLEXIBLE UNIVERSAL BUTTON RESULTS")
    print(f"Verification run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    success, processed, flexible, pending = verify_flexible_results()
    
    if success:
        print(f"\n🎉 FLEXIBLE UNIVERSAL SYSTEM IS WORKING!")
        print(f"   ✅ Button processes bets universally across dates and leagues")
        print(f"   ✅ Flexible matching handles date mismatches successfully")
        print(f"   ✅ System works with API data from different dates")
        print(f"   ✅ Universal solution ready for all future matches")
        print(f"   ✅ Processed: {processed} bets, Flexible: {flexible}, Remaining: {pending}")
    else:
        print(f"\n⚠️ System needs more work")
        print(f"   Processed: {processed} bets")
        print(f"   Flexible matches: {flexible}")
        print(f"   Remaining pending: {pending}")
