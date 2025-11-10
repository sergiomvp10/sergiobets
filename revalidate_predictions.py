#!/usr/bin/env python3
"""
Script to re-validate predictions that may have been marked incorrectly
Specifically fixes "Victoria [Team]" and Double Chance predictions
"""

import os
import sys
from track_record import TrackRecordManager
from dotenv import load_dotenv

load_dotenv()

def main():
    """Re-validate recent predictions"""
    api_key = os.getenv('FOOTYSTATS_API_KEY')
    
    if not api_key:
        print("❌ FOOTYSTATS_API_KEY not found in environment")
        sys.exit(1)
    
    print("🔄 Iniciando re-validación de predicciones...")
    print("=" * 80)
    
    manager = TrackRecordManager(api_key)
    
    print("\n📊 Actualizando predicciones de los últimos 10 días...")
    result = manager.actualizar_historial_con_resultados(dias_atras=10)
    
    print("\n✅ Re-validación completada!")
    print(f"   Predicciones actualizadas: {result.get('actualizadas', 0)}")
    print(f"   Predicciones pendientes: {result.get('pendientes', 0)}")
    print(f"   Errores: {result.get('errores', 0)}")
    
    print("\n📈 Estadísticas actualizadas:")
    metrics = manager.calcular_metricas_rendimiento()
    print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print(f"   ROI: {metrics.get('roi', 0):.1f}%")
    print(f"   Total predicciones: {metrics.get('total_predicciones', 0)}")
    print(f"   Aciertos: {metrics.get('aciertos', 0)}")
    print(f"   Fallos: {metrics.get('fallos', 0)}")
    print(f"   Pendientes: {metrics.get('pendientes', 0)}")

if __name__ == "__main__":
    main()
