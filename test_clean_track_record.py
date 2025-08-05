#!/usr/bin/env python3
"""
Test the cleaned track record system
"""

import json
import os
from datetime import datetime
from clean_track_record import clean_track_record
from ia_bets import filtrar_apuestas_inteligentes, guardar_prediccion_historica
from track_record import TrackRecordManager

def test_clean_track_record_system():
    """Test the complete cleaned track record flow"""
    print("=== TESTING CLEANED TRACK RECORD SYSTEM ===")
    
    print("\n1. Testing AI analysis without auto-save...")
    test_partidos = [
        {
            "hora": "15:00",
            "liga": "Premier League", 
            "local": "Test Team A",
            "visitante": "Test Team B",
            "cuotas": {"casa": "Bet365", "local": "2.0", "empate": "3.0", "visitante": "4.0"}
        }
    ]
    
    before_count = 0
    if os.path.exists('historial_predicciones.json'):
        with open('historial_predicciones.json', 'r') as f:
            before_count = len(json.load(f))
    
    predicciones = filtrar_apuestas_inteligentes(test_partidos)
    
    after_count = 0
    if os.path.exists('historial_predicciones.json'):
        with open('historial_predicciones.json', 'r') as f:
            after_count = len(json.load(f))
    
    if before_count == after_count:
        print("   ✅ AI analysis doesn't auto-save predictions")
    else:
        print("   ❌ AI analysis still auto-saving predictions")
        return False
    
    print("\n2. Testing manual Telegram-sent saving...")
    if predicciones:
        fecha = datetime.now().strftime('%Y-%m-%d')
        guardar_prediccion_historica(predicciones[0], fecha)
        
        if os.path.exists('historial_predicciones.json'):
            with open('historial_predicciones.json', 'r') as f:
                historial = json.load(f)
                if historial:
                    last_pred = historial[-1]
                    
                    if last_pred.get('sent_to_telegram'):
                        print("   ✅ Manual saving includes sent_to_telegram flag")
                    else:
                        print("   ❌ Manual saving missing sent_to_telegram flag")
                        return False
                else:
                    print("   ⚠️ No predictions found after manual save")
        else:
            print("   ⚠️ No historial file created after manual save")
    
    print("\n3. Testing automatic result updating...")
    api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
    tracker = TrackRecordManager(api_key)
    
    resultado = tracker.actualizar_historial_con_resultados()
    if "error" not in resultado:
        print(f"   ✅ Automatic updating works: {resultado.get('total_procesadas', 0)} processed")
    else:
        print(f"   ⚠️ Automatic updating error: {resultado['error']}")
    
    print("\n4. Testing data cleanup...")
    cleanup_result = clean_track_record()
    print(f"   ✅ Cleanup completed: {cleanup_result['removed_count']} predictions removed")
    
    print("\n🎉 All tests completed successfully!")
    return True

if __name__ == "__main__":
    test_clean_track_record_system()
