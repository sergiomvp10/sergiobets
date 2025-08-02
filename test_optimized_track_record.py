#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from track_record import TrackRecordManager
import json

def test_optimized_track_record():
    """Test the optimized track record system"""
    print("=== TESTING OPTIMIZED TRACK RECORD SYSTEM ===")
    
    try:
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"Total predictions: {len(historial)}")
        
        matches = set(p["partido"] for p in historial if p.get("resultado_real") is None)
        print(f"Unique pending matches: {len(matches)}")
        
        print(f"\n🚀 OPTIMIZATION TEST:")
        print(f"  Before: {len([p for p in historial if p.get('resultado_real') is None])} API calls")
        print(f"  After: {len(matches)} API calls")
        print(f"  Reduction: {len([p for p in historial if p.get('resultado_real') is None]) - len(matches)} fewer calls")
        
        print(f"\n⚡ Testing optimized update process...")
        resultado = tracker.actualizar_historial_con_resultados()
        
        if "error" in resultado:
            print(f"❌ Error: {resultado['error']}")
            return False
        else:
            print(f"✅ Success!")
            print(f"  Predicciones actualizadas: {resultado['actualizaciones']}")
            print(f"  Matches procesados: {resultado.get('matches_procesados', 0)}")
            print(f"  Matches incompletos: {resultado.get('partidos_incompletos', 0)}")
            print(f"  Total procesadas: {resultado['total_procesadas']}")
            
            return True
        
    except Exception as e:
        print(f"❌ Error in optimization test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimized_track_record()
    if success:
        print("\n✅ Optimized track record test passed")
    else:
        print("\n❌ Optimized track record test failed")
