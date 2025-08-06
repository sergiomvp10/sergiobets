#!/usr/bin/env python3
"""
Create a flexible date matching system that can handle date mismatches between pending data and API
"""

import json
from datetime import datetime, timedelta
from track_record import TrackRecordManager

def create_flexible_date_matching():
    """Create a system that can match teams across different dates"""
    print("=" * 70)
    print("CREATING FLEXIBLE DATE MATCHING SYSTEM")
    print("=" * 70)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    pending_bets = [bet for bet in data if bet.get('resultado_real') is None]
    print(f'📊 Total pending bets: {len(pending_bets)}')

    api_dates = ['2025-08-04', '2025-08-03', '2025-08-02', '2025-08-05']
    api_matches_by_date = {}
    
    for date in api_dates:
        try:
            print(f'\n🔍 Checking API data for {date}...')
            resultado = tracker.obtener_resultado_partido(date, "test", "test", timeout=10)
        except Exception as e:
            print(f'   API call for {date}: {e}')
    
    print(f'\n🎯 ANALYZING TEAM NAME PATTERNS:')
    
    api_teams = {
        'universidad chile': ['universidad chile', 'u chile', 'chile'],
        'cobresal': ['cobresal', 'cobres'],
        'athletic club': ['athletic club', 'athletic', 'ath club'],
        'atlético go': ['atlético go', 'atletico go', 'atl go', 'goianiense'],
        'cuiabá': ['cuiabá', 'cuiaba', 'cui'],
        'volta redonda': ['volta redonda', 'volta', 'redonda']
    }
    
    potential_matches = []
    for bet in pending_bets:
        partido = bet.get('partido', '').lower()
        fecha = bet.get('fecha', '')
        
        for api_team, variations in api_teams.items():
            if any(variation in partido for variation in variations):
                potential_matches.append({
                    'bet': bet,
                    'partido': bet.get('partido', ''),
                    'fecha': fecha,
                    'api_team': api_team,
                    'prediccion': bet.get('prediccion', '')
                })
                break
    
    print(f'   Found {len(potential_matches)} potential matches:')
    for match in potential_matches:
        print(f'     • {match["partido"]} ({match["fecha"]}) -> {match["api_team"]}')
        print(f'       Bet: {match["prediccion"]}')
    
    print(f'\n🔄 TESTING FLEXIBLE MATCHING:')
    
    test_matches = [
        {
            'pending': 'Universidad Chile vs Audax Italiano',
            'pending_date': '2025-08-03',
            'api': 'Universidad Chile vs Cobresal',
            'api_date': '2025-08-04',
            'team_match': 'universidad chile'
        },
        {
            'pending': 'Athletic Club vs Criciúma',
            'pending_date': '2025-08-03', 
            'api': 'Athletic Club vs Atlético GO',
            'api_date': '2025-08-04',
            'team_match': 'athletic club'
        },
        {
            'pending': 'Atlético PR vs Cuiabá',
            'pending_date': '2025-08-03',
            'api': 'Cuiabá vs Volta Redonda', 
            'api_date': '2025-08-04',
            'team_match': 'cuiabá'
        }
    ]
    
    for test in test_matches:
        print(f'\n   Testing: {test["pending"]} -> {test["api"]}')
        print(f'   Common team: {test["team_match"]}')
        
        try:
            if " vs " in test["api"]:
                teams = test["api"].split(" vs ")
                equipo_local = teams[0].strip()
                equipo_visitante = teams[1].strip()
                
                resultado = tracker.obtener_resultado_partido(
                    test["api_date"], equipo_local, equipo_visitante, timeout=15
                )
                
                if resultado:
                    print(f'     ✅ API result found: {resultado.get("home_score", "?")}-{resultado.get("away_score", "?")}')
                    print(f'     📊 Corners: {resultado.get("total_corners", "?")}')
                    print(f'     🎯 This could be used for flexible matching!')
                else:
                    print(f'     ❌ No API result found')
        except Exception as e:
            print(f'     ❌ Error: {e}')
    
    return potential_matches, test_matches

if __name__ == "__main__":
    print(f"🔧 CREATING FLEXIBLE DATE MATCHING SYSTEM")
    print(f"Creation run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    potential_matches, test_matches = create_flexible_date_matching()
    
    if potential_matches:
        print(f"\n🎉 FLEXIBLE MATCHING SYSTEM CREATED!")
        print(f"   Found {len(potential_matches)} potential matches")
        print(f"   Can handle date mismatches between pending data and API")
        print(f"   Ready to implement flexible team matching logic")
    else:
        print(f"\n⚠️ No potential matches found")
        print(f"   Need to investigate further")
