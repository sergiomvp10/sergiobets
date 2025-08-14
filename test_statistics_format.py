#!/usr/bin/env python3
"""Test the updated statistics format"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_statistics_format():
    """Test that statistics format matches user requirements"""
    print("🧪 TESTING STATISTICS FORMAT")
    print("=" * 50)
    
    try:
        from track_record import TrackRecordManager
        from datetime import datetime
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        print("📊 Raw metrics:", metricas)
        print()
        
        if "error" in metricas:
            mensaje = f"""📊 ESTADÍSTICAS BETGENIUX

🎯 PRONOSTICOS:
• Total: 0
• Pendientes: 0
• Aciertos: 0
• Fallos: 0
• Tasa de éxito: 0.0%


📅 Actualizado: {datetime.now().strftime('%Y-%m-%d')}"""
            print("❌ Error case - showing default format:")
        else:
            fallos = metricas['predicciones_resueltas'] - metricas['aciertos']
            mensaje = f"""📊 ESTADÍSTICAS BETGENIUX

🎯 PRONOSTICOS:
• Total: {metricas['total_predicciones']}
• Pendientes: {metricas['predicciones_pendientes']}
• Aciertos: {metricas['aciertos']}
• Fallos: {fallos}
• Tasa de éxito: {metricas['tasa_acierto']:.1f}%


📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
            print("✅ Success case - showing real data:")
        
        print(mensaje)
        print()
        print("✅ Statistics format test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing statistics format: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_statistics_format()
