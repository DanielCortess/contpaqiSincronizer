@echo off
REM Guardar la ruta en una variable
set "EXE_PATH=C:\Users\Usuario\Documents\SincronizadorContpaqi\release\SincronizadorContpaqiService.exe"

echo.
echo ========== INSTALADOR DE SERVICIO (CMD) ==========
echo.

REM Detener servicio si existe
echo [1] Deteniendo servicio...
net stop SincronizadorContpaqiService >nul 2>nul
timeout /t 2 >nul

REM Eliminar servicio si existe
echo [2] Eliminando servicio viejo...
sc delete SincronizadorContpaqiService >nul 2>nul
timeout /t 3 >nul

REM Crear nuevo servicio
echo [3] Creando nuevo servicio...
sc create SincronizadorContpaqiService binPath= "%EXE_PATH%" start= auto DisplayName= "Sincronizador Contpaqi"
if not "%errorlevel%"=="0" (
    echo [ERROR] No se pudo crear el servicio (error %errorlevel%)
    pause
    exit /b 1
)

REM Añadir descripcion
sc description SincronizadorContpaqiService "Sincroniza datos entre Netvy y Contpaqi."

timeout /t 2 >nul

REM Iniciar
echo [4] Iniciando servicio...
sc start SincronizadorContpaqiService
timeout /t 3 >nul

REM Verificar
echo [5] Estado final:
sc query SincronizadorContpaqiService | find /I "RUNNING"
if "%errorlevel%"=="0" (
    echo.
    echo [OK] SERVICIO INSTALADO Y EJECUTANDOSE
    echo.
) else (
    echo.
    echo [ERROR] Servicio no se inicio. Visor de Eventos -> Sistema
    echo.
)

pause
