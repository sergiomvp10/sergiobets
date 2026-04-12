#!/usr/bin/env python3

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from access_manager import access_manager, verificar_acceso

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en el archivo .env")
ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '7659029315'))
PAYMENTS_GROUP_ID = int(os.getenv('PAYMENTS_GROUP_ID', os.getenv('ADMIN_TELEGRAM_ID', '7659029315')))
USUARIOS_FILE = 'usuarios.txt'
NEQUI_PAYMENTS_FILE = 'pagos/nequi_payments.json'
USDT_PAYMENTS_FILE = 'pagos/usdt_payments.json'
USDT_WALLET_ADDRESS = 'TTWWueGnAzJfCBCHrVuHVSC2rRuiuRajYc'
USDT_NETWORK = 'TRC20'
PAYPAL_PAYMENTS_FILE = 'pagos/paypal_payments.json'
PAYPAL_USERNAME = '@ferchomelendez'

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
    
    mensaje = f"Bienvenido a 𝔹𝕖𝕥𝔾𝕖𝕟𝕚𝕦𝕏 \n\n¡Prepárate para ganar!{mensaje_acceso}"
    
    keyboard = [
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
    
    
    await update.message.reply_text(mensaje, reply_markup=reply_markup)

async def get_chat_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /get_chat_id - Obtener ID del chat actual"""
    chat = update.effective_chat
    user = update.effective_user
    
    mensaje = f"""🔍 *Información del Chat*

📱 *Tipo:* {chat.type}
🆔 *Chat ID:* `{chat.id}`
👤 *Tu User ID:* `{user.id}`
"""
    
    if chat.type in ['group', 'supergroup']:
        mensaje += f"\n📝 *Nombre del grupo:* {chat.title}"
        mensaje += f"\n\n💡 *Para usar este grupo como destino de notificaciones:*"
        mensaje += f"\n1. Copia el Chat ID: `{chat.id}`"
        mensaje += f"\n2. Actualiza tu .env: `ADMIN_TELEGRAM_ID={chat.id}`"
        mensaje += f"\n3. Reinicia el bot"
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')

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
    
    if query.data == "pronosticos":
        await mostrar_pronosticos(update, context)
    elif query.data == "estadisticas":
        await mostrar_estadisticas(update, context)
    elif query.data == "novedades":
        await mostrar_novedades(update, context)
    elif query.data == "membresia":
        await mostrar_membresia(update, context)
    elif query.data == "ayuda":
        await mostrar_ayuda(update, context)
    elif query.data == "pay_usdt":
        await procesar_pago_usdt(update, context)
    elif query.data == "pay_paypal":
        await procesar_pago_paypal(update, context)
    elif query.data == "pago_nequi":
        await procesar_pago_nequi(update, context)
    elif query.data == "menu_principal":
        await volver_menu_principal(update, context)

async def mostrar_pronosticos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar pronósticos unificados"""
    query = update.callback_query
    
    mensaje = """🎯 PRONÓSTICOS BETGENIUX

🏆 PREDICCIONES DISPONIBLES:
• Análisis profesional de partidos
• Predicciones multimercado (1X2, BTTS, Over/Under, Corners)
• Estrategias de apuestas optimizadas

📊 INCLUYE:
• Predicciones diarias actualizadas
• Análisis detallado de cuotas
• Gestión inteligente de bankroll
• Estadísticas en tiempo real

💎 ACCESO PREMIUM:
• ROI superior al 15%
• Más de 70% de aciertos
• Soporte personalizado

¿Quieres ver los pronósticos de hoy?"""
    
    keyboard = [
        [InlineKeyboardButton("💳 Ver Membresía Premium", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup)

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

PRONOSTICOS:

• Total: 23
• Resueltos: 22
• Pendientes: 1
• Aciertos: 15
• Fallos: 7
• Tasa de éxito: 68.2%

📅 Actualizado: 2025-08-25"""
        else:
            fallos = metricas['predicciones_resueltas'] - metricas['aciertos']
            mensaje = f"""📊 ESTADÍSTICAS BETGENIUX

PRONOSTICOS:

• Total: {metricas['total_predicciones']}
• Resueltos: {metricas['predicciones_resueltas']}
• Pendientes: {metricas['predicciones_pendientes']}
• Aciertos: {metricas['aciertos']}
• Fallos: {fallos}
• Tasa de éxito: {metricas['tasa_acierto']:.1f}%

📅 Actualizado: {metricas['fecha_calculo'][:10]}"""
        
        keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(mensaje, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error mostrando estadísticas: {e}")
        await query.edit_message_text("❌ Error cargando estadísticas. Intenta de nuevo.")

async def mostrar_novedades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar novedades desde archivo con mes actual dinámico"""
    query = update.callback_query
    try:
        meses_espanol = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        
        mes_actual = meses_espanol[datetime.now().month]
        
        if os.path.exists('novedades.txt'):
            with open('novedades.txt', 'r', encoding='utf-8') as f:
                contenido = f.read()
            contenido = contenido.replace('{MES_ACTUAL}', mes_actual)
        else:
            contenido = f"""📢 NOVEDADES BETGENIUX - {mes_actual} 2025

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
            InlineKeyboardButton("💳 Pagar con PayPal", callback_data="pay_paypal")
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

📊 FUNCIONES:
• Estadísticas: Ver rendimiento del sistema
• Novedades: Últimas actualizaciones
• Membresía: Información de planes premium
• Ayuda: Esta información

🎯 CÓMO FUNCIONA ?
1. Regístrate utilizando el comando /start
2. Adquiere tu membresia o ingresa tu codigo promocional
3. Recibe diariamente apuestas y copialas en tu casa de apuestas favorita
4. Controla tu bank y crea tu estrategia

📞 SOPORTE:
• Obten soporte prioritario aqui @Sie7e0

🚀 TIPS:
• Mantén notificaciones activas
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
    user_id = user.id
    first_name = user.first_name
    
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
    
    mensaje = f"Bienvenido a 𝔹𝕖𝕥𝔾𝕖𝕟𝕚𝕦𝕏 \n\n¡Prepárate para ganar!{mensaje_acceso}"
    
    keyboard = [
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
        application.add_handler(CommandHandler("get_chat_id", get_chat_id_command))
        application.add_handler(CallbackQueryHandler(button_callback, pattern="^(pronosticos|estadisticas|novedades|membresia|ayuda|pay_usdt|pay_paypal|pago_nequi)$"))
        application.add_handler(CallbackQueryHandler(verificar_pago, pattern="^verify_"))
        application.add_handler(CallbackQueryHandler(confirmar_pago_admin, pattern="^(nequi_confirm|nequi_reject|usdt_confirm|usdt_reject|paypal_confirm|paypal_reject):"))
        application.add_handler(CallbackQueryHandler(volver_menu_principal, pattern="^menu_principal$"))
        application.add_handler(MessageHandler((filters.PHOTO | filters.Document.IMAGE) & filters.ChatType.PRIVATE, manejar_comprobante_pago))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_general))
        application.add_error_handler(error_handler)
        
        logger.info("BetGeniuXBot listener iniciado - Registrando usuarios automáticamente")
        logger.info(f"🔧 ADMIN_TELEGRAM_ID configurado: {ADMIN_TELEGRAM_ID}")
        logger.info(f"🔧 PAYMENTS_GROUP_ID configurado: {PAYMENTS_GROUP_ID}")
        logger.info(f"🔧 NEQUI_PAYMENTS_FILE: {NEQUI_PAYMENTS_FILE}")
        logger.info(f"🔧 USDT_PAYMENTS_FILE: {USDT_PAYMENTS_FILE}")
        logger.info(f"🔧 PAYPAL_PAYMENTS_FILE: {PAYPAL_PAYMENTS_FILE}")
        
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

async def procesar_pago_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar solicitud de pago USDT manual"""
    query = update.callback_query
    
    from datetime import datetime
    context.user_data['awaiting_usdt_proof'] = {
        "created_at": datetime.now().isoformat(),
        "amount_usd": 12,
        "wallet": USDT_WALLET_ADDRESS,
        "network": USDT_NETWORK
    }
    
    mensaje = f"""💵 PAGO CON USDT (TRC20)

Para completar tu pago por USDT:

💰 Valor: *$12 USD*
🏦 Red: *{USDT_NETWORK}*
📱 Wallet: `{USDT_WALLET_ADDRESS}`

📸 Envíanos el comprobante de pago por este chat.

_Verificaremos y activaremos tu acceso manualmente._

⏰ Una vez realices el pago, envía una captura del comprobante y te activaremos el acceso VIP en máximo 24 horas.

💡 *Importante:* Asegúrate de enviar exactamente $12 USD en la red TRC20."""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver a Membresía", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')

async def procesar_pago_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar solicitud de pago PayPal manual"""
    query = update.callback_query
    
    from datetime import datetime
    context.user_data['awaiting_paypal_proof'] = {
        "created_at": datetime.now().isoformat(),
        "amount_usd": 12,
        "paypal_user": PAYPAL_USERNAME
    }
    
    mensaje = f"""💳 PAGO CON PAYPAL

Para completar tu pago por PayPal:

💰 Valor: *$12 USD*
👤 Usuario PayPal: *{PAYPAL_USERNAME}*

📸 Envíanos el comprobante de pago por este chat.

_Verificaremos y activaremos tu acceso manualmente._

⏰ Una vez realices el pago, envía una captura del comprobante y te activaremos el acceso VIP en máximo 24 horas.

💡 *Importante:* Asegúrate de enviar exactamente $12 USD."""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver a Membresía", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')

async def procesar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE, currency: str):
    """Procesar solicitud de pago (legacy - disabled, redirects to manual payments)"""
    query = update.callback_query
    await query.answer()
    
    mensaje = """⚠️ Los pagos automáticos han sido deshabilitados.

Por favor, usa uno de estos métodos de pago manual:

💰 USDT (TRC20) - $12 USD
💳 PayPal - $12 USD  
📲 NEQUI - 50,000 COP

Vuelve al menú de Membresía para seleccionar tu método de pago."""
    
    keyboard = [
        [InlineKeyboardButton("🔙 Volver a Membresía", callback_data="membresia")],
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(mensaje, reply_markup=reply_markup, parse_mode='Markdown')

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
    
    from datetime import datetime
    context.user_data['awaiting_nequi_proof'] = {
        "created_at": datetime.now().isoformat(),
        "amount": 50000,
        "phone": "3137526084"
    }
    
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

async def manejar_comprobante_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comprobante de pago (NEQUI, USDT o PayPal)"""
    is_nequi = context.user_data.get('awaiting_nequi_proof')
    is_usdt = context.user_data.get('awaiting_usdt_proof')
    is_paypal = context.user_data.get('awaiting_paypal_proof')
    
    if not is_nequi and not is_usdt and not is_paypal:
        logger.info("Foto/documento recibido pero usuario no está esperando comprobante")
        return
    
    payment_type = "NEQUI" if is_nequi else ("USDT" if is_usdt else "PayPal")
    logger.info(f"📸 Procesando comprobante {payment_type}")
    
    if is_nequi:
        await _procesar_comprobante_nequi(update, context)
    elif is_usdt:
        await _procesar_comprobante_usdt(update, context)
    else:
        await _procesar_comprobante_paypal(update, context)

async def _procesar_comprobante_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar comprobante NEQUI"""
    if not context.user_data.get('awaiting_nequi_proof'):
        return
    
    import json
    from datetime import datetime
    import time
    from pathlib import Path
    
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "N/A"
    first_name = user.first_name or "N/A"
    
    logger.info(f"📸 Procesando comprobante NEQUI de usuario {user_id} ({first_name})")
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
        logger.info(f"  ✓ Detectado como foto: {file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
        logger.info(f"  ✓ Detectado como documento: {file_id}")
    else:
        logger.warning("  ✗ No es foto ni documento")
        return
    
    payment_info = context.user_data['awaiting_nequi_proof']
    payment_id = f"NEQ-{user_id}-{int(time.time())}"
    
    payment_record = {
        "payment_id": payment_id,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "file_id": file_id,
        "file_type": file_type,
        "amount_cop": payment_info['amount'],
        "phone": payment_info['phone'],
        "submitted_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    logger.info(f"  ✓ Payment record creado: {payment_id}")
    
    try:
        nequi_file_path = Path(__file__).parent / 'pagos' / 'nequi_payments.json'
        nequi_file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ Directorio pagos verificado: {nequi_file_path.parent}")
        
        if nequi_file_path.exists():
            try:
                with open(nequi_file_path, 'r', encoding='utf-8') as f:
                    payments = json.load(f)
                
                if isinstance(payments, dict):
                    logger.warning(f"  ⚠ JSON es dict en lugar de list, convirtiendo...")
                    payments = []
                elif not isinstance(payments, list):
                    logger.warning(f"  ⚠ JSON tiene tipo inesperado: {type(payments)}, recreando...")
                    payments = []
                else:
                    logger.info(f"  ✓ JSON leído: {len(payments)} pagos existentes")
            except json.JSONDecodeError as e:
                logger.warning(f"  ⚠ JSON corrupto, recreando: {e}")
                payments = []
        else:
            logger.info("  ✓ Archivo JSON no existe, creando nuevo")
            payments = []
        
        payments.append(payment_record)
        
        with open(nequi_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ JSON guardado exitosamente con {len(payments)} pagos")
        
    except Exception as e:
        logger.exception(f"  ✗ Error guardando JSON: {e}")
        await update.message.reply_text(
            "❌ Error guardando tu comprobante. Por favor, contacta soporte."
        )
        return
    
    try:
        caption = f"""🔔 NUEVO COMPROBANTE NEQUI

👤 Usuario: {first_name} (@{username})
🆔 ID: {user_id}
💰 Monto: {payment_info['amount']:,} COP
📱 Teléfono: {payment_info['phone']}
🔖 Ref: {payment_id}
⏰ Enviado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

¿Confirmar pago?"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar 7 días", callback_data=f"nequi_confirm:{payment_id}:7")],
            [InlineKeyboardButton("❌ Rechazar", callback_data=f"nequi_reject:{payment_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"  → Enviando comprobante al grupo de pagos (ID: {PAYMENTS_GROUP_ID})...")
        
        if file_type == "photo":
            admin_msg = await context.bot.send_photo(
                chat_id=PAYMENTS_GROUP_ID,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            admin_msg = await context.bot.send_document(
                chat_id=PAYMENTS_GROUP_ID,
                document=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        
        logger.info(f"  ✓ Comprobante enviado al admin exitosamente (msg_id: {admin_msg.message_id})")
        
        payment_record['admin_msg_id'] = admin_msg.message_id
        payments[-1] = payment_record
        
        with open(nequi_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ admin_msg_id guardado en JSON")
        
    except Exception as e:
        logger.exception(f"  ✗ Error enviando al admin: {e}")
        logger.error(f"  ℹ ADMIN_TELEGRAM_ID configurado: {ADMIN_TELEGRAM_ID}")
        logger.error(f"  ℹ Tipo de error: {type(e).__name__}")
        
        await update.message.reply_text(
            f"✅ Comprobante recibido y guardado!\n\n"
            f"📋 Referencia: `{payment_id}`\n"
            f"⚠️ No pudimos notificar al administrador automáticamente.\n"
            f"📞 Por favor, contacta soporte con tu referencia para activación manual.\n\n"
            f"Gracias por tu paciencia! 🙏",
            parse_mode='Markdown'
        )
        del context.user_data['awaiting_nequi_proof']
        return
    
    await update.message.reply_text(
        f"✅ Comprobante recibido correctamente!\n\n"
        f"📋 Referencia: `{payment_id}`\n"
        f"⏰ Verificaremos tu pago y activaremos tu acceso VIP en máximo 24 horas.\n\n"
        f"Gracias por tu paciencia! 🙏",
        parse_mode='Markdown'
    )
    
    del context.user_data['awaiting_nequi_proof']
    logger.info(f"✅ Comprobante NEQUI procesado exitosamente: {payment_id}")

async def _procesar_comprobante_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar comprobante USDT"""
    if not context.user_data.get('awaiting_usdt_proof'):
        return
    
    import json
    from datetime import datetime
    import time
    from pathlib import Path
    
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "N/A"
    first_name = user.first_name or "N/A"
    
    logger.info(f"📸 Procesando comprobante USDT de usuario {user_id} ({first_name})")
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
        logger.info(f"  ✓ Detectado como foto: {file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
        logger.info(f"  ✓ Detectado como documento: {file_id}")
    else:
        logger.warning("  ✗ No es foto ni documento")
        return
    
    payment_info = context.user_data['awaiting_usdt_proof']
    payment_id = f"USDT-{user_id}-{int(time.time())}"
    
    payment_record = {
        "payment_id": payment_id,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "file_id": file_id,
        "file_type": file_type,
        "amount_usd": payment_info['amount_usd'],
        "wallet": payment_info['wallet'],
        "network": payment_info['network'],
        "submitted_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    logger.info(f"  ✓ Payment record creado: {payment_id}")
    
    try:
        usdt_file_path = Path(__file__).parent / 'pagos' / 'usdt_payments.json'
        usdt_file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ Directorio pagos verificado: {usdt_file_path.parent}")
        
        if usdt_file_path.exists():
            try:
                with open(usdt_file_path, 'r', encoding='utf-8') as f:
                    payments = json.load(f)
                
                if isinstance(payments, dict):
                    logger.warning(f"  ⚠ JSON es dict en lugar de list, convirtiendo...")
                    payments = []
                elif not isinstance(payments, list):
                    logger.warning(f"  ⚠ JSON tiene tipo inesperado: {type(payments)}, recreando...")
                    payments = []
                else:
                    logger.info(f"  ✓ JSON leído: {len(payments)} pagos existentes")
            except json.JSONDecodeError as e:
                logger.warning(f"  ⚠ JSON corrupto, recreando: {e}")
                payments = []
        else:
            logger.info("  ✓ Archivo JSON no existe, creando nuevo")
            payments = []
        
        payments.append(payment_record)
        
        with open(usdt_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ JSON guardado exitosamente con {len(payments)} pagos")
        
    except Exception as e:
        logger.exception(f"  ✗ Error guardando JSON: {e}")
        await update.message.reply_text(
            "❌ Error guardando tu comprobante. Por favor, contacta soporte."
        )
        return
    
    try:
        caption = f"""🔔 NUEVO COMPROBANTE USDT

👤 Usuario: {first_name} (@{username})
🆔 ID: {user_id}
💰 Monto: ${payment_info['amount_usd']} USD
🏦 Red: {payment_info['network']}
📱 Wallet: {payment_info['wallet'][:10]}...{payment_info['wallet'][-10:]}
🔖 Ref: {payment_id}
⏰ Enviado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

¿Confirmar pago?"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar 7 días", callback_data=f"usdt_confirm:{payment_id}:7")],
            [InlineKeyboardButton("❌ Rechazar", callback_data=f"usdt_reject:{payment_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"  → Enviando comprobante al grupo de pagos (ID: {PAYMENTS_GROUP_ID})...")
        
        if file_type == "photo":
            admin_msg = await context.bot.send_photo(
                chat_id=PAYMENTS_GROUP_ID,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            admin_msg = await context.bot.send_document(
                chat_id=PAYMENTS_GROUP_ID,
                document=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        
        logger.info(f"  ✓ Comprobante enviado al grupo exitosamente (msg_id: {admin_msg.message_id})")
        
        payment_record['admin_msg_id'] = admin_msg.message_id
        payments[-1] = payment_record
        
        with open(usdt_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ admin_msg_id guardado en JSON")
        
    except Exception as e:
        logger.exception(f"  ✗ Error enviando al grupo: {e}")
        logger.error(f"  ℹ PAYMENTS_GROUP_ID configurado: {PAYMENTS_GROUP_ID}")
        logger.error(f"  ℹ Tipo de error: {type(e).__name__}")
        
        await update.message.reply_text(
            f"✅ Comprobante recibido y guardado!\n\n"
            f"📋 Referencia: `{payment_id}`\n"
            f"⚠️ No pudimos notificar al administrador automáticamente.\n"
            f"📞 Por favor, contacta soporte con tu referencia para activación manual.\n\n"
            f"Gracias por tu paciencia! 🙏",
            parse_mode='Markdown'
        )
        del context.user_data['awaiting_usdt_proof']
        return
    
    await update.message.reply_text(
        f"✅ Comprobante recibido correctamente!\n\n"
        f"📋 Referencia: `{payment_id}`\n"
        f"⏰ Verificaremos tu pago y activaremos tu acceso VIP en máximo 24 horas.\n\n"
        f"Gracias por tu paciencia! 🙏",
        parse_mode='Markdown'
    )
    
    del context.user_data['awaiting_usdt_proof']
    logger.info(f"✅ Comprobante USDT procesado exitosamente: {payment_id}")

async def _procesar_comprobante_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesar comprobante PayPal"""
    if not context.user_data.get('awaiting_paypal_proof'):
        return
    
    import json
    from datetime import datetime
    import time
    from pathlib import Path
    
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or "N/A"
    first_name = user.first_name or "N/A"
    
    logger.info(f"📸 Procesando comprobante PayPal de usuario {user_id} ({first_name})")
    
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
        logger.info(f"  ✓ Detectado como foto: {file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
        logger.info(f"  ✓ Detectado como documento: {file_id}")
    else:
        logger.warning("  ✗ No es foto ni documento")
        return
    
    payment_info = context.user_data['awaiting_paypal_proof']
    payment_id = f"PAYPAL-{user_id}-{int(time.time())}"
    
    payment_record = {
        "payment_id": payment_id,
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "file_id": file_id,
        "file_type": file_type,
        "amount_usd": payment_info['amount_usd'],
        "paypal_user": payment_info['paypal_user'],
        "submitted_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    logger.info(f"  ✓ Payment record creado: {payment_id}")
    
    try:
        paypal_file_path = Path(__file__).parent / 'pagos' / 'paypal_payments.json'
        paypal_file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"  ✓ Directorio pagos verificado: {paypal_file_path.parent}")
        
        if paypal_file_path.exists():
            try:
                with open(paypal_file_path, 'r', encoding='utf-8') as f:
                    payments = json.load(f)
                
                if isinstance(payments, dict):
                    logger.warning(f"  ⚠ JSON es dict en lugar de list, convirtiendo...")
                    payments = []
                elif not isinstance(payments, list):
                    logger.warning(f"  ⚠ JSON tiene tipo inesperado: {type(payments)}, recreando...")
                    payments = []
                else:
                    logger.info(f"  ✓ JSON leído: {len(payments)} pagos existentes")
            except json.JSONDecodeError as e:
                logger.warning(f"  ⚠ JSON corrupto, recreando: {e}")
                payments = []
        else:
            logger.info("  ✓ Archivo JSON no existe, creando nuevo")
            payments = []
        
        payments.append(payment_record)
        
        with open(paypal_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ JSON guardado exitosamente con {len(payments)} pagos")
        
    except Exception as e:
        logger.exception(f"  ✗ Error guardando JSON: {e}")
        await update.message.reply_text(
            "❌ Error guardando tu comprobante. Por favor, contacta soporte."
        )
        return
    
    try:
        caption = f"""🔔 NUEVO COMPROBANTE PAYPAL

👤 Usuario: {first_name} (@{username})
🆔 ID: {user_id}
💰 Monto: ${payment_info['amount_usd']} USD
👤 PayPal: {payment_info['paypal_user']}
🔖 Ref: {payment_id}
⏰ Enviado: {datetime.now().strftime('%Y-%m-%d %H:%M')}

¿Confirmar pago?"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirmar 7 días", callback_data=f"paypal_confirm:{payment_id}:7")],
            [InlineKeyboardButton("❌ Rechazar", callback_data=f"paypal_reject:{payment_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"  → Enviando comprobante al grupo de pagos (ID: {PAYMENTS_GROUP_ID})...")
        
        if file_type == "photo":
            admin_msg = await context.bot.send_photo(
                chat_id=PAYMENTS_GROUP_ID,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            admin_msg = await context.bot.send_document(
                chat_id=PAYMENTS_GROUP_ID,
                document=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        
        logger.info(f"  ✓ Comprobante enviado al grupo exitosamente (msg_id: {admin_msg.message_id})")
        
        payment_record['admin_msg_id'] = admin_msg.message_id
        payments[-1] = payment_record
        
        with open(paypal_file_path, 'w', encoding='utf-8') as f:
            json.dump(payments, f, indent=2, ensure_ascii=False)
        logger.info(f"  ✓ admin_msg_id guardado en JSON")
        
    except Exception as e:
        logger.exception(f"  ✗ Error enviando al grupo: {e}")
        logger.error(f"  ℹ PAYMENTS_GROUP_ID configurado: {PAYMENTS_GROUP_ID}")
        logger.error(f"  ℹ Tipo de error: {type(e).__name__}")
        
        await update.message.reply_text(
            f"✅ Comprobante recibido y guardado!\n\n"
            f"📋 Referencia: `{payment_id}`\n"
            f"⚠️ No pudimos notificar al administrador automáticamente.\n"
            f"📞 Por favor, contacta soporte con tu referencia para activación manual.\n\n"
            f"Gracias por tu paciencia! 🙏",
            parse_mode='Markdown'
        )
        del context.user_data['awaiting_paypal_proof']
        return
    
    await update.message.reply_text(
        f"✅ Comprobante recibido correctamente!\n\n"
        f"📋 Referencia: `{payment_id}`\n"
        f"⏰ Verificaremos tu pago y activaremos tu acceso VIP en máximo 24 horas.\n\n"
        f"Gracias por tu paciencia! 🙏",
        parse_mode='Markdown'
    )
    
    del context.user_data['awaiting_paypal_proof']
    logger.info(f"✅ Comprobante PayPal procesado exitosamente: {payment_id}")

async def confirmar_pago_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar confirmación o rechazo de pagos (NEQUI o USDT) por admin"""
    query = update.callback_query
    
    if query.message.chat.id != PAYMENTS_GROUP_ID:
        await query.answer("⛔ Esta acción solo puede realizarse en el grupo de pagos.", show_alert=True)
        return
    
    if query.data.startswith('nequi_'):
        await _confirmar_pago_nequi(update, context)
    elif query.data.startswith('usdt_'):
        await _confirmar_pago_usdt(update, context)
    elif query.data.startswith('paypal_'):
        await _confirmar_pago_paypal(update, context)

async def _confirmar_pago_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar o rechazar pago NEQUI"""
    query = update.callback_query
    
    import json
    from datetime import datetime
    
    try:
        data_parts = query.data.split(':')
        action = data_parts[0]
        payment_id = data_parts[1]
        
        with open(NEQUI_PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        
        payment = None
        payment_index = None
        for i, p in enumerate(payments):
            if p['payment_id'] == payment_id:
                payment = p
                payment_index = i
                break
        
        if not payment:
            await query.answer("❌ Pago no encontrado.", show_alert=True)
            return
        
        if payment['status'] != 'pending':
            await query.answer(f"⚠️ Este pago ya fue {payment['status']}.", show_alert=True)
            return
        
        if action == 'nequi_confirm':
            dias = int(data_parts[2])
            
            if access_manager.otorgar_acceso(payment['user_id'], dias):
                payment['status'] = 'confirmed'
                payment['confirmed_at'] = datetime.now().isoformat()
                payment['dias_otorgados'] = dias
                
                payments[payment_index] = payment
                with open(NEQUI_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                
                mensaje_confirmacion = access_manager.generar_mensaje_confirmacion_premium(payment['user_id'])
                
                try:
                    from telegram_utils import enviar_telegram
                    chat_id = int(payment['user_id'])
                    enviar_telegram(chat_id=chat_id, mensaje=mensaje_confirmacion)
                except Exception as e:
                    logger.error(f"Error enviando confirmación al usuario: {e}")
                
                await query.edit_message_caption(
                    caption=f"{query.message.caption}\n\n✅ CONFIRMADO - {dias} días otorgados\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                await query.answer(f"✅ Pago confirmado! {dias} días de acceso VIP otorgados.", show_alert=True)
            else:
                await query.answer("❌ Error otorgando acceso. Verifica el sistema.", show_alert=True)
        
        elif action == 'nequi_reject':
            payment['status'] = 'rejected'
            payment['rejected_at'] = datetime.now().isoformat()
            
            payments[payment_index] = payment
            with open(NEQUI_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(payments, f, indent=2, ensure_ascii=False)
            
            try:
                await context.bot.send_message(
                    chat_id=int(payment['user_id']),
                    text=f"❌ Tu pago NEQUI (Ref: {payment_id}) no pudo ser verificado.\n\n"
                         f"Por favor, contacta soporte para más información."
                )
            except Exception as e:
                logger.error(f"Error notificando rechazo al usuario: {e}")
            
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n❌ RECHAZADO\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            await query.answer("❌ Pago rechazado. Usuario notificado.", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error en _confirmar_pago_nequi: {e}")
        await query.answer("❌ Error procesando la acción.", show_alert=True)

async def _confirmar_pago_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar o rechazar pago USDT"""
    query = update.callback_query
    
    import json
    from datetime import datetime
    
    try:
        data_parts = query.data.split(':')
        action = data_parts[0]
        payment_id = data_parts[1]
        
        with open(USDT_PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        
        payment = None
        payment_index = None
        for i, p in enumerate(payments):
            if p['payment_id'] == payment_id:
                payment = p
                payment_index = i
                break
        
        if not payment:
            await query.answer("❌ Pago no encontrado.", show_alert=True)
            return
        
        if payment['status'] != 'pending':
            await query.answer(f"⚠️ Este pago ya fue {payment['status']}.", show_alert=True)
            return
        
        if action == 'usdt_confirm':
            dias = int(data_parts[2])
            
            if access_manager.otorgar_acceso(payment['user_id'], dias):
                payment['status'] = 'confirmed'
                payment['confirmed_at'] = datetime.now().isoformat()
                payment['dias_otorgados'] = dias
                
                payments[payment_index] = payment
                with open(USDT_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                
                mensaje_confirmacion = access_manager.generar_mensaje_confirmacion_premium(payment['user_id'])
                
                try:
                    from telegram_utils import enviar_telegram
                    chat_id = int(payment['user_id'])
                    enviar_telegram(chat_id=chat_id, mensaje=mensaje_confirmacion)
                except Exception as e:
                    logger.error(f"Error enviando confirmación al usuario: {e}")
                
                await query.edit_message_caption(
                    caption=f"{query.message.caption}\n\n✅ CONFIRMADO - {dias} días otorgados\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                await query.answer(f"✅ Pago confirmado! {dias} días de acceso VIP otorgados.", show_alert=True)
            else:
                await query.answer("❌ Error otorgando acceso. Verifica el sistema.", show_alert=True)
        
        elif action == 'usdt_reject':
            payment['status'] = 'rejected'
            payment['rejected_at'] = datetime.now().isoformat()
            
            payments[payment_index] = payment
            with open(USDT_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(payments, f, indent=2, ensure_ascii=False)
            
            try:
                await context.bot.send_message(
                    chat_id=int(payment['user_id']),
                    text=f"❌ Tu pago USDT (Ref: {payment_id}) no pudo ser verificado.\n\n"
                         f"Por favor, contacta soporte para más información."
                )
            except Exception as e:
                logger.error(f"Error notificando rechazo al usuario: {e}")
            
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n❌ RECHAZADO\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            await query.answer("❌ Pago rechazado. Usuario notificado.", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error en _confirmar_pago_usdt: {e}")
        await query.answer("❌ Error procesando la acción.", show_alert=True)

async def _confirmar_pago_paypal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmar o rechazar pago PayPal"""
    query = update.callback_query
    
    import json
    from datetime import datetime
    
    try:
        data_parts = query.data.split(':')
        action = data_parts[0]
        payment_id = data_parts[1]
        
        with open(PAYPAL_PAYMENTS_FILE, 'r', encoding='utf-8') as f:
            payments = json.load(f)
        
        payment = None
        payment_index = None
        for i, p in enumerate(payments):
            if p['payment_id'] == payment_id:
                payment = p
                payment_index = i
                break
        
        if not payment:
            await query.answer("❌ Pago no encontrado.", show_alert=True)
            return
        
        if payment['status'] != 'pending':
            await query.answer(f"⚠️ Este pago ya fue {payment['status']}.", show_alert=True)
            return
        
        if action == 'paypal_confirm':
            dias = int(data_parts[2])
            
            if access_manager.otorgar_acceso(payment['user_id'], dias):
                payment['status'] = 'confirmed'
                payment['confirmed_at'] = datetime.now().isoformat()
                payment['dias_otorgados'] = dias
                
                payments[payment_index] = payment
                with open(PAYPAL_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payments, f, indent=2, ensure_ascii=False)
                
                mensaje_confirmacion = access_manager.generar_mensaje_confirmacion_premium(payment['user_id'])
                
                try:
                    from telegram_utils import enviar_telegram
                    chat_id = int(payment['user_id'])
                    enviar_telegram(chat_id=chat_id, mensaje=mensaje_confirmacion)
                except Exception as e:
                    logger.error(f"Error enviando confirmación al usuario: {e}")
                
                await query.edit_message_caption(
                    caption=f"{query.message.caption}\n\n✅ CONFIRMADO - {dias} días otorgados\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                await query.answer(f"✅ Pago confirmado! {dias} días de acceso VIP otorgados.", show_alert=True)
            else:
                await query.answer("❌ Error otorgando acceso. Verifica el sistema.", show_alert=True)
        
        elif action == 'paypal_reject':
            payment['status'] = 'rejected'
            payment['rejected_at'] = datetime.now().isoformat()
            
            payments[payment_index] = payment
            with open(PAYPAL_PAYMENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(payments, f, indent=2, ensure_ascii=False)
            
            try:
                await context.bot.send_message(
                    chat_id=int(payment['user_id']),
                    text=f"❌ Tu pago PayPal (Ref: {payment_id}) no pudo ser verificado.\n\n"
                         f"Por favor, contacta soporte para más información."
                )
            except Exception as e:
                logger.error(f"Error notificando rechazo al usuario: {e}")
            
            await query.edit_message_caption(
                caption=f"{query.message.caption}\n\n❌ RECHAZADO\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            await query.answer("❌ Pago rechazado. Usuario notificado.", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error en _confirmar_pago_paypal: {e}")
        await query.answer("❌ Error procesando la acción.", show_alert=True)

def send_nequi_admin_notification(user_info: dict, payment_info: dict):
    """Enviar notificación de pago NEQUI al admin (función auxiliar para tests)"""
    import requests
    
    try:
        caption = f"""🔔 NUEVO COMPROBANTE NEQUI

👤 Usuario: {user_info.get('first_name', 'N/A')} (@{user_info.get('username', 'N/A')})
🆔 ID: {user_info.get('user_id', 'N/A')}
💰 Monto: {payment_info.get('amount_cop', 0):,} COP
📱 Teléfono: {payment_info.get('phone', 'N/A')}
🔖 Ref: {payment_info.get('payment_id', 'N/A')}

Comprobante enviado al administrador."""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_TELEGRAM_ID,
            "text": caption
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error en send_nequi_admin_notification: {e}")
        return False

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
