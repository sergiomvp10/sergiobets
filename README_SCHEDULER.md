# 🤖 SergioBets - Scheduler Automatizado 24/7

Sistema que envía pronósticos automáticamente a usuarios premium en horarios programados.

## 🎯 ¿Qué hace?

**Envío Automático de Pronósticos:**

🌅 **Cada día a las 6:59 AM (hora de Phoenix):**
- Selecciona los 3 mejores pronósticos del día
- Los envía con 2 minutos de diferencia:
  - 6:59 AM → Pronóstico #1
  - 7:01 AM → Pronóstico #2
  - 7:03 AM → Pronóstico #3
- Solo a usuarios premium activos

⏰ **2 horas antes de cada partido:**
- Envía el pronóstico de ese partido
- Solo a usuarios premium
- No envía duplicados

## 📋 GUÍA DE DEPLOYMENT EN RENDER (PASO A PASO)

### PASO 1: Crear Base de Datos PostgreSQL

1. Ve a https://dashboard.render.com/
2. Click en **"New +"** (botón azul arriba a la derecha)
3. Selecciona **"PostgreSQL"**
4. Configuración:
   - **Name**: `sergiobets-db`
   - **Database**: `sergiobets`
   - **User**: (déjalo como está, se genera automático)
   - **Region**: Selecciona **"Oregon (US West)"** o el más cercano
   - **PostgreSQL Version**: Déjalo en la versión más reciente
   - **Plan**: Selecciona **"Free"** (o "Starter" si quieres más capacidad)
5. Click en **"Create Database"** (botón azul abajo)
6. **IMPORTANTE**: Espera 2-3 minutos a que se cree la base de datos
7. Cuando esté lista, verás una pantalla con información de conexión
8. **COPIA** el **"Internal Database URL"** (empieza con `postgresql://`)
   - Se ve así: `postgresql://usuario:password@host.render.com/database`
   - **GUÁRDALO** en un lugar seguro, lo necesitarás después

### PASO 2: Ejecutar Migración de Base de Datos

1. En la misma pantalla de tu base de datos en Render
2. Click en la pestaña **"Shell"** (arriba)
3. Espera a que se abra la consola (puede tardar 10-20 segundos)
4. Abre el archivo `create_scheduled_notifications_table.sql` de tu repositorio
5. **COPIA TODO** el contenido del archivo
6. **PEGA** el contenido en la consola de Render
7. Presiona **Enter**
8. Deberías ver mensajes como:
   ```
   CREATE TABLE
   CREATE INDEX
   CREATE INDEX
   CREATE INDEX
   ```
9. Si ves esos mensajes, ¡perfecto! La tabla se creó correctamente

### PASO 3: Crear Background Worker (Scheduler)

1. Ve a https://dashboard.render.com/
2. Click en **"New +"** (botón azul arriba a la derecha)
3. Selecciona **"Background Worker"**
4. Conecta tu repositorio:
   - Si es la primera vez, click en **"Connect GitHub"**
   - Autoriza a Render para acceder a tus repositorios
   - Busca y selecciona **"sergiomvp10/sergiobets"**
5. Configuración:
   - **Name**: `sergiobets-scheduler`
   - **Region**: Selecciona **"Oregon (US West)"** (el mismo que la base de datos)
   - **Branch**: Selecciona **"devin/1761852552-update-footystats-api"**
     - (Después de hacer merge del PR, cambia a "main")
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduler_service.py`
6. Click en **"Advanced"** (abajo)
7. Click en **"Add Environment Variable"**
8. Agrega estas variables **UNA POR UNA**:

   ```
   DATABASE_URL
   (pega aquí el Internal Database URL que copiaste en el PASO 1)

   TELEGRAM_BOT_TOKEN
   (pega aquí tu token del bot de Telegram)

   FOOTYSTATS_API_KEY
   (pega aquí tu API key de FootyStats)

   TIMEZONE
   America/Phoenix

   MORNING_SEND_TIME
   06:59

   MORNING_MAX
   3

   MORNING_SPACING_SECONDS
   120

   PREMATCH_HOURS_BEFORE
   2
   ```

9. Click en **"Create Background Worker"** (botón azul abajo)
10. Espera 2-5 minutos a que se despliegue

### PASO 4: Verificar que Funciona

1. En la pantalla de tu Background Worker en Render
2. Click en la pestaña **"Logs"** (arriba)
3. Deberías ver mensajes como:
   ```
   🚀 Starting Prediction Scheduler Service...
   ⏰ Timezone: America/Phoenix
   🌅 Morning: 06:59
   ✅ Database table ensured
   ✅ Scheduled morning job at 06:59 America/Phoenix
   ✅ Scheduled prematch job at 00:05 America/Phoenix
   🔄 Running initial prematch scheduling...
   ✅ Scheduler started!
   📋 Scheduled jobs:
     - morning_predictions: 2025-11-01 06:59:00-07:00
     - prematch_scheduling: 2025-11-01 00:05:00-07:00
   ```

4. Si ves esos mensajes, **¡FELICIDADES!** El scheduler está funcionando 24/7

## ❌ Si algo sale mal

### Error: "DATABASE_URL environment variable not set"
- Verifica que agregaste la variable `DATABASE_URL` en el PASO 3
- Verifica que copiaste el "Internal Database URL" completo

### Error: "relation 'scheduled_notifications' does not exist"
- Repite el PASO 2 (ejecutar la migración SQL)
- Asegúrate de copiar TODO el contenido del archivo SQL

### Error: "TELEGRAM_BOT_TOKEN environment variable not set"
- Verifica que agregaste la variable `TELEGRAM_BOT_TOKEN` en el PASO 3

### El scheduler no envía mensajes
1. Verifica que el Background Worker esté corriendo (en Render Dashboard)
2. Verifica que tengas usuarios premium activos
3. Revisa los logs para ver si hay errores

## 📊 ¿Cómo saber si está funcionando?

**Logs que indican que todo está bien:**
- `✅ Scheduler started!` - El scheduler inició correctamente
- `🌅 Starting morning predictions job...` - Ejecutó el job de la mañana
- `📅 Scheduled morning prediction 1/3 at 06:59` - Programó un envío
- `📤 Sending morning prediction for match X...` - Está enviando un pronóstico
- `✅ Sent to X premium users` - Envió exitosamente

**Logs normales (no son errores):**
- `⚠️ No matches found for today` - No hay partidos hoy (normal en algunos días)
- `⚠️ No valid predictions for morning send` - No hay pronósticos que cumplan los criterios de IA

## 🔧 Mantenimiento

### Ver qué pronósticos se han enviado

1. Ve a tu base de datos en Render Dashboard
2. Click en "Shell"
3. Ejecuta:
```sql
SELECT * FROM scheduled_notifications 
WHERE DATE(sent_at) = CURRENT_DATE
ORDER BY sent_at DESC;
```

### Limpiar notificaciones antiguas (opcional)

```sql
DELETE FROM scheduled_notifications
WHERE kickoff_utc < NOW() - INTERVAL '7 days';
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Verifica que todas las variables de entorno estén configuradas
3. Verifica que la tabla de BD esté creada correctamente

---

**¡Listo!** Tu sistema de pronósticos automatizado está funcionando 24/7 en la nube. 🎉
