param(
    [string]$CerPath = "",
    [ValidateSet("CurrentUser", "LocalMachine")]
    [string]$Scope = "CurrentUser"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

if ([string]::IsNullOrWhiteSpace($CerPath)) {
    $CerPath = Join-Path $repoRoot "dist\signing\SincronizadorContpaqiDev.cer"
}

if (-not (Test-Path $CerPath)) {
    throw "No se encontro el archivo CER: $CerPath"
}

$rootStore = "Cert:\$Scope\Root"
$publisherStore = "Cert:\$Scope\TrustedPublisher"

Import-Certificate -FilePath $CerPath -CertStoreLocation $rootStore | Out-Null
Import-Certificate -FilePath $CerPath -CertStoreLocation $publisherStore | Out-Null

Write-Host "Certificado importado correctamente"
Write-Host "Root: $rootStore"
Write-Host "TrustedPublisher: $publisherStore"
