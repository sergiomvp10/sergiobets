# BetGeniuX - Sistema de Pagos NOWPayments

## Configuración del Sistema de Pagos

### Variables de Entorno Requeridas (.env)
```
NOWPAYMENTS_API_KEY=tu_api_key_aqui
TELEGRAM_BOT_TOKEN=tu_token_de_botfather_aqui
ADMIN_TELEGRAM_ID=tu_telegram_id_aqui
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

#### Método Recomendado: Launcher Automático con ngrok
```bash
# Instalar ngrok primero desde https://ngrok.com/download
# Luego ejecutar el launcher automático:
python launch_with_ngrok.py
```

Este script automáticamente:
- Inicia el servidor webhook en puerto 5000
- Lanza túnel ngrok para exposición pública
- Obtiene y guarda la URL pública automáticamente en `ngrok_url.txt`
- Actualiza la URL en el bot de Telegram dinámicamente
- Mantiene todo corriendo hasta que presiones Ctrl+C
- Proporciona enlaces directos para pagos web

#### Características del Launcher:
- ✅ Detección automática de ngrok instalado
- ✅ Manejo de túneles existentes
- ✅ Extracción de URL desde API de ngrok (http://127.0.0.1:4040/api/tunnels)
- ✅ Persistencia de URL en archivo `ngrok_url.txt`
- ✅ Integración automática con bot de Telegram
- ✅ Endpoints listos: `/webhook/nowpayments` y `/api/create_payment`

#### Método Manual (para desarrollo)

##### 1. Iniciar Servidor de Webhooks
```bash
cd pagos
python start_webhook_server.py
```

##### 2. Exponer Puerto Públicamente
```bash
# En otra terminal:
ngrok http 5000
```

##### 3. Configurar Webhook en NOWPayments
- URL: `https://tu-ngrok-url.ngrok.io/webhook/nowpayments`
- Método: POST
- Eventos: payment.finished, payment.confirmed

##### 4. Probar el Sistema
```bash
python test_ngrok_integration.py
```

### ⚠️ Importante para Producción
- **NO uses localhost** en producción
- **Siempre usa ngrok o un dominio público** para webhooks
- El launcher automático maneja esto por ti
- La URL de ngrok se actualiza automáticamente en el bot de Telegram
- Los usuarios pueden pagar tanto desde el bot como desde la interfaz web

### Integración con Telegram Bot
El bot de Telegram ahora incluye:
- Botón "Membresía" con opciones de pago USDT/Litecoin
- Enlaces dinámicos a la interfaz web de pagos
- Verificación automática de estado de pagos
- Notificaciones de confirmación automáticas

Cuando ngrok está corriendo, el bot muestra:
```
💳 También puedes pagar directamente aquí:
👉 [Pagar ahora](https://tu-ngrok-url.ngrok.io/api/create_payment)
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

#### Error: "ngrok not found"
- Instalar ngrok desde https://ngrok.com/download
- Agregar ngrok al PATH del sistema
- Configurar authtoken: `ngrok authtoken YOUR_TOKEN`

#### Webhook no recibe confirmaciones
- Verificar que el servidor esté ejecutándose en puerto 5000
- Confirmar que el puerto esté expuesto públicamente con ngrok
- Revisar configuración de webhook en NOWPayments dashboard
- Verificar que la URL de webhook sea accesible desde internet

#### Pagos no se confirman automáticamente
- Verificar logs del servidor de webhooks
- Confirmar que el `payment_id` coincida entre sistemas
- Revisar estado del pago en NOWPayments dashboard
- Verificar que ngrok esté corriendo y la URL sea válida

#### Bot de Telegram no muestra enlace de pago
- Verificar que `ngrok_url.txt` contenga una URL válida
- Reiniciar el launcher: `python launch_with_ngrok.py`
- Verificar que el bot tenga acceso al archivo de URL
