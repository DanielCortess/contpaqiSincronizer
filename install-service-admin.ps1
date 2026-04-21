param(
    [string]$ServiceExePath = "C:\Users\Usuario\Documents\SincronizadorContpaqi\release\SincronizadorContpaqiService.exe"
)

$LOG = "C:\temp_install_service.log"

function Log { param($msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LOG -Value $line
}

Log "=== Instalador de Servicio ==="
Log "EXE: $ServiceExePath"

# Check admin
$admin = [System.Security.Principal.WindowsIdentity]::GetCurrent().Groups.Contains([System.Security.Principal.SecurityIdentifier]"S-1-5-32-544")
if (-not $admin) {
    Log "ERROR: Requiere permisos de administrador"
    exit 1
}
Log "OK: Ejecutando como admin"

# Validate EXE
if (-not (Test-Path $ServiceExePath)) {
    Log "ERROR: EXE no existe: $ServiceExePath"
    exit 1
}
Log "OK: EXE encontrado"

# Stop service if running
Log "Deteniendo servicio (si existe)..."
Stop-Service SincronizadorContpaqiService -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Try direct remove via EXE
Log "Removiendo servicio viejo (via EXE)..."
& $ServiceExePath remove 2>&1 | ForEach { Log "  $_" }
Start-Sleep -Seconds 3

# Verify removed
$svc = Get-Service SincronizadorContpaqiService -ErrorAction SilentlyContinue
if ($svc) {
    Log "WARN: Servicio aun existe. Intentando borrar con sc delete..."
    & sc.exe delete SincronizadorContpaqiService 2>&1 | ForEach { Log "  $_" }
    Start-Sleep -Seconds 3
}

# Check again
$svc = Get-Service SincronizadorContpaqiService -ErrorAction SilentlyContinue
if ($svc) {
    Log "ERROR: No se pudo eliminar el servicio anterior"
    Log "  State: $($svc.Status)"
    exit 1
}
Log "OK: Servicio anterior removido"

# Install fresh
Log "Instalando servicio..."
& $ServiceExePath --startup auto install 2>&1 | ForEach { Log "  $_" }
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: Instalacion fallo (exitcode $LASTEXITCODE)"
    exit 1
}
Start-Sleep -Seconds 2
Log "OK: Servicio instalado"

# Verify installed
$svc = Get-Service SincronizadorContpaqiService -ErrorAction SilentlyContinue
if (-not $svc) {
    Log "ERROR: Servicio no aparece despues de instalar"
    exit 1
}

$reg = Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\services\SincronizadorContpaqiService
Log "StartType: $($reg.Start) (2=Auto, 3=Manual, 4=Disabled)"

# Start
Log "Iniciando servicio..."
& $ServiceExePath start 2>&1 | ForEach { Log "  $_" }
Start-Sleep -Seconds 3

# Final check
$svc = Get-Service SincronizadorContpaqiService
Log "Estado final: $($svc.Status)"

if ($svc.Status -eq "Running") {
    Log "=== EXITO: Servicio instalado y ejecutandose ==="
    Log "Ver logs en: $LOG"
    exit 0
} else {
    Log "=== FALLO: Servicio no se inicio ==="
    Log "Ver logs en: $LOG"
    exit 1
}
