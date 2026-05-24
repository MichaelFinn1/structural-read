param(
    [Parameter(Mandatory=$true)]
    [string]$TerrainId,

    [Parameter(Mandatory=$true)]
    [string]$ReplayId,

    [Parameter(Mandatory=$true)]
    [int]$BlueSize,

    [Parameter(Mandatory=$true)]
    [int]$GreenSize,

    [Parameter(Mandatory=$true)]
    [int]$GreenStart,

    [Parameter(Mandatory=$true)]
    [int]$GreenEnd,

    [Parameter(Mandatory=$true)]
    [string]$TraversalDirection,

    [int]$PriorBlueSize = 0,

    [int]$PriorGreenSize = 0,

    [int]$PriorGreenStart = 0,

    [int]$PriorGreenEnd = 0,

    [ValidateSet(
        "test",
        "manual",
        "session",
        "handoff"
    )]
    [string]$ReceiptType = "manual",

    [Parameter(Mandatory=$true)]
    [ValidateSet(
        "seam_emerged",
        "wave_train",
        "fragmentation",
        "smoothing",
        "bridge",
        "unresolved",
        "basin",
        "inversion",
        "repeat",
        "disappearance",
        "carrier",
        "articulation",
        "other"
    )]
    [string]$OperatorMarker,

    [Parameter(Mandatory=$true)]
    [ValidateSet(
        "stabilized_under_widening",
        "fragmented_under_narrowing",
        "persisted_across_transition",
        "emerged_only_in_transition",
        "dissolved_upward",
        "recomposed_downward",
        "held_local_only",
        "smoothed_out",
        "became_ambiguous",
        "other"
    )]
    [string]$ObservedRelation,

    [ValidateSet(
        "strong",
        "moderate",
        "weak",
        "fragmented",
        "smooth",
        "unresolved",
        "unknown"
    )]
    [string]$LocalLegibility = "unknown",

    [string]$BandSequence = "",

    [string]$OptionalNote = "",

    [string]$ReceiptCsv = ".\src\LOG_STRUCTURE_SURFACE_V0\traversal_receipts_v0\receipts\traversal_receipts_v0.csv"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Header = "receipt_id,ts_utc,terrain_id,replay_id,blue_size,green_size,green_start,green_end,traversal_direction,prior_blue_size,prior_green_size,operator_marker,observed_relation,local_legibility,band_sequence,optional_note,prior_green_start,prior_green_end,receipt_type"

$dir = Split-Path $ReceiptCsv -Parent
if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

if (-not (Test-Path $ReceiptCsv)) {
    $Header | Set-Content $ReceiptCsv -Encoding UTF8
} else {
    $first = Get-Content $ReceiptCsv -TotalCount 1
    if ($first -notmatch "prior_green_start") {
        $old = Import-Csv $ReceiptCsv
        $tmp = "$ReceiptCsv.tmp"

        $upgraded = foreach ($r in $old) {
            [pscustomobject]@{
                receipt_id = $r.receipt_id
                ts_utc = $r.ts_utc
                terrain_id = $r.terrain_id
                replay_id = $r.replay_id
                blue_size = $r.blue_size
                green_size = $r.green_size
                green_start = $r.green_start
                green_end = $r.green_end
                traversal_direction = $r.traversal_direction
                prior_blue_size = $r.prior_blue_size
                prior_green_size = $r.prior_green_size
                operator_marker = $r.operator_marker
                observed_relation = $r.observed_relation
                local_legibility = $r.local_legibility
                band_sequence = $r.band_sequence
                optional_note = $r.optional_note
                prior_green_start = ""
                prior_green_end = ""
                receipt_type = "manual"
            }
        }

        $upgraded | Export-Csv $tmp -NoTypeInformation -Encoding UTF8
        Move-Item $tmp $ReceiptCsv -Force
    }
}

function Escape-Csv {
    param([string]$Value)

    if ($null -eq $Value) {
        return '""'
    }

    $v = $Value.Replace('"','""')
    return '"' + $v + '"'
}

$receiptId = "trv_" + (Get-Date -Format "yyyyMMdd_HHmmss_fff")
$ts = (Get-Date).ToUniversalTime().ToString("o")

$fields = @(
    $receiptId,
    $ts,
    $TerrainId,
    $ReplayId,
    "$BlueSize",
    "$GreenSize",
    "$GreenStart",
    "$GreenEnd",
    $TraversalDirection,
    "$PriorBlueSize",
    "$PriorGreenSize",
    $OperatorMarker,
    $ObservedRelation,
    $LocalLegibility,
    $BandSequence,
    $OptionalNote,
    "$PriorGreenStart",
    "$PriorGreenEnd",
    $ReceiptType
)

$line = ($fields | ForEach-Object { Escape-Csv $_ }) -join ","

Add-Content -Path $ReceiptCsv -Value $line -Encoding UTF8

Write-Host "APPENDED $receiptId"
Write-Host "TO $ReceiptCsv"
