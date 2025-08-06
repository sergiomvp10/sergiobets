#!/usr/bin/env python3
"""
Check Athletic Club bets status in historial_predicciones.json
"""

import json

def check_athletic_bets():
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('=== ALL ATHLETIC CLUB BETS ===')
    athletic_bets = [bet for bet in data if 'Athletic Club' in bet.get('partido', '') or 'Atletico GO' in bet.get('partido', '')]
    for i, bet in enumerate(athletic_bets):
        status = 'PENDING' if bet.get('resultado_real') is None else ('WON' if bet.get('acierto') else 'LOST')
        print(f'{i+1}. {bet.get("fecha")} | {bet.get("partido")} | {bet.get("prediccion")} | {status}')

    print('\n=== CORNER BETS ===')
    corner_bets = [bet for bet in data if 'corners' in bet.get('prediccion', '').lower()]
    for i, bet in enumerate(corner_bets):
        status = 'PENDING' if bet.get('resultado_real') is None else ('WON' if bet.get('acierto') else 'LOST')
        print(f'{i+1}. {bet.get("fecha")} | {bet.get("partido")} | {bet.get("prediccion")} | {status}')

    print('\n=== SPECIFIC ATHLETIC CLUB vs ATLETICO GO BETS ===')
    specific_bets = [bet for bet in data if 'Athletic Club' in bet.get('partido', '') and 'Atletico GO' in bet.get('partido', '')]
    for i, bet in enumerate(specific_bets):
        status = 'PENDING' if bet.get('resultado_real') is None else ('WON' if bet.get('acierto') else 'LOST')
        print(f'{i+1}. {bet.get("fecha")} | {bet.get("partido")} | {bet.get("prediccion")} | {status}')
        if bet.get('resultado_real'):
            print(f'   Match ID: {bet.get("resultado_real", {}).get("match_id", "N/A")}')
            print(f'   Corners: {bet.get("resultado_real", {}).get("total_corners", "N/A")}')

if __name__ == "__main__":
    check_athletic_bets()
