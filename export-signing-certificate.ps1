param(
    [string]$Subject = "CN=SincronizadorContpaqi Dev",
    [string]$OutputDir = "",
    [string]$PfxPassword = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $repoRoot "dist\signing"
}

New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null

$cert = Get-ChildItem -Path "Cert:\CurrentUser\My" |
    Where-Object {
        $_.Subject -eq $Subject -and
        $_.EnhancedKeyUsageList.FriendlyName -contains "Code Signing"
    } |
    Sort-Object NotAfter -Descending |
    Select-Object -First 1

if (-not $cert) {
    throw "No se encontro certificado de firma para Subject '$Subject' en Cert:\CurrentUser\My"
}

$cerPath = Join-Path $OutputDir "SincronizadorContpaqiDev.cer"
$pfxPath = Join-Path $OutputDir "SincronizadorContpaqiDev.pfx"

Export-Certificate -Cert $cert -FilePath $cerPath -Force | Out-Null

if ([string]::IsNullOrWhiteSpace($PfxPassword)) {
    $securePassword = Read-Host "Ingrese password para exportar PFX" -AsSecureString
}
else {
    $securePassword = ConvertTo-SecureString $PfxPassword -AsPlainText -Force
}

Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $securePassword -Force | Out-Null

Write-Host "Certificado exportado correctamente"
Write-Host "CER: $cerPath"
Write-Host "PFX: $pfxPath"
Write-Host "Thumbprint: $($cert.Thumbprint)"
