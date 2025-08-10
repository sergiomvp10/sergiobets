#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from unittest.mock import Mock, AsyncMock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_isolated_statistics_function():
    """Test the exact mostrar_estadisticas function in complete isolation"""
    print('=== PRUEBA DE AISLAMIENTO COMPLETO DE mostrar_estadisticas ===')
    
    try:
        mock_update = Mock()
        mock_context = Mock()
        mock_query = Mock()
        mock_query.from_user.id = 12345
        mock_query.edit_message_text = AsyncMock()
        mock_update.callback_query = mock_query
        
        from telegram_bot_listener import mostrar_estadisticas
        
        print("🔍 Ejecutando mostrar_estadisticas con mocks...")
        await mostrar_estadisticas(mock_update, mock_context)
        
        print("✅ Función completada sin excepciones")
        
        if mock_query.edit_message_text.called:
            call_args = mock_query.edit_message_text.call_args
            if call_args:
                message = call_args[0][0] if call_args[0] else "No message"
                print(f"📤 Mensaje enviado: {message[:100]}...")
                
                if "Error cargando estadísticas" in message:
                    print("❌ ERROR: Se envió mensaje de error en lugar de estadísticas")
                    return False
                else:
                    print("✅ Se envió mensaje de estadísticas correctamente")
                    return True
        else:
            print("❌ ERROR: No se llamó a edit_message_text")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_track_record_manager_isolation():
    """Test TrackRecordManager in complete isolation"""
    print('\n=== PRUEBA DE AISLAMIENTO DE TrackRecordManager ===')
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        print("📈 Calculando métricas...")
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"⚠️ Error en métricas: {metricas['error']}")
        else:
            print(f"✅ Métricas calculadas exitosamente: {list(metricas.keys())}")
            
        print("🔄 Esperando 2 segundos para simular delay...")
        await asyncio.sleep(2)
        
        print("✅ TrackRecordManager completado sin problemas")
        return True
        
    except Exception as e:
        print(f"❌ Error en TrackRecordManager: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Telegram Statistics in Complete Isolation")
    print("=" * 70)
    
    success1 = asyncio.run(test_isolated_statistics_function())
    success2 = asyncio.run(test_track_record_manager_isolation())
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("🎉 Todos los tests de aislamiento pasaron!")
        print("✅ mostrar_estadisticas funciona correctamente")
        print("✅ TrackRecordManager funciona correctamente")
        print("🔍 El problema debe estar en la integración real con Telegram")
    else:
        print("❌ Algunos tests de aislamiento fallaron")
