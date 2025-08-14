import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c')
TELEGRAM_CHAT_ID = '7659029315'
USUARIOS_FILE = 'usuarios.txt'

def cargar_usuarios_registrados(bot_username="BetGeniuXbot"):
    """Cargar lista de usuarios registrados para bot específico"""
    try:
        from access_manager import access_manager
        usuarios_bot = access_manager.listar_usuarios_por_bot(bot_username)
        return [{'user_id': user['user_id'], 'username': user['username'], 'first_name': user['first_name']} for user in usuarios_bot]
    except Exception as e:
        print(f"Error cargando usuarios del bot {bot_username}: {e}")
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
        except Exception as e2:
            print(f"Error cargando usuarios desde archivo: {e2}")
        return usuarios

def enviar_telegram_masivo(mensaje, token=None, bot_username="BetGeniuXbot"):
    """Enviar mensaje a todos los usuarios del bot específico"""
    if mensaje is None:
        return {"exito": False, "error": "Mensaje vacío"}
    
    if token is None:
        token = TELEGRAM_TOKEN
    
    usuarios = cargar_usuarios_registrados(bot_username)
    
    if not usuarios:
        print("⚠️ No hay usuarios registrados. Enviando a chat_id por defecto.")
        exito = enviar_telegram(token, TELEGRAM_CHAT_ID, mensaje)
        return {
            "exito": exito,
            "total_usuarios": 0,
            "enviados_exitosos": 1 if exito else 0,
            "errores": 0 if exito else 1,
            "usuarios_bloqueados": 0,
            "detalles_errores": [] if exito else ["Error enviando a chat_id por defecto"]
        }
    
    resultados = {
        "total_usuarios": len(usuarios),
        "enviados_exitosos": 0,
        "errores": 0,
        "usuarios_bloqueados": 0,
        "detalles_errores": []
    }
    
    print(f"📤 Enviando mensaje a {len(usuarios)} usuarios registrados...")
    
    for usuario in usuarios:
        try:
            user_id = usuario['user_id']
            username = usuario['username']
            first_name = usuario['first_name']
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": mensaje
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            resultados["enviados_exitosos"] += 1
            print(f"  ✅ Enviado a {first_name} (@{username})")
            
        except requests.exceptions.HTTPError as e:
            if "403" in str(e) or "blocked" in str(e).lower():
                resultados["usuarios_bloqueados"] += 1
                print(f"  🚫 Usuario bloqueó el bot: {first_name} (@{username})")
            else:
                resultados["errores"] += 1
                error_msg = f"Error HTTP enviando a {first_name}: {e}"
                resultados["detalles_errores"].append(error_msg)
                print(f"  ❌ {error_msg}")
                
        except requests.exceptions.RequestException as e:
            resultados["errores"] += 1
            error_msg = f"Error de conexión enviando a {first_name}: {e}"
            resultados["detalles_errores"].append(error_msg)
            print(f"  ❌ {error_msg}")
            
        except Exception as e:
            resultados["errores"] += 1
            error_msg = f"Error general enviando a {first_name}: {e}"
            resultados["detalles_errores"].append(error_msg)
            print(f"  ❌ {error_msg}")
    
    print(f"📊 Resumen: {resultados['enviados_exitosos']} enviados, {resultados['errores']} errores, {resultados['usuarios_bloqueados']} bloqueados")
    
    resultados["exito"] = resultados["enviados_exitosos"] > 0
    return resultados

def enviar_telegram(token=None, chat_id=None, mensaje=None):
    """Función original para compatibilidad - envía a un chat_id específico"""
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
