param(
    [string]$IndexPath = ".\DESCENT_PACKET_INDEX_V0.csv"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $IndexPath)) {
    Write-Host "Packet index not found:"
    Write-Host $IndexPath
    exit 1
}

$rows = @(Import-Csv $IndexPath)

Write-Host ""
Write-Host "DESCENT PACKET INDEX"
Write-Host "===================="
Write-Host ""

foreach ($row in $rows) {
    Write-Host "Packet: $($row.packet_id)"
    Write-Host "  Terrain: $($row.terrain)"
    Write-Host "  Type: $($row.packet_type)"
    Write-Host "  Status: $($row.traversal_status)"
    Write-Host "  Before: $($row.claim_before)"
    Write-Host "  After:  $($row.claim_after)"
    Write-Host "  Unresolved scale: $($row.unresolved_scale_behavior)"
    Write-Host "  Decision: $($row.decision)"
    Write-Host ""
}
