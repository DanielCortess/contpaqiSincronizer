param(
    [string]$ExePath = "",
    [string]$PfxPath = "",
    [string]$PfxPassword = "",
    [string]$TimestampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $ExePath = Join-Path $repoRoot "dist\SincronizadorContpaqiService.exe"
}
if ([string]::IsNullOrWhiteSpace($PfxPath)) {
    $PfxPath = Join-Path $repoRoot "dist\signing\SincronizadorContpaqiDev.pfx"
}

if (-not (Test-Path $ExePath)) {
    throw "No se encontro el EXE: $ExePath"
}
if (-not (Test-Path $PfxPath)) {
    throw "No se encontro el PFX: $PfxPath"
}

if ([string]::IsNullOrWhiteSpace($PfxPassword)) {
    $securePassword = Read-Host "Ingrese password del PFX" -AsSecureString
}
else {
    $securePassword = ConvertTo-SecureString $PfxPassword -AsPlainText -Force
}

$pfx = Get-PfxCertificate -FilePath $PfxPath -Password $securePassword
if (-not $pfx) {
    throw "No se pudo abrir el PFX. Verifique el password."
}

$signResult = Set-AuthenticodeSignature -FilePath $ExePath -Certificate $pfx -TimestampServer $TimestampServer
if ($signResult.Status -ne "Valid" -and $signResult.Status -ne "UnknownError") {
    throw "Error al firmar: $($signResult.Status) - $($signResult.StatusMessage)"
}

$verify = Get-AuthenticodeSignature -FilePath $ExePath
Write-Host "Firma aplicada"
Write-Host "Status: $($verify.Status)"
Write-Host "Message: $($verify.StatusMessage)"
if ($verify.SignerCertificate) {
    Write-Host "Thumbprint: $($verify.SignerCertificate.Thumbprint)"
    Write-Host "Subject: $($verify.SignerCertificate.Subject)"
}
