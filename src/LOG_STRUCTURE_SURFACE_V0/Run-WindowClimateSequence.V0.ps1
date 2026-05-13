param(
  [Parameter(Mandatory=$true)]
  [string]$WindowGeometryCsv
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$Rows = @(Import-Csv $WindowGeometryCsv)

if ($Rows.Count -eq 0) {
  throw "No rows found."
}

$CsvItem = Get-Item $WindowGeometryCsv
$OutDir = Join-Path $CsvItem.Directory.FullName "window_climate_sequence_v0"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$OutRows = @()

for ($i = 0; $i -lt $Rows.Count; $i++) {

  $R = $Rows[$i]

  $PrevClimate = "boundary"
  $NextClimate = "boundary"

  if ($i -gt 0) {
    $PrevClimate = $Rows[$i - 1].participation_climate
  }

  if ($i -lt ($Rows.Count - 1)) {
    $NextClimate = $Rows[$i + 1].participation_climate
  }

  $Enclosure = [double]$R.enclosure_ratio
  $Edge = [double]$R.edge_ratio
  $Middle = [double]$R.middle_ratio
  $Residual = [double]$R.residual_ratio
  $Diversity = [double]$R.diversity_ratio

  $EdgeMargin = [math]::Round($Edge - $Enclosure, 3)

  $EdgeToBracketedRatio = 0

  if ($Enclosure -gt 0) {
    $EdgeToBracketedRatio = [math]::Round($Edge / $Enclosure, 3)
  }

  $MiddleLiftClass = "low"

  if ($Middle -ge 0.12) {
    $MiddleLiftClass = "high"
  }
  elseif ($Middle -ge 0.07) {
    $MiddleLiftClass = "moderate"
  }

  $LocalTopology = "ordinary"

  if (
    $R.participation_climate -eq "permeability_coupled" -and
    $PrevClimate -ne "permeability_coupled" -and
    $NextClimate -ne "permeability_coupled"
  ) {
    $LocalTopology = "localized_inversion_basin"
  }
  elseif (
    $R.participation_climate -eq "quietly_consolidated" -and
    $PrevClimate -eq "quietly_consolidated" -and
    $NextClimate -eq "quietly_consolidated"
  ) {
    $LocalTopology = "enclosure_corridor"
  }
  elseif (
    $R.participation_climate -eq "enclosure_dominant" -and
    $PrevClimate -eq "enclosure_dominant" -and
    $NextClimate -eq "enclosure_dominant"
  ) {
    $LocalTopology = "enclosure_band"
  }
  elseif (
    $R.participation_climate -eq "permeability_coupled"
  ) {
    $LocalTopology = "permeability_cluster"
  }

  $OutRows += [pscustomobject]@{
    window = $R.window
    prev_climate = $PrevClimate
    climate = $R.participation_climate
    next_climate = $NextClimate
    enclosure_ratio = $Enclosure
    edge_ratio = $Edge
    middle_ratio = $Middle
    residual_ratio = $Residual
    diversity_ratio = $Diversity
    edge_margin = $EdgeMargin
    edge_to_bracketed_ratio = $EdgeToBracketedRatio
    middle_lift_class = $MiddleLiftClass
    local_topology = $LocalTopology
    local_note = ""
  }
}

$OutCsv = Join-Path $OutDir "window_climate_sequence.csv"

$OutRows |
  Export-Csv $OutCsv -NoTypeInformation -Encoding UTF8

$HtmlRows = foreach ($R in $OutRows) {
@"
<tr class='$($R.local_topology)'>
  <td>$($R.window)</td>
  <td>$($R.prev_climate)</td>
  <td>$($R.climate)</td>
  <td>$($R.next_climate)</td>
  <td>$($R.enclosure_ratio)</td>
  <td>$($R.edge_ratio)</td>
  <td>$($R.middle_ratio)</td>
  <td>$($R.residual_ratio)</td>
  <td>$($R.diversity_ratio)</td>
  <td>$($R.edge_margin)</td>
  <td>$($R.edge_to_bracketed_ratio)</td>
  <td>$($R.middle_lift_class)</td>
  <td>$($R.local_topology)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Window Climate Sequence V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:28px; }
.card { max-width:1500px; margin:auto; background:#111820; border:1px solid #2c3945; border-radius:14px; padding:24px; }
.note { color:#aaa; line-height:1.7; margin-bottom:24px; }
table { width:100%; border-collapse:collapse; font-size:12px; }
th { text-align:left; color:#aaa; border-bottom:1px solid #444; padding:7px; }
td { border-bottom:1px solid #27313a; padding:7px; }
.localized_inversion_basin { background:rgba(196,143,255,.18); }
.permeability_cluster { background:rgba(196,143,255,.10); }
.enclosure_corridor { background:rgba(120,200,120,.10); }
.enclosure_band { background:rgba(90,169,230,.08); }
.ordinary { background:rgba(180,180,180,.04); }
.boundary { color:#999; margin-top:28px; border-top:1px solid #2c3945; padding-top:18px; line-height:1.7; }
</style>
</head>
<body>
<div class='card'>

<h1>Window Climate Sequence V0</h1>

<div class='note'>
Observer-only cross-window topology surface.
<br><br>
This exposes neighbor-context patterns across participation climates.
It does not infer entity movement, lifecycle, causality, anomaly, or hidden system state.
</div>

<table>
<tr>
  <th>window</th>
  <th>prev</th>
  <th>climate</th>
  <th>next</th>
  <th>enclosure</th>
  <th>edge</th>
  <th>middle</th>
  <th>residual</th>
  <th>diversity</th>
  <th>edge margin</th>
  <th>edge/bracketed</th>
  <th>middle lift</th>
  <th>local topology</th>
</tr>

$($HtmlRows -join "`r`n")

</table>

<div class='boundary'>
Boundary:
Cross-window topology describes adjacency among window climates.
It does not describe object motion or hidden trajectory.
<br><br>
One-line hold:
Expose climate shifts without inferring trajectories.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "WINDOW_CLIMATE_SEQUENCE_V0.html"

Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== WINDOW CLIMATE SEQUENCE COMPLETE ==="
Write-Host $HtmlPath
Write-Host ""
Write-Host "CSV:"
Write-Host $OutCsv
