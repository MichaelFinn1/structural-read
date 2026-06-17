param(
  [Parameter(Mandatory=$true)]
  [string]$LogSurfaceRoot,

  [Parameter(Mandatory=$true)]
  [ValidateSet("stable","middle","residual")]
  [string]$Class,

  [int]$MaxTemplates = 16
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)
  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$CsvPath = Join-Path $LogSurfaceRoot "log_template_surface.csv"
if (-not (Test-Path $CsvPath)) { throw "Missing log_template_surface.csv" }

$Rows = Import-Csv $CsvPath

$BandRows = @(
  $Rows |
    Where-Object { $_.class -eq $Class } |
    Sort-Object {[int]$_.count} -Descending
)

if ($BandRows.Count -eq 0) { throw "No rows for class: $Class" }

$TotalTemplates = $BandRows.Count
$TotalLines = ($BandRows | Measure-Object -Property count -Sum).Sum

$Top10 = ($BandRows | Select-Object -First 10 | Measure-Object -Property count -Sum).Sum
$Top10Share = if ($TotalLines -gt 0) { [math]::Round(($Top10 / $TotalLines) * 100, 1) } else { 0 }

$Counts = @($BandRows | ForEach-Object { [int]$_.count })
$MaxCount = ($Counts | Measure-Object -Maximum).Maximum
$MinCount = ($Counts | Measure-Object -Minimum).Minimum

$ModeText =
  if ($Class -eq "stable") { "Top recurring structures" }
  elseif ($Class -eq "middle") { "Texture samples from diffuse recurrence" }
  else { "Small sample from sparse residual structure" }

$Take =
  if ($Class -eq "stable") { $MaxTemplates }
  elseif ($Class -eq "middle") { [math]::Min(12, $BandRows.Count) }
  else { [math]::Min(8, $BandRows.Count) }

$Representative = @($BandRows | Select-Object -First $Take)

$RowsHtml = foreach ($r in $Representative) {
  $Count = [int]$r.count
  $Width = if ($MaxCount -gt 0) {
    [math]::Max(4,[math]::Min(100,[math]::Round(($Count / $MaxCount) * 100)))
  } else { 4 }

@"
<div class='template-row'>
  <div class='template-left'>
    <div class='template-count'>$Count</div>
    <div class='template-bar-wrap'><div class='template-bar' style='width:${Width}%'></div></div>
  </div>
  <div class='template-text'>$($r.template)</div>
</div>
"@
}

$BucketGroups = $BandRows |
  ForEach-Object {
    $c = [int]$_.count
    $bucket =
      if ($c -eq 1) { "1" }
      elseif ($c -eq 2) { "2" }
      elseif ($c -le 4) { "3_to_4" }
      elseif ($c -le 10) { "5_to_10" }
      elseif ($c -le 50) { "11_to_50" }
      else { "51_plus" }

    [pscustomobject]@{
      bucket = $bucket
      count = $c
    }
  } |
  Group-Object bucket

$BucketOrder = @("1","2","3_to_4","5_to_10","11_to_50","51_plus")

$BucketLines = foreach ($b in $BucketOrder) {
  $g = $BucketGroups | Where-Object { $_.Name -eq $b } | Select-Object -First 1
  if ($g) {
    $templates = $g.Count
    $lines = ($g.Group | Measure-Object -Property count -Sum).Sum
    $share = if ($TotalLines -gt 0) { [math]::Round(($lines / $TotalLines) * 100, 1) } else { 0 }
    "<div class='bucket'><span>$b</span><strong>$templates templates</strong><em>$lines lines / $share%</em></div>"
  }
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Representative Slice</title>
<style>
body { font-family: Segoe UI, Arial; background: #111; color: #eee; margin: 24px; }
.card { max-width: 1100px; margin: auto; background: #1b1b1b; border-radius: 12px; padding: 24px; }
h1 { margin-top: 0; }
.meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0; }
.metric { background: #242424; border-radius: 10px; padding: 12px; }
.metric div { color: #aaa; font-size: 12px; }
.metric strong { font-size: 22px; }
.band { display: inline-block; padding: 6px 12px; border-radius: 8px; background: #333; margin-bottom: 8px; }
.mode { color: #bbb; margin-bottom: 18px; }
.buckets { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin: 18px 0 26px 0; }
.bucket { background: #242424; border-radius: 8px; padding: 10px; font-size: 12px; }
.bucket span { display:block; color:#aaa; }
.bucket strong { display:block; margin-top:4px; }
.bucket em { display:block; color:#aaa; margin-top:4px; font-style:normal; }
.template-row { display: grid; grid-template-columns: 120px 1fr; gap: 12px; margin-bottom: 9px; align-items: start; }
.template-count { font-size: 12px; color: #aaa; margin-bottom: 4px; }
.template-bar-wrap { background: #222; height: 8px; border-radius: 6px; overflow: hidden; }
.template-bar { height: 100%; background: #66ccff; }
.template-text { font-family: Consolas, monospace; font-size: 12px; line-height: 1.35; color: #ddd; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.boundary { margin-top: 28px; font-size: 12px; color: #aaa; line-height: 1.6; }
</style>
</head>
<body>
<div class='card'>
<h1>Representative Slice Card</h1>

<div class='band'>Focus band: $Class</div>
<div class='mode'>$ModeText</div>

<div class='meta'>
  <div class='metric'><div>Templates</div><strong>$TotalTemplates</strong></div>
  <div class='metric'><div>Lines</div><strong>$TotalLines</strong></div>
  <div class='metric'><div>Top 10 share</div><strong>$Top10Share%</strong></div>
  <div class='metric'><div>Count range</div><strong>$MinCount-$MaxCount</strong></div>
</div>

<div class='buckets'>
$($BucketLines -join "`r`n")
</div>

$($RowsHtml -join "`r`n")

<div class='boundary'>
Boundary: This surface presents representative recurring structures from one already-surfaced band. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.<br><br>
One-line hold: Descend into representative structure while preserving terrain context.
</div>

</div>
</body>
</html>
"@

$OutPath = Join-Path $LogSurfaceRoot ("LOG_STRUCTURE_REPRESENTATIVE_SLICE_" + $Class.ToUpper() + "_V0.html")
Write-AtomicText -Path $OutPath -Text $Html

Write-Host ""
Write-Host "=== REPRESENTATIVE SLICE COMPLETE ==="
Write-Host $OutPath
