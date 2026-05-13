param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Safe-ImportCsv {
  param([string]$Path)

  if (Test-Path $Path) {
    return @(Import-Csv $Path)
  }

  return @()
}

$OutDir = Join-Path $TerrainRoot "_surface_work\terrain_ecology_comparison_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$StableRows = Safe-ImportCsv (
  Join-Path $TerrainRoot "_surface_work\cross_scale_profile_prototype_v0\stable_profile_summary.csv"
)

$MiddleRows = Safe-ImportCsv (
  Join-Path $TerrainRoot "_surface_work\reuse_geometry_distribution_v0\reuse_geometry_distribution_surface.csv"
)

$ResidualRows = Safe-ImportCsv (
  Join-Path $TerrainRoot "_surface_work\residual_shape_ecology_v0\residual_shape_summary.csv"
)

$TransitionRows = Safe-ImportCsv (
  Join-Path $TerrainRoot "_surface_work\transition_surface_v0\transition_summary.csv"
)

$Files = @()

$Files += $MiddleRows.file
$Files += $ResidualRows.file
$Files += $TransitionRows.file

$Files = @(
  $Files |
    Where-Object { $_ -and $_.Trim() -ne "" } |
    Sort-Object -Unique
)

$SummaryRows = @()

foreach ($File in $Files) {

  $Residual = @(
    $ResidualRows |
      Where-Object { $_.file -eq $File }
  ) | Select-Object -First 1

  $MiddleBucket4 = @(
    $MiddleRows |
      Where-Object {
        $_.file -eq $File -and
        [int]$_.bucket -eq 4
      }
  )

  $DominantMiddle = ""

  if ($MiddleBucket4.Count -gt 0) {

    $Top = $MiddleBucket4 |
      Sort-Object {[double]$_.pct_of_bucket} -Descending |
      Select-Object -First 1

    $DominantMiddle = $Top.pattern_signature
  }

  $SummaryRows += [pscustomobject]@{
    file = $File

    residual_forms =
      if ($Residual) { $Residual.residual_count } else { "" }

    residual_family_count =
      if ($Residual) { $Residual.residual_prefix_family_count } else { "" }

    residual_largest_family_share =
      if ($Residual) { $Residual.largest_residual_family_share } else { "" }

    residual_attachment_ratio =
      if ($Residual) { $Residual.residual_attachment_ratio } else { "" }

    dominant_middle_bucket4 =
      $DominantMiddle
  }
}

$CsvPath = Join-Path $OutDir "terrain_ecology_summary.csv"

$SummaryRows |
  Sort-Object file |
  Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$RowsHtml = foreach ($R in ($SummaryRows | Sort-Object file)) {

@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.dominant_middle_bucket4)</td>
  <td>$($R.residual_forms)</td>
  <td>$($R.residual_family_count)</td>
  <td>$($R.residual_largest_family_share)%</td>
  <td>$($R.residual_attachment_ratio)%</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Terrain Ecology Comparison V0</title>

<style>
body {
  background:#0b0f14;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:28px;
}

.card {
  max-width:1200px;
  margin:auto;
}

h1 {
  margin:0 0 10px 0;
}

.note {
  color:#aaa;
  line-height:1.6;
  margin-bottom:22px;
  max-width:980px;
}

table {
  width:100%;
  border-collapse:collapse;
  font-size:13px;
}

th {
  text-align:left;
  color:#aaa;
  border-bottom:1px solid #34414d;
  padding:10px;
}

td {
  border-bottom:1px solid #24313a;
  padding:10px;
}

.boundary {
  margin-top:24px;
  color:#999;
  font-size:12px;
  line-height:1.7;
  border-top:1px solid #333;
  padding-top:16px;
}
</style>
</head>

<body>
<div class='card'>

<h1>Terrain Ecology Comparison V0</h1>

<div class='note'>
Observer-only terrain comparison surface.
This page compares stable/middle/residual posture summaries without ranking, anomaly scoring, semantic grouping, or ontology collapse.
</div>

<table>
<tr>
  <th>file</th>
  <th>dominant bucket-4 topology</th>
  <th>residual forms</th>
  <th>rough residual families</th>
  <th>largest residual family share</th>
  <th>residual attachment ratio</th>
</tr>

$($RowsHtml -join "`r`n")

</table>

<div class='boundary'>

Current boundary:
stable / middle / residual / transition remain independent persistence regimes.

This page is a comparison scaffold only.

One-line hold:
Different terrains may differ less by anomaly amount and more by how persistence, circulation, reuse, and edge variation distribute across scales.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "TERRAIN_ECOLOGY_COMPARISON_V0.html"

Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== TERRAIN ECOLOGY COMPARISON COMPLETE ==="
Write-Host $HtmlPath
