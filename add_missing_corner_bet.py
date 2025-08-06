#!/usr/bin/env python3
"""
Add the missing Athletic Club vs Atletico GO corner bet that should exist
"""

import json
from datetime import datetime

def add_missing_corner_bet():
    """Add the Athletic Club vs Atletico GO corner bet that the user mentioned"""
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    backup_filename = f'historial_predicciones_backup_missing_bet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup created: {backup_filename}")
    
    existing_corner_bet = None
    for bet in data:
        if ('Athletic Club' in bet.get('partido', '') and 
            'Atletico GO' in bet.get('partido', '') and 
            'corners' in bet.get('prediccion', '').lower()):
            existing_corner_bet = bet
            break
    
    if existing_corner_bet:
        print(f"✅ Corner bet already exists: {existing_corner_bet['prediccion']}")
        print(f"   Status: {'PENDING' if existing_corner_bet.get('resultado_real') is None else ('WON' if existing_corner_bet.get('acierto') else 'LOST')}")
        return
    
    missing_bet = {
        "fecha": "2025-08-04",  # Correct date from Flashscore
        "partido": "Athletic Club vs Atlético GO",
        "prediccion": "Más de 8.5 corners",
        "cuota": 1.50,
        "stake": 10.0,
        "ganancia_potencial": 15.0,
        "timestamp": "2025-08-04T20:00:00",
        "resultado_real": None,  # Pending status
        "acierto": None,
        "ganancia": None
    }
    
    data.append(missing_bet)
    
    with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Added missing corner bet:")
    print(f"   Date: {missing_bet['fecha']}")
    print(f"   Match: {missing_bet['partido']}")
    print(f"   Bet: {missing_bet['prediccion']}")
    print(f"   Status: PENDING (ready for update)")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    
    corner_bets = [bet for bet in updated_data if 
                   'Athletic Club' in bet.get('partido', '') and 
                   'Atletico GO' in bet.get('partido', '') and 
                   'corners' in bet.get('prediccion', '').lower()]
    
    print(f"✅ Verification: Found {len(corner_bets)} Athletic Club vs Atletico GO corner bet(s)")

if __name__ == "__main__":
    print("🔧 ADDING MISSING ATHLETIC CLUB vs ATLETICO GO CORNER BET")
    add_missing_corner_bet()
    print("✅ Ready to test 'Actualizar Resultados' button")
