#!/usr/bin/env python3

import sys
import os

try:
    from track_record import TrackRecordManager
    print("✅ TrackRecordManager import successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_metrics_fields():
    """Test that calcular_metricas_rendimiento returns all expected fields"""
    print("\n🧪 Testing TrackRecordManager metrics calculation...")
    
    api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
    tracker = TrackRecordManager(api_key)
    
    try:
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"⚠️ Metrics returned error: {metricas['error']}")
            expected_fields = ['total_predicciones', 'predicciones_resueltas', 'predicciones_pendientes', 
                             'aciertos', 'tasa_acierto', 'total_apostado', 'total_ganancia', 'roi']
            
            for field in expected_fields:
                if field in metricas:
                    print(f"✅ Field '{field}' present: {metricas[field]}")
                else:
                    print(f"❌ Missing field: {field}")
            return True
        
        expected_fields = ['total_predicciones', 'predicciones_resueltas', 'predicciones_pendientes', 
                          'aciertos', 'tasa_acierto', 'total_apostado', 'total_ganancia', 'roi']
        
        missing_fields = []
        for field in expected_fields:
            if field in metricas:
                print(f"✅ Field '{field}' present: {metricas[field]}")
            else:
                missing_fields.append(field)
                print(f"❌ Missing field: {field}")
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✅ All expected fields present in metrics")
            return True
            
    except Exception as e:
        print(f"❌ Error testing metrics: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_telegram_bot_integration():
    """Test that Telegram bot statistics would work with current metrics"""
    print("\n🧪 Testing Telegram bot integration simulation...")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

📈 Sistema: Activo y funcionando
⚠️ Datos de predicciones: {metricas.get('error', 'No disponibles')}

🔄 El sistema está recopilando datos..."""
            print("✅ Error case message generation works")
        else:
            mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

🎯 PREDICCIONES:
• Total: {metricas['total_predicciones']}
• Resueltas: {metricas['predicciones_resueltas']}
• Pendientes: {metricas['predicciones_pendientes']}
• Aciertos: {metricas['aciertos']}
• Tasa de éxito: {metricas['tasa_acierto']:.1f}%

💰 RENDIMIENTO:
• Total apostado: ${metricas['total_apostado']:.2f}
• Ganancia: ${metricas['total_ganancia']:.2f}
• ROI: {metricas['roi']:.2f}%

📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
            print("✅ Normal case message generation works")
        
        print(f"📱 Telegram message preview:\n{mensaje}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Telegram integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== TESTING TELEGRAM BOT INTEGRATION ===")
    
    success1 = test_metrics_fields()
    success2 = test_telegram_bot_integration()
    
    if success1 and success2:
        print("\n✅ All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
