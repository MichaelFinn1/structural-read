param(
  [Parameter(Mandatory=$true)]
  [string]$ParticipationPathCsv
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$Rows = @(Import-Csv $ParticipationPathCsv)

if ($Rows.Count -eq 0) {
  throw "No rows found in participation path CSV."
}

$CsvItem = Get-Item $ParticipationPathCsv
$OutDir = Join-Path $CsvItem.Directory.FullName "window_participation_geometry_v0"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$OutRows = @()

foreach ($R in $Rows) {

  $StableBracketed = [int]$R.stable_bracketed
  $StableEdge = [int]$R.stable_edge
  $MiddleAttached = [int]$R.middle_attached
  $ResidualClustered = [int]$R.residual_clustered
  $ExactTemplates = [int]$R.exact_template_count
  $Occurrences = [int]$R.family_occurrences

  if ($Occurrences -le 0) {
    continue
  }

  $EnclosureRatio = 0
  $EdgeRatio = 0
  $MiddleRatio = 0
  $ResidualRatio = 0
  $DiversityRatio = 0

  if ($Occurrences -gt 0) {
    $EnclosureRatio = [math]::Round($StableBracketed / $Occurrences, 3)
    $EdgeRatio = [math]::Round($StableEdge / $Occurrences, 3)
    $MiddleRatio = [math]::Round($MiddleAttached / $Occurrences, 3)
    $ResidualRatio = [math]::Round($ResidualClustered / $Occurrences, 3)
    $DiversityRatio = [math]::Round($ExactTemplates / $Occurrences, 3)
  }

  $ParticipationClimate = "balanced"

  if (
    $EdgeRatio -ge $EnclosureRatio -and
    $MiddleRatio -ge 0.10
  ) {
    $ParticipationClimate = "permeability_coupled"
  }
  elseif (
    $EnclosureRatio -ge 0.85 -and
    $EdgeRatio -le 0.10
  ) {
    $ParticipationClimate = "quietly_consolidated"
  }
  elseif (
    $EnclosureRatio -gt $EdgeRatio
  ) {
    $ParticipationClimate = "enclosure_dominant"
  }
  elseif (
    $EdgeRatio -gt $EnclosureRatio
  ) {
    $ParticipationClimate = "boundary_dense"
  }

  $OutRows += [pscustomobject]@{
    window = $R.window
    occurrences = $Occurrences
    exact_templates = $ExactTemplates
    enclosure_ratio = $EnclosureRatio
    edge_ratio = $EdgeRatio
    middle_ratio = $MiddleRatio
    residual_ratio = $ResidualRatio
    diversity_ratio = $DiversityRatio
    participation_climate = $ParticipationClimate
  }
}

$OutCsv = Join-Path $OutDir "window_participation_geometry.csv"

$OutRows |
  Export-Csv $OutCsv -NoTypeInformation -Encoding UTF8

$HtmlRows = foreach ($R in $OutRows) {

@"
<tr class='$($R.participation_climate)'>
<td>$($R.window)</td>
<td>$($R.occurrences)</td>
<td>$($R.exact_templates)</td>
<td>$($R.enclosure_ratio)</td>
<td>$($R.edge_ratio)</td>
<td>$($R.middle_ratio)</td>
<td>$($R.residual_ratio)</td>
<td>$($R.diversity_ratio)</td>
<td>$($R.participation_climate)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Window Participation Geometry V0</title>

<style>
body {
  background:#0b0f14;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:28px;
}

.card {
  max-width:1400px;
  margin:auto;
  background:#111820;
  border:1px solid #2c3945;
  border-radius:14px;
  padding:24px;
}

.note {
  color:#aaa;
  line-height:1.7;
  margin-bottom:24px;
}

table {
  width:100%;
  border-collapse:collapse;
  font-size:13px;
}

th {
  text-align:left;
  color:#aaa;
  border-bottom:1px solid #444;
  padding:8px;
}

td {
  border-bottom:1px solid #27313a;
  padding:8px;
}

.enclosure_dominant {
  background:rgba(90,169,230,.10);
}

.boundary_dense {
  background:rgba(229,89,52,.12);
}

.permeability_coupled {
  background:rgba(196,143,255,.14);
}

.quietly_consolidated {
  background:rgba(120,200,120,.10);
}

.balanced {
  background:rgba(180,180,180,.05);
}

.boundary {
  color:#999;
  margin-top:28px;
  border-top:1px solid #2c3945;
  padding-top:18px;
  line-height:1.7;
}

code {
  color:#cfe9ff;
}
</style>
</head>

<body>

<div class='card'>

<h1>Window Participation Geometry V0</h1>

<div class='note'>
Observer-only comparative participation geometry across bounded windows.
<br><br>

This surface does NOT infer:
<ul>
<li>identity</li>
<li>lifecycle</li>
<li>importance</li>
<li>prediction</li>
<li>causality</li>
<li>system truth</li>
</ul>

It only exposes how participation posture organizes locally across windows.
</div>

<table>

<tr>
<th>window</th>
<th>occurrences</th>
<th>exact templates</th>
<th>enclosure ratio</th>
<th>edge ratio</th>
<th>middle ratio</th>
<th>residual ratio</th>
<th>diversity ratio</th>
<th>participation climate</th>
</tr>

$($HtmlRows -join "`r`n")

</table>

<div class='boundary'>

Boundary:
Participation climates are observational posture summaries only.
They are not developmental stages, anomaly labels, or hidden-state inference.

<br><br>

One-line hold:
Observe how recurrence and variation spatially coexist across windows without turning posture into destiny.

</div>

</div>

</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "WINDOW_PARTICIPATION_GEOMETRY_V0.html"

Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== WINDOW PARTICIPATION GEOMETRY COMPLETE ==="
Write-Host $HtmlPath
Write-Host ""
Write-Host "CSV:"
Write-Host $OutCsv
