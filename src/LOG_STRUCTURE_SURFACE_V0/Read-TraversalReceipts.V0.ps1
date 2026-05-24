param(
    [Parameter(Mandatory=$true)]
    [string]$ReplayId,

    [string]$ReceiptCsv = ".\src\LOG_STRUCTURE_SURFACE_V0\traversal_receipts_v0\receipts\traversal_receipts_v0.csv"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$rows = Import-Csv $ReceiptCsv |
    Where-Object { $_.replay_id -eq $ReplayId } |
    Sort-Object ts_utc

if (@($rows).Count -eq 0) {
    Write-Host "NO RECEIPTS FOR $ReplayId"
    exit 0
}

$rows |
Select-Object `
    receipt_id,
    terrain_id,
    blue_size,
    green_size,
    prior_green_start,
    prior_green_end,
    green_start,
    green_end,
    traversal_direction,
    operator_marker,
    observed_relation,
    local_legibility,
    band_sequence,
    optional_note |
Format-List
