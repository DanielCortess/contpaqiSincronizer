param(
    [string]$PythonExe = "",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$srcRoot = Join-Path $repoRoot "Src"
$serviceScript = Join-Path $srcRoot "SyncContpaqWindowsService.py"
$distDir = Join-Path $repoRoot "dist"
$buildDir = Join-Path $repoRoot "build"
$specFile = Join-Path $repoRoot "SincronizadorContpaqiService.spec"

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

Write-Host "Usando Python: $PythonExe"

if ($Clean) {
    if (Test-Path $distDir) { Remove-Item -Recurse -Force $distDir }
    if (Test-Path $buildDir) { Remove-Item -Recurse -Force $buildDir }
    if (Test-Path $specFile) { Remove-Item -Force $specFile }
}

& $PythonExe -m pip install --upgrade pip | Out-Null
& $PythonExe -m pip install pywin32 pyinstaller

if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron instalar dependencias de build (pywin32, pyinstaller)."
}

Push-Location $repoRoot
try {
    & $PythonExe -m PyInstaller `
        --noconfirm `
        --clean `
        --name SincronizadorContpaqiService `
        --onefile `
        --paths $srcRoot `
        --hidden-import win32timezone `
        --hidden-import pywintypes `
        --hidden-import pythoncom `
        $serviceScript

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller fallo al generar el ejecutable."
    }
}
finally {
    Pop-Location
}

$targetConf = Join-Path $distDir "conf.json"
Copy-Item -Path (Join-Path $srcRoot "conf.json") -Destination $targetConf -Force

Write-Host "Build completado."
Write-Host "EXE: $(Join-Path $distDir 'SincronizadorContpaqiService.exe')"
Write-Host "Config: $targetConf"
Write-Host "Para instalar: .\install-service.ps1"
