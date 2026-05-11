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

  $StableTemplates = 0
  $MiddleTemplates = 0
  $ResidualTemplates = 0

  foreach ($v in $Counts.Values) {
    if ($v -ge 5) {
      $Stable += $v
      $StableTemplates += 1
    }
    elseif ($v -ge 2) {
      $Middle += $v
      $MiddleTemplates += 1
    }
    else {
      $Residual += $v
      $ResidualTemplates += 1
    }
  }

  $TemplateCount = $Counts.Keys.Count

  $Top10Lines = (
    $Counts.GetEnumerator() |
      Sort-Object Value -Descending |
      Select-Object -First 10 |
      Measure-Object -Property Value -Sum
  ).Sum

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
    stable_lines = $Stable
    middle_lines = $Middle
    residual_lines = $Residual
    stable_templates = $StableTemplates
    middle_templates = $MiddleTemplates
    residual_templates = $ResidualTemplates
    stable_pct = if ($TotalLines -gt 0) { [math]::Round(($Stable / $TotalLines) * 100,1) } else { 0 }
    middle_pct = if ($TotalLines -gt 0) { [math]::Round(($Middle / $TotalLines) * 100,1) } else { 0 }
    residual_pct = if ($TotalLines -gt 0) { [math]::Round(($Residual / $TotalLines) * 100,1) } else { 0 }
    top10_share_pct = $Top10Share
    templates_per_1000_lines = $TemplateDensity
  }
}

$Rows = @($Rows | Sort-Object lines -Descending)

$MaxLines = ($Rows | Measure-Object -Property lines -Maximum).Maximum
if (-not $MaxLines -or $MaxLines -eq 0) { $MaxLines = 1 }

$OutDir = Join-Path $Path "_surface_work\log_structure_file_texture_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$CsvPath = Join-Path $OutDir "log_file_texture_profile.csv"
$Rows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$DetailDir = Join-Path $Path "_surface_work\log_structure_file_detail_v0"

$MaxDensity = ($Rows | Measure-Object -Property templates_per_1000_lines -Maximum).Maximum
if (-not $MaxDensity -or $MaxDensity -eq 0) { $MaxDensity = 1 }

