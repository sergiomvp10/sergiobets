import os
import json
import csv
import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class NOWPaymentsAPI:
    """Cliente para la API de NOWPayments"""
    
    def __init__(self):
        self.api_key = os.getenv('NOWPAYMENTS_API_KEY')
        self.base_url = "https://api.nowpayments.io/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
    def get_available_currencies(self) -> List[str]:
        """Obtener monedas disponibles"""
        try:
            response = requests.get(f"{self.base_url}/currencies", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                currencies = data.get('currencies', [])
                if isinstance(currencies, list):
                    return currencies
                else:
                    return []
            return []
        except Exception as e:
            logger.error(f"Error obteniendo monedas: {e}")
            return []
    
    def get_minimum_payment_amount(self, currency_from: str, currency_to: str = "usd") -> float:
        """Obtener monto mínimo de pago"""
        try:
            url = f"{self.base_url}/min-amount"
            params = {
                "currency_from": currency_from,
                "currency_to": currency_to
            }
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return float(data.get('min_amount', 0))
            return 0
        except Exception as e:
            logger.error(f"Error obteniendo monto mínimo: {e}")
            return 0
    
    def create_payment(self, price_amount: float, price_currency: str, pay_currency: str, 
                      order_id: str, order_description: str, ipn_callback_url: str = None) -> Dict:
        """Crear un nuevo pago"""
        try:
            payload = {
                "price_amount": price_amount,
                "price_currency": price_currency,
                "pay_currency": pay_currency,
                "order_id": order_id,
                "order_description": order_description
            }
            
            if ipn_callback_url:
                payload["ipn_callback_url"] = ipn_callback_url
            
            response = requests.post(f"{self.base_url}/payment", 
                                   headers=self.headers, 
                                   json=payload)
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Error creando pago: {response.status_code} - {response.text}")
                return {"error": f"Error {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"Error en create_payment: {e}")
            return {"error": str(e)}
    
    def get_payment_status(self, payment_id: str) -> Dict:
        """Obtener estado de un pago"""
        try:
            response = requests.get(f"{self.base_url}/payment/{payment_id}", 
                                  headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Error {response.status_code}"}
        except Exception as e:
            logger.error(f"Error obteniendo estado del pago: {e}")
            return {"error": str(e)}

class PaymentManager:
    """Gestor de pagos para SergioBets"""
    
    def __init__(self):
        self.nowpayments = NOWPaymentsAPI()
        self.payments_file = "pagos/registro_pagos.csv"
        self.pending_payments_file = "pagos/pagos_pendientes.json"
        self.vip_users_file = "pagos/usuarios_vip.json"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Asegurar que los archivos necesarios existan"""
        os.makedirs("pagos", exist_ok=True)
        
        if not os.path.exists(self.payments_file):
            with open(self.payments_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'fecha', 'user_id', 'username', 'monto', 'moneda', 
                    'payment_id', 'order_id', 'estado', 'direccion_pago'
                ])
        
        for file_path in [self.pending_payments_file, self.vip_users_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
    
    def create_membership_payment(self, user_id: str, username: str, 
                                currency: str, membership_type: str = "weekly") -> Dict:
        """Crear pago para membresía"""
        
        price_usd = 12.00
        order_id = f"sergiobets_{user_id}_{int(datetime.now().timestamp())}"
        description = f"SergioBets 7-Day VIP Access - User {username}"
        
        payment_data = self.nowpayments.create_payment(
            price_amount=price_usd,
            price_currency="usd",
            pay_currency=currency.lower(),
            order_id=order_id,
            order_description=description
        )
        
        if "error" not in payment_data:
            self._save_pending_payment(user_id, username, payment_data, membership_type)
            
            return {
                "success": True,
                "payment_id": payment_data.get("payment_id"),
                "pay_address": payment_data.get("pay_address"),
                "pay_amount": payment_data.get("pay_amount"),
                "pay_currency": payment_data.get("pay_currency"),
                "order_id": order_id,
                "price_amount": price_usd
            }
        else:
            return {"success": False, "error": payment_data.get("error")}
    
    def _save_pending_payment(self, user_id: str, username: str, payment_data: Dict, membership_type: str):
        """Guardar pago pendiente"""
        try:
            with open(self.pending_payments_file, 'r', encoding='utf-8') as f:
                pending = json.load(f)
            
            payment_id = payment_data.get("payment_id")
            pending[payment_id] = {
                "user_id": user_id,
                "username": username,
                "membership_type": membership_type,
                "created_at": datetime.now().isoformat(),
                "payment_data": payment_data
            }
            
            with open(self.pending_payments_file, 'w', encoding='utf-8') as f:
                json.dump(pending, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando pago pendiente: {e}")
    
    def confirm_payment(self, payment_id: str) -> Dict:
        """Confirmar pago y activar VIP"""
        try:
            with open(self.pending_payments_file, 'r', encoding='utf-8') as f:
                pending = json.load(f)
            
            if payment_id not in pending:
                return {"success": False, "error": "Pago no encontrado"}
            
            payment_info = pending[payment_id]
            user_id = payment_info["user_id"]
            username = payment_info["username"]
            membership_type = payment_info["membership_type"]
            payment_data = payment_info["payment_data"]
            
            self._register_confirmed_payment(payment_info, payment_data)
            
            self._activate_vip_user(user_id, username, membership_type)
            
            del pending[payment_id]
            with open(self.pending_payments_file, 'w', encoding='utf-8') as f:
                json.dump(pending, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "user_id": user_id,
                "username": username,
                "amount": payment_data.get("pay_amount"),
                "currency": payment_data.get("pay_currency"),
                "membership_type": membership_type
            }
            
        except Exception as e:
            logger.error(f"Error confirmando pago: {e}")
            return {"success": False, "error": str(e)}
    
    def _register_confirmed_payment(self, payment_info: Dict, payment_data: Dict):
        """Registrar pago confirmado en CSV"""
        try:
            with open(self.payments_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    payment_info["user_id"],
                    payment_info["username"],
                    payment_data.get("pay_amount", ""),
                    payment_data.get("pay_currency", ""),
                    payment_data.get("payment_id", ""),
                    payment_data.get("order_id", ""),
                    "confirmed",
                    payment_data.get("pay_address", "")
                ])
        except Exception as e:
            logger.error(f"Error registrando pago en CSV: {e}")
    
    def _activate_vip_user(self, user_id: str, username: str, membership_type: str):
        """Activar usuario VIP"""
        try:
            with open(self.vip_users_file, 'r', encoding='utf-8') as f:
                vip_users = json.load(f)
            
            from datetime import timedelta
            now = datetime.now()
            expiry = now + timedelta(days=7)
            
            vip_users[user_id] = {
                "username": username,
                "membership_type": membership_type,
                "activated_at": now.isoformat(),
                "expires_at": expiry.isoformat(),
                "active": True
            }
            
            with open(self.vip_users_file, 'w', encoding='utf-8') as f:
                json.dump(vip_users, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error activando usuario VIP: {e}")
    
    def is_vip_user(self, user_id: str) -> bool:
        """Verificar si un usuario es VIP activo"""
        try:
            with open(self.vip_users_file, 'r', encoding='utf-8') as f:
                vip_users = json.load(f)
            
            if user_id not in vip_users:
                return False
            
            user_data = vip_users[user_id]
            if not user_data.get("active", False):
                return False
            
            expiry_date = datetime.fromisoformat(user_data["expires_at"])
            return datetime.now() < expiry_date
            
        except Exception as e:
            logger.error(f"Error verificando usuario VIP: {e}")
            return False
    
    def get_vip_users(self) -> Dict:
        """Obtener lista de usuarios VIP"""
        try:
            with open(self.vip_users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error obteniendo usuarios VIP: {e}")
            return {}
    
    def get_payment_history(self) -> List[Dict]:
        """Obtener historial de pagos"""
        try:
            payments = []
            with open(self.payments_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payments.append(row)
            return payments
        except Exception as e:
            logger.error(f"Error obteniendo historial de pagos: {e}")
            return []
