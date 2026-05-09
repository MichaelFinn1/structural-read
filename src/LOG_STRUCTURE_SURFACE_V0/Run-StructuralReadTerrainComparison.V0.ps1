param(
  [Parameter(Mandatory=$true)]
  [string]$PanelRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)
  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$Profiles = @(
  Get-ChildItem $PanelRoot -Recurse -Filter "log_file_texture_profile.csv" |
    Sort-Object FullName
)

if ($Profiles.Count -eq 0) {
  throw "No log_file_texture_profile.csv files found. Run Run-LogStructureFileTextureBars.V0.ps1 on terrains first."
}

$Rows = @()

foreach ($p in $Profiles) {
  $terrain = $p.FullName.Substring($PanelRoot.Length).TrimStart("\").Split("\")[0]
  $files = @(Import-Csv $p.FullName)

  if ($files.Count -eq 0) { continue }

  $totalLines = ($files | Measure-Object -Property lines -Sum).Sum
  $totalTemplates = ($files | Measure-Object -Property templates -Sum).Sum

  $weightedStable = 0
  $weightedMiddle = 0
  $weightedResidual = 0
  $weightedTop10 = 0
  $weightedDensity = 0

  foreach ($f in $files) {
    $lines = [double]$f.lines

    if ($totalLines -gt 0) {
      $weightedStable += $lines * [double]$f.stable_pct
      $weightedMiddle += $lines * [double]$f.middle_pct
      $weightedResidual += $lines * [double]$f.residual_pct
      $weightedTop10 += $lines * [double]$f.top10_share_pct
      $weightedDensity += $lines * [double]$f.templates_per_1000_lines
    }
  }

  $Rows += [pscustomobject]@{
    terrain = $terrain
    files = $files.Count
    lines = [int]$totalLines
    templates = [int]$totalTemplates
    stable_pct = if ($totalLines -gt 0) { [math]::Round($weightedStable / $totalLines, 1) } else { 0 }
    middle_pct = if ($totalLines -gt 0) { [math]::Round($weightedMiddle / $totalLines, 1) } else { 0 }
    residual_pct = if ($totalLines -gt 0) { [math]::Round($weightedResidual / $totalLines, 1) } else { 0 }
    top10_share_pct = if ($totalLines -gt 0) { [math]::Round($weightedTop10 / $totalLines, 1) } else { 0 }
    templates_per_1000_lines = if ($totalLines -gt 0) { [math]::Round($weightedDensity / $totalLines, 1) } else { 0 }
    source_profile = $p.FullName
  }
}

$Rows = @($Rows | Sort-Object terrain)

$OutDir = Join-Path $PanelRoot "_surface_work\structural_read_comparison_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$CsvPath = Join-Path $OutDir "structural_read_terrain_comparison.csv"
$Rows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$MaxLines = ($Rows | Measure-Object -Property lines -Maximum).Maximum
if (-not $MaxLines -or $MaxLines -eq 0) { $MaxLines = 1 }

$RowHtml = foreach ($r in $Rows) {
  $barWidth = [math]::Max(100, [math]::Round(([double]$r.lines / $MaxLines) * 850))
  $stableW = [math]::Round(($r.stable_pct / 100) * $barWidth)
  $middleW = [math]::Round(($r.middle_pct / 100) * $barWidth)
  $residualW = [math]::Max(2, $barWidth - $stableW - $middleW)

@"
<div class='terrain-row'>

  <div class='terrain-head'>
    <div class='terrain-name'>$($r.terrain)</div>
    <div class='terrain-meta'>
      files=$($r.files) | lines=$($r.lines) | templates=$($r.templates) | top10=$($r.top10_share_pct)% | templates/1k=$($r.templates_per_1000_lines)
    </div>
  </div>

  <div class='bar-wrap'>
    <div class='terrain-bar' style='width:${barWidth}px'>
      <div class='stable' style='width:${stableW}px'></div>
      <div class='middle' style='width:${middleW}px'></div>
      <div class='residual' style='width:${residualW}px'></div>
    </div>
  </div>

  <div class='shares'>
    stable=$($r.stable_pct)% / middle=$($r.middle_pct)% / residual=$($r.residual_pct)%
  </div>

</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Structural Read Terrain Comparison</title>

<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  margin:0;
  padding:30px;
}

.card {
  max-width:1180px;
  margin:auto;
  background:#1b1b1b;
  border-radius:16px;
  padding:28px;
}

h1 { margin-top:0; }

.metahead {
  color:#aaa;
  margin-bottom:26px;
}

.legend {
  display:flex;
  gap:18px;
  flex-wrap:wrap;
  color:#bbb;
  font-size:12px;
  margin-bottom:28px;
}

.dot {
  width:10px;
  height:10px;
  display:inline-block;
  border-radius:2px;
  margin-right:5px;
}

.terrain-row {
  margin-bottom:30px;
  padding-bottom:22px;
  border-bottom:1px solid #333;
}

.terrain-name {
  font-size:17px;
  font-weight:600;
}

.terrain-meta {
  color:#999;
  font-size:12px;
  margin-top:4px;
  margin-bottom:10px;
}

.bar-wrap {
  width:900px;
  background:#101010;
  border-radius:10px;
  padding:7px;
  border:1px solid #333;
}

.terrain-bar {
  height:38px;
  display:flex;
  overflow:hidden;
  border-radius:8px;
  background:#222;
}

.stable { background:#5bc0eb; }
.middle { background:#9bc53d; }
.residual { background:#e55934; }

.shares {
  margin-top:8px;
  color:#aaa;
  font-size:12px;
}

.exports {
  background:#202020;
  border-radius:10px;
  padding:14px;
  color:#bbb;
  font-size:13px;
  line-height:1.7;
  margin-top:28px;
}

.boundary {
  margin-top:34px;
  color:#999;
  font-size:12px;
  line-height:1.7;
}
</style>
</head>

<body>
<div class='card'>

<h1>Structural Read Terrain Comparison</h1>

<div class='metahead'>
Comparative structural navigation across terrain folders. Each row is one terrain.
</div>

<div class='legend'>
  <div><span class='dot' style='background:#5bc0eb'></span>stable</div>
  <div><span class='dot' style='background:#9bc53d'></span>middle</div>
  <div><span class='dot' style='background:#e55934'></span>residual</div>
  <div>longer bar = more indexed lines</div>
</div>

$($RowHtml -join "`r`n")

<div class='exports'>
CSV export: $CsvPath
</div>

<div class='boundary'>
Boundary: This surface compares structural profiles across terrains. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.
<br><br>
One-line hold: Compare terrain shapes; do not rank terrain meaning.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "STRUCTURAL_READ_TERRAIN_COMPARISON_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== STRUCTURAL READ TERRAIN COMPARISON COMPLETE ==="
Write-Host $HtmlPath
