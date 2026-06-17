param(
    [Parameter(Mandatory=$true)]
    [string]$ReplayId,

    [string]$ReceiptCsv = ".\src\LOG_STRUCTURE_SURFACE_V0\traversal_receipts_v0\receipts\traversal_receipts_v0.csv",

    [string]$OutCsv = ".\src\LOG_STRUCTURE_SURFACE_V0\traversal_receipts_v0\receipts\traversal_session_summary_v0.csv"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $ReceiptCsv)) {
    throw "Missing receipt CSV: $ReceiptCsv"
}

$rows = Import-Csv $ReceiptCsv | Where-Object { $_.replay_id -eq $ReplayId }

if (@($rows).Count -eq 0) {
    throw "No receipts found for replay_id: $ReplayId"
}

$ordered = $rows | Sort-Object ts_utc

$first = $ordered | Select-Object -First 1
$last = $ordered | Select-Object -Last 1

$markerSeq = ($ordered | ForEach-Object { $_.operator_marker }) -join " -> "
$relationSeq = ($ordered | ForEach-Object { $_.observed_relation }) -join " -> "
$legibilitySeq = ($ordered | ForEach-Object { $_.local_legibility }) -join " -> "

$movementCount = @($ordered).Count

$summaryLine = "Traversal $ReplayId moved from $($first.green_start)-$($first.green_end) to $($last.green_start)-$($last.green_end) across $movementCount receipt(s): $markerSeq."

$outRow = [pscustomobject]@{
    replay_id = $ReplayId
    terrain_id = $first.terrain_id
    first_span = "$($first.green_start)-$($first.green_end)"
    last_span = "$($last.green_start)-$($last.green_end)"
    movement_count = $movementCount
    marker_sequence = $markerSeq
    relation_sequence = $relationSeq
    legibility_sequence = $legibilitySeq
    summary_line = $summaryLine
}

$exists = Test-Path $OutCsv

if (-not $exists) {
    $outRow | Export-Csv $OutCsv -NoTypeInformation -Encoding UTF8
} else {
    $tmp = "$OutCsv.tmp"
    $all = @(Import-Csv $OutCsv | Where-Object { $_.replay_id -ne $ReplayId })
    $all += $outRow
    $all | Export-Csv $tmp -NoTypeInformation -Encoding UTF8
    Move-Item $tmp $OutCsv -Force
}

Write-Host "WROTE $OutCsv"
Write-Host $summaryLine
