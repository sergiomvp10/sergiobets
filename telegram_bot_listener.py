#!/usr/bin/env python3

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from access_manager import access_manager, verificar_acceso

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c')
USUARIOS_FILE = 'usuarios.txt'

def cargar_usuarios_registrados():
    """Cargar usuarios ya registrados desde el archivo"""
    return access_manager.listar_usuarios()

def registrar_usuario(user_id, username, first_name):
    """Registrar nuevo usuario usando access_manager"""
    return access_manager.registrar_usuario(str(user_id), username, first_name)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /start con menú interactivo"""
    user = update.effective_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    es_nuevo = registrar_usuario(user_id, username, first_name)
    
    access_manager.limpiar_usuarios_expirados()
    
    tiene_acceso = verificar_acceso(str(user_id))
    if not tiene_acceso:
        mensaje_acceso = "\n\n⚠️ Tu acceso premium ha expirado o no tienes acceso premium.\nContacta soporte para renovarlo o adquiere una membresía."
    else:
        usuario_info = access_manager.obtener_usuario(str(user_id))
        if usuario_info and usuario_info.get('fecha_expiracion'):
            from datetime import datetime
            try:
                fecha_exp = datetime.fromisoformat(usuario_info['fecha_expiracion'])
                mensaje_acceso = f"\n\n👑 Acceso Premium Activo hasta: {fecha_exp.strftime('%Y-%m-%d %H:%M')}"
            except:
                mensaje_acceso = "\n\n👑 Acceso Premium Activo"
        else:
            mensaje_acceso = ""
    
    if es_nuevo:
        mensaje = f"¡Hola {first_name}! 👋\n\nBienvenido a BetGeniuX 🎯\n\nTe has registrado exitosamente para recibir nuestros pronósticos de apuestas deportivas.\n\n¡Prepárate para ganar! 💰{mensaje_acceso}"
    else:
        mensaje = f"¡Hola de nuevo {first_name}! 👋\n\nYa estás registrado en BetGeniuX 🎯\n\n¡Listo para más pronósticos ganadores! 💰{mensaje_acceso}"
    
    keyboard = [
        [
            InlineKeyboardButton("💲 GRATIS", callback_data="gratis"),
            InlineKeyboardButton("💰 PREMIUM", callback_data="premium")
        ],
        [
            InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="estadisticas"),
            InlineKeyboardButton("📢 ANUNCIOS", callback_data="novedades")
        ],
        [
            InlineKeyboardButton("⭐ MEMBRESIA", callback_data="membresia"),
            InlineKeyboardButton("❓ AYUDA", callback_data="ayuda")
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
    
    if query.data == "gratis":
        await mostrar_gratis(update, context)
    elif query.data == "premium":
        await mostrar_premium(update, context)
    elif query.data == "estadisticas":
        await mostrar_estadisticas(update, context)
    elif query.data == "novedades":
        await mostrar_novedades(update, context)
    elif query.data == "membresia":
        await mostrar_membresia(update, context)
    elif query.data == "ayuda":
        await mostrar_ayuda(update, context)
    elif query.data == "pay_usdt":
        await procesar_pago(update, context, "usdttrc20")
    elif query.data == "pay_ltc":
        await procesar_pago(update, context, "ltc")
    elif query.data == "pago_nequi":
        await procesar_pago_nequi(update, context)
    elif query.data == "menu_principal":
        await volver_menu_principal(update, context)

async def mostrar_gratis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar contenido gratuito"""
    query = update.callback_query
    
    mensaje = """💲 CONTENIDO GRATUITO BETGENIUX

🎯 PREDICCIONES BÁSICAS:
• Análisis de partidos principales
• Tips básicos de apuestas
• Estadísticas generales

📊 ACCESO INCLUYE:
• Predicciones diarias seleccionadas
• Análisis de cuotas básico
• Tips de gestión de bankroll

🔄 Para acceder a predicciones premium y análisis avanzado, consulta nuestra membresía.

¿Te gustaría ver las predicciones gratuitas de hoy?"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

async def mostrar_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar contenido premium"""
    query = update.callback_query
    
    mensaje = """💰 CONTENIDO PREMIUM BETGENIUX

🏆 PREDICCIONES VIP:
• Análisis profesional completo
• Predicciones de alta confianza
• Estrategias avanzadas de apuestas

💎 ACCESO PREMIUM INCLUYE:
• Predicciones diarias premium
• Análisis detallado de mercados
• Gestión avanzada de bankroll
• Soporte personalizado
• Estadísticas en tiempo real

📈 RESULTADOS COMPROBADOS:
• ROI superior al 15%
• Más de 70% de aciertos
• Seguimiento detallado

¿Quieres acceder al contenido premium?"""
    
    keyboard = [
        [InlineKeyboardButton("💳 Ver Membresía", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

async def mostrar_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas del sistema"""
    query = update.callback_query
    try:
        from track_record import TrackRecordManager
        
        api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
        tracker = TrackRecordManager(api_key)
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            mensaje = f"""📊 ESTADÍSTICAS BETGENIUX

📈 Sistema: Activo y funcionando
⚠️ Datos de predicciones: {metricas.get('error', 'No disponibles')}

🔄 El sistema está recopilando datos..."""
        else:
            mensaje = f"""📊 ESTADÍSTICAS BETGENIUX

🎯 PREDICCIONES:
• Total: {metricas['total_predicciones']}
• Resueltas: {metricas['predicciones_resueltas']}
• Pendientes: {metricas['predicciones_pendientes']}
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
            contenido = """📢 NOVEDADES BETGENIUX

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
    """Mostrar información de membresía con opciones de pago"""
    query = update.callback_query
    
    ngrok_url = get_current_ngrok_url()
    
    if ngrok_url:
        mensaje = f"""MEMBRESÍA VIP BETGENIUX

⭐ ACCESO VIP 7 DÍAS ⭐

• Predicciones diarias exclusivas de alta confianza
• Alertas en tiempo real
• Soporte prioritario


💰 PRECIO
• 7 días de acceso VIP: 12$ / 50.000 COP

🔐 MÉTODOS DE PAGO DISPONIBLES:

• USDT (TRC20)
• Litecoin (LTC)
• NEQUI (Colombia)

🚀 ¡Selecciona tu método de pago preferido!"""
    else:
        mensaje = """MEMBRESÍA VIP BETGENIUX

⭐ ACCESO VIP 7 DÍAS ⭐

• Predicciones diarias exclusivas de alta confianza
• Alertas en tiempo real
• Soporte prioritario


💰 PRECIO
• 7 días de acceso VIP: 12$ / 50.000 COP

🔐 MÉTODOS DE PAGO DISPONIBLES:

• USDT (TRC20)
• Litecoin (LTC)
• NEQUI (Colombia)

🚀 ¡Selecciona tu método de pago preferido!"""
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Pagar con USDT (TRC20)", callback_data="pay_usdt"),
            InlineKeyboardButton("🪙 Pagar con Litecoin", callback_data="pay_ltc")
        ],
        [InlineKeyboardButton("📲 Pagar con NEQUI", callback_data="pago_nequi")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')

async def mostrar_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar información de ayuda"""
    query = update.callback_query
    mensaje = """❓ AYUDA - BETGENIUX

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
    
    mensaje = f"¡Hola {first_name}! 👋\n\nYa estás registrado en BetGeniuX 🎯\n\n¡Listo para más pronósticos ganadores! 💰\n\n🔽 Selecciona una opción del menú:"
    
    keyboard = [
        [
            InlineKeyboardButton("💲 GRATIS", callback_data="gratis"),
            InlineKeyboardButton("💰 PREMIUM", callback_data="premium")
        ],
        [
            InlineKeyboardButton("📊 ESTADÍSTICAS", callback_data="estadisticas"),
            InlineKeyboardButton("📢 ANUNCIOS", callback_data="novedades")
        ],
        [
            InlineKeyboardButton("⭐ MEMBRESIA", callback_data="membresia"),
            InlineKeyboardButton("❓ AYUDA", callback_data="ayuda")
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
        application.add_handler(CallbackQueryHandler(button_callback, pattern="^(estadisticas|novedades|membresia|ayuda|pay_usdt|pay_ltc|pago_nequi)$"))
        application.add_handler(CallbackQueryHandler(verificar_pago, pattern="^verify_"))
        application.add_handler(CallbackQueryHandler(volver_menu_principal, pattern="^menu_principal$"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_general))
        application.add_error_handler(error_handler)
        
        logger.info("BetGeniuXBot listener iniciado - Registrando usuarios automáticamente")
        
        application.run_polling(stop_signals=None)
        
    except Exception as e:
        logger.error(f"Error iniciando bot listener: {e}")
        return False
    
    return True

def obtener_usuarios_registrados():
    """Obtener lista de usuarios registrados"""
    return access_manager.listar_usuarios()

def contar_usuarios_registrados():
    """Contar total de usuarios registrados"""
    return access_manager.contar_usuarios_registrados()

def get_current_ngrok_url():
    """Obtener URL actual de ngrok desde archivo"""
    import os
    try:
        if os.path.exists("ngrok_url.txt"):
            with open("ngrok_url.txt", 'r') as f:
                url = f.read().strip()
                return url if url else None
    except:
        pass
    return None

def check_and_restart_ngrok():
    """Verificar si ngrok está corriendo y reiniciarlo si es necesario"""
    import requests
    import subprocess
    import time
    
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            
            for tunnel in tunnels:
                if tunnel.get('proto') == 'https':
                    url = tunnel.get('public_url')
                    if url:
                        with open("ngrok_url.txt", 'w') as f:
                            f.write(url)
                        return url
        
        print("⚠️ ngrok no está corriendo. Ejecuta: python launch_with_ngrok.py")
        return None
        
    except Exception as e:
        print(f"⚠️ Error verificando ngrok: {e}")
        return None

async def procesar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE, currency: str):
    """Procesar solicitud de pago"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    username = query.from_user.username or "sin_username"
    
    try:
        from pagos.payments import PaymentManager
        payment_manager = PaymentManager()
        
        result = payment_manager.create_membership_payment(
            user_id=user_id,
            username=username,
            currency=currency,
            membership_type="weekly"
        )
        
        if result.get("success"):
            currency_name = "USDT" if currency.startswith("usdt") else "Litecoin"
            if currency.lower() in ["usdt", "usdttrc20"]:
                instruction_text = "1. Envía exactamente 12 USDT en la red TRC20"
            else:
                instruction_text = f"1. Envía exactamente {result['pay_amount']} {result['pay_currency'].upper()}"
            
            mensaje = f"""💳 PAGO GENERADO - {currency_name}

🔐 Detalles del pago:
• Monto: {result['pay_amount']} {result['pay_currency']}
• Dirección: `{result['pay_address']}`
• ID de pago: {result['payment_id']}

📋 INSTRUCCIONES:
{instruction_text}
2. A la dirección mostrada arriba
3. El pago se confirmará automáticamente
4. Recibirás tu acceso VIP inmediatamente

⏰ Este pago expira en 30 minutos.
🔄 Puedes verificar el estado con el botón de abajo"""
            
            keyboard = [
                [InlineKeyboardButton("🔍 Verificar Pago", callback_data=f"verify_{result['payment_id']}")],
                [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.edit_message_text(
                f"❌ Error creando el pago: {result.get('error')}\n\n🔙 Intenta nuevamente.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="membresia")]])
            )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error del sistema: {str(e)}\n\n🔙 Intenta más tarde.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="membresia")]])
        )

