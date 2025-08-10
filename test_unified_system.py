#!/usr/bin/env python3
"""
Test script for the unified BetGeniuX system
"""

import json
import os
from datetime import datetime

def test_unified_system():
    """Test the unified system functionality"""
    print("=" * 60)
    print("TESTING BETGENIUX UNIFIED SYSTEM")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    print("1. Checking unified file...")
    if os.path.exists('betgeniux_unified.py'):
        stat = os.stat('betgeniux_unified.py')
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"   ✅ betgeniux_unified.py: {size:,} bytes (modified: {modified})")
    else:
        print("   ❌ betgeniux_unified.py: NOT FOUND")
        return
    
    print("\n2. Testing bet categorization logic...")
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        pendientes = [p for p in historial if p.get("resultado_real") is None or p.get("acierto") is None]
        acertados = [p for p in historial if p.get("acierto") == True]
        fallados = [p for p in historial if p.get("acierto") == False]
        
        print(f"   ⏳ Pendientes: {len(pendientes)}")
        print(f"   ✅ Acertados: {len(acertados)}")
        print(f"   ❌ Fallados: {len(fallados)}")
        
        athletic_corner = None
        for bet in acertados:
            if 'Athletic Club' in bet.get('partido', '') and 'corner' in bet.get('prediccion', '').lower():
                athletic_corner = bet
                break
        
        if athletic_corner:
            print(f"   ✅ Athletic Club corner bet found in Acertados")
            print(f"      Partido: {athletic_corner.get('partido')}")
            print(f"      Predicción: {athletic_corner.get('prediccion')}")
            print(f"      Corners totales: {athletic_corner.get('resultado_real', {}).get('total_corners', 'N/A')}")
        else:
            print(f"   ❌ Athletic Club corner bet NOT found in Acertados")
        
    except Exception as e:
        print(f"   ❌ Error testing categorization: {e}")
    
    print("\n3. Testing sent_to_telegram field...")
    try:
        telegram_sent = [p for p in historial if p.get("sent_to_telegram") == True]
        telegram_none = [p for p in historial if p.get("sent_to_telegram") is None]
        telegram_false = [p for p in historial if p.get("sent_to_telegram") == False]
        
        print(f"   📱 Marked as sent to Telegram: {len(telegram_sent)}")
        print(f"   ⚪ sent_to_telegram is None: {len(telegram_none)}")
        print(f"   ❌ sent_to_telegram is False: {len(telegram_false)}")
        
        if len(telegram_sent) > 0:
            print(f"   ✅ sent_to_telegram field is working")
        else:
            print(f"   ⚠️  sent_to_telegram field needs implementation")
        
    except Exception as e:
        print(f"   ❌ Error testing sent_to_telegram: {e}")
    
    print("\n4. Testing handicap bet validation...")
    try:
        handicap_bets = []
        for pred in historial:
            bet_type = pred.get('prediccion', '').lower()
            if '+0.5' in bet_type or '-0.5' in bet_type:
                handicap_bets.append(pred)
        
        print(f"   🎯 Total handicap bets found: {len(handicap_bets)}")
        
        handicap_resolved = [h for h in handicap_bets if h.get('resultado_real') is not None]
        handicap_pending = [h for h in handicap_bets if h.get('resultado_real') is None]
        
        print(f"   ✅ Resolved handicap bets: {len(handicap_resolved)}")
        print(f"   ⏳ Pending handicap bets: {len(handicap_pending)}")
        
        if len(handicap_bets) > 0:
            sample_bet = handicap_bets[0]
            print(f"   📋 Sample handicap bet: {sample_bet.get('prediccion')}")
            print(f"      Status: {sample_bet.get('acierto')}")
        
    except Exception as e:
        print(f"   ❌ Error testing handicap bets: {e}")
    
    print("\n5. Testing imports...")
    try:
        import tkinter as tk
        print("   ✅ tkinter import successful")
        
        from track_record import TrackRecordManager
        print("   ✅ TrackRecordManager import successful")
        
        print("   ✅ All critical imports working")
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
    
    print("\n" + "=" * 60)
    print("UNIFIED SYSTEM TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_unified_system()
