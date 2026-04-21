param(
    [string]$PythonExe = "",
    [string]$ServiceName = "SincronizadorContpaqiService",
    [string]$ServiceExe = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$serviceScript = Join-Path $repoRoot "Src\SyncContpaqWindowsService.py"
$defaultServiceExe = Join-Path $repoRoot "dist\SincronizadorContpaqiService.exe"
$useExe = $false

if ([string]::IsNullOrWhiteSpace($ServiceExe)) {
    $ServiceExe = $defaultServiceExe
}

if (Test-Path $ServiceExe) {
    $useExe = $true
}

if (-not $useExe) {
    if ([string]::IsNullOrWhiteSpace($PythonExe)) {
        $venv32Python = Join-Path $repoRoot ".venv32\Scripts\python.exe"
        $venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

        if (Test-Path $venv32Python) {
            $PythonExe = $venv32Python
        }
        elseif (Test-Path $venvPython) {
            $PythonExe = $venvPython
        }
        else {
            $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
            if (-not $pythonCmd) {
                throw "No se encontro Python. Pase -PythonExe con la ruta del ejecutable."
            }
            $PythonExe = $pythonCmd.Source
        }
    }
}

if (-not $useExe -and -not (Test-Path $serviceScript)) {
    throw "No se encontro el script del servicio: $serviceScript"
}

$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "El servicio no existe: $ServiceName"
    exit 0
}

if ($useExe) {
    & $ServiceExe stop | Out-Null
    & $ServiceExe remove | Out-Null
}
else {
    & $PythonExe $serviceScript stop | Out-Null
    & $PythonExe $serviceScript remove | Out-Null
}

Write-Host "Servicio detenido y eliminado: $ServiceName"
