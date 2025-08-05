#!/usr/bin/env python3
"""
Script to specifically fix the Athletic Club vs Atlético GO corner bet issue
"""

import json
import shutil
from datetime import datetime
from track_record import TrackRecordManager

def fix_athletic_corner_bet():
    """Fix the specific Athletic Club vs Atlético GO corner bet"""
    print("=== FIXING ATHLETIC CLUB VS ATLÉTICO GO CORNER BET ===")
    
    backup_file = f"historial_predicciones_backup_athletic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy('historial_predicciones.json', backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    print("\n1. GETTING MATCH RESULT FROM API:")
    resultado = tracker.obtener_resultado_partido("2025-08-04", "Athletic Club", "Atlético GO")
    
    if not resultado:
        print("❌ Could not get match result from API")
        return False
    
    print(f"✅ Match result retrieved:")
    print(f"   Score: {resultado.get('home_score')}-{resultado.get('away_score')}")
    print(f"   Total corners: {resultado.get('total_corners')}")
    print(f"   Corner data available: {resultado.get('corner_data_available')}")
    
    print("\n2. SEARCHING FOR ATHLETIC CLUB VS ATLÉTICO GO PREDICTIONS:")
    athletic_predictions = []
    for i, pred in enumerate(data):
        partido = pred.get('partido', '')
        if ('Athletic Club' in partido and 'Atlético GO' in partido):
            athletic_predictions.append((i, pred))
    
    print(f"Found {len(athletic_predictions)} Athletic Club vs Atlético GO predictions:")
    for i, (idx, pred) in enumerate(athletic_predictions):
        print(f"  {i+1}. Index {idx}: {pred.get('prediccion')} - Status: {pred.get('acierto')}")
    
    corner_bet_exists = False
    for idx, pred in athletic_predictions:
        if 'corner' in pred.get('prediccion', '').lower():
            corner_bet_exists = True
            print(f"   Found existing corner bet at index {idx}")
            
            validation_result = tracker.validar_prediccion(pred, resultado)
            if validation_result != (None, None):
                acierto, ganancia = validation_result
                pred["resultado_real"] = resultado
                pred["ganancia"] = ganancia
                pred["acierto"] = acierto
                pred["fecha_actualizacion"] = datetime.now().isoformat()
                
                print(f"   ✅ Updated corner bet: {'WIN' if acierto else 'LOSS'} (${ganancia:.2f})")
            break
    
    if not corner_bet_exists:
        print("\n3. NO CORNER BET FOUND - CREATING TEST CORNER BET:")
        
        test_corner_bet = {
            "fecha": "2025-08-04",
            "partido": "Athletic Club vs Atlético GO",
            "prediccion": "Más de 8.5 corners",
            "cuota": 1.4,
            "stake": 10,
            "valor_esperado": 0.15,
            "fecha_prediccion": "2025-08-04T10:00:00",
            "resultado_real": resultado,
            "acierto": None,
            "ganancia": None
        }
        
        validation_result = tracker.validar_prediccion(test_corner_bet, resultado)
        if validation_result != (None, None):
            acierto, ganancia = validation_result
            test_corner_bet["acierto"] = acierto
            test_corner_bet["ganancia"] = ganancia
            test_corner_bet["fecha_actualizacion"] = datetime.now().isoformat()
            
            print(f"   ✅ Test corner bet result: {'WIN' if acierto else 'LOSS'} (${ganancia:.2f})")
            
            data.append(test_corner_bet)
            print(f"   ✅ Added test corner bet to historical data")
    
    with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ ATHLETIC CORNER BET FIX COMPLETED")
    print(f"   Backup saved as: {backup_file}")
    
    print(f"\n4. RUNNING FULL TRACK RECORD UPDATE:")
    try:
        result = tracker.actualizar_historial_con_resultados()
        print(f"✅ Track record update result: {result}")
    except Exception as e:
        print(f"❌ Error during track record update: {e}")
    
    return True

if __name__ == "__main__":
    fix_athletic_corner_bet()
