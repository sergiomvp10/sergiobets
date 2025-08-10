#!/usr/bin/env python3
"""
Servidor de webhooks para BetGeniuX - NOWPayments Integration
Ejecutar este script para iniciar el servidor de webhooks
"""

import os
import sys
from dotenv import load_dotenv

def validate_environment():
    """Validar variables de entorno necesarias"""
    load_dotenv()
    
    required_vars = [
        'NOWPAYMENTS_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'ADMIN_TELEGRAM_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Asegúrate de configurar estas variables en el archivo .env")
        return False
    
    print("✅ Variables de entorno configuradas correctamente")
    return True

def main():
    """Función principal"""
    print("🚀 BetGeniuX - Servidor de Webhooks NOWPayments")
    print("=" * 50)
    
    if not validate_environment():
        sys.exit(1)
    
    print("🔧 Iniciando servidor...")
    print("📡 Webhook endpoint: http://localhost:5000/webhook/nowpayments")
    print("🔧 API endpoint: http://localhost:5000/api/create_payment")
    print("💳 Listo para recibir pagos...")
    print("\n⚠️  IMPORTANTE: Para producción, exponer el puerto 5000 públicamente")
    print("   Ejemplo con ngrok: ngrok http 5000")
    print("\n🛑 Presiona Ctrl+C para detener el servidor")
    print("=" * 50)
    
    try:
        from webhook_server import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
