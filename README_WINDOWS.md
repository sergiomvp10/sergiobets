# BetGeniuX - Guía de Instalación para Windows

## 📋 Requisitos Previos

1. **Python 3.12** - Descargar desde [python.org](https://www.python.org/downloads/)
2. **ngrok** - Descargar desde [ngrok.com](https://ngrok.com/download)
3. **Git** (opcional) - Para clonar el repositorio

## 🚀 Instalación Paso a Paso

### Paso 1: Preparar el Entorno

1. Instala Python 3.12 (asegúrate de marcar "Add Python to PATH")
2. Instala ngrok y agrégalo al PATH del sistema
3. Abre Command Prompt o PowerShell como administrador

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Paso 3: Configurar ngrok

```bash
ngrok authtoken 30oNthnDV9dPuUUep11CEifBDMy_6p7AgEgmyaMHiYedDYDd8
```

### Paso 4: Probar Compatibilidad

```bash
python test_windows_compatibility.py
```

Si todos los tests pasan, continúa al siguiente paso.

### Paso 5: Compilar el Ejecutable

**Opción A: Usar el script automático (Recomendado)**
```bash
compile_windows.bat
```

**Opción B: Compilar manualmente**

Para versión con consola (debugging):
```bash
pyinstaller --onefile --console --name BetGeniuX-Console ^
    --hidden-import=flask ^
    --hidden-import=telegram ^
    --hidden-import=telegram.ext ^
    --hidden-import=requests ^
    --hidden-import=python-dotenv ^
    --hidden-import=asyncio ^
    --hidden-import=threading ^
    --hidden-import=subprocess ^
    --hidden-import=logging ^
    --hidden-import=traceback ^
    --add-data ".env;." ^
    --add-data "pagos;pagos" ^
    betgeniux_unified.py
```

Para versión sin consola:
```bash
pyinstaller --onefile --windowed --name BetGeniuX ^
    --hidden-import=flask ^
    --hidden-import=telegram ^
    --hidden-import=telegram.ext ^
    --hidden-import=requests ^
    --hidden-import=python-dotenv ^
    --hidden-import=asyncio ^
    --hidden-import=threading ^
    --hidden-import=subprocess ^
    --hidden-import=logging ^
    --hidden-import=traceback ^
    --add-data ".env;." ^
    --add-data "pagos;pagos" ^
    betgeniux_unified.py
```

## 🧪 Pruebas

### 1. Probar Versión Console (Recomendado primero)

```bash
dist\BetGeniuX-Console.exe
```

Esta versión muestra la consola y todos los mensajes de error. Úsala para:
- Verificar que todos los servicios inician correctamente
- Ver cualquier error que pueda ocurrir
- Confirmar que ngrok se conecta correctamente
- Revisar logs detallados en tiempo real

### 2. Probar Versión Windowed

```bash
dist\BetGeniuX.exe
```

Esta versión no muestra consola. Úsala solo después de confirmar que la versión console funciona.

## 🔧 Solución de Problemas

### Error: "This app can't run on your PC"

- **Causa**: Ejecutable compilado en Linux no es compatible con Windows
- **Solución**: Compilar en Windows usando las instrucciones de arriba

### Error: "ngrok not found"

- **Causa**: ngrok no está en el PATH del sistema
- **Solución**: 
  1. Descargar ngrok desde [ngrok.com](https://ngrok.com/download)
  2. Extraer ngrok.exe a una carpeta (ej: C:\ngrok\)
  3. Agregar esa carpeta al PATH del sistema

### Error: "Module not found"

- **Causa**: Dependencias de Python no instaladas
- **Solución**: `pip install -r requirements.txt`

### El .exe no hace nada al hacer doble clic

1. **SIEMPRE ejecuta primero `BetGeniuX-Console.exe`** para ver errores
2. Revisa el archivo `sergiobets_debug.log` que se crea automáticamente
3. Verifica que todos los archivos estén en la misma carpeta que el .exe
4. Comprueba que ngrok esté configurado con el authtoken correcto

### Errores de importación en PyInstaller

- **Causa**: Dependencias no incluidas en el ejecutable
- **Solución**: Usar el script `compile_windows.bat` que incluye todos los hidden imports necesarios

### El webhook server no inicia

1. Revisa `sergiobets_debug.log` para errores específicos
2. Verifica que el puerto 5000 no esté ocupado
3. Confirma que Flask esté instalado correctamente

## 📁 Estructura de Archivos Requerida

```
BetGeniuX/
├── BetGeniuX.exe (o BetGeniuX-Console.exe)
├── .env
├── sergiobets_debug.log (se crea automáticamente)
├── pagos/
│   ├── webhook_server.py
│   ├── payments.py
│   └── start_webhook_server.py
└── telegram_bot_listener.py
```

## 📊 Archivos de Debug

### sergiobets_debug.log
Este archivo se crea automáticamente y contiene:
- Información de inicio del sistema
- Detalles de cada servicio que se inicia
- Errores específicos con stack traces
- Estado de dependencias y archivos

**Siempre revisa este archivo si tienes problemas.**

## 📞 Soporte

Si tienes problemas, sigue este orden:

1. **Ejecuta `BetGeniuX-Console.exe`** para ver errores en tiempo real
2. **Revisa `sergiobets_debug.log`** para detalles específicos
3. Verifica que ngrok esté configurado correctamente: `ngrok version`
4. Confirma que todas las dependencias estén instaladas: `pip list`
5. Verifica la estructura de archivos según la lista de arriba

## 🎯 Uso Normal

Una vez que todo funcione:

1. Ejecuta `BetGeniuX.exe` (versión sin consola)
2. El sistema iniciará automáticamente:
   - Servidor webhook en puerto 5000
   - Túnel ngrok con URL pública
   - Bot de Telegram
3. Configura la URL de ngrok en tu dashboard de NOWPayments
4. ¡El sistema está listo para recibir pagos!

## ⚠️ Notas Importantes

- **Siempre prueba la versión console primero** antes de usar la versión windowed
- **El archivo de debug se sobrescribe** cada vez que ejecutas la aplicación
- **Mantén todos los archivos juntos** en la misma carpeta que el .exe
- **No muevas el .exe** sin mover también las carpetas `pagos` y el archivo `.env`
