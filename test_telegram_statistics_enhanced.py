#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from unittest.mock import Mock, AsyncMock
from track_record import TrackRecordManager
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_telegram_statistics():
    """Test enhanced version that mimics the exact Telegram bot flow"""
    print('=== PRUEBA MEJORADA DE ESTADÍSTICAS DE TELEGRAM ===')
    
    try:
        mock_update = Mock()
        mock_context = Mock()
        mock_query = Mock()
        mock_query.from_user.id = 12345
        mock_query.edit_message_text = AsyncMock()
        mock_update.callback_query = mock_query
        
        logger.info(f"🔍 mostrar_estadisticas iniciado para usuario {mock_query.from_user.id}")
        
        logger.info("📊 Importando TrackRecordManager...")
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        logger.info("🔧 Creando instancia de TrackRecordManager...")
        tracker = TrackRecordManager(api_key)
        
        logger.info("📈 Calculando métricas de rendimiento...")
        metricas = tracker.calcular_metricas_rendimiento()
        logger.info(f"✅ Métricas calculadas: {list(metricas.keys())}")
        
        if "error" in metricas:
            logger.warning(f"⚠️ Error en métricas: {metricas.get('error')}")
            mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

📈 Sistema: Activo y funcionando
⚠️ Datos de predicciones: {metricas.get('error', 'No disponibles')}

🔄 El sistema está recopilando datos..."""
        else:
            logger.info("📊 Formateando mensaje de estadísticas...")
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
            
            logger.info(f"📝 Mensaje formateado: {len(mensaje)} caracteres")
        
        logger.info("⌨️ Creando keyboard markup...")
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info("📤 Enviando mensaje a Telegram...")
        await mock_query.edit_message_text(mensaje, reply_markup=reply_markup)
        logger.info("✅ Mensaje enviado exitosamente a Telegram")
        
        await asyncio.sleep(0.1)
        logger.info("🎯 mostrar_estadisticas completado exitosamente")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error mostrando estadísticas: {e}")
        import traceback
        logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_telegram_statistics())
    if success:
        print("✅ Test completado exitosamente")
    else:
        print("❌ Test falló")
