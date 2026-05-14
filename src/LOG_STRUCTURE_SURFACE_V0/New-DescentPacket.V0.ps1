param(
    [Parameter(Mandatory=$true)]
    [string]$PacketId,

    [Parameter(Mandatory=$true)]
    [string]$Terrain,

    [Parameter(Mandatory=$true)]
    [string]$PacketType,

    [Parameter(Mandatory=$true)]
    [string]$Claim,

    [Parameter(Mandatory=$true)]
    [string]$Question
)

$packetPath = ".\descent_packets\$PacketId"

New-Item `
    -ItemType Directory `
    -Path $packetPath `
    -Force | Out-Null

@"
# $PacketId

Status: open

Packet type: $PacketType

Terrain: $Terrain

Source read: REGIME_ECOLOGY_COMPARISON_V0

Claim under reread:

$Claim

Structural question:

$Question

Boundary:

This packet does not infer:
- anomaly
- causality
- operational meaning
- hidden system state
- lifecycle
- intent

Return required:

- What held?
- What weakened?
- What changed?
- What remains unresolved?
- Bank, revise, stop, or invalidate?
"@ | Set-Content `
        "$packetPath\README.md" `
        -Encoding UTF8

@"
# RETURN_READ

Packet: $PacketId

Status: draft

## Evidence touched

TBD

## What held?

TBD

## What weakened?

TBD

## What changed?

TBD

## What remains unresolved?

TBD

## Decision

TBD

## Boundary

This return read remains observer-side only.

It does not infer:
- anomaly
- causality
- hidden state
- operational meaning
- lifecycle
- intent
"@ | Set-Content `
        "$packetPath\RETURN_READ.md" `
        -Encoding UTF8

$row = [pscustomobject]@{
    packet_id = $PacketId
    source_read_id = "REGIME_ECOLOGY_COMPARISON_V0"
    packet_type = $PacketType
    terrain = $Terrain
    claim = $Claim
    question = $Question
    descent_target = "pending_local_surfaces"
    status = "open"
    boundary = "observer-side recurrence texture only; no lifecycle, anomaly, causality, or hidden state"
    unresolved_scale_behavior = ""
    unresolved_attachment_structure = ""
    unresolved_middle_distribution = ""
}

$manifest = @(Import-Csv ".\DESCENT_MANIFEST_V0.csv")
$manifest = @($manifest) + @($row)

$manifest |
Export-Csv `
    ".\DESCENT_MANIFEST_V0.csv" `
    -NoTypeInformation `
    -Encoding UTF8

Write-Host ""
Write-Host "DESCENT PACKET CREATED"
Write-Host $PacketId
Write-Host ""
