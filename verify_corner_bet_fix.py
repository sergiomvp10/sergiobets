#!/usr/bin/env python3
"""
Verification script to confirm the Athletic Club vs Atlético GO corner bet fix
"""

import json

def verify_corner_bet_fix():
    """Verify that the corner bet has been fixed correctly"""
    print("=== VERIFYING CORNER BET FIX ===")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corner_bet_found = False
    for i, pred in enumerate(data):
        if ('Athletic Club' in pred.get('partido', '') and 
            'Atlético GO' in pred.get('partido', '') and
            'corner' in pred.get('prediccion', '').lower()):
            
            corner_bet_found = True
            print(f"✅ Found corner bet at index {i}:")
            print(f"   Partido: {pred.get('partido')}")
            print(f"   Predicción: {pred.get('prediccion')}")
            print(f"   Fecha: {pred.get('fecha')}")
            print(f"   Acierto: {pred.get('acierto')}")
            print(f"   Ganancia: ${pred.get('ganancia')}")
            
            if pred.get('resultado_real'):
                corners = pred['resultado_real'].get('total_corners')
                print(f"   Total corners: {corners}")
                print(f"   Corner data available: {pred['resultado_real'].get('corner_data_available')}")
                
                if corners and corners > 8.5:
                    if pred.get('acierto') == True:
                        print(f"   ✅ CORRECT: {corners} corners > 8.5, bet marked as WIN")
                    else:
                        print(f"   ❌ ERROR: {corners} corners > 8.5, but bet marked as LOSS")
                else:
                    print(f"   ⚠️  WARNING: Corner data may be missing or insufficient")
            else:
                print(f"   ❌ ERROR: No resultado_real data found")
            break
    
    if not corner_bet_found:
        print("❌ ERROR: No corner bet found for Athletic Club vs Atlético GO")
        
        athletic_predictions = []
        for i, pred in enumerate(data):
            if ('Athletic Club' in pred.get('partido', '') and 
                'Atlético GO' in pred.get('partido', '')):
                athletic_predictions.append((i, pred))
        
        print(f"\nFound {len(athletic_predictions)} total predictions for Athletic Club vs Atlético GO:")
        for i, (idx, pred) in enumerate(athletic_predictions):
            print(f"  {i+1}. Index {idx}: {pred.get('prediccion')} - Status: {pred.get('acierto')}")
    
    total_corner_bets = sum(1 for pred in data if 'corner' in pred.get('prediccion', '').lower())
    print(f"\n📊 SUMMARY:")
    print(f"   Total corner bets in historical data: {total_corner_bets}")
    print(f"   Athletic Club vs Atlético GO corner bet: {'FOUND' if corner_bet_found else 'NOT FOUND'}")
    
    return corner_bet_found

if __name__ == "__main__":
    verify_corner_bet_fix()
