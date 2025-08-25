#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_track_record_system():
    """Test the complete track record system"""
    print("=== TESTING TRACK RECORD SYSTEM ===")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
        tracker = TrackRecordManager(api_key)
        
        print("1. Testing metrics calculation...")
        metricas = tracker.calcular_metricas_rendimiento()
        print(f"   Total predicciones: {metricas.get('total_predicciones', 0)}")
        print(f"   Predicciones resueltas: {metricas.get('predicciones_resueltas', 0)}")
        
        if metricas.get('predicciones_resueltas', 0) > 0:
            print(f"   Tasa de acierto: {metricas.get('tasa_acierto', 0):.1f}%")
            print(f"   ROI: {metricas.get('roi', 0):.2f}%")
        
        print("\n2. Testing prediction validation logic...")
        prediccion_test = {
            "prediccion": "Más de 2.5 goles",
            "stake": 10,
            "cuota": 1.5
        }
        
        resultado_test = {
            "total_goals": 3,
            "home_score": 2,
            "away_score": 1
        }
        
        acierto, ganancia = tracker.validar_prediccion(prediccion_test, resultado_test)
        print(f"   Predicción 'Más de 2.5 goles' con 3 goles: {acierto} (ganancia: ${ganancia})")
        
        print("\n3. Testing result update simulation...")
        resultado_update = tracker.actualizar_historial_con_resultados()
        print(f"   Resultado: {resultado_update}")
        
        print("\n✅ Track record system test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in track record test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_track_record_system()
    if success:
        print("✅ Track record test passed")
    else:
        print("❌ Track record test failed")
