#!/usr/bin/env python3
"""
Clean track record to remove predictions not sent to Telegram
"""

import json
import shutil
from datetime import datetime
from json_storage import cargar_json, guardar_json

def clean_track_record():
    """Clean historical predictions to keep only Telegram-sent ones"""
    
    backup_file = f"historial_predicciones_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        shutil.copy("historial_predicciones.json", backup_file)
        print(f"✅ Backup created: {backup_file}")
    except FileNotFoundError:
        print("⚠️ No existing historial_predicciones.json found")
        return {
            "original_count": 0,
            "cleaned_count": 0,
            "removed_count": 0,
            "backup_file": None
        }
    
    historial = cargar_json("historial_predicciones.json") or []
    print(f"📊 Total predictions before cleanup: {len(historial)}")
    
    cleaned_historial = []
    
    for pred in historial:
        if pred.get("resultado_real") is not None:
            pred["sent_to_telegram"] = True
            cleaned_historial.append(pred)
        elif pred.get("timestamp"):
            try:
                pred_date = datetime.fromisoformat(pred["timestamp"].replace('Z', '+00:00'))
                days_old = (datetime.now() - pred_date).days
                if days_old <= 7:
                    pred["sent_to_telegram"] = True
                    cleaned_historial.append(pred)
            except:
                pass
    
    guardar_json("historial_predicciones.json", cleaned_historial)
    
    print(f"✅ Cleaned predictions: {len(cleaned_historial)}")
    print(f"🗑️ Removed predictions: {len(historial) - len(cleaned_historial)}")
    
    return {
        "original_count": len(historial),
        "cleaned_count": len(cleaned_historial),
        "removed_count": len(historial) - len(cleaned_historial),
        "backup_file": backup_file
    }

if __name__ == "__main__":
    result = clean_track_record()
    print(f"\n📋 Cleanup Summary:")
    print(f"   Original: {result['original_count']}")
    print(f"   Cleaned: {result['cleaned_count']}")
    print(f"   Removed: {result['removed_count']}")
    print(f"   Backup: {result['backup_file']}")
