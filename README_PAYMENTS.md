# SergioBets - Sistema de Pagos NOWPayments

## Configuración del Sistema de Pagos

### Variables de Entorno Requeridas (.env)
```
NOWPAYMENTS_API_KEY=S8G1SYG-0QT4ADE-KM01W2R-3CND6KS
TELEGRAM_BOT_TOKEN=7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A
ADMIN_TELEGRAM_ID=6712715589
```

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Estructura del Sistema de Pagos

#### Archivos Principales
- `pagos/payments.py` - API de NOWPayments y gestión de pagos
- `pagos/webhook_server.py` - Servidor de webhooks para confirmaciones
- `pagos/start_webhook_server.py` - Script de inicio del servidor
- `pagos/test_payments.py` - Pruebas del sistema

#### Archivos de Datos
- `pagos/registro_pagos.csv` - Historial de pagos confirmados
- `pagos/pagos_pendientes.json` - Pagos en proceso
- `pagos/usuarios_vip.json` - Usuarios VIP activos

### Configuración de Membresía
- **Precio**: $12.00 USD
- **Duración**: 7 días de acceso VIP
- **Monedas aceptadas**: USDT (ERC-20) y Litecoin

### Flujo de Pago

1. **Usuario inicia pago**: Desde bot de Telegram → "Membresía" → Selecciona moneda
2. **Generación de pago**: Sistema crea dirección única y monto específico
3. **Usuario realiza pago**: Envía criptomoneda a la dirección generada
4. **Confirmación automática**: Webhook de NOWPayments confirma el pago
5. **Activación VIP**: Sistema activa acceso VIP automáticamente
6. **Notificaciones**: Admin y usuario reciben confirmación por Telegram

### Ejecutar el Sistema

#### 1. Iniciar Servidor de Webhooks
```bash
cd pagos
python start_webhook_server.py
```

#### 2. Exponer Puerto Públicamente (para producción)
```bash
# Usando ngrok (ejemplo)
ngrok http 5000
```

#### 3. Configurar Webhook en NOWPayments
- URL: `https://tu-dominio.com/webhook/nowpayments`
- Método: POST

#### 4. Probar el Sistema
```bash
python pagos/test_payments.py
```

### API Endpoints

#### Crear Pago (Testing)
```
POST /api/create_payment
{
    "user_id": "123456789",
    "username": "test_user",
    "currency": "ltc",
    "membership_type": "weekly"
}
```

#### Verificar Estado de Pago
```
GET /api/payment_status/{payment_id}
```

#### Obtener Usuarios VIP
```
GET /api/vip_users
```

#### Historial de Pagos
```
GET /api/payment_history
```

### Monedas Soportadas
- **USDT**: `usdterc20` (Ethereum ERC-20)
- **Litecoin**: `ltc`

### Notificaciones

#### Mensaje al Admin (ID: 6712715589)
```
✅ Pago Confirmado
👤 Usuario: @username
💰 Monto: 0.001 LTC
📆 Fecha: 2024-08-04 12:30:45
🔐 Acceso VIP activado correctamente
```

#### Mensaje al Usuario
```
✅ Tu pago fue confirmado. Acceso VIP activado.
```

### Seguridad
- API keys almacenadas en `.env` (no en código)
- Validación de webhooks de NOWPayments
- Registro completo de todas las transacciones
- Manejo de errores y timeouts

### Troubleshooting

#### Error: "Invalid API key"
- Verificar que `NOWPAYMENTS_API_KEY` esté correcta en `.env`
- Confirmar que la API key tenga permisos necesarios

#### Webhook no recibe confirmaciones
- Verificar que el servidor esté ejecutándose en puerto 5000
- Confirmar que el puerto esté expuesto públicamente
- Revisar configuración de webhook en NOWPayments dashboard

#### Pagos no se confirman automáticamente
- Verificar logs del servidor de webhooks
- Confirmar que el `payment_id` coincida entre sistemas
- Revisar estado del pago en NOWPayments dashboard
