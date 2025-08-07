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

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A')
USUARIOS_FILE = 'usuarios.json'  # Migrated to JSON format

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
        mensaje = f"¡Hola {first_name}! 👋\n\nBienvenido a SergioBets 🎯\n\nTe has registrado exitosamente para recibir nuestros pronósticos de apuestas deportivas.\n\n¡Prepárate para ganar! 💰{mensaje_acceso}"
    else:
        mensaje = f"¡Hola de nuevo {first_name}! 👋\n\nYa estás registrado en SergioBets 🎯\n\n¡Listo para más pronósticos ganadores! 💰{mensaje_acceso}"
    
    keyboard = [
        [
            InlineKeyboardButton("🆓 Predicciones Gratuitas", callback_data="predicciones_gratuitas"),
            InlineKeyboardButton("💎 Predicciones Premium", callback_data="predicciones_premium")
        ],
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
    elif query.data == "predicciones_premium":
        await enviar_predicciones_premium_bot(update, context)
    elif query.data == "predicciones_gratuitas":
        await enviar_predicciones_gratuitas_bot(update, context)
    elif query.data == "menu_principal":
        await volver_menu_principal(update, context)
    elif query.data == "pay_usdt":
        await procesar_pago(update, context, "usdttrc20")
    elif query.data == "pay_ltc":
        await procesar_pago(update, context, "ltc")
    elif query.data == "pago_nequi":
        await procesar_pago_nequi(update, context)

async def mostrar_estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar estadísticas del sistema con métricas claras"""
    query = update.callback_query
    
    logger.info(f"🔍 mostrar_estadisticas iniciado para usuario {query.from_user.id}")
    
    try:
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
        await query.edit_message_text(mensaje, reply_markup=reply_markup)
        logger.info("✅ Mensaje enviado exitosamente a Telegram")
        
        try:
            logger.info("🔍 Verificando estado post-envío...")
            import asyncio
            await asyncio.sleep(0.01)
            logger.info("✅ Verificación post-envío completada")
        except Exception as post_send_error:
            logger.error(f"❌ Error en verificación post-envío: {post_send_error}")
            logger.error(f"📋 Tipo de excepción post-envío: {type(post_send_error).__name__}")
        
        logger.info("🎯 mostrar_estadisticas completado exitosamente - RETORNANDO INMEDIATAMENTE")
        return
        
    except Exception as e:
        logger.error(f"❌ Error mostrando estadísticas: {e}")
        logger.error(f"📋 Tipo de excepción: {type(e).__name__}")
        logger.error(f"📋 Módulo de excepción: {type(e).__module__}")
        logger.error(f"📋 Args de excepción: {e.args}")
        
        if isinstance(e, asyncio.TimeoutError):
            logger.error("🕐 TIMEOUT ERROR: Problema de tiempo de espera en Telegram API")
        elif isinstance(e, ConnectionError):
            logger.error("🌐 CONNECTION ERROR: Problema de conexión con Telegram")
        elif isinstance(e, AttributeError):
            logger.error("🔧 ATTRIBUTE ERROR: Problema de atributo - posible objeto None")
        elif "telegram" in str(type(e)).lower():
            logger.error("📱 TELEGRAM API ERROR: Error específico de la API de Telegram")
        
        import traceback
        logger.error(f"📋 Traceback completo: {traceback.format_exc()}")
        
        logger.error("🔍 Verificando si el error ocurrió después del envío exitoso...")
        
        try:
            await query.edit_message_text("❌ Error cargando estadísticas. Intenta de nuevo.")
            logger.error("⚠️ Mensaje de error enviado como fallback")
        except Exception as edit_error:
            logger.error(f"💥 Error adicional al editar mensaje: {edit_error}")

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
    """Mostrar información de membresía con opciones de pago"""
    query = update.callback_query
    
    ngrok_url = get_current_ngrok_url()
    
    if ngrok_url:
        mensaje = f"""💳 MEMBRESÍA VIP SERGIOBETS

🌟 ACCESO VIP (7 DÍAS):
• Predicciones exclusivas de alta confianza
• Acceso a estadísticas avanzadas
• Alertas en tiempo real
• Soporte prioritario
• Análisis detallado de mercados

💰 PRECIO:
• 7 días de acceso VIP: 12$ / 50.000 COP

🔐 MÉTODOS DE PAGO DISPONIBLES:
• USDT (TRC20)
• Litecoin (LTC)
• NEQUI (Colombia)

🚀 ¡Selecciona tu método de pago preferido!

💳 También puedes pagar directamente aquí:
👉 [Pagar ahora]({ngrok_url}/api/create_payment)"""
    else:
        mensaje = """💳 MEMBRESÍA VIP SERGIOBETS

🌟 ACCESO VIP (7 DÍAS):
• Predicciones exclusivas de alta confianza
• Acceso a estadísticas avanzadas
• Alertas en tiempo real
• Soporte prioritario
• Análisis detallado de mercados

💰 PRECIO:
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
            InlineKeyboardButton("🆓 Predicciones Gratuitas", callback_data="predicciones_gratuitas"),
            InlineKeyboardButton("💎 Predicciones Premium", callback_data="predicciones_premium")
        ],
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
        application.add_handler(CallbackQueryHandler(button_callback, pattern="^(estadisticas|novedades|membresia|ayuda|pay_usdt|pay_ltc|pago_nequi)$"))
        application.add_handler(CallbackQueryHandler(verificar_pago, pattern="^verify_"))
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
async def enviar_predicciones_premium_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar predicciones premium solo a usuarios con suscripción activa"""
    query = update.callback_query
    user_id = query.from_user.id
    
    from access_manager import verificar_acceso
    
    if not verificar_acceso(str(user_id)):
        await query.edit_message_text(
            "❌ Acceso denegado\n\nEsta función es exclusiva para usuarios premium.\n\n💳 Adquiere tu membresía para acceder a predicciones exclusivas.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 Obtener Premium", callback_data="membresia")]])
        )
        return
    
    try:
        from footystats_api import obtener_partidos_del_dia
        from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia
        from datetime import datetime
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        partidos = obtener_partidos_del_dia(fecha)
        predicciones = filtrar_apuestas_inteligentes(partidos)
        
        if predicciones:
            mensaje = generar_mensaje_ia(predicciones[:3], fecha)
            mensaje += f"\n\n💎 Predicciones PREMIUM exclusivas\n📅 {fecha}"
            
            keyboard = [[InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(mensaje, reply_markup=reply_markup)
        else:
            await query.edit_message_text(
                f"📊 No hay predicciones premium disponibles para hoy ({fecha})\n\nIntenta más tarde o contacta soporte.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_principal")]])
            )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error obteniendo predicciones premium: {e}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_principal")]])
        )

async def enviar_predicciones_gratuitas_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enviar predicciones gratuitas a todos los usuarios"""
    query = update.callback_query
    
    try:
        from footystats_api import obtener_partidos_del_dia
        from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia
        from datetime import datetime
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        partidos = obtener_partidos_del_dia(fecha)
        predicciones = filtrar_apuestas_inteligentes(partidos)
        
        if predicciones:
            mensaje = generar_mensaje_ia(predicciones[:1], fecha)
            mensaje += f"\n\n🆓 Predicción GRATUITA del día\n📅 {fecha}\n\n💎 ¿Quieres más predicciones? Obtén acceso premium"
            
            keyboard = [
                [InlineKeyboardButton("💳 Obtener Premium", callback_data="membresia")],
                [InlineKeyboardButton("🔙 Volver al Menú", callback_data="menu_principal")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(mensaje, reply_markup=reply_markup)
        else:
            await query.edit_message_text(
                f"📊 No hay predicciones disponibles para hoy ({fecha})\n\nIntenta más tarde.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_principal")]])
            )
    except Exception as e:
        await query.edit_message_text(
            f"❌ Error obteniendo predicciones: {e}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_principal")]])
        )


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
