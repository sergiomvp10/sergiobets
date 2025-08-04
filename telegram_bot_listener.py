#!/usr/bin/env python3

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A')
USUARIOS_FILE = 'usuarios.txt'

def cargar_usuarios_registrados():
    """Cargar usuarios ya registrados desde el archivo"""
    usuarios_registrados = set()
    try:
        if os.path.exists(USUARIOS_FILE):
            with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip() and ' - ' in linea:
                        user_id = linea.split(' - ')[0].strip()
                        usuarios_registrados.add(user_id)
    except Exception as e:
        logger.error(f"Error cargando usuarios registrados: {e}")
    return usuarios_registrados

def registrar_usuario(user_id, username, first_name):
    """Registrar nuevo usuario en el archivo usuarios.txt"""
    try:
        usuarios_registrados = cargar_usuarios_registrados()
        
        if str(user_id) not in usuarios_registrados:
            username_str = username if username else "sin_username"
            first_name_str = first_name if first_name else "sin_nombre"
            
            with open(USUARIOS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{user_id} - {username_str} - {first_name_str}\n")
            
            logger.info(f"Usuario registrado: {user_id} - {username_str} - {first_name_str}")
            return True
        else:
            logger.info(f"Usuario ya registrado: {user_id}")
            return False
    except Exception as e:
        logger.error(f"Error registrando usuario: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /start"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    es_nuevo = registrar_usuario(user_id, username, first_name)
    
    if es_nuevo:
        mensaje = f"¡Hola {first_name}! 👋\n\nBienvenido a SergioBets 🎯\n\nTe has registrado exitosamente para recibir nuestros pronósticos de apuestas deportivas.\n\n¡Prepárate para ganar! 💰"
    else:
        mensaje = f"¡Hola de nuevo {first_name}! 👋\n\nYa estás registrado en SergioBets 🎯\n\n¡Listo para más pronósticos ganadores! 💰"
    
    await update.message.reply_text(mensaje)

async def mensaje_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar cualquier mensaje para registrar usuario automáticamente"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    registrar_usuario(user_id, username, first_name)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar errores del bot"""
    logger.warning(f'Update {update} caused error {context.error}')

def iniciar_bot_listener():
    """Iniciar el bot listener para registrar usuarios"""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_general))
        application.add_error_handler(error_handler)
        
        logger.info("Bot listener iniciado - Registrando usuarios automáticamente")
        
        application.run_polling(stop_signals=None)
        
    except Exception as e:
        logger.error(f"Error iniciando bot listener: {e}")
        return False
    
    return True

def obtener_usuarios_registrados():
    """Obtener lista de usuarios registrados"""
    usuarios = []
    try:
        if os.path.exists(USUARIOS_FILE):
            with open(USUARIOS_FILE, 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip() and ' - ' in linea:
                        partes = linea.strip().split(' - ')
                        if len(partes) >= 3:
                            usuarios.append({
                                'user_id': partes[0],
                                'username': partes[1],
                                'first_name': partes[2]
                            })
    except Exception as e:
        logger.error(f"Error obteniendo usuarios registrados: {e}")
    
    return usuarios

def contar_usuarios_registrados():
    """Contar total de usuarios registrados"""
    return len(obtener_usuarios_registrados())

def iniciar_bot_en_hilo():
    """Iniciar el bot listener en un hilo separado para integración con la app principal"""
    import threading
    
    def ejecutar_bot():
        try:
            iniciar_bot_listener()
        except Exception as e:
            logger.error(f"Error en hilo del bot: {e}")
    
    hilo_bot = threading.Thread(target=ejecutar_bot, daemon=True)
    hilo_bot.start()
    logger.info("Bot listener iniciado en hilo separado")
    return hilo_bot

if __name__ == "__main__":
    print("🤖 Iniciando SergioBets Bot Listener...")
    print("📝 Registrando usuarios automáticamente...")
    print("💬 Los usuarios pueden usar /start o enviar cualquier mensaje")
    print("📁 Usuarios se guardan en usuarios.txt")
    print("\nPresiona Ctrl+C para detener el bot\n")
    
    try:
        iniciar_bot_listener()
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando bot: {e}")
