import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
try:
    from .payments import PaymentManager
except ImportError:
    from payments import PaymentManager

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from telegram_utils import enviar_telegram
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)
payment_manager = PaymentManager()

ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID', '6712715589')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

@app.route('/webhook/nowpayments', methods=['POST'])
def nowpayments_webhook():
    """Webhook para recibir notificaciones de NOWPayments"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        payment_status = data.get('payment_status')
        payment_id = data.get('payment_id')
        
        logger.info(f"Webhook recibido - Payment ID: {payment_id}, Status: {payment_status}")
        
        if payment_status in ['confirmed', 'finished']:
            result = payment_manager.confirm_payment(payment_id)
            
            if result.get("success"):
                await_send_admin_notification(result)
                
                await_send_user_confirmation(result)
                
                return jsonify({"status": "success", "message": "Payment processed"}), 200
            else:
                logger.error(f"Error procesando pago: {result.get('error')}")
                return jsonify({"error": result.get('error')}), 400
        
        return jsonify({"status": "ignored", "message": f"Status {payment_status} not processed"}), 200
        
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return jsonify({"error": str(e)}), 500

def await_send_admin_notification(payment_result):
    """Enviar notificación al administrador"""
    try:
        username = payment_result.get('username', 'sin_username')
        amount = payment_result.get('amount', '0')
        currency = payment_result.get('currency', '').upper()
        membership_type = payment_result.get('membership_type', 'monthly')
        
        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        mensaje = f"""✅ Pago Confirmado
👤 Usuario: @{username}
💰 Monto: {amount} {currency}
📆 Fecha: {fecha}
🔐 Acceso VIP activado correctamente"""
        
        if TELEGRAM_TOKEN and ADMIN_TELEGRAM_ID:
            enviar_telegram(TELEGRAM_TOKEN, ADMIN_TELEGRAM_ID, mensaje)
        else:
            logger.warning("Telegram token o admin ID no configurados")
        
    except Exception as e:
        logger.error(f"Error enviando notificación al admin: {e}")

def await_send_user_confirmation(payment_result):
    """Enviar confirmación al usuario"""
    try:
        user_id = payment_result.get('user_id')
        
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from access_manager import access_manager
            
            if access_manager.otorgar_acceso(user_id, 7):
                logger.info(f"✅ Acceso premium otorgado a usuario {user_id}")
                
                mensaje = access_manager.generar_mensaje_confirmacion_premium(user_id)
                logger.info(f"✅ Mensaje de confirmación generado para usuario {user_id}")
            else:
                logger.error(f"❌ Error otorgando acceso premium a usuario {user_id}")
                mensaje = "✅ Tu pago fue confirmado. Acceso VIP activado."
                
        except Exception as e:
            logger.error(f"❌ Error activando acceso VIP: {e}")
            mensaje = "✅ Tu pago fue confirmado. Acceso VIP activado."
        
        if TELEGRAM_TOKEN and user_id:
            enviar_telegram(TELEGRAM_TOKEN, user_id, mensaje)
            logger.info(f"✅ Mensaje de confirmación enviado a usuario {user_id}")
        else:
            logger.warning("Telegram token o user ID no disponibles")
        
    except Exception as e:
        logger.error(f"Error enviando confirmación al usuario: {e}")

@app.route('/api/create_payment', methods=['POST', 'GET'])
def create_payment_api():
    """API endpoint para crear pagos"""
    try:
        if request.method == 'GET':
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>BetGeniuX - Crear Pago</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                    button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                    .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
                    .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                    .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                </style>
            </head>
            <body>
                <h1>🎯 BetGeniuX - Crear Pago VIP</h1>
                <p>Crea un pago para membresía VIP de 7 días por $12 USD</p>
                
                <form id="paymentForm">
                    <div class="form-group">
                        <label for="user_id">ID de Usuario Telegram:</label>
                        <input type="text" id="user_id" name="user_id" required placeholder="123456789">
                    </div>
                    
                    <div class="form-group">
                        <label for="username">Nombre de Usuario:</label>
                        <input type="text" id="username" name="username" placeholder="@usuario">
                    </div>
                    
                    <div class="form-group">
                        <label for="currency">Criptomoneda:</label>
                        <select id="currency" name="currency" required>
                            <option value="usdterc20">USDT (ERC-20)</option>
                            <option value="ltc">Litecoin (LTC)</option>
                        </select>
                    </div>
                    
                    <button type="submit">💳 Crear Pago</button>
                </form>
                
                <div id="result"></div>
                
                <script>
                document.getElementById('paymentForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const formData = new FormData(e.target);
                    const data = Object.fromEntries(formData);
                    data.membership_type = 'weekly';
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = '<p>⏳ Creando pago...</p>';
                    
                    try {
                        const response = await fetch('/api/create_payment', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            resultDiv.innerHTML = `
                                <div class="result success">
                                    <h3>✅ Pago creado exitosamente</h3>
                                    <p><strong>ID de Pago:</strong> ${result.payment_id}</p>
                                    <p><strong>Dirección:</strong> <code>${result.pay_address}</code></p>
                                    <p><strong>Monto:</strong> ${result.pay_amount} ${result.pay_currency.toUpperCase()}</p>
                                    <p><strong>Estado:</strong> ${result.payment_status}</p>
                                    <p>💡 Envía exactamente <strong>${result.pay_amount} ${result.pay_currency.toUpperCase()}</strong> a la dirección mostrada.</p>
                                </div>
                            `;
                        } else {
                            resultDiv.innerHTML = `
                                <div class="result error">
                                    <h3>❌ Error creando pago</h3>
                                    <p>${result.error}</p>
                                </div>
                            `;
                        }
                    } catch (error) {
                        resultDiv.innerHTML = `
                            <div class="result error">
                                <h3>❌ Error de conexión</h3>
                                <p>${error.message}</p>
                            </div>
                        `;
                    }
                });
                </script>
            </body>
            </html>
            """
        
        data = request.get_json()
        
        user_id = data.get('user_id')
        username = data.get('username', 'web_user')
        currency = data.get('currency', 'usdterc20')
        membership_type = data.get('membership_type', 'weekly')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        result = payment_manager.create_membership_payment(
            user_id=user_id,
            username=username,
            currency=currency,
            membership_type=membership_type
        )
        
        return jsonify(result), 200 if result.get("success") else 400
        
    except Exception as e:
        logger.error(f"Error en API create_payment: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment_status/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """Obtener estado de un pago"""
    try:
        nowpayments = payment_manager.nowpayments
        status = nowpayments.get_payment_status(payment_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error obteniendo estado del pago: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/vip_users', methods=['GET'])
def get_vip_users():
    """Obtener lista de usuarios VIP"""
    try:
        vip_users = payment_manager.get_vip_users()
        return jsonify(vip_users), 200
    except Exception as e:
        logger.error(f"Error obteniendo usuarios VIP: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment_history', methods=['GET'])
def get_payment_history():
    """Obtener historial de pagos"""
    try:
        history = payment_manager.get_payment_history()
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "BetGeniuX Payment Server"}), 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("🚀 Iniciando servidor de pagos BetGeniuX...")
    print("📡 Webhook endpoint: /webhook/nowpayments")
    print("🔧 API endpoint: /api/create_payment")
    print("💳 Servidor listo para recibir pagos...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
