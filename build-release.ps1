#Requires -RunAsAdministrator
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PYTHON          = ".\.venv32\Scripts\python.exe"
$ENTRY_POINT     = "Src\SyncContpaqWindowsService.py"
$EXE_NAME        = "SincronizadorContpaqiService"
$DIST_PATH       = "release"
$WORK_PATH       = "build_signed"
$CONF_SRC        = "Src\conf.json"
$INSTALLER_CMD   = "instalar-servicio.cmd"
$UNINSTALLER_CMD = "desinstalar-servicio.cmd"
$SERVICE_NAME    = "SincronizadorContpaqiService"
$CERT_THUMBPRINT = "439196A8A5A2AF4046741BCCABD1C4FC2A407AC3"
$TIMESTAMP_URL   = "http://timestamp.digicert.com"
$SIGNTOOL        = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.28000.0\x86\signtool.exe"
$PACKAGE_DIR     = Join-Path $DIST_PATH $EXE_NAME
$EXE_PATH        = Join-Path $PACKAGE_DIR "$EXE_NAME.exe"

function Write-Step { param($msg) Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "  [OK] $msg"  -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "[FAIL] $msg"  -ForegroundColor Red }

Write-Step "Parando servicio si esta en ejecucion..."
$svc = Get-Service -Name $SERVICE_NAME -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -ne "Stopped") {
    Stop-Service -Name $SERVICE_NAME -Force
    Start-Sleep -Seconds 2
    Write-Ok "Servicio detenido."
} else {
    Write-Ok "Servicio no estaba corriendo."
}
$proc = Get-Process -Name $EXE_NAME -ErrorAction SilentlyContinue
if ($proc) {
    $proc | Stop-Process -Force
    Start-Sleep -Seconds 1
    Write-Ok "Proceso terminado."
}

Write-Step "Limpiando builds anteriores..."
if (Test-Path $WORK_PATH) {
    Remove-Item $WORK_PATH -Recurse -Force
    Write-Ok "Eliminado: $WORK_PATH"
}

if (-not (Test-Path $DIST_PATH)) {
    New-Item -ItemType Directory -Path $DIST_PATH | Out-Null
}

$generatedArtifacts = @(
    $PACKAGE_DIR,
    (Join-Path $DIST_PATH "$EXE_NAME.exe"),
    (Join-Path $DIST_PATH "signature-status.json")
)

foreach ($artifact in $generatedArtifacts) {
    if (Test-Path $artifact) {
        Remove-Item $artifact -Recurse -Force
        Write-Ok "Eliminado: $artifact"
    }
}

Write-Step "Compilando con PyInstaller..."
if (-not (Test-Path $PYTHON)) { Write-Fail "No se encontro Python en: $PYTHON"; exit 1 }

& $PYTHON -m PyInstaller `
    --onedir `
    --name $EXE_NAME `
    --distpath $DIST_PATH `
    --workpath $WORK_PATH `
    --paths Src `
    --hidden-import win32timezone `
    --hidden-import pywintypes `
    --hidden-import servicemanager `
    --hidden-import win32service `
    --hidden-import win32serviceutil `
    --hidden-import pythoncom `
    $ENTRY_POINT

if ($LASTEXITCODE -ne 0) { Write-Fail "PyInstaller fallo con codigo $LASTEXITCODE"; exit 1 }
if (-not (Test-Path $EXE_PATH)) { Write-Fail "No se genero el EXE: $EXE_PATH"; exit 1 }
Write-Ok "EXE generado: $EXE_PATH"

Write-Step "Firmando EXE..."
if (-not (Test-Path $SIGNTOOL)) { Write-Fail "No se encontro signtool en: $SIGNTOOL"; exit 1 }

& $SIGNTOOL sign /sha1 $CERT_THUMBPRINT /fd SHA256 /tr $TIMESTAMP_URL /td SHA256 $EXE_PATH
if ($LASTEXITCODE -ne 0) { Write-Fail "signtool fallo con codigo $LASTEXITCODE"; exit 1 }
Write-Ok "EXE firmado."

Write-Step "Verificando firma..."
$sig = Get-AuthenticodeSignature $EXE_PATH
if ($sig.Status -ne "Valid") { Write-Fail "Firma NO valida. Estado: $($sig.Status)"; exit 1 }

[PSCustomObject]@{
    Status        = [int]$sig.Status
    StatusMessage = $sig.StatusMessage
    Thumbprint    = $sig.SignerCertificate.Thumbprint
    Subject       = $sig.SignerCertificate.Subject
    GeneradoEn    = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json | Out-File "$DIST_PATH\signature-status.json" -Encoding utf8
Write-Ok "Firma valida. Thumbprint: $($sig.SignerCertificate.Thumbprint)"

Write-Step "Copiando conf.json..."
if (Test-Path $CONF_SRC) {
    Copy-Item $CONF_SRC (Join-Path $PACKAGE_DIR "conf.json") -Force
    Write-Ok "conf.json copiado en: $PACKAGE_DIR"
} else {
    Write-Host "  [WARN] No se encontro $CONF_SRC" -ForegroundColor Yellow
}

Write-Step "Copiando instalador CMD..."
if (Test-Path $INSTALLER_CMD) {
    Copy-Item $INSTALLER_CMD (Join-Path $DIST_PATH "instalar-servicio.cmd") -Force
    Write-Ok "instalar-servicio.cmd copiado."
} else {
    Write-Host "  [WARN] No se encontro $INSTALLER_CMD" -ForegroundColor Yellow
}

Write-Step "Copiando desinstalador CMD..."
if (Test-Path $UNINSTALLER_CMD) {
    Copy-Item $UNINSTALLER_CMD (Join-Path $DIST_PATH "desinstalar-servicio.cmd") -Force
    Write-Ok "desinstalar-servicio.cmd copiado."
} else {
    Write-Host "  [WARN] No se encontro $UNINSTALLER_CMD" -ForegroundColor Yellow
}

Write-Host "`n=================================================" -ForegroundColor Cyan
Write-Host "  RELEASE GENERADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  Carpeta: $((Resolve-Path $DIST_PATH).Path)"
Get-ChildItem $DIST_PATH | ForEach-Object {
    if ($_.PSIsContainer) {
        $bytes = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($null -eq $bytes) { $bytes = 0 }
    } else {
        $bytes = $_.Length
    }

    $kb = [math]::Round($bytes / 1KB, 0)
    Write-Host ("    " + $_.Name + " (" + $kb + " KB)")
}
Write-Host ""