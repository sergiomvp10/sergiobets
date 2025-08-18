#!/usr/bin/env python3
"""Test the complete GUI to Telegram bot integration flow"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_telegram_integration():
    """Test the complete integration between GUI and Telegram bot"""
    print("🔗 TESTING GUI TO TELEGRAM BOT INTEGRATION")
    print("=" * 70)
    
    try:
        if not os.path.exists('historial_predicciones.json'):
            print("❌ historial_predicciones.json not found")
            return False
        
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"📊 Total predictions in historial: {len(historial)}")
        
        sent_predictions = [p for p in historial if p.get('sent_to_telegram') == True]
        print(f"📱 Predictions sent to Telegram: {len(sent_predictions)}")
        
        gui_sent_predictions = [p for p in sent_predictions if p.get('fecha_envio_telegram')]
        print(f"🖥️ Predictions sent via GUI button: {len(gui_sent_predictions)}")
        
        from datetime import datetime, timedelta
        
        fecha_limite = datetime.now() - timedelta(days=7)
        pronosticos_recientes = []
        
        for pred in historial:
            if (pred.get('sent_to_telegram') and 
                pred.get('fecha_envio_telegram')):
                try:
                    fecha_envio = datetime.fromisoformat(pred['fecha_envio_telegram'])
                    if fecha_envio >= fecha_limite:
                        pronosticos_recientes.append(pred)
                except:
                    continue
        
        pronosticos_recientes.sort(key=lambda x: x.get('fecha_envio_telegram', ''), reverse=True)
        recent_top_5 = pronosticos_recientes[:5]
        
        print(f"📅 Recent predictions (last 7 days): {len(pronosticos_recientes)}")
        print(f"🎯 Top 5 recent predictions for bot display: {len(recent_top_5)}")
        
        if recent_top_5:
            print(f"\n🤖 TELEGRAM BOT WOULD DISPLAY:")
            print("=" * 50)
            for i, pred in enumerate(recent_top_5, 1):
                partido = pred.get('partido', 'N/A')
                prediccion = pred.get('prediccion', 'N/A')
                cuota = pred.get('cuota', 'N/A')
                fecha = pred.get('fecha', 'N/A')
                
                acierto = pred.get('acierto')
                if acierto is True:
                    estado = "✅ GANADA"
                elif acierto is False:
                    estado = "❌ PERDIDA"
                else:
                    estado = "⏳ PENDIENTE"
                
                print(f"🎯 PRONÓSTICO #{i}")
                print(f"⚽ {partido}")
                print(f"🎲 {prediccion}")
                print(f"💰 Cuota: {cuota}")
                print(f"📅 Fecha: {fecha}")
                print(f"📊 Estado: {estado}")
                print()
        else:
            print("\n🤖 TELEGRAM BOT WOULD DISPLAY:")
            print("=" * 50)
            print("🎯 Los pronósticos se envían desde la aplicación principal.")
            print("Cuando se publiquen nuevos pronósticos, aparecerán aquí automáticamente.")
        
        integration_working = len(gui_sent_predictions) > 0 and len(recent_top_5) > 0
        
        print(f"\n🔗 INTEGRATION STATUS:")
        print("=" * 30)
        print(f"✅ GUI sends predictions: {'YES' if len(gui_sent_predictions) > 0 else 'NO'}")
        print(f"✅ Bot can read predictions: {'YES' if len(recent_top_5) > 0 else 'NO'}")
        print(f"✅ Integration working: {'YES' if integration_working else 'NO'}")
        
        print(f"\n📋 TEST RECOMMENDATIONS:")
        print("=" * 30)
        print("1. Launch sergiobets_unified.py")
        print("2. Select some predictions using checkboxes")
        print("3. Click '📌 Enviar Pronóstico Seleccionado' button")
        print("4. Start Telegram bot with /start command")
        print("5. Click '🎯 PRONÓSTICOS' button")
        print("6. Verify predictions appear with correct details and status")
        
        return integration_working
        
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_telegram_integration()
    if success:
        print("\n✅ GUI TO TELEGRAM INTEGRATION TEST PASSED")
        print("🎯 Ready for manual testing with actual GUI and bot")
    else:
        print("\n⚠️ INTEGRATION TEST SHOWS ISSUES")
        print("🔧 May need to send predictions via GUI first")
