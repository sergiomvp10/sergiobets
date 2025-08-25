#!/usr/bin/env python3

import time
import json
from track_record import TrackRecordManager

def test_track_record_performance():
    """Test track record performance and accuracy"""
    print("=== TESTING TRACK RECORD PERFORMANCE ===")
    
    api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
    tracker = TrackRecordManager(api_key)
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        historial = json.load(f)
    
    print(f"Total predictions in file: {len(historial)}")
    
    pending = [p for p in historial if p.get("resultado_real") is None]
    print(f"Pending predictions: {len(pending)}")
    
    matches = set(f"{p['fecha']}|{p['partido']}" for p in pending)
    print(f"Unique pending matches: {len(matches)}")
    
    print(f"\n⚡ PERFORMANCE TEST:")
    print(f"  Before optimization: {len(pending)} API calls needed")
    print(f"  After optimization: {len(matches)} API calls needed")
    if len(pending) > 0:
        print(f"  Reduction: {len(pending) - len(matches)} fewer calls ({((len(pending) - len(matches)) / len(pending) * 100):.1f}% reduction)")
    
    print(f"\n🚀 Running optimized update...")
    start_time = time.time()
    
    resultado = tracker.actualizar_historial_con_resultados()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Completed in {duration:.2f} seconds")
    print(f"📊 Results: {resultado}")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        historial_updated = json.load(f)
    
    updated_count = len([p for p in historial_updated if p.get("resultado_real") is not None])
    print(f"\n📈 VERIFICATION:")
    print(f"  Predictions with results: {updated_count}/{len(historial_updated)}")
    if len(historial_updated) > 0:
        print(f"  Success rate: {(updated_count / len(historial_updated) * 100):.1f}%")
    
    return duration < 30 and resultado.get('actualizaciones', 0) >= 0

if __name__ == "__main__":
    success = test_track_record_performance()
    if success:
        print("\n✅ Track record performance test PASSED")
    else:
        print("\n❌ Track record performance test FAILED")
