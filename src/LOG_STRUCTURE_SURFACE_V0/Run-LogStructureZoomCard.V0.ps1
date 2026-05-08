param(
  [Parameter(Mandatory=$true)]
  [string]$LogSurfaceRoot,

  [string]$Class = "auto",

  [int]$TopN = 12
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path, [string]$Text)
  $tmp = "$Path.tmp"
  $Text | Set-Content $tmp -Encoding UTF8
  Move-Item -Force $tmp $Path
}

$TemplatePath = Join-Path $LogSurfaceRoot "log_template_surface.csv"
$ReadPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_READ_V0.md"

if (-not (Test-Path $TemplatePath)) {
  throw "Missing log_template_surface.csv at: $TemplatePath"
}

$Rows = @(Import-Csv $TemplatePath)

if ($Rows.Count -eq 0) {
  throw "No template rows found."
}

if ($Class -eq "auto") {
  $ClassSummary = $Rows |
    Group-Object class |
    ForEach-Object {
      $sum = 0
      foreach ($r in $_.Group) {
        $sum += [int]$r.count
      }

      [pscustomobject]@{
        class = $_.Name
        line_count = $sum
        template_count = $_.Count
      }
    } |
    Sort-Object line_count -Descending

  $FocusClass = ($ClassSummary | Where-Object { $_.class -eq "middle" } | Select-Object -First 1).class

  if (-not $FocusClass) {
    $FocusClass = ($ClassSummary | Where-Object { $_.class -eq "residual" } | Select-Object -First 1).class
  }

  if (-not $FocusClass) {
    $FocusClass = ($ClassSummary | Select-Object -First 1).class
  }
} else {
  $FocusClass = $Class
}

$FocusRows = @(
  $Rows |
    Where-Object { $_.class -eq $FocusClass } |
    Sort-Object {[int]$_.count} -Descending |
    Select-Object -First $TopN
)

$TotalFocusLines = 0
foreach ($r in $FocusRows) {
  $TotalFocusLines += [int]$r.count
}

$Items = @()
$HtmlItems = @()

foreach ($r in $FocusRows) {
  $count = [int]$r.count
  $template = $r.template

  $pct = 0
  if ($TotalFocusLines -gt 0) {
    $pct = [math]::Round(($count / $TotalFocusLines) * 100, 1)
  }

  $width = [math]::Max(1, [math]::Round($pct))

  $Items += "- count=$count / share=$pct% :: $template"

  $safeTemplate = [System.Net.WebUtility]::HtmlEncode($template)

  $HtmlItems += @"
<div class="row">
  <div class="label">count=$count / $pct%</div>
  <div class="barwrap"><div class="bar" style="width:$width%"></div></div>
  <div class="template">$safeTemplate</div>
</div>
"@
}

if ($Items.Count -eq 0) {
  $Items += "- none surfaced"
  $HtmlItems += "<p>none surfaced</p>"
}

$MdPath = Join-Path $LogSurfaceRoot ("LOG_STRUCTURE_ZOOM_CARD_" + $FocusClass.ToUpperInvariant() + "_V0.md")
$HtmlPath = Join-Path $LogSurfaceRoot ("LOG_STRUCTURE_ZOOM_CARD_" + $FocusClass.ToUpperInvariant() + "_V0.html")

$Md = @"
# LOG_STRUCTURE_ZOOM_CARD_$($FocusClass.ToUpperInvariant())_V0

Status: structural_zoom_card

## Focus band

$FocusClass

## Source

$LogSurfaceRoot

## Top templates in focus band

$($Items -join "`r`n")

## Boundary

This card zooms into one already-surfaced structural band.

It does not infer incidents, severity, anomaly, cause, importance, or action.

## One-line hold

Zoom into structure; do not promote meaning.
"@

$Html = @"
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>LOG_STRUCTURE_ZOOM_CARD_$($FocusClass.ToUpperInvariant())_V0</title>
<style>
body { font-family: Segoe UI, Arial, sans-serif; margin: 32px; max-width: 1000px; }
.card { border: 1px solid #ccc; border-radius: 12px; padding: 24px; }
h1 { margin-top: 0; }
.row { margin: 14px 0; }
.label { font-size: 13px; margin-bottom: 4px; }
.barwrap { height: 16px; border: 1px solid #aaa; border-radius: 6px; overflow: hidden; }
.bar { height: 100%; background: #d9ead3; }
.template { margin-top: 5px; font-family: Consolas, monospace; font-size: 13px; white-space: normal; }
.boundary { margin-top: 24px; font-size: 14px; color: #444; }
</style>
</head>
<body>
<div class="card">
<h1>Log Structure Zoom Card</h1>
<h2>Focus band: $FocusClass</h2>

$($HtmlItems -join "`r`n")

<div class="boundary">
<p><b>Boundary:</b> This card zooms into one already-surfaced structural band. It does not infer incidents, severity, anomaly, cause, importance, or action.</p>
<p><b>One-line hold:</b> Zoom into structure; do not promote meaning.</p>
</div>
</div>
</body>
</html>
"@

Write-AtomicText -Path $MdPath -Text $Md
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== LOG STRUCTURE ZOOM CARD COMPLETE ==="
Write-Host $HtmlPath
