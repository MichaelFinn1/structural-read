param(
    [Parameter(Mandatory=$true)]
    [string]$PacketId
)

$packetPath = Join-Path ".\descent_packets" $PacketId

if (-not (Test-Path $packetPath)) {
    Write-Host ""
    Write-Host "PACKET NOT FOUND"
    Write-Host $PacketId
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "OPENING PACKET"
Write-Host $PacketId
Write-Host ""

Invoke-Item $packetPath

