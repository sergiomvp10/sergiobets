# 🤖 GUÍA DE DESPLIEGUE: BOT LISTENER EN RENDER

## 📋 RESUMEN

El **scheduler** ya está funcionando 24/7 enviando predicciones automáticamente.

Ahora necesitas desplegar el **bot listener** para que responda a comandos como /start, /help, etc.

---

## 🚀 PASOS PARA DESPLEGAR EL BOT LISTENER

### 1️⃣ IR A RENDER DASHBOARD

1. Ve a: https://dashboard.render.com
2. Asegúrate de estar en tu cuenta

### 2️⃣ CREAR NUEVO BACKGROUND WORKER

1. Click en **"New +"** (arriba derecha)
2. Selecciona **"Background Worker"**
3. Conecta tu repositorio: **sergiomvp10/sergiobets**
4. Click en **"Connect"**

### 3️⃣ CONFIGURAR EL SERVICIO

**Configuración básica:**
- **Name:** `betgeniux-bot`
- **Region:** Oregon (US West) - *mismo que el scheduler*
- **Branch:** `devin/1761852552-update-footystats-api`
- **Root Directory:** (dejar vacío)
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python telegram_bot_listener.py`

**Plan:**
- Selecciona **"Starter"** ($7/mes) - *mismo que el scheduler*

### 4️⃣ CONFIGURAR VARIABLES DE ENTORNO

Click en **"Advanced"** y agrega estas variables de entorno:

```
TELEGRAM_BOT_TOKEN=8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c
ADMIN_TELEGRAM_ID=7659029315
PAYMENTS_GROUP_ID=7659029315
DATABASE_URL=(copiar del scheduler betgeniux-scheduler)
TIMEZONE=America/Phoenix
FOOTYSTATS_API_KEY=1d19b51cc6be6520d3b96a60c3d0fb862b120d9826886671c28dd796989048ee
```

**IMPORTANTE:** Copia el `DATABASE_URL` del servicio **betgeniux-scheduler** (mismo valor).

### 5️⃣ CREAR EL SERVICIO

1. Click en **"Create Background Worker"**
2. Espera 2-3 minutos mientras se despliega
3. Verifica los logs

### 6️⃣ VERIFICAR QUE FUNCIONA

**En los logs deberías ver:**
```
🤖 Iniciando BetGeniuX Bot Listener...
📝 Registrando usuarios automáticamente...
BetGeniuXBot listener iniciado - Registrando usuarios automáticamente
🔧 ADMIN_TELEGRAM_ID configurado: 7659029315
```

**Prueba en Telegram:**
1. Abre tu bot: @BetGeniuXbot
2. Envía: `/start`
3. Deberías recibir el menú con botones

---

## ✅ RESULTADO FINAL

Tendrás **DOS servicios corriendo 24/7 en Render:**

1. **betgeniux-scheduler** ✅
   - Envía predicciones automáticamente
   - Corre a las 6:59 AM y 2h antes de partidos

2. **betgeniux-bot** ✅
   - Responde a /start, /help
   - Maneja menú interactivo
   - Procesa pagos
   - Registra usuarios

**Costo total:** $14/mes (2 servicios × $7)

---

## 🔧 TROUBLESHOOTING

**Si el bot no responde:**
1. Verifica que el servicio esté "Live" (verde)
2. Revisa los logs para errores
3. Confirma que TELEGRAM_BOT_TOKEN es correcto
4. Asegúrate de estar hablando con el bot correcto (@BetGeniuXbot)

**Si hay error de webhook:**
- El bot usa polling, no webhook
- Si antes usaste webhook, bórralo: https://api.telegram.org/bot<TOKEN>/deleteWebhook

---

## 📞 SOPORTE

Si tienes problemas, comparte:
1. Screenshot de los logs del servicio betgeniux-bot
2. El error específico que ves
3. Si el servicio está "Live" o "Failed"