$RowHtml = foreach ($r in $Rows) {

  $SafeFile = $r.file_name -replace '[^A-Za-z0-9_.-]', '_'
  $DetailPath = Join-Path $DetailDir ("LOG_STRUCTURE_FILE_DETAIL_" + $SafeFile + ".html")

  $barWidth = [math]::Max(120, [math]::Round(($r.lines / $MaxLines) * 900))
  $barHeight = [math]::Max(26, [math]::Min(70, [math]::Round(26 + (($r.templates_per_1000_lines / $MaxDensity) * 44))))
  $stableWidth = [math]::Round(($r.stable_pct / 100) * $barWidth)
  $middleWidth = [math]::Round(($r.middle_pct / 100) * $barWidth)
  $residualWidth = [math]::Max(2, $barWidth - $stableWidth - $middleWidth)

  $stableTexture =
    if ($r.top10_share_pct -ge 50) { "smooth" }
    elseif ($r.top10_share_pct -ge 25) { "light_stripe" }
    else { "dense_stripe" }

  $middleTexture =
    if ($r.middle_templates -gt 500) { "dense_grain" }
    elseif ($r.middle_templates -gt 100) { "medium_grain" }
    else { "light_grain" }

  $residualTexture =
    if ($r.residual_pct -ge 10) { "strong_frag" }
    elseif ($r.residual_pct -ge 4) { "medium_frag" }
    else { "light_frag" }

@"
<div class='file-row'>

  <div class='file-head'>
    <div class='file-name'><a href="file:///$DetailPath">$($r.file_name)</a></div>
    <div class='file-meta'>
      lines=$($r.lines) | templates=$($r.templates) | top10=$($r.top10_share_pct)% | templates/1k=$($r.templates_per_1000_lines)
    </div>
  </div>

  <div class='texture-wrap'>
    <div class='texture-bar' style='width:${barWidth}px; height:${barHeight}px'>

      <div class='seg stable $stableTexture' style='width:${stableWidth}px'></div>

      <div class='seg middle $middleTexture' style='width:${middleWidth}px'></div>

      <div class='seg residual $residualTexture' style='width:${residualWidth}px'></div>

    </div>
  </div>

  <div class='file-shares'>
    stable=$($r.stable_pct)% / middle=$($r.middle_pct)% / residual=$($r.residual_pct)%
  </div>

</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>File Texture Profile Bars</title>

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

h1 {
  margin-top:0;
}

.metahead {
  color:#aaa;
  margin-bottom:24px;
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

.file-row {
  margin-bottom:28px;
  padding-bottom:20px;
  border-bottom:1px solid #333;
}

a {
  color:#8fd8f4;
  text-decoration:none;
}

a:hover {
  text-decoration:underline;
}

.file-name {
  font-size:16px;
  font-weight:600;
}

.file-meta {
  color:#999;
  font-size:12px;
  margin-top:4px;
  margin-bottom:10px;
}

.texture-wrap {
  width:930px;
  background:#101010;
  border-radius:10px;
  padding:7px;
  border:1px solid #333;
}

.texture-bar {
  height:42px;
  display:flex;
  overflow:hidden;
  border-radius:8px;
  background:#222;
}

.seg {
  height:100%;
  flex-shrink:0;
}

.stable {
  background:#5bc0eb;
}

.middle {
  background:#9bc53d;
}

.residual {
  background:#e55934;
}

.smooth {
  background:#5bc0eb;
}

.light_stripe {
  background:repeating-linear-gradient(
    90deg,
    #5bc0eb 0px,
    #5bc0eb 12px,
    #8fd8f4 12px,
    #8fd8f4 15px
  );
}

.dense_stripe {
  background:repeating-linear-gradient(
    90deg,
    #5bc0eb 0px,
    #5bc0eb 5px,
    #9ee2f7 5px,
    #9ee2f7 7px
  );
}

.light_grain {
  background:repeating-linear-gradient(
    90deg,
    #9bc53d 0px,
    #9bc53d 14px,
    #b7da64 14px,
    #b7da64 16px
  );
}

.medium_grain {
  background:repeating-linear-gradient(
    90deg,
    #9bc53d 0px,
    #9bc53d 8px,
    #b7da64 8px,
    #b7da64 11px
  );
}

.dense_grain {
  background:repeating-linear-gradient(
    90deg,
    #9bc53d 0px,
    #9bc53d 4px,
    #c8e57c 4px,
    #c8e57c 6px
  );
}

.light_frag {
  background:repeating-linear-gradient(
    90deg,
    #e55934 0px,
    #e55934 18px,
    #f0886f 18px,
    #f0886f 20px
  );
}

.medium_frag {
  background:repeating-linear-gradient(
    90deg,
    #e55934 0px,
    #e55934 10px,
    #f0886f 10px,
    #f0886f 14px
  );
}

.strong_frag {
  background:repeating-linear-gradient(
    90deg,
    #e55934 0px,
    #e55934 5px,
    #f0886f 5px,
    #f0886f 9px
  );
}

.file-shares {
  margin-top:8px;
  color:#aaa;
  font-size:12px;
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

<h1>File Texture Profile Bars</h1>

<div class='metahead'>
Each file is one proportional bar. Bar length reflects file volume. Bar height reflects template density. Color regions show stable / middle / residual. Internal texture shows concentration or dispersion.
</div>

<div class='legend'>
  <div><span class='dot' style='background:#5bc0eb'></span>stable</div>
  <div><span class='dot' style='background:#9bc53d'></span>middle</div>
  <div><span class='dot' style='background:#e55934'></span>residual</div>
  <div>longer bar = more lines</div>
  <div>taller bar = higher template density</div>
  <div>more texture = more dispersion</div>
</div>

$($RowHtml -join "`r`n")

<div class='boundary'>
Boundary: This surface presents file-level structural profiles using recurrence observables. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.
<br><br>
One-line hold: Let each file bar carry volume, band share, and internal texture.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "LOG_STRUCTURE_FILE_TEXTURE_PROFILE_BARS_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== FILE TEXTURE PROFILE BARS COMPLETE ==="
Write-Host $HtmlPath


