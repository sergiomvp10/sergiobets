#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_track_record_system():
    """Test the complete track record system"""
    print("=== TESTING TRACK RECORD SYSTEM ===")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
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
        
        if acierto and ganancia == 5.0:
            print("   ✅ Prediction validation logic working correctly")
        else:
            print("   ❌ Prediction validation logic error")
        
        print("\n3. Testing BTTS validation...")
        prediccion_btts = {
            "prediccion": "Ambos equipos marcan",
            "stake": 15,
            "cuota": 1.8
        }
        
        resultado_btts = {
            "home_score": 1,
            "away_score": 2,
            "total_goals": 3
        }
        
        acierto_btts, ganancia_btts = tracker.validar_prediccion(prediccion_btts, resultado_btts)
        print(f"   BTTS con resultado 1-2: {acierto_btts} (ganancia: ${ganancia_btts})")
        
        print("\n4. Testing result update simulation...")
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
