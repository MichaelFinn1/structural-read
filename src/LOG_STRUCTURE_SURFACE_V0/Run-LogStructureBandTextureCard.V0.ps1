param(
  [Parameter(Mandatory=$true)]
  [string]$LogSurfaceRoot,

  [string]$Class = "middle"
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path, [string]$Text)
  $tmp = "$Path.tmp"
  $Text | Set-Content $tmp -Encoding UTF8
  Move-Item -Force $tmp $Path
}

function Get-Bucket {
  param([int]$Count)

  if ($Count -eq 1) { return "1" }
  if ($Count -eq 2) { return "2" }
  if ($Count -le 4) { return "3_to_4" }
  if ($Count -le 9) { return "5_to_9" }
  if ($Count -le 49) { return "10_to_49" }
  if ($Count -le 199) { return "50_to_199" }
  return "200_plus"
}

$TemplatePath = Join-Path $LogSurfaceRoot "log_template_surface.csv"

if (-not (Test-Path $TemplatePath)) {
  throw "Missing log_template_surface.csv at: $TemplatePath"
}

$Rows = @(
  Import-Csv $TemplatePath |
    Where-Object { $_.class -eq $Class }
)

if ($Rows.Count -eq 0) {
  throw "No rows found for class: $Class"
}

$TotalLines = 0
foreach ($r in $Rows) {
  $TotalLines += [int]$r.count
}

$Top10Lines = 0
foreach ($r in ($Rows | Sort-Object {[int]$_.count} -Descending | Select-Object -First 10)) {
  $Top10Lines += [int]$r.count
}

$Top10Share = 0
if ($TotalLines -gt 0) {
  $Top10Share = [math]::Round(($Top10Lines / $TotalLines) * 100, 1)
}

$Buckets = $Rows |
  ForEach-Object {
    [pscustomobject]@{
      bucket = Get-Bucket -Count ([int]$_.count)
      count = [int]$_.count
    }
  } |
  Group-Object bucket |
  ForEach-Object {
    $lineSum = 0
    foreach ($x in $_.Group) {
      $lineSum += $x.count
    }

    [pscustomobject]@{
      bucket = $_.Name
      template_count = $_.Count
      line_count = $lineSum
    }
  }

$BucketOrder = @("1","2","3_to_4","5_to_9","10_to_49","50_to_199","200_plus")
$Buckets = $Buckets | Sort-Object { $BucketOrder.IndexOf($_.bucket) }

$MdRows = @()
$HtmlRows = @()

foreach ($b in $Buckets) {
  $pct = 0
  if ($TotalLines -gt 0) {
    $pct = [math]::Round(($b.line_count / $TotalLines) * 100, 1)
  }

  $width = [math]::Max(1, [math]::Round($pct))

  $MdRows += "- $($b.bucket): templates=$($b.template_count), lines=$($b.line_count), share=$pct%"

  $HtmlRows += @"
<div class="row">
  <div class="label">$($b.bucket): templates=$($b.template_count), lines=$($b.line_count), share=$pct%</div>
  <div class="barwrap"><div class="bar" style="width:$width%"></div></div>
</div>
"@
}

$Upper = $Class.ToUpperInvariant()
$MdPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_BAND_TEXTURE_CARD_${Upper}_V0.md"
$HtmlPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_BAND_TEXTURE_CARD_${Upper}_V0.html"

$Md = @"
# LOG_STRUCTURE_BAND_TEXTURE_CARD_${Upper}_V0

Status: structural_band_texture_card

## Focus band

$Class

## Texture summary

- template_count: $($Rows.Count)
- line_count: $TotalLines
- top_10_template_line_share: $Top10Share%

## Count buckets

$($MdRows -join "`r`n")

## Boundary

This card visualizes distribution texture inside one already-surfaced band.

It does not infer incidents, severity, anomaly, cause, importance, or action.

## One-line hold

Show band texture; do not assign meaning.
"@

$Html = @"
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>LOG_STRUCTURE_BAND_TEXTURE_CARD_${Upper}_V0</title>
<style>
body { font-family: Segoe UI, Arial, sans-serif; margin: 32px; max-width: 900px; }
.card { border: 1px solid #ccc; border-radius: 12px; padding: 24px; }
h1 { margin-top: 0; }
.meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 18px 0; }
.box { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
.row { margin: 14px 0; }
.label { font-size: 13px; margin-bottom: 4px; }
.barwrap { height: 18px; border: 1px solid #aaa; border-radius: 6px; overflow: hidden; }
.bar { height: 100%; background: #cfe2f3; }
.boundary { margin-top: 24px; font-size: 14px; color: #444; }
</style>
</head>
<body>
<div class="card">
<h1>Log Structure Band Texture Card</h1>
<h2>Focus band: $Class</h2>

<div class="meta">
<div class="box"><b>Templates</b><br>$($Rows.Count)</div>
<div class="box"><b>Lines</b><br>$TotalLines</div>
<div class="box"><b>Top 10 share</b><br>$Top10Share%</div>
</div>

<h3>Count buckets</h3>
$($HtmlRows -join "`r`n")

<div class="boundary">
<p><b>Boundary:</b> This card visualizes distribution texture inside one already-surfaced band. It does not infer incidents, severity, anomaly, cause, importance, or action.</p>
<p><b>One-line hold:</b> Show band texture; do not assign meaning.</p>
</div>
</div>
</body>
</html>
"@

Write-AtomicText -Path $MdPath -Text $Md
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== BAND TEXTURE CARD COMPLETE ==="
Write-Host $HtmlPath
