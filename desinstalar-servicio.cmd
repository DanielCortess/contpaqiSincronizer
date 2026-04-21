@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SERVICE_NAME=SincronizadorContpaqiService"

:: Verificar privilegios de administrador
if /I "%~1"=="_elevated" goto :admin_ok

net session >nul 2>&1
if not "%errorlevel%"=="0" (
    echo [INFO] Solicitando permisos de administrador...
    echo [INFO] Esta ventana se cerrara y se abrira otra consola elevada.
    timeout /t 2 >nul
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%ComSpec%' -ArgumentList '/k ""%~f0"" _elevated' -Verb RunAs"
    if not "%errorlevel%"=="0" (
        echo [ERROR] No se pudo elevar permisos - UAC cancelado o bloqueado.
        echo.
        pause
    )
    exit /b
)

:admin_ok

echo.
echo ================================================
echo   Desinstalador de servicio Sincronizador Contpaqi
echo ================================================
echo.

echo [INFO] Verificando servicio...
sc query "%SERVICE_NAME%" >nul 2>&1
if not "%errorlevel%"=="0" (
    echo [INFO] El servicio no existe. No hay nada que desinstalar.
    echo.
    pause
    exit /b 0
)

echo [INFO] Forzando detencion del servicio...
sc config "%SERVICE_NAME%" start= disabled >nul 2>&1
sc stop "%SERVICE_NAME%" >nul 2>&1

for /L %%I in (1,1,5) do (
    sc query "%SERVICE_NAME%" | findstr /I "STOPPED" >nul 2>&1
    if "!errorlevel!"=="0" goto :stopped
    timeout /t 1 >nul
)

:stopped
set "PID="
for /f "tokens=3" %%P in ('sc queryex "%SERVICE_NAME%" ^| findstr /R /C:"PID"') do set "PID=%%P"
if defined PID (
    if not "!PID!"=="0" (
        echo [INFO] Finalizando proceso PID !PID! ...
        taskkill /PID !PID! /T /F >nul 2>&1
        timeout /t 1 >nul
    )
)

reg query "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%\PythonClass" >nul 2>&1
if "%errorlevel%"=="0" (
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%\PythonClass" /f >nul 2>&1
)

echo [INFO] Eliminando servicio (forzado)...
set "DELETED=0"
for /L %%I in (1,1,8) do (
    sc delete "%SERVICE_NAME%" >nul 2>&1
    timeout /t 1 >nul
    sc query "%SERVICE_NAME%" >nul 2>&1
    if not "!errorlevel!"=="0" (
        set "DELETED=1"
        goto :deleted
    )
)

if "%DELETED%"=="0" (
    echo [WARN] No fue posible eliminar con sc.exe. Intentando limpieza directa en registro...
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%" /f >nul 2>&1
    timeout /t 1 >nul
    sc query "%SERVICE_NAME%" >nul 2>&1
    if "%errorlevel%"=="0" (
        echo [ERROR] El servicio aun aparece registrado.
        echo.
        pause
        exit /b 1
    )
)

:deleted

echo.
echo [OK] Servicio desinstalado correctamente.
echo      Nombre: %SERVICE_NAME%
echo.
pause
exit /b 0
