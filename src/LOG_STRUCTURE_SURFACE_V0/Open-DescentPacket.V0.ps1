param(
    [Parameter(Mandatory=$true)]
    [string]$PacketId
)

$ErrorActionPreference = "Stop"

$packetPath = Join-Path ".\descent_packets" $PacketId

if (-not (Test-Path $packetPath)) {
    Write-Host ""
    Write-Host "PACKET NOT FOUND"
    Write-Host $PacketId
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "DESCENT PACKET REPLAY"
Write-Host "====================="
Write-Host ""
Write-Host "Packet: $PacketId"
Write-Host "Path:   $packetPath"
Write-Host ""

$readme = Join-Path $packetPath "README.md"
$return = Join-Path $packetPath "RETURN_READ.md"

if (Test-Path $readme) {
    Write-Host "Opening README.md"
    Invoke-Item $readme
} else {
    Write-Host "README.md missing"
}

if (Test-Path $return) {
    Write-Host "Opening RETURN_READ.md"
    Invoke-Item $return
} else {
    Write-Host "RETURN_READ.md missing"
}

$htmlFiles = Get-ChildItem $packetPath -File -Filter "*.html"

foreach ($file in $htmlFiles) {
    Write-Host "Opening evidence surface: $($file.Name)"
    Invoke-Item $file.FullName
}

Write-Host ""
Write-Host "Replay hold:"
Write-Host "- read packet question"
Write-Host "- read what held"
Write-Host "- read what weakened"
Write-Host "- read unresolveds"
Write-Host "- do not infer beyond packet boundary"
Write-Host ""
