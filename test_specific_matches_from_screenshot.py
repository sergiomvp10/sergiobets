#!/usr/bin/env python3
"""
Test specific matches from user's screenshot to verify they get processed
"""

import json
from datetime import datetime
from track_record import TrackRecordManager

def test_specific_matches():
    """Test the specific matches from user's screenshot"""
    print("=" * 70)
    print("TESTING SPECIFIC MATCHES FROM USER SCREENSHOT")
    print("=" * 70)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    target_matches = ['Athletic Club vs Atlético GO', 'Deportivo Cali vs Llaneros', 'Independiente Medellín vs Millonarios', 'Atlético PR vs Paysandu']
    
    print('Testing specific matches from user screenshot...')
    result = tracker.actualizar_historial_con_resultados(max_matches=10, timeout_per_match=15)
    print(f'Result: {result}')
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for bet in data:
        partido = bet.get('partido', '')
        for target in target_matches:
            if any(team.strip() in partido for team in target.split(' vs ')):
                status = 'PENDING' if bet.get('resultado_real') is None else ('WON' if bet.get('acierto') else 'LOST')
                print(f'{partido}: {status}')
                break

if __name__ == "__main__":
    test_specific_matches()
