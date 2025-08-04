import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from payments import PaymentManager
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
        
        enviar_telegram(mensaje, TELEGRAM_TOKEN, ADMIN_TELEGRAM_ID)
        
    except Exception as e:
        logger.error(f"Error enviando notificación al admin: {e}")

def await_send_user_confirmation(payment_result):
    """Enviar confirmación al usuario"""
    try:
        user_id = payment_result.get('user_id')
        
        mensaje = "✅ Tu pago fue confirmado. Acceso VIP activado."
        
        enviar_telegram(mensaje, TELEGRAM_TOKEN, user_id)
        
    except Exception as e:
        logger.error(f"Error enviando confirmación al usuario: {e}")

@app.route('/api/create_payment', methods=['POST'])
def create_payment_api():
    """API endpoint para crear pagos (para testing)"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        username = data.get('username', 'test_user')
        currency = data.get('currency', 'usdt')
        membership_type = data.get('membership_type', 'monthly')
        
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
    return jsonify({"status": "healthy", "service": "SergioBets Payment Server"}), 200

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("🚀 Iniciando servidor de pagos SergioBets...")
    print("📡 Webhook endpoint: /webhook/nowpayments")
    print("🔧 API endpoint: /api/create_payment")
    print("💳 Servidor listo para recibir pagos...")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
