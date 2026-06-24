# Script simple para instalar servicio - ejecutar desde PowerShell como admin

$EXE = "C:\Users\Usuario\Documents\SincronizadorContpaqi\release\SincronizadorContpaqiService.exe"

Write-Host "[1] Removiendo servicio viejo..."
& $EXE remove 2>&1
Start-Sleep -Seconds 2

Write-Host "[2] Instalando..."
& $EXE --startup auto install 2>&1
Start-Sleep -Seconds 2

Write-Host "[2.1] Configurando recuperación automática..."
& sc.exe failure SincronizadorContpaqiService reset= 86400 actions= restart/5000/restart/15000/restart/60000 2>&1
& sc.exe failureflag SincronizadorContpaqiService 1 2>&1

Write-Host "[3] Iniciando..."
& $EXE start 2>&1
Start-Sleep -Seconds 3

Write-Host "[4] Estado final:"
Get-Service SincronizadorContpaqiService
