#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from track_record import TrackRecordManager
from datetime import datetime

def test_statistics_display():
    """Test the improved statistics display for Telegram"""
    print('=== PRUEBA DE ESTADÍSTICAS MEJORADAS PARA TELEGRAM ===')
    
    try:
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"❌ Error obteniendo métricas: {metricas['error']}")
            return False
        
        fallos = metricas['predicciones_resueltas'] - metricas['aciertos']
        porcentaje_acertividad = metricas['tasa_acierto']
        
        mensaje_telegram = f"""📊 ESTADÍSTICAS SERGIOBETS

🎯 RENDIMIENTO GENERAL:
✅ Aciertos: {metricas['aciertos']}
❌ Fallos: {fallos}
📈 Porcentaje de Acertividad: {porcentaje_acertividad:.1f}%

📋 RESUMEN DE PREDICCIONES:
- Total predicciones: {metricas['total_predicciones']}
- Predicciones resueltas: {metricas['predicciones_resueltas']}
- Predicciones pendientes: {metricas['predicciones_pendientes']}

💰 RENDIMIENTO FINANCIERO:
- Total apostado: ${metricas['total_apostado']:.2f}
- Ganancia total: ${metricas['total_ganancia']:.2f}
- ROI: {metricas['roi']:.2f}%

📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        print("MENSAJE DE ESTADÍSTICAS PARA TELEGRAM:")
        print("=" * 50)
        print(mensaje_telegram)
        print("=" * 50)
        
        print("\n✅ Mejoras implementadas:")
        print("- Sección destacada con aciertos, fallos y porcentaje de acertividad")
        print("- Formato más claro y fácil de leer")
        print("- Métricas organizadas por categorías")
        print("- Uso de emojis para mejor visualización")
        
        total_resueltas = metricas['predicciones_resueltas']
        aciertos = metricas['aciertos']
        fallos_calculados = total_resueltas - aciertos
        
        print(f"\n🔍 Verificación de datos:")
        print(f"- Predicciones resueltas: {total_resueltas}")
        print(f"- Aciertos: {aciertos}")
        print(f"- Fallos calculados: {fallos_calculados}")
        print(f"- Porcentaje: {(aciertos/total_resueltas*100):.1f}%" if total_resueltas > 0 else "- Porcentaje: N/A")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

if __name__ == "__main__":
    test_statistics_display()
