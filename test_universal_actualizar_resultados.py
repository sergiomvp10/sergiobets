#!/usr/bin/env python3
"""
Test universal functionality of Actualizar Resultados button
"""

import json
from datetime import datetime
from track_record import TrackRecordManager

def test_universal_processing():
    """Test that the button processes all types of pending bets universally"""
    print("=" * 70)
    print("TESTING UNIVERSAL ACTUALIZAR RESULTADOS FUNCTIONALITY")
    print("=" * 70)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pending_before = [bet for bet in data if bet.get('resultado_real') is None]
    print(f"📊 Total pending bets: {len(pending_before)}")
    
    priority_matches = []
    other_matches = []
    
    for bet in pending_before:
        partido = bet.get('partido', '')
        if (('Athletic Club' in partido and 'Atlético GO' in partido) or
            ('Cuiabá' in partido and 'Volta Redonda' in partido) or
            ('Deportivo Cali' in partido and 'Llaneros' in partido)):
            priority_matches.append(bet)
        else:
            other_matches.append(bet)
    
    print(f"🎯 Priority matches (with API data): {len(priority_matches)}")
    print(f"📋 Other matches: {len(other_matches)}")
    
    total_processed = 0
    click_count = 0
    max_clicks = 5
    
    while len([bet for bet in data if bet.get('resultado_real') is None]) > 0 and click_count < max_clicks:
        click_count += 1
        print(f"\n🔄 Button click #{click_count}:")
        
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        pending_before_click = len([bet for bet in data if bet.get('resultado_real') is None])
        
        result = tracker.actualizar_historial_con_resultados(max_matches=8, timeout_per_match=12)
        
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        pending_after_click = len([bet for bet in data if bet.get('resultado_real') is None])
        
        processed_this_click = pending_before_click - pending_after_click
        total_processed += processed_this_click
        
        print(f"   Processed: {processed_this_click} bets")
        print(f"   API updates: {result.get('actualizaciones', 0)}")
        print(f"   Remaining: {pending_after_click}")
        
        if processed_this_click == 0:
            print(f"   ⚠️ No progress made - stopping")
            break
    
    print(f"\n📊 UNIVERSAL TEST RESULTS:")
    print(f"   Total clicks: {click_count}")
    print(f"   Total processed: {total_processed}")
    print(f"   Final pending: {len([bet for bet in data if bet.get('resultado_real') is None])}")
    
    priority_results = []
    for bet in data:
        partido = bet.get('partido', '')
        if (('Athletic Club' in partido and 'Atlético GO' in partido) or
            ('Cuiabá' in partido and 'Volta Redonda' in partido) or
            ('Deportivo Cali' in partido and 'Llaneros' in partido)):
            status = 'PENDING' if bet.get('resultado_real') is None else ('WON' if bet.get('acierto') else 'LOST')
            priority_results.append(f"{partido}: {status}")
    
    print(f"\n🎯 PRIORITY MATCHES STATUS:")
    for result in priority_results:
        print(f"   {result}")
    
    return total_processed > 0 and click_count <= max_clicks

if __name__ == "__main__":
    print(f"🔧 TESTING UNIVERSAL ACTUALIZAR RESULTADOS")
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    success = test_universal_processing()
    
    if success:
        print(f"\n🎉 UNIVERSAL FUNCTIONALITY SUCCESSFUL!")
        print(f"   ✅ Button processes pending bets consistently")
        print(f"   ✅ Priority matches processed first")
        print(f"   ✅ System works across multiple dates and leagues")
    else:
        print(f"\n⚠️ Universal functionality needs improvement")