async def verificar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verificar estado de un pago"""
    query = update.callback_query
    payment_id = query.data.replace("verify_", "")
    
    try:
        from pagos.payments import PaymentManager
        payment_manager = PaymentManager()
        
        status = payment_manager.nowpayments.get_payment_status(payment_id)
        
        if "error" not in status:
            payment_status = status.get("payment_status", "unknown")
            
            if payment_status in ["confirmed", "finished"]:
                mensaje = "✅ ¡Pago confirmado! Tu acceso VIP ha sido activado."
            elif payment_status == "waiting":
                mensaje = "⏳ Pago pendiente. Esperando confirmación de la red..."
            elif payment_status == "confirming":
                mensaje = "🔄 Pago en proceso de confirmación..."
            else:
                mensaje = f"📊 Estado del pago: {payment_status}"
        else:
            mensaje = f"❌ Error verificando pago: {status.get('error')}"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Verificar de nuevo", callback_data=f"verify_{payment_id}")],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(mensaje, reply_markup=reply_markup)
        
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error del sistema: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_principal")]])
        )

async def procesar_pago_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar solicitud de pago NEQUI"""
    query = update.callback_query
    
    mensaje = """📲 PAGO CON NEQUI

Para completar tu pago por NEQUI:

💰 Valor: *50.000 COP*
📱 Número: *3137526084*
📸 Envíanos el comprobante de pago por este chat.

_Verificaremos y activaremos tu acceso manualmente._

⏰ Una vez realices el pago, envía una captura del comprobante y te activaremos el acceso VIP en máximo 24 horas."""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver a Membresía", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')

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
    logger.info("BetGeniuXBot listener iniciado en hilo separado")
    return hilo_bot

if __name__ == "__main__":
    print("🤖 Iniciando BetGeniuX Bot Listener...")
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
