@echo off
setlocal EnableExtensions

set "SERVICE_NAME=SincronizadorContpaqiService"
set "SERVICE_DISPLAY=Sincronizador Contpaqi"
set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%release\SincronizadorContpaqiService\SincronizadorContpaqiService.exe"
if not exist "%EXE_PATH%" set "EXE_PATH=%SCRIPT_DIR%SincronizadorContpaqiService\SincronizadorContpaqiService.exe"

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
echo   Instalador de servicio Sincronizador Contpaqi
echo ================================================
echo.

if not exist "%EXE_PATH%" (
    echo [ERROR] No se encontro el EXE onedir del servicio.
    echo         Ruta esperada: release\SincronizadorContpaqiService\SincronizadorContpaqiService.exe
    if exist "%SCRIPT_DIR%release\SincronizadorContpaqiService.exe" (
        echo [INFO] Detectado EXE onefile legado en release. Ese formato puede causar error 7039 en servicios.
        echo [INFO] Regenera release con build-release.ps1 para producir formato onedir.
    )
    if exist "%SCRIPT_DIR%SincronizadorContpaqiService.exe" (
        echo [INFO] Detectado EXE onefile legado en carpeta actual. Ese formato puede causar error 7039 en servicios.
        echo [INFO] Regenera release con build-release.ps1 para producir formato onedir.
    )
    echo [ERROR] No se encontro el EXE en:
    echo         %EXE_PATH%
    echo.
    pause
    exit /b 1
)

:: Estrategia: si existe, actualizar en sitio (sin borrar). Si no existe, instalar.
echo [INFO] Verificando servicio existente...
sc query "%SERVICE_NAME%" >nul 2>&1
if "%errorlevel%"=="0" (
    echo [INFO] Servicio existente detectado. Reinstalando limpio...
    sc stop "%SERVICE_NAME%" >nul 2>&1
    timeout /t 2 >nul
    sc delete "%SERVICE_NAME%" >nul 2>&1
    timeout /t 2 >nul
) else (
    echo [INFO] Servicio no existe. Creando registro del servicio...
)

sc create "%SERVICE_NAME%" binPath= "\"%EXE_PATH%\"" start= auto DisplayName= "%SERVICE_DISPLAY%" >nul
if not "%errorlevel%"=="0" (
    echo [ERROR] No se pudo crear el servicio con sc.exe.
    echo.
    pause
    exit /b 1
)

sc description "%SERVICE_NAME%" "Sincroniza datos entre Netvy y Contpaqi." >nul

sc query "%SERVICE_NAME%" >nul 2>&1
if not "%errorlevel%"=="0" (
    echo [ERROR] El servicio no quedo registrado en Windows.
    echo.
    pause
    exit /b 1
) else (
    echo [INFO] Servicio registrado correctamente.
)

reg query "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%\PythonClass" >nul 2>&1
if "%errorlevel%"=="0" (
    reg delete "HKLM\SYSTEM\CurrentControlSet\Services\%SERVICE_NAME%\PythonClass" /f >nul 2>&1
)

echo [INFO] Iniciando servicio...
sc start "%SERVICE_NAME%" >nul
if not "%errorlevel%"=="0" (
    "%EXE_PATH%" start >nul 2>&1
)
timeout /t 2 >nul
sc query "%SERVICE_NAME%" | findstr /I "RUNNING" >nul
if not "%errorlevel%"=="0" (
    echo [ERROR] El servicio se instalo, pero no pudo iniciar.
    echo        Revisa el Visor de eventos de Windows y ProgramData\SincronizadorContpaqi\conf.json.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Servicio instalado e iniciado correctamente.
echo      Nombre: %SERVICE_NAME%
echo      EXE   : %EXE_PATH%
echo.
pause
exit /b 0
