#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from track_record import VALID_MATCH_STATUSES, INVALID_MATCH_STATUSES

def check_historical_data():
    """Check the current state of historical predictions"""
    print("=== CHECKING HISTORICAL PREDICTIONS DATA ===")
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"Total predictions in history: {len(historial)}")
        
        resolved_count = 0
        pending_count = 0
        invalid_status_count = 0
        
        for i, pred in enumerate(historial):
            resultado_real = pred.get("resultado_real")
            
            if resultado_real is None:
                pending_count += 1
                if i < 3:  # Show first 3 examples
                    print(f"  Pending: {pred.get('partido', 'Unknown')} ({pred.get('fecha', 'Unknown')})")
            else:
                status = resultado_real.get("status", "").lower().strip()
                if status in VALID_MATCH_STATUSES:
                    resolved_count += 1
                    if resolved_count <= 3:  # Show first 3 examples
                        acierto = pred.get("acierto", "Unknown")
                        print(f"  Resolved: {pred.get('partido', 'Unknown')} - {'WIN' if acierto else 'LOSS'} (Status: {status})")
                else:
                    invalid_status_count += 1
                    print(f"  ⚠️ Invalid status: {pred.get('partido', 'Unknown')} - Status: {status}")
        
        print(f"\n=== SUMMARY ===")
        print(f"✅ Resolved (valid status): {resolved_count}")
        print(f"⏳ Pending (no result): {pending_count}")
        print(f"❌ Invalid status: {invalid_status_count}")
        
        print(f"\n=== STATUS FILTERING RULES ===")
        print(f"Valid statuses: {VALID_MATCH_STATUSES}")
        print(f"Invalid statuses: {INVALID_MATCH_STATUSES}")
        
        return {
            "total": len(historial),
            "resolved": resolved_count,
            "pending": pending_count,
            "invalid": invalid_status_count
        }
        
    except FileNotFoundError:
        print("❌ historial_predicciones.json not found")
        return None
    except Exception as e:
        print(f"❌ Error checking historical data: {e}")
        return None

if __name__ == "__main__":
    result = check_historical_data()
    if result:
        print(f"\n✅ Historical data check completed")
    else:
        print(f"\n❌ Historical data check failed")
