#!/usr/bin/env python3

import asyncio
from telegram_bot_listener import iniciar_bot_listener

if __name__ == "__main__":
    print("🤖 Iniciando SergioBets Bot Listener...")
    print("📝 Registrando usuarios automáticamente...")
    print("💬 Los usuarios pueden usar /start o enviar cualquier mensaje")
    print("📁 Usuarios se guardan en usuarios.txt")
    print("\nPresiona Ctrl+C para detener el bot\n")
    
    try:
        asyncio.run(iniciar_bot_listener())
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando bot: {e}")
