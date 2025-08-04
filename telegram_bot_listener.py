#!/usr/bin/env python3

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
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
    """Manejar comando /start con menú interactivo"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    es_nuevo = registrar_usuario(user_id, username, first_name)
    
    if es_nuevo:
        mensaje = f"¡Hola {first_name}! 👋\n\nBienvenido a SergioBets 🎯\n\nTe has registrado exitosamente para recibir nuestros pronósticos de apuestas deportivas.\n\n¡Prepárate para ganar! 💰"
    else:
        mensaje = f"¡Hola de nuevo {first_name}! 👋\n\nYa estás registrado en SergioBets 🎯\n\n¡Listo para más pronósticos ganadores! 💰"
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Estadísticas", callback_data="estadisticas"),
            InlineKeyboardButton("📢 Novedades", callback_data="novedades")
        ],
        [
            InlineKeyboardButton("💳 Membresia", callback_data="membresia"),
            InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensaje += "\n\n🔽 Selecciona una opción del menú:"
    
    await update.message.reply_text(mensaje, reply_markup=reply_markup)

async def mensaje_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar cualquier mensaje para registrar usuario automáticamente"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    registrar_usuario(user_id, username, first_name)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar callbacks de botones del menú"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "estadisticas":
        await mostrar_estadisticas(update, context)
    elif query.data == "novedades":
        await mostrar_novedades(update, context)
    elif query.data == "membresia":
        await mostrar_membresia(update, context)
    elif query.data == "ayuda":
        await mostrar_ayuda(update, context)

async def mostrar_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas del sistema"""
    query = update.callback_query
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        total_usuarios = contar_usuarios_registrados()
        
        if "error" in metricas:
            mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

👥 Usuarios registrados: {total_usuarios}
📈 Sistema: Activo y funcionando
⚠️ Datos de predicciones: {metricas.get('error', 'No disponibles')}

🔄 El sistema está recopilando datos..."""
        else:
            mensaje = f"""📊 ESTADÍSTICAS SERGIOBETS

👥 USUARIOS:
• Registrados: {total_usuarios}

🎯 PREDICCIONES:
• Total: {metricas['total_predicciones']}
• Resueltas: {metricas['predicciones_resueltas']}
• Aciertos: {metricas['aciertos']}
• Tasa de éxito: {metricas['tasa_acierto']:.1f}%

💰 RENDIMIENTO:
• Total apostado: ${metricas['total_apostado']:.2f}
• Ganancia: ${metricas['total_ganancia']:.2f}
• ROI: {metricas['roi']:.2f}%

📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
        
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(mensaje, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error mostrando estadísticas: {e}")
        await query.edit_message_text("❌ Error cargando estadísticas. Intenta de nuevo.")

async def mostrar_novedades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar novedades desde archivo"""
    query = update.callback_query
    try:
        if os.path.exists('novedades.txt'):
            with open('novedades.txt', 'r', encoding='utf-8') as f:
                contenido = f.read()
        else:
            contenido = """📢 NOVEDADES SERGIOBETS

🎯 Sistema activo y funcionando
📊 Estadísticas disponibles en tiempo real
🤖 IA generando predicciones diariamente

¡Mantente atento a futuras actualizaciones!"""
        
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(contenido, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error mostrando novedades: {e}")
        await query.edit_message_text("❌ Error cargando novedades. Intenta de nuevo.")

async def mostrar_membresia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar información de membresía"""
    query = update.callback_query
    mensaje = """💳 MEMBRESÍA PREMIUM SERGIOBETS

🌟 BENEFICIOS PREMIUM:
• Predicciones exclusivas de alta confianza
• Acceso a estadísticas avanzadas
• Alertas en tiempo real
• Soporte prioritario
• Análisis detallado de mercados

💰 PRECIOS:
• Mensual: $29.99 USD
• Trimestral: $79.99 USD (33% descuento)
• Anual: $299.99 USD (58% descuento)

🔐 MÉTODOS DE PAGO:
• Bitcoin (BTC)
• Ethereum (ETH)
• USDT (Tether)
• Tarjeta de crédito

📞 Para adquirir tu membresía, contacta:
@sergiomvp10

🚀 ¡Únete a los ganadores!"""
    
    keyboard = [
        [InlineKeyboardButton("📞 Contactar", url="https://t.me/sergiomvp10")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

async def mostrar_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar información de ayuda"""
    query = update.callback_query
    mensaje = """❓ AYUDA - SERGIOBETS

🤖 COMANDOS DISPONIBLES:
• /start - Mostrar menú principal
• Cualquier mensaje - Registro automático

📊 FUNCIONES:
• Estadísticas: Ver rendimiento del sistema
• Novedades: Últimas actualizaciones
• Membresía: Información de planes premium
• Ayuda: Esta información

🎯 CÓMO FUNCIONA:
1. Regístrate enviando cualquier mensaje
2. Recibirás pronósticos automáticamente
3. Revisa estadísticas para ver rendimiento
4. Considera membresía premium para más beneficios

📞 SOPORTE:
• Telegram: @sergiomvp10
• Problemas técnicos: Reportar en el chat

🚀 TIPS:
• Mantén notificaciones activas
• Revisa estadísticas regularmente
• Sigue las recomendaciones de stake
• Apuesta con responsabilidad

⚠️ IMPORTANTE:
Las apuestas conllevan riesgo. Nunca apuestes más de lo que puedes permitirte perder."""
    
    keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

async def volver_menu_principal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Volver al menú principal"""
    query = update.callback_query
    user = query.from_user
    first_name = user.first_name
    
    mensaje = f"¡Hola {first_name}! 👋\n\nYa estás registrado en SergioBets 🎯\n\n¡Listo para más pronósticos ganadores! 💰\n\n🔽 Selecciona una opción del menú:"
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Estadísticas", callback_data="estadisticas"),
            InlineKeyboardButton("📢 Novedades", callback_data="novedades")
        ],
        [
            InlineKeyboardButton("💳 Membresia", callback_data="membresia"),
            InlineKeyboardButton("❓ Ayuda", callback_data="ayuda")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar errores del bot"""
    logger.warning(f'Update {update} caused error {context.error}')

def iniciar_bot_listener():
    """Iniciar el bot listener para registrar usuarios"""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(button_callback, pattern="^(estadisticas|novedades|membresia|ayuda)$"))
        application.add_handler(CallbackQueryHandler(volver_menu_principal, pattern="^menu_principal$"))
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
    import asyncio
    
    def ejecutar_bot():
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
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
