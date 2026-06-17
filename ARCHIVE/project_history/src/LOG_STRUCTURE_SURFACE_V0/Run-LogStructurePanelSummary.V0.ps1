param(
  [Parameter(Mandatory=$true)]
  [string]$PanelRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Text
  )

  $tmp = "$Path.tmp"
  $Text | Set-Content $tmp -Encoding UTF8
  Move-Item -Force $tmp $Path
}

function Read-Field {
  param(
    [string[]]$Lines,
    [string]$Name
  )

  $pattern = "^- " + [regex]::Escape($Name) + ": "
  $line = $Lines | Where-Object { $_ -match $pattern } | Select-Object -First 1

  if (-not $line) {
    return ""
  }

  return ($line -replace $pattern, "").Trim()
}

$Reads = @(
  Get-ChildItem -LiteralPath $PanelRoot -Recurse -Filter "LOG_STRUCTURE_READ_V0.md" |
    Sort-Object FullName
)

$Rows = foreach ($read in $Reads) {
  $lines = Get-Content $read.FullName

  $terrain = $read.FullName.Substring($PanelRoot.Length).TrimStart("\").Split("\")[0]

  [pscustomobject]@{
    terrain = $terrain
    log_files_seen = [int](Read-Field -Lines $lines -Name "log_files_seen")
    lines_indexed = [int](Read-Field -Lines $lines -Name "lines_indexed")
    stable_line_count = [int](Read-Field -Lines $lines -Name "stable_line_count")
    middle_line_count = [int](Read-Field -Lines $lines -Name "middle_line_count")
    residual_line_count = [int](Read-Field -Lines $lines -Name "residual_line_count")
    template_count = [int](Read-Field -Lines $lines -Name "template_count")
    read_path = $read.FullName
  }
}

$OutDir = Join-Path $PanelRoot "_surface_work\log_structure_panel_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$CsvPath = Join-Path $OutDir "log_structure_panel_summary.csv"
$Rows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$TerrainLines = @()
foreach ($r in $Rows) {
  $TerrainLines += "- $($r.terrain): files=$($r.log_files_seen), lines=$($r.lines_indexed), stable=$($r.stable_line_count), middle=$($r.middle_line_count), residual=$($r.residual_line_count), templates=$($r.template_count)"
}

$HighestResidual = $Rows | Sort-Object residual_line_count -Descending | Select-Object -First 1
$HighestMiddle = $Rows | Sort-Object middle_line_count -Descending | Select-Object -First 1
$HighestTemplate = $Rows | Sort-Object template_count -Descending | Select-Object -First 1

$ReadText = @"
# LOG_STRUCTURE_PANEL_SUMMARY_V0

Status: external_operational_log_panel_summary

## Panel root

$PanelRoot

## Terrains surfaced

$($TerrainLines -join "`r`n")

## Readability pressure signals

- highest_residual_terrain: $($HighestResidual.terrain) / $($HighestResidual.residual_line_count)
- highest_middle_terrain: $($HighestMiddle.terrain) / $($HighestMiddle.middle_line_count)
- highest_template_count_terrain: $($HighestTemplate.terrain) / $($HighestTemplate.template_count)

## Outputs

- log_structure_panel_summary.csv
- LOG_STRUCTURE_PANEL_SUMMARY_V0.md

## Boundary

This panel read compares structural reduction surfaces only.

It does not:
- identify incidents
- rank severity
- claim anomaly
- recommend action
- assign operational meaning
- benchmark against anomaly detection systems

## Standing read

The same reducer ran across multiple public operational log terrains without changing method.

## One-line hold

Panel comparison exposes portability and readability pressure, not operational conclusions.
"@

$ReadPath = Join-Path $OutDir "LOG_STRUCTURE_PANEL_SUMMARY_V0.md"
Write-AtomicText -Path $ReadPath -Text $ReadText

Write-Host ""
Write-Host "=== LOG STRUCTURE PANEL SUMMARY COMPLETE ==="
Write-Host $ReadPath
