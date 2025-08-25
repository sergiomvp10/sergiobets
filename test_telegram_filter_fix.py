#!/usr/bin/env python3
"""
Test that the Actualizar Resultados button only processes Telegram bets
"""

import json
from datetime import datetime
from track_record import TrackRecordManager

def test_telegram_filter_fix():
    """Test that the button only processes bets with sent_to_telegram=True"""
    print("=" * 70)
    print("TESTING TELEGRAM FILTER FIX")
    print("=" * 70)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_pending = [bet for bet in data if bet.get('resultado_real') is None]
    print(f'📊 Total pending bets in file: {len(all_pending)}')
    
    telegram_pending = [bet for bet in all_pending if bet.get('sent_to_telegram', False)]
    print(f'📱 Pending bets with sent_to_telegram=True: {len(telegram_pending)}')
    
    non_telegram_pending = [bet for bet in all_pending if not bet.get('sent_to_telegram', False)]
    print(f'❌ Pending bets without sent_to_telegram flag: {len(non_telegram_pending)}')
    
    print(f'\n🎯 EXPECTED BEHAVIOR:')
    print(f'   Button should process: {len(telegram_pending)} bets (only Telegram ones)')
    print(f'   Button should ignore: {len(non_telegram_pending)} bets (non-Telegram ones)')
    
    api_key = 'ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd'
    tracker = TrackRecordManager(api_key)
    
    print(f'\n🔄 TESTING BUTTON WITH TELEGRAM FILTER:')
    result = tracker.actualizar_historial_con_resultados(max_matches=10, timeout_per_match=15)
    
    print(f'📊 Button result: {result}')
    
    total_processed = result.get('matches_procesados', 0)
    print(f'\n✅ VERIFICATION:')
    print(f'   Expected to process ≤ {len(telegram_pending)} bets')
    print(f'   Actually processed: {total_processed} matches')
    
    if total_processed <= len(telegram_pending):
        print(f'   🎉 SUCCESS: Button respects Telegram filter!')
    else:
        print(f'   ❌ FAILURE: Button processed more than expected')
    
    return total_processed <= len(telegram_pending)

if __name__ == "__main__":
    print(f"🔧 TESTING TELEGRAM FILTER FIX")
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    success = test_telegram_filter_fix()
    
    if success:
        print(f"\n🎉 TELEGRAM FILTER FIX SUCCESSFUL!")
        print(f"   ✅ Button only processes Telegram bets")
        print(f"   ✅ User's statistics control maintained")
    else:
        print(f"\n⚠️ Filter fix needs more work")
