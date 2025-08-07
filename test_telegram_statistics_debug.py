#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from track_record import TrackRecordManager
from datetime import datetime
import asyncio
from unittest.mock import Mock, AsyncMock

def test_statistics_message_formatting():
    """Test the complete statistics message formatting that happens in Telegram"""
    print('=== PRUEBA DE FORMATEO COMPLETO DE MENSAJE DE ESTADÍSTICAS ===')
    
    try:
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"❌ Error obteniendo métricas: {metricas['error']}")
            return False
        
        fallos = metricas['predicciones_resueltas'] - metricas['aciertos']
        porcentaje_acertividad = metricas['tasa_acierto']
        
        mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

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

📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
        
        print("MENSAJE FORMATEADO EXITOSAMENTE:")
        print("=" * 60)
        print(mensaje)
        print("=" * 60)
        print(f"Longitud del mensaje: {len(mensaje)} caracteres")
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print("✅ Keyboard markup creado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de formateo: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mock_telegram_call():
    """Test simulating the Telegram API call"""
    print('\n=== PRUEBA DE LLAMADA SIMULADA A TELEGRAM API ===')
    
    try:
        mock_query = Mock()
        mock_query.edit_message_text = AsyncMock()
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        fallos = metricas['predicciones_resueltas'] - metricas['aciertos']
        porcentaje_acertividad = metricas['tasa_acierto']
        
        mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

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

📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await mock_query.edit_message_text(mensaje, reply_markup=reply_markup)
        
        print("✅ Llamada simulada a Telegram API exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error en llamada simulada: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Telegram Statistics Debug")
    print("=" * 60)
    
    success1 = test_statistics_message_formatting()
    
    success2 = asyncio.run(test_mock_telegram_call())
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 Todos los tests pasaron! El problema puede estar en la integración real con Telegram.")
        print("✅ Formateo de mensaje funciona correctamente")
        print("✅ Llamada simulada funciona correctamente")
        print("🔍 El error probablemente ocurre en la interacción real con la API de Telegram")
    else:
        print("❌ Algunos tests fallaron. Revisar los errores arriba.")
