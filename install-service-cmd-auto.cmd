@echo off
REM Automatico sin pause - para uso dentro de scripts
set "EXE_PATH=C:\Users\Usuario\Documents\SincronizadorContpaqi\release\SincronizadorContpaqiService.exe"

echo [1] Deteniendo servicio...
net stop SincronizadorContpaqiService >nul 2>nul
timeout /t 2 >nul

echo [2] Eliminando servicio viejo...
sc delete SincronizadorContpaqiService >nul 2>nul
timeout /t 3 >nul

echo [3] Creando nuevo servicio...
sc create SincronizadorContpaqiService binPath= "%EXE_PATH%" start= auto DisplayName= "Sincronizador Contpaqi"

sc description SincronizadorContpaqiService "Sincroniza datos entre Netvy y Contpaqi."

timeout /t 2 >nul

echo [4] Iniciando servicio...
sc start SincronizadorContpaqiService
timeout /t 3 >nul

echo [5] Estado:
sc query SincronizadorContpaqiService | find "RUNNING"
if "%errorlevel%"=="0" (
    echo [OK] Servicio instalado y ejecutandose
) else (
    echo [ERROR] Servicio no esta en RUNNING
)
