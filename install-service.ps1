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
    Write-Host "Instalando servicio desde EXE: $ServiceExe"
}
else {
    if (-not (Test-Path $serviceScript)) {
        throw "No se encontro el script del servicio: $serviceScript"
    }

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

    if (-not (Test-Path $PythonExe)) {
        throw "No se encontro Python en: $PythonExe"
    }

    Write-Host "Instalando servicio desde Python: $PythonExe"

    & $PythonExe -c "import win32serviceutil" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "pywin32 no esta instalado en ese Python. Instale con: $PythonExe -m pip install pywin32"
    }
}

$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "El servicio ya existe, se detendra y eliminara antes de reinstalar."
    if ($useExe) {
        & $ServiceExe stop | Out-Null
        & $ServiceExe remove | Out-Null
    }
    else {
        & $PythonExe $serviceScript stop | Out-Null
        & $PythonExe $serviceScript remove | Out-Null
    }
}

if ($useExe) {
    & $ServiceExe --startup auto install
}
else {
    & $PythonExe $serviceScript --startup auto install
}

if ($LASTEXITCODE -ne 0) {
    throw "Fallo la instalacion del servicio."
}

if ($useExe) {
    & $ServiceExe start
}
else {
    & $PythonExe $serviceScript start
}

if ($LASTEXITCODE -ne 0) {
    throw "El servicio se instalo pero no pudo iniciar."
}

Write-Host "Servicio instalado e iniciado correctamente: $ServiceName"
