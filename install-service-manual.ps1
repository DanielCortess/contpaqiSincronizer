# Script simple para instalar servicio - ejecutar desde PowerShell como admin

$EXE = "C:\Users\Usuario\Documents\SincronizadorContpaqi\release\SincronizadorContpaqiService.exe"

Write-Host "[1] Removiendo servicio viejo..."
& $EXE remove 2>&1
Start-Sleep -Seconds 2

Write-Host "[2] Instalando..."
& $EXE --startup auto install 2>&1
Start-Sleep -Seconds 2

Write-Host "[3] Iniciando..."
& $EXE start 2>&1
Start-Sleep -Seconds 3

Write-Host "[4] Estado final:"
Get-Service SincronizadorContpaqiService
