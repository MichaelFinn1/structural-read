param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainId,

  [Parameter(Mandatory=$true)]
  [string]$SourceLog,

  [Parameter(Mandatory=$true)]
  [string]$MemberRoot,

  [Parameter(Mandatory=$true)]
  [string]$AdapterId,

  [Parameter(Mandatory=$true)]
  [string]$ObserverConstitutionId,

  [int]$TerritoryStart = 1,

  [int]$TerritoryEnd = 137074,

  [int]$BinSize = 500,

  [string]$WindowSizes = "25,50,75,100,125,150,175,200,225,250,300,375,500,625,750,875,1000"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][AllowEmptyString()][string[]]$Lines
  )

  $Parent = Split-Path -Parent $Path
  if ($Parent) {
    New-Item -ItemType Directory -Force $Parent | Out-Null
  }

  $Tmp = "$Path.tmp"
  $Lines | Set-Content $Tmp -Encoding UTF8
  Move-Item $Tmp $Path -Force
}

if (-not (Test-Path $SourceLog)) {
  throw "SourceLog not found: $SourceLog"
}

$Measured = Join-Path $MemberRoot "measured"
New-Item -ItemType Directory -Force $Measured | Out-Null

$TraversalCsv = Join-Path $Measured "traversal_windows_v0.csv"
$LadderCsv = Join-Path $Measured "focus_ladder_surface_v0.csv"
$TransitionCsv = Join-Path $Measured "focus_transition_surface_v0.csv"
$LocalizationCsv = Join-Path $Measured "focus_transition_localization_v0.csv"
$CandidateCsv = Join-Path $Measured "focus_candidate_zones_v0.csv"
$GeometryCsv = Join-Path $Measured "inter_zone_geometry_observables_v0.csv"
$ReceiptPath = Join-Path $MemberRoot "CONTACT_PACKET_RUN_RECEIPT_V0.md"

Write-Host "CONTACT PACKET"
Write-Host "TerrainId: $TerrainId"
Write-Host "AdapterId: $AdapterId"
Write-Host "ObserverConstitutionId: $ObserverConstitutionId"
Write-Host "SourceLog: $SourceLog"
Write-Host "MemberRoot: $MemberRoot"
Write-Host ""

python ".\tools\Build-TraversalWindowsFromLog.V1.py" `
  --raw-log $SourceLog `
  --out-csv $TraversalCsv `
  --window-sizes $WindowSizes

python ".\tools\Build-FocusLadderSurface.V57A.py" `
  --terrain-id $TerrainId `
  --windows-csv $TraversalCsv `
  --out-csv $LadderCsv `
  --focus-sizes $WindowSizes

python ".\tools\Build-FocusTransitionSurface.V57B.py" `
  --terrain-id $TerrainId `
  --ladder-csv $LadderCsv `
  --out-csv $TransitionCsv

python ".\tools\Build-FocusTransitionLocalization.V57B2.py" `
  --terrain-id $TerrainId `
  --transition-csv $TransitionCsv `
  --out-csv $LocalizationCsv `
  --bin-size $BinSize

python ".\tools\Build-FocusCandidateZones.V57C.py" `
  --terrain-id $TerrainId `
  --localization-csv $LocalizationCsv `
  --out-csv $CandidateCsv `
  --bin-size $BinSize

python ".\tools\Build-InterZoneGeometryObservables.V58G2.py" `
  --terrain-id $TerrainId `
  --candidate-zones-csv $CandidateCsv `
  --out-csv $GeometryCsv `
  --territory-start $TerritoryStart `
  --territory-end $TerritoryEnd

$LocalizationSummary = Import-Csv $LocalizationCsv |
  Group-Object localization_class |
  Sort-Object Count -Descending |
  ForEach-Object { "- $($_.Name): $($_.Count)" }

$CandidateSummary = Import-Csv $CandidateCsv |
  Group-Object candidate_type |
  Sort-Object Count -Descending |
  ForEach-Object { "- $($_.Name): $($_.Count)" }

if ($null -eq $CandidateSummary -or @($CandidateSummary).Count -eq 0) {
  $CandidateSummary = @("- none: 0")
}

$Geometry = Import-Csv $GeometryCsv | Select-Object -First 1

$ReceiptLines = @(
"# CONTACT_PACKET_RUN_RECEIPT_V0",
"",
"Status:",
"completed",
"",
"## Terrain",
"",
$TerrainId,
"",
"## Adapter",
"",
$AdapterId,
"",
"## Observer constitution",
"",
$ObserverConstitutionId,
"",
"## Parameters",
"",
"- bin_size: $BinSize",
"- territory_start: $TerritoryStart",
"- territory_end: $TerritoryEnd",
"- window_sizes: $WindowSizes",
"",
"## Outputs",
"",
"- traversal_windows_v0.csv",
"- focus_ladder_surface_v0.csv",
"- focus_transition_surface_v0.csv",
"- focus_transition_localization_v0.csv",
"- focus_candidate_zones_v0.csv",
"- inter_zone_geometry_observables_v0.csv",
"",
"## Localization summary",
""
)

$ReceiptLines += $LocalizationSummary
$ReceiptLines += @(
"",
"## Candidate summary",
""
)
$ReceiptLines += $CandidateSummary
$ReceiptLines += @(
"",
"## Geometry summary",
"",
"- candidate_count: $($Geometry.candidate_count)",
"- candidate_span_ratio: $($Geometry.candidate_span_ratio)",
"- quiet_span_ratio: $($Geometry.quiet_span_ratio)",
"- quiet_gap_count: $($Geometry.quiet_gap_count)",
"- largest_quiet_gap: $($Geometry.largest_quiet_gap)",
"- occupied_extent_ratio: $($Geometry.occupied_extent_ratio)",
"",
"## Boundary",
"",
"No interpretation.",
"No promotion.",
"No apparatus tuning.",
"No adapter selection.",
"No terrain selection.",
"No next move selected by wrapper."
)

Write-AtomicText -Path $ReceiptPath -Lines $ReceiptLines

Write-Host ""
Write-Host "SUMMARY"

Import-Csv $GeometryCsv |
  Format-Table `
    terrain_id,
    candidate_count,
    candidate_span_ratio,
    quiet_span_ratio,
    quiet_gap_count,
    largest_quiet_gap,
    occupied_extent_ratio `
    -Auto

Write-Host ""
Write-Host "WROTE RECEIPT $ReceiptPath"

