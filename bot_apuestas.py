from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime
from dotenv import load_dotenv
import os
import json

# Cargar token del archivo .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Tu ID de administrador (para el progreso)
ADMIN_ID = 7659029315

# /start con menú
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    print(f"✅ Usuario conectado: {user_id}")

    keyboard = [
        [InlineKeyboardButton("📊 Estadísticas", callback_data='estadisticas')],
        [InlineKeyboardButton("📈 Pronósticos del día", callback_data='pronosticos')],
        [InlineKeyboardButton("🧠 Último pronóstico", callback_data='ultimopick')],
        [InlineKeyboardButton("⚽ Partidos del día", callback_data='partidos_dia')],
        [InlineKeyboardButton("📈 Progreso", callback_data='progreso')],
        [InlineKeyboardButton("⚙️ Configuración", callback_data='configuracion')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("👋 Bienvenido al bot de apuestas, Jefe. Elige una opción:", reply_markup=reply_markup)

# 📊 Últimos 30 pronósticos
def mostrar_estadisticas(update: Update, context: CallbackContext):
    try:
        with open("registro_pronosticos.txt", "r", encoding="utf-8") as file:
            pronosticos = file.readlines()
    except FileNotFoundError:
        pronosticos = ["No hay pronósticos registrados aún."]

    pronosticos = pronosticos[-30:]

    mensaje = "📊 Últimos 30 pronósticos:\n\n"
    for pronostico in pronosticos:
        linea = pronostico.strip()
        if "Ganado" in linea:
            linea = "✅ " + linea
        elif "Perdido" in linea:
            linea = "❌ " + linea
        mensaje += f"{linea}\n"

    query = update.callback_query
    query.message.reply_text(mensaje)

# 📈 Pronósticos del día
def mostrar_pronosticos_dia(update: Update, context: CallbackContext):
    hoy = datetime.today().strftime('%Y-%m-%d')
    try:
        with open("registro_pronosticos.txt", "r", encoding="utf-8") as file:
            pronosticos = file.readlines()
    except FileNotFoundError:
        update.callback_query.message.reply_text("⚠️ No hay pronósticos registrados aún.")
        return

    pronosticos_hoy = [p for p in pronosticos if hoy in p]
    if not pronosticos_hoy:
        update.callback_query.message.reply_text("📜 Aún no se han registrado pronósticos para hoy.")
        return

    mensaje = f"📈 Pronósticos del día:\n\n"
    for linea in pronosticos_hoy:
        linea = linea.strip()
        if "Ganado" in linea:
            mensaje += f"✅ {linea}\n"
        elif "Perdido" in linea:
            mensaje += f"❌ {linea}\n"
        else:
            mensaje += f"➖ {linea}\n"

    update.callback_query.message.reply_text(mensaje)

# 🧠 Último pronóstico
def mostrar_ultimo_pick(update: Update, context: CallbackContext):
    try:
        with open("ultimo_pick.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            mensaje = data.get("mensaje", "⚠️ No se encontró ningún pronóstico.")

        update.callback_query.message.reply_text(mensaje)
    except Exception as e:
        update.callback_query.message.reply_text("❌ No se pudo leer el último pronóstico.")
        print(f"Error leyendo ultimo_pick.json: {e}")

# ⚽ Partidos del día
def mostrar_partidos_dia(update: Update, context: CallbackContext):
    try:
        with open("partidos.json", "r", encoding="utf-8") as file:
            partidos = json.load(file)
    except FileNotFoundError:
        update.callback_query.message.reply_text("⚠️ No hay partidos cargados aún.")
        return

    if not partidos:
        update.callback_query.message.reply_text("⚠️ Hoy no hay partidos programados.")
        return

    mensaje = f"⚽ MATCHES OF THE DAY ({datetime.today().strftime('%Y-%m-%d')})\n\n"
    for partido in partidos:
        mensaje += (
            f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
            f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"
        )

    update.callback_query.message.reply_text(mensaje)

# 📈 Progreso (solo para el admin)
def mostrar_progreso(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        update.callback_query.message.reply_text("⛔ Esta función es privada.")
        return

    try:
        with open("progreso.json", "r", encoding="utf-8") as f:
            progreso = json.load(f)

        deposito = progreso["deposito"]
        meta = progreso["meta"]
        saldo = progreso["saldo_actual"]
        progreso_porcentaje = (saldo - deposito) / (meta - deposito) * 100
        progreso_porcentaje = max(0, min(progreso_porcentaje, 100))

        mensaje = (
            f"📈 Tu progreso actual:\n\n"
            f"💵 Depósito inicial: ${deposito}\n"
            f"🎯 Meta objetivo: ${meta}\n"
            f"📈 Saldo actual: ${saldo}\n"
            f"✅ Avance: {progreso_porcentaje:.2f}%"
        )

        update.callback_query.message.reply_text(mensaje)
    except Exception as e:
        update.callback_query.message.reply_text("❌ Error al leer el progreso.")
        print(f"Error leyendo progreso.json: {e}")

# ⚙️ Manejo de botones del menú
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'estadisticas':
        mostrar_estadisticas(update, context)
    elif data == 'pronosticos':
        mostrar_pronosticos_dia(update, context)
    elif data == 'ultimopick':
        mostrar_ultimo_pick(update, context)
    elif data == 'partidos_dia':
        mostrar_partidos_dia(update, context)
    elif data == 'progreso':
        mostrar_progreso(update, context)
    elif data == 'configuracion':
        query.edit_message_text(text="⚙️ Opciones de configuración del bot.")

# Iniciar el bot
def main():
    try:
        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CallbackQueryHandler(button))

        print("🤖 Bot SergioBets está en línea.")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")

if __name__ == '__main__':
    main()