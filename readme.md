# ⚽ SergioBets – Sistema Inteligente de Apuestas Deportivas con IA

**SergioBets** es un sistema completo de apuestas deportivas con inteligencia artificial que combina predicciones avanzadas, gestión automatizada de usuarios, sistema de pagos integrado y seguimiento detallado del rendimiento.

---

## 🚀 Características Principales

### 🤖 Inteligencia Artificial Avanzada
- **Predicciones IA** con análisis probabilístico y value betting
- **Filtros inteligentes** por liga, mercado y probabilidad
- **Análisis de valor** automático para identificar las mejores oportunidades
- **Machine Learning** para mejorar predicciones basadas en resultados históricos

### 📱 Bot de Telegram Completo
- **Menú interactivo** con navegación por botones
- **Registro automático** de usuarios nuevos
- **Sistema VIP** con acceso premium a predicciones exclusivas
- **Notificaciones** automáticas de picks y resultados

### 💳 Sistema de Pagos Integrado
- **NOWPayments** para procesamiento de criptomonedas
- **Webhooks automáticos** para confirmación de pagos
- **Gestión de membresías** VIP con renovación automática
- **Túnel ngrok** para exposición segura de webhooks

### 📊 Track Record Automático
- **Seguimiento en tiempo real** de todas las predicciones
- **Comparación automática** con resultados reales
- **Métricas detalladas**: ROI, tasa de aciertos, beneficio neto
- **Historial completo** de rendimiento financiero

### 🖥️ Interfaz Gráfica Unificada
- **Dashboard central** que controla todos los componentes
- **Monitoreo en tiempo real** del bot, webhooks y túnel
- **Gestión visual** de usuarios, predicciones y pagos
- **Logs integrados** para debugging y monitoreo

---

## 🏗️ Arquitectura del Sistema

### Aplicación Principal
| Archivo | Función |
|---------|---------|
| `sergiobets_unified.py` | **Aplicación principal unificada** - Combina GUI, webhook server, túnel ngrok y bot de Telegram |
| `crudo.py` | **Interfaz gráfica legacy** - GUI con Tkinter para gestión manual |

### Módulos de IA y Predicciones
| Archivo | Función |
|---------|---------|
| `ia_bets.py` | **Motor de IA** - Genera predicciones inteligentes con filtros avanzados |
| `track_record.py` | **Sistema de seguimiento** - Compara predicciones vs resultados reales |
| `value_betting.py` | **Análisis de valor** - Identifica oportunidades de value betting |

### Sistema de Comunicación
| Archivo | Función |
|---------|---------|
| `telegram_bot_listener.py` | **Bot de Telegram** - Maneja usuarios, pagos y distribución de picks |
| `telegram_utils.py` | **Utilidades de Telegram** - Funciones auxiliares para envío de mensajes |

### Gestión de Datos
| Archivo | Función |
|---------|---------|
| `db.py` | **Base de datos PostgreSQL** - Almacenamiento persistente |
| `json_storage.py` | **Almacenamiento JSON** - Gestión de archivos de configuración |
| `user_management.py` | **Gestión de usuarios** - Control de acceso y membresías |

### APIs y Servicios Externos
| Archivo | Función |
|---------|---------|
| `api_config.py` | **Configuración de APIs** - Claves y endpoints externos |
| `payment_handler.py` | **Procesador de pagos** - Integración con NOWPayments |
| `ngrok_manager.py` | **Gestor de túneles** - Exposición segura de webhooks |

---

## 🚀 Instalación y Configuración

### Requisitos del Sistema
```bash
# Python 3.8+
pip install -r requirements.txt
```

### Variables de Entorno Requeridas
```bash
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_bot
TELEGRAM_CHANNEL_ID=tu_canal_id

# Base de Datos
DATABASE_URL=postgresql://usuario:password@host:puerto/database

# Pagos (NOWPayments)
NOWPAYMENTS_API_KEY=tu_api_key
NOWPAYMENTS_IPN_SECRET=tu_secret_key

# Ngrok (opcional para webhooks)
NGROK_AUTH_TOKEN=tu_ngrok_token
```

### Configuración Inicial
1. **Configurar bot de Telegram** con BotFather
2. **Crear base de datos PostgreSQL**
3. **Configurar cuenta NOWPayments** para pagos
4. **Ejecutar migraciones** de base de datos
5. **Configurar webhooks** para pagos automáticos

---

## 🎯 Uso del Sistema

### Modo Unificado (Recomendado)
```bash
python sergiobets_unified.py
```
Ejecuta todos los componentes en una sola aplicación:
- ✅ Bot de Telegram activo
- ✅ Servidor de webhooks funcionando
- ✅ Túnel ngrok expuesto
- ✅ Interfaz gráfica de control

### Modo Legacy
```bash
python crudo.py
```
Interfaz gráfica tradicional para uso manual.

---

## 📈 Funcionalidades Avanzadas

### Sistema VIP
- **Acceso premium** a predicciones exclusivas
- **Filtros avanzados** por probabilidad y valor
- **Soporte prioritario** y actualizaciones tempranas
- **Estadísticas detalladas** de rendimiento

### Gestión Automática
- **Registro automático** de nuevos usuarios
- **Procesamiento de pagos** sin intervención manual
- **Distribución automática** de picks a usuarios VIP
- **Seguimiento en tiempo real** de todas las transacciones

### Métricas y Análisis
- **ROI calculado** automáticamente
- **Tasa de aciertos** por tipo de apuesta
- **Beneficio neto** acumulado
- **Gráficos de rendimiento** histórico

---

## 🔧 Desarrollo y Contribución

### Estructura Modular
El sistema está diseñado con arquitectura modular para facilitar:
- ✅ **Mantenimiento** independiente de componentes
- ✅ **Escalabilidad** horizontal y vertical
- ✅ **Testing** unitario y de integración
- ✅ **Despliegue** flexible en diferentes entornos

### Documentación Adicional
- 📖 `README_WINDOWS.md` - Guía de compilación para Windows
- 💳 `README_PAYMENTS.md` - Configuración detallada del sistema de pagos
- 🏗️ `IMPLEMENTATION_SUMMARY.md` - Resumen técnico de la implementación

---

## 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contacta al desarrollador principal.

**Desarrollado por:** Sergio MVP  
**Versión:** 2.0 (Sistema Unificado con IA)  
**Última actualización:** Agosto 2025
