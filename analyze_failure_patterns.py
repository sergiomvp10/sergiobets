#!/usr/bin/env python3
"""
Analyze failure patterns in SergioBets prediction system
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
import sys

def analyze_prediction_failures():
    """Analyze historical prediction data to identify failure patterns"""
    
    try:
        with open('historial_predicciones.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No historical data found")
        return
    
    print("📊 SERGIOBETS FAILURE ANALYSIS")
    print("=" * 60)
    
    total_predictions = len(data)
    successful = sum(1 for p in data if p.get('acierto', False))
    failed = total_predictions - successful
    
    print(f"📈 OVERALL PERFORMANCE:")
    print(f"   Total predictions: {total_predictions}")
    print(f"   Successful: {successful} ({successful/total_predictions*100:.1f}%)")
    print(f"   Failed: {failed} ({failed/total_predictions*100:.1f}%)")
    print()
    
    prediction_types = Counter()
    success_by_type = Counter()
    failure_reasons = defaultdict(list)
    
    for p in data:
        pred_type = p.get('prediccion', '').lower()
        
        if 'goles' in pred_type:
            if 'más de' in pred_type:
                category = 'Over Goals'
            else:
                category = 'Under Goals'
        elif 'corners' in pred_type:
            if 'más de' in pred_type:
                category = 'Over Corners'
            else:
                category = 'Under Corners'
        elif 'tarjetas' in pred_type:
            category = 'Cards'
        elif 'marcan' in pred_type or 'btts' in pred_type:
            category = 'BTTS'
        elif any(x in pred_type for x in ['+0.5', '-0.5', '+1.5', '-1.5']):
            category = 'Handicap'
        elif any(x in pred_type for x in ['victoria', 'local', 'visitante', 'empate']):
            category = '1X2'
        else:
            category = 'Other'
        
        prediction_types[category] += 1
        
        if p.get('acierto', False):
            success_by_type[category] += 1
        else:
            resultado_real = p.get('resultado_real', {})
            if not resultado_real:
                failure_reasons[category].append("No match data")
            elif resultado_real.get('status', '').lower() not in ['complete', 'finished', 'ft']:
                failure_reasons[category].append("Match not finished")
            elif 'corners' in pred_type and resultado_real.get('total_corners', 0) == 0:
                failure_reasons[category].append("Missing corner data")
            else:
                failure_reasons[category].append("Prediction incorrect")
    
    print("📈 SUCCESS RATE BY MARKET TYPE:")
    for category in sorted(prediction_types.keys()):
        success_rate = (success_by_type[category] / prediction_types[category]) * 100
        print(f"   {category}: {success_by_type[category]}/{prediction_types[category]} ({success_rate:.1f}%)")
    print()
    
    high_value_bets = [p for p in data if p.get('valor_esperado', 0) > 0.1]
    medium_value_bets = [p for p in data if 0.0 <= p.get('valor_esperado', 0) <= 0.1]
    low_value_bets = [p for p in data if p.get('valor_esperado', 0) < 0.0]
    
    print("💰 VALUE BETTING PERFORMANCE:")
    if high_value_bets:
        high_success = sum(1 for p in high_value_bets if p.get('acierto', False))
        print(f"   High value bets (>10% EV): {high_success}/{len(high_value_bets)} ({high_success/len(high_value_bets)*100:.1f}%)")
    
    if medium_value_bets:
        med_success = sum(1 for p in medium_value_bets if p.get('acierto', False))
        print(f"   Medium value bets (0-10% EV): {med_success}/{len(medium_value_bets)} ({med_success/len(medium_value_bets)*100:.1f}%)")
    
    if low_value_bets:
        low_success = sum(1 for p in low_value_bets if p.get('acierto', False))
        print(f"   Negative value bets (<0% EV): {low_success}/{len(low_value_bets)} ({low_success/len(low_value_bets)*100:.1f}%)")
    print()
    
    print("🔍 FAILURE PATTERNS BY MARKET:")
    for category, reasons in failure_reasons.items():
        if reasons:
            reason_counts = Counter(reasons)
            print(f"   {category}:")
            for reason, count in reason_counts.most_common():
                print(f"     - {reason}: {count} times")
    print()
    
    recent_predictions = [p for p in data if p.get('fecha', '') >= '2025-08-01']
    if recent_predictions:
        recent_success = sum(1 for p in recent_predictions if p.get('acierto', False))
        print(f"📅 RECENT PERFORMANCE (Aug 2025):")
        print(f"   Recent predictions: {len(recent_predictions)}")
        print(f"   Recent success rate: {recent_success/len(recent_predictions)*100:.1f}%")
    
    print("\n🎯 IMPROVEMENT OPPORTUNITIES:")
    
    corner_bets = [p for p in data if 'corners' in p.get('prediccion', '').lower()]
    corner_data_issues = sum(1 for p in corner_bets 
                           if p.get('resultado_real') is not None 
                           and p.get('resultado_real', {}).get('total_corners', 0) == 0 
                           and not p.get('acierto', False))
    
    if corner_data_issues > 0:
        print(f"   1. Corner data validation: {corner_data_issues} corner bets failed due to missing data")
    
    negative_ev_bets = len(low_value_bets)
    if negative_ev_bets > 0:
        print(f"   2. Value betting threshold: {negative_ev_bets} bets had negative expected value")
    
    unfinished_matches = sum(1 for p in data 
                           if p.get('resultado_real') is not None
                           and p.get('resultado_real', {}).get('status', '').lower() 
                           not in ['complete', 'finished', 'ft'] 
                           and not p.get('acierto', False))
    
    if unfinished_matches > 0:
        print(f"   3. Match status validation: {unfinished_matches} predictions marked failed for unfinished matches")

if __name__ == "__main__":
    analyze_prediction_failures()
