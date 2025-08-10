#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_telegram_api_failure_scenarios():
    """Test various failure scenarios that might occur in live Telegram integration"""
    print('=== PRUEBA DE ESCENARIOS DE FALLO DE TELEGRAM API ===')
    
    scenarios = [
        ("timeout_after_send", "Timeout después de envío exitoso"),
        ("connection_error", "Error de conexión"),
        ("attribute_error", "Error de atributo"),
        ("telegram_api_error", "Error específico de Telegram API"),
        ("async_timing_issue", "Problema de timing async")
    ]
    
    for scenario_name, scenario_desc in scenarios:
        print(f"\n🧪 Testing scenario: {scenario_desc}")
        
        try:
            mock_update = Mock()
            mock_context = Mock()
            mock_query = Mock()
            mock_query.from_user.id = 12345
            
            if scenario_name == "timeout_after_send":
                async def timeout_edit(*args, **kwargs):
                    await asyncio.sleep(0.01)
                    raise asyncio.TimeoutError("Timeout after successful send")
                mock_query.edit_message_text = timeout_edit
                
            elif scenario_name == "connection_error":
                async def connection_error_edit(*args, **kwargs):
                    await asyncio.sleep(0.01)
                    raise ConnectionError("Connection lost after send")
                mock_query.edit_message_text = connection_error_edit
                
            elif scenario_name == "attribute_error":
                async def attribute_error_edit(*args, **kwargs):
                    await asyncio.sleep(0.01)
                    raise AttributeError("'NoneType' object has no attribute 'something'")
                mock_query.edit_message_text = attribute_error_edit
                
            elif scenario_name == "telegram_api_error":
                try:
                    from telegram.error import TelegramError
                    async def telegram_error_edit(*args, **kwargs):
                        await asyncio.sleep(0.01)
                        raise TelegramError("Telegram API error after send")
                    mock_query.edit_message_text = telegram_error_edit
                except ImportError:
                    async def telegram_error_edit(*args, **kwargs):
                        await asyncio.sleep(0.01)
                        raise RuntimeError("Telegram API error after send")
                    mock_query.edit_message_text = telegram_error_edit
                
            elif scenario_name == "async_timing_issue":
                async def timing_issue_edit(*args, **kwargs):
                    await asyncio.sleep(0.01)
                    await asyncio.sleep(0.001)
                    raise RuntimeError("Async timing issue")
                mock_query.edit_message_text = timing_issue_edit
            
            mock_update.callback_query = mock_query
            
            from telegram_bot_listener import mostrar_estadisticas
            
            with patch('telegram_bot_listener.logger') as mock_logger:
                await mostrar_estadisticas(mock_update, mock_context)
                
                error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
                if any("Error mostrando estadísticas" in call for call in error_calls):
                    print(f"✅ Scenario {scenario_name} handled correctly")
                else:
                    print(f"❌ Scenario {scenario_name} not handled properly")
            
        except Exception as e:
            print(f"❌ Unexpected error in scenario {scenario_name}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_api_failure_scenarios())
