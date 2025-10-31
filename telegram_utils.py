import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en el archivo .env")

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7659029315')
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

def cargar_usuarios_premium(bot_username="BetGeniuXbot"):
    """Cargar lista de usuarios premium activos para bot específico"""
    try:
        from access_manager import access_manager
        usuarios_premium = access_manager.listar_usuarios_premium()
        return [
            {'user_id': user['user_id'], 'username': user.get('username', 'Unknown'), 'first_name': user.get('first_name', 'Usuario')}
            for user in usuarios_premium
            if user.get('bot_username') == bot_username
        ]
    except Exception as e:
        print(f"Error cargando usuarios premium del bot {bot_username}: {e}")
        return []

def cargar_usuarios_no_premium(bot_username="BetGeniuXbot"):
    """Cargar lista de usuarios sin membresía activa para bot específico"""
    try:
        from access_manager import access_manager
        todos_usuarios = access_manager.listar_usuarios_por_bot(bot_username)
        usuarios_premium_ids = {user['user_id'] for user in access_manager.listar_usuarios_premium()}
        
        return [
            {'user_id': user['user_id'], 'username': user.get('username', 'Unknown'), 'first_name': user.get('first_name', 'Usuario')}
            for user in todos_usuarios
            if user['user_id'] not in usuarios_premium_ids
        ]
    except Exception as e:
        print(f"Error cargando usuarios no premium del bot {bot_username}: {e}")
        return []

def enviar_telegram_masivo(mensaje, token=None, bot_username="BetGeniuXbot", only_premium=False, exclude_premium=False):
    """Enviar mensaje a usuarios del bot específico
    
    Args:
        mensaje: Mensaje a enviar
        token: Token del bot (opcional, usa TELEGRAM_BOT_TOKEN por defecto)
        bot_username: Nombre del bot (por defecto "BetGeniuXbot")
        only_premium: Si True, solo envía a usuarios premium activos (por defecto False)
        exclude_premium: Si True, solo envía a usuarios sin membresía activa (por defecto False)
    """
    if mensaje is None:
        return {"exito": False, "error": "Mensaje vacío"}
    
    if token is None:
        token = TELEGRAM_TOKEN
    
    if only_premium:
        usuarios = cargar_usuarios_premium(bot_username)
        audiencia = "premium activos"
    elif exclude_premium:
        usuarios = cargar_usuarios_no_premium(bot_username)
        audiencia = "sin membresía activa"
    else:
        usuarios = cargar_usuarios_registrados(bot_username)
        audiencia = "registrados"
    
    if not usuarios:
        if only_premium or exclude_premium:
            print(f"⚠️ No hay usuarios {audiencia} en el bot {bot_username}.")
            return {
                "exito": False,
                "total_usuarios": 0,
                "enviados_exitosos": 0,
                "errores": 0,
                "usuarios_bloqueados": 0,
                "detalles_errores": [f"No hay usuarios {audiencia}"],
                "audiencia": audiencia
            }
        else:
            print("⚠️ No hay usuarios registrados. Enviando a chat_id por defecto.")
            exito = enviar_telegram(token, TELEGRAM_CHAT_ID, mensaje)
            return {
                "exito": exito,
                "total_usuarios": 0,
                "enviados_exitosos": 1 if exito else 0,
                "errores": 0 if exito else 1,
                "usuarios_bloqueados": 0,
                "detalles_errores": [] if exito else ["Error enviando a chat_id por defecto"],
                "audiencia": audiencia
            }
    
    resultados = {
        "total_usuarios": len(usuarios),
        "enviados_exitosos": 0,
        "errores": 0,
        "usuarios_bloqueados": 0,
        "detalles_errores": [],
        "audiencia": audiencia
    }
    
    print(f"📤 Enviando mensaje a {len(usuarios)} usuarios {audiencia}...")
    
    for usuario in usuarios:
        try:
            user_id = usuario['user_id']
            username = usuario['username']
            first_name = usuario['first_name']
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": str(user_id).strip(),
                "text": mensaje
            }
            
            response = requests.post(url, data=payload, timeout=10)
            
            try:
                data = response.json()
            except ValueError:
                resultados["errores"] += 1
                error_msg = f"Respuesta no-JSON de Telegram para {first_name}"
                resultados["detalles_errores"].append(error_msg)
                print(f"  ❌ {error_msg}")
                continue
            
            ok = bool(data.get("ok"))
            if ok:
                resultados["enviados_exitosos"] += 1
                print(f"  ✅ Enviado a {first_name} (@{username})")
            else:
                desc = data.get("description", "sin descripción")
                code = data.get("error_code", response.status_code)
                
                if code == 403 or "blocked" in desc.lower() or "forbidden" in desc.lower():
                    resultados["usuarios_bloqueados"] += 1
                    print(f"  🚫 Usuario bloqueó el bot: {first_name} (@{username})")
                else:
                    resultados["errores"] += 1
                    error_msg = f"Telegram error {code} para {first_name}: {desc}"
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

def enviar_telegram(token=None, chat_id=None, mensaje=None, parse_mode=None, timeout=10):
    """Función original para compatibilidad - envía a un chat_id específico"""
    if mensaje is None:
        return False
    
    if token is None:
        token = TELEGRAM_TOKEN
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    
    chat_id = str(chat_id).strip()
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
            
        response = requests.post(url, data=payload, timeout=timeout)
        
        try:
            data = response.json()
        except ValueError:
            print(f"❌ Telegram non-JSON response: {response.status_code} {response.text[:200]}")
            return False
        
        ok = bool(data.get("ok"))
        if ok:
            print(f"✅ Mensaje enviado exitosamente a chat_id: {chat_id}")
            return True
        
        desc = data.get("description", "sin descripción")
        code = data.get("error_code", response.status_code)
        print(f"❌ Telegram error {code}: {desc} (chat_id: {chat_id})")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión enviando mensaje a Telegram: {e}")
        return False
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")
        return False
