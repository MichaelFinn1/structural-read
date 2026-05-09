param(
  [Parameter(Mandatory=$true)]
  [string]$Path
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)
  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Normalize-Template {
  param([string]$Line)

  $t = $Line
  $t = $t -replace '\b\d{1,3}(\.\d{1,3}){3}\b','<ip>'
  $t = $t -replace '[A-Fa-f0-9]{8,}','<hex>'
  $t = $t -replace '\b\d+\b','<num>'
  $t = $t -replace '\s+',' '

  return $t.Trim()
}

$LogFiles = @(
  Get-ChildItem $Path -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$Rows = @()

foreach ($f in $LogFiles) {
  Write-Host "Reading $($f.Name)..."

  $Counts = @{}
  $Lines = Get-Content $f.FullName -ErrorAction SilentlyContinue

  foreach ($line in $Lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }

    $t = Normalize-Template $line

    if (-not $Counts.ContainsKey($t)) {
      $Counts[$t] = 0
    }

    $Counts[$t] += 1
  }

  $TotalLines = ($Counts.Values | Measure-Object -Sum).Sum
  if (-not $TotalLines) { $TotalLines = 0 }

  $Stable = 0
  $Middle = 0
  $Residual = 0

  foreach ($v in $Counts.Values) {
    if ($v -ge 5) { $Stable += $v }
    elseif ($v -ge 2) { $Middle += $v }
    else { $Residual += $v }
  }

  $TemplateCount = $Counts.Keys.Count

  $Top10 = (
    $Counts.GetEnumerator() |
      Sort-Object Value -Descending |
      Select-Object -First 10
  )

  $Top10Lines = ($Top10 | Measure-Object -Property Value -Sum).Sum
  if (-not $Top10Lines) { $Top10Lines = 0 }

  $Top10Share = if ($TotalLines -gt 0) {
    [math]::Round(($Top10Lines / $TotalLines) * 100,1)
  } else { 0 }

  $TemplateDensity = if ($TotalLines -gt 0) {
    [math]::Round(($TemplateCount / $TotalLines) * 1000,1)
  } else { 0 }

  $Rows += [pscustomobject]@{
    file_name = $f.Name
    lines = $TotalLines
    templates = $TemplateCount
    stable_pct = if ($TotalLines -gt 0) { [math]::Round(($Stable / $TotalLines) * 100,1) } else { 0 }
    middle_pct = if ($TotalLines -gt 0) { [math]::Round(($Middle / $TotalLines) * 100,1) } else { 0 }
    residual_pct = if ($TotalLines -gt 0) { [math]::Round(($Residual / $TotalLines) * 100,1) } else { 0 }
    top10_share_pct = $Top10Share
    templates_per_1000_lines = $TemplateDensity
  }
}

$Rows = @($Rows | Sort-Object lines -Descending)

$TotalTerrainLines = ($Rows | Measure-Object -Property lines -Sum).Sum
if (-not $TotalTerrainLines) { $TotalTerrainLines = 0 }

foreach ($r in $Rows) {
  if ($TotalTerrainLines -gt 0) {
    $share = [math]::Round(($r.lines / $TotalTerrainLines) * 100,1)
  } else {
    $share = 0
  }

  $r | Add-Member -NotePropertyName file_line_share_pct -NotePropertyValue $share -Force
}

$OutDir = Join-Path $Path "_surface_work\log_structure_file_profiles_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$CsvPath = Join-Path $OutDir "log_file_profile_surface.csv"
$Rows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$MaxDensity = ($Rows | Measure-Object -Property templates_per_1000_lines -Maximum).Maximum
if (-not $MaxDensity -or $MaxDensity -eq 0) { $MaxDensity = 1 }

$MaxResidual = ($Rows | Measure-Object -Property residual_pct -Maximum).Maximum
if (-not $MaxResidual -or $MaxResidual -eq 0) { $MaxResidual = 1 }

$MaxLines = ($Rows | Measure-Object -Property lines -Maximum).Maximum
if (-not $MaxLines -or $MaxLines -eq 0) { $MaxLines = 1 }

