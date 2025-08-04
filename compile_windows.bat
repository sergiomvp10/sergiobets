@echo off
echo ========================================
echo SergioBets Windows Compilation Script
echo ========================================

echo.
echo 1. Testing compatibility...
python test_windows_compatibility.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Compatibility test failed!
    echo Fix the issues above before continuing.
    pause
    exit /b 1
)

echo.
echo 2. Installing PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo 3. Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo 4. Compiling CONSOLE version (for debugging)...
pyinstaller --onefile --console --name SergioBets-Console ^
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
    sergiobets_unified.py

if %ERRORLEVEL% neq 0 (
    echo ERROR: Console version compilation failed!
    pause
    exit /b 1
)

echo.
echo 5. Testing console version...
echo Running SergioBets-Console.exe for 10 seconds...
timeout /t 2 /nobreak > nul
start /wait /b dist\SergioBets-Console.exe &
timeout /t 10 /nobreak > nul
taskkill /f /im SergioBets-Console.exe > nul 2>&1

echo.
echo 6. Compiling WINDOWED version (no console)...
pyinstaller --onefile --windowed --name SergioBets ^
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
    sergiobets_unified.py

echo.
echo ========================================
echo Compilation complete!
echo ========================================
echo.
echo Files created:
echo - dist\SergioBets-Console.exe (shows console for debugging)
echo - dist\SergioBets.exe (no console window)
echo.
echo IMPORTANT:
echo 1. Test SergioBets-Console.exe first to see any errors
echo 2. Check sergiobets_debug.log for detailed logs
echo 3. If console version works, then use SergioBets.exe
echo.
pause
