#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from track_record import TrackRecordManager, VALID_MATCH_STATUSES, INVALID_MATCH_STATUSES

def test_status_filtering():
    """Test the enhanced status filtering logic"""
    print("=== TESTING ENHANCED STATUS FILTERING ===")
    
    try:
        api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
        tracker = TrackRecordManager(api_key)
        
        print("1. Testing valid status constants...")
        print(f"   Valid statuses: {VALID_MATCH_STATUSES}")
        print(f"   Invalid statuses: {INVALID_MATCH_STATUSES}")
        
        print("\n2. Testing historical data correction...")
        correccion_result = tracker.corregir_datos_historicos()
        print(f"   Correcciones realizadas: {correccion_result.get('correcciones', 0)}")
        print(f"   Total predicciones: {correccion_result.get('total_predicciones', 0)}")
        
        print("\n3. Testing result update with status filtering...")
        update_result = tracker.actualizar_historial_con_resultados()
        print(f"   Actualizaciones: {update_result.get('actualizaciones', 0)}")
        print(f"   Partidos incompletos: {update_result.get('partidos_incompletos', 0)}")
        print(f"   Errores: {update_result.get('errores', 0)}")
        
        print("\n4. Testing metrics calculation...")
        metricas = tracker.calcular_metricas_rendimiento()
        if "error" not in metricas:
            print(f"   Predicciones resueltas: {metricas.get('predicciones_resueltas', 0)}")
            print(f"   Total predicciones: {metricas.get('total_predicciones', 0)}")
        
        print("\n✅ Status filtering test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in status filtering test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_status_filtering()
    if success:
        print("✅ Status filtering test passed")
    else:
        print("❌ Status filtering test failed")