$DotHtml = foreach ($r in $Rows) {
  $x = [math]::Round(40 + (($r.templates_per_1000_lines / $MaxDensity) * 620),0)
  $y = [math]::Round(310 - (($r.residual_pct / $MaxResidual) * 240),0)
  $size = [math]::Round(10 + (($r.lines / $MaxLines) * 28),0)

@"
<div class='dot' style='left:${x}px; top:${y}px; width:${size}px; height:${size}px;'>
  <span>$($r.file_name)</span>
</div>
"@
}

$RowHtml = foreach ($r in $Rows) {
@"
<div class='row'>

  <div class='fileline'>
    <div class='name'>$($r.file_name)</div>
    <div class='meta'>lines=$($r.lines) | templates=$($r.templates) | file share=$($r.file_line_share_pct)%</div>
  </div>

  <div class='band'>
    <div class='stable' style='width:$($r.stable_pct)%'></div>
    <div class='middle' style='width:$($r.middle_pct)%'></div>
    <div class='residual' style='width:$($r.residual_pct)%'></div>
  </div>

  <div class='shares'>
    stable=$($r.stable_pct)% |
    middle=$($r.middle_pct)% |
    residual=$($r.residual_pct)% |
    top10=$($r.top10_share_pct)% |
    templates/1k=$($r.templates_per_1000_lines)
  </div>

</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>File Profile Map</title>
<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  margin:0;
  padding:30px;
}
.card {
  max-width:1200px;
  margin:auto;
  background:#1b1b1b;
  border-radius:16px;
  padding:28px;
}
h1 { margin-top:0; }
.metahead {
  color:#aaa;
  margin-bottom:22px;
}
.map {
  position:relative;
  width:720px;
  height:340px;
  background:#151515;
  border:1px solid #333;
  border-radius:12px;
  margin-bottom:28px;
}
.axis-x {
  position:absolute;
  left:40px;
  right:40px;
  bottom:28px;
  height:1px;
  background:#555;
}
.axis-y {
  position:absolute;
  left:40px;
  top:40px;
  bottom:28px;
  width:1px;
  background:#555;
}
.axis-label-x {
  position:absolute;
  bottom:5px;
  left:250px;
  color:#aaa;
  font-size:12px;
}
.axis-label-y {
  position:absolute;
  top:12px;
  left:48px;
  color:#aaa;
  font-size:12px;
}
.dot {
  position:absolute;
  border-radius:50%;
  background:#66ccff;
  opacity:0.85;
  transform:translate(-50%,-50%);
  border:1px solid #eee;
}
.dot span {
  position:absolute;
  left:12px;
  top:-2px;
  white-space:nowrap;
  font-size:11px;
  color:#ddd;
}
.legend {
  color:#aaa;
  font-size:12px;
  margin-bottom:24px;
}
.row {
  margin-bottom:22px;
  padding-bottom:16px;
  border-bottom:1px solid #333;
}
.name {
  font-size:15px;
  font-weight:600;
  margin-bottom:5px;
}
.meta {
  color:#999;
  font-size:12px;
  margin-bottom:8px;
}
.band {
  width:100%;
  height:22px;
  display:flex;
  overflow:hidden;
  border-radius:7px;
  background:#222;
}
.stable { background:#5bc0eb; }
.middle { background:#9bc53d; }
.residual { background:#e55934; }
.shares {
  margin-top:6px;
  color:#aaa;
  font-size:11px;
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

<h1>File Profile Map</h1>

<div class='metahead'>
Spatial file profile surface. Each dot is one file.
</div>

<div class='map'>
  <div class='axis-x'></div>
  <div class='axis-y'></div>
  <div class='axis-label-x'>template density →</div>
  <div class='axis-label-y'>residual share ↑</div>
  $($DotHtml -join "`r`n")
</div>

<div class='legend'>
Dot size = file line volume. X = templates per 1000 lines. Y = residual share.
</div>

$($RowHtml -join "`r`n")

<div class='boundary'>
Boundary: This surface presents file-level structural profiles using recurrence observables. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.
<br><br>
One-line hold: Show terrain shape through stacked file-level structural profiles.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "LOG_STRUCTURE_FILE_PROFILE_MAP_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== FILE PROFILE MAP COMPLETE ==="
Write-Host $HtmlPath
