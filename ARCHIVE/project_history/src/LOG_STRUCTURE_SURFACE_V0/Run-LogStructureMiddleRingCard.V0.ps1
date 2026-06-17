param(
  [Parameter(Mandatory=$true)]
  [string]$LogSurfaceRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$CsvPath = Join-Path $LogSurfaceRoot "log_template_surface.csv"

if (-not (Test-Path $CsvPath)) {
  throw "Missing log_template_surface.csv"
}

$Rows = Import-Csv $CsvPath

$Middle = @(
  $Rows |
    Where-Object { $_.class -eq "middle" }
)

if ($Middle.Count -eq 0) {
  throw "No middle-band rows found."
}

$TotalTemplates = $Middle.Count
$TotalLines = ($Middle | Measure-Object -Property count -Sum).Sum

$BucketRows = @(
  [pscustomobject]@{
    bucket = "2"
    rows = @($Middle | Where-Object { [int]$_.count -eq 2 })
    color = "#5bc0eb"
  },
  [pscustomobject]@{
    bucket = "3_to_4"
    rows = @($Middle | Where-Object {
      ([int]$_.count -ge 3) -and
      ([int]$_.count -le 4)
    })
    color = "#9bc53d"
  },
  [pscustomobject]@{
    bucket = "5_to_10"
    rows = @($Middle | Where-Object {
      ([int]$_.count -ge 5) -and
      ([int]$_.count -le 10)
    })
    color = "#fde74c"
  }
)

$BucketRows = @(
  $BucketRows |
    Where-Object { $_.rows.Count -gt 0 }
)

$RingSegments = @()

foreach ($b in $BucketRows) {

  $TemplateCount = $b.rows.Count

  $LineCount = (
    $b.rows |
      Measure-Object -Property count -Sum
  ).Sum

  $Share = if ($TotalLines -gt 0) {
    ($LineCount / $TotalLines)
  }
  else {
    0
  }

  $Degrees = [math]::Round($Share * 360, 1)

  $RingSegments += [pscustomobject]@{
    bucket = $b.bucket
    templates = $TemplateCount
    lines = $LineCount
    share = [math]::Round($Share * 100, 1)
    degrees = $Degrees
    color = $b.color
  }
}

$LegendHtml = foreach ($r in $RingSegments) {

@"
<div class='legend-row'>
  <div class='legend-color' style='background:$($r.color)'></div>

  <div class='legend-text'>
    <strong>$($r.bucket)</strong>
    —
    templates=$($r.templates),
    lines=$($r.lines),
    share=$($r.share)%
  </div>
</div>
"@
}

$ConicStops = @()

$Current = 0

foreach ($r in $RingSegments) {

  $Start = $Current
  $End = $Current + $r.degrees

  $ConicStops += "$($r.color) ${Start}deg ${End}deg"

  $Current = $End
}

$ConicGradient = $ConicStops -join ", "

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Middle Band Ring Card</title>

<style>

body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  margin:0;
  padding:30px;
}

.card {
  max-width:900px;
  margin:auto;
  background:#1b1b1b;
  border-radius:16px;
  padding:28px;
}

h1 {
  margin-top:0;
}

.meta {
  color:#aaa;
  margin-bottom:24px;
}

.ring-wrap {
  display:flex;
  align-items:center;
  gap:40px;
  margin-top:20px;
  margin-bottom:30px;
}

.ring {
  width:260px;
  height:260px;
  border-radius:50%;
  background:
    conic-gradient($ConicGradient);
  position:relative;
  flex-shrink:0;
}

.ring::after {
  content:"";
  position:absolute;
  inset:48px;
  background:#1b1b1b;
  border-radius:50%;
}

.center-label {
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-direction:column;
  z-index:2;
  text-align:center;
  font-size:14px;
}

.center-label strong {
  font-size:34px;
}

.legend {
  flex:1;
}

.legend-row {
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom:14px;
}

.legend-color {
  width:18px;
  height:18px;
  border-radius:4px;
}

.legend-text {
  font-size:14px;
  color:#ddd;
}

.boundary {
  color:#aaa;
  font-size:12px;
  line-height:1.6;
  margin-top:20px;
}

</style>
</head>

<body>

<div class='card'>

<h1>Middle Band Texture Ring</h1>

<div class='meta'>
Diffuse recurrence texture surface for middle-band structures.
</div>

<div class='ring-wrap'>

  <div class='ring'>

    <div class='center-label'>
      <div>templates</div>
      <strong>$TotalTemplates</strong>
      <div>lines: $TotalLines</div>
    </div>

  </div>

  <div class='legend'>
    $($LegendHtml -join "`r`n")
  </div>

</div>

<div class='boundary'>

Boundary: This card visualizes recurrence distribution texture inside one already-surfaced middle band. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.

<br><br>

One-line hold: Show diffuse recurrence texture without forcing hierarchical ranking.

</div>

</div>

</body>
</html>
"@

$OutPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_MIDDLE_RING_CARD_V0.html"

Write-AtomicText -Path $OutPath -Text $Html

Write-Host ""
Write-Host "=== MIDDLE RING CARD COMPLETE ==="
Write-Host $OutPath
