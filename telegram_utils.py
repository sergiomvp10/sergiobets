import requests

TELEGRAM_TOKEN = '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A'
TELEGRAM_CHAT_ID = '7659029315'

def enviar_telegram(token, chat_id, mensaje):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje
        }
        requests.post(url, data=payload)
    except Exception as e:
        print("Error enviando mensaje a Telegram:", e)
