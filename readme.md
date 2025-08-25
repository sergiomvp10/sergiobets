# ⚽ BetGeniuX – Bot de Apuestas Deportivas

**BetGeniuX** es un bot de apuestas deportivas desarrollado en Python con interfaz gráfica (Tkinter), que muestra partidos, cuotas, envía pronósticos por Telegram y gestiona el progreso del usuario.

> 🔧 **Estado**: Verificación de acceso al repositorio y funcionalidad de lint completada

---

## 🚀 Características principales

- 📅 Consulta partidos diarios (simulados o reales)
- 💰 Muestra cuotas de apuestas por casa
- 📢 Envía picks y pronósticos al canal de Telegram
- 📊 Calcula progreso del bankroll
- 🔐 Separación de funciones en módulos para mejor mantenimiento

---

## 🧱 Estructura del proyecto

| Archivo / Módulo | Función |
|------------------|---------|
| `crudo.py` | Archivo principal con interfaz gráfica |
| `telegram_utils.py` | Envía mensajes a Telegram |
| `json_storage.py` | Guarda y carga archivos JSON |
| `db.py` | Conexión a base de datos PostgreSQL |
| `api_config.py` | Configuración de APIs externas |
| `partidos.json` | Partidos simulados o guardados |
| `progreso.json` | Seguimiento de balance del usuario |
| `ultimo_pick.json` | Último pick enviado |
| `registro_pronosticos.txt` | Historial de pronósticos |

---

## 📦 Requisitos

```bash
pip install -r requirements.txt
