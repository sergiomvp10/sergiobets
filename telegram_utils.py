import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A')
TELEGRAM_CHAT_ID = '7659029315'

def enviar_telegram(token=None, chat_id=None, mensaje=None):
    if mensaje is None:
        return False
    
    if token is None:
        token = TELEGRAM_TOKEN
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje
        }
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión enviando mensaje a Telegram: {e}")
        return False
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return False
