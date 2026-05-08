param(
  [Parameter(Mandatory=$true)]
  [string]$LogSurfaceRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Text
  )

  $tmp = "$Path.tmp"
  $Text | Set-Content $tmp -Encoding UTF8
  Move-Item -Force $tmp $Path
}

function Read-Field {
  param(
    [string[]]$Lines,
    [string]$Name
  )

  $pattern = "^- " + [regex]::Escape($Name) + ": "
  $line = $Lines | Where-Object { $_ -match $pattern } | Select-Object -First 1

  if (-not $line) {
    return "0"
  }

  return ($line -replace $pattern, "").Trim()
}

$ReadPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_READ_V0.md"

if (-not (Test-Path $ReadPath)) {
  throw "Missing LOG_STRUCTURE_READ_V0.md at: $ReadPath"
}

$Lines = Get-Content $ReadPath

$InputPath = ""
for ($i = 0; $i -lt $Lines.Count; $i++) {
  if ($Lines[$i] -eq "## Input") {
    $InputPath = $Lines[$i + 2]
    break
  }
}

$TerrainName = Split-Path $InputPath -Leaf

$LinesIndexed = [int](Read-Field -Lines $Lines -Name "lines_indexed")
$Stable = [int](Read-Field -Lines $Lines -Name "stable_line_count")
$Middle = [int](Read-Field -Lines $Lines -Name "middle_line_count")
$Residual = [int](Read-Field -Lines $Lines -Name "residual_line_count")
$Templates = [int](Read-Field -Lines $Lines -Name "template_count")

$Total = $Stable + $Middle + $Residual
if ($Total -le 0) {
  $Total = 1
}

$StablePct = [math]::Round(($Stable / $Total) * 100, 1)
$MiddlePct = [math]::Round(($Middle / $Total) * 100, 1)
$ResidualPct = [math]::Round(($Residual / $Total) * 100, 1)

$StableWidth = [math]::Max(1, [math]::Round($StablePct))
$MiddleWidth = [math]::Max(1, [math]::Round($MiddlePct))
$ResidualWidth = [math]::Max(1, [math]::Round($ResidualPct))

$MdPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_TERRAIN_CARD_V0.md"
$HtmlPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_TERRAIN_CARD_V0.html"

$Md = @"
# LOG_STRUCTURE_TERRAIN_CARD_V0

Status: structural_visual_card

## Terrain

$TerrainName

## Core shape

- lines_indexed: $LinesIndexed
- template_count: $Templates
- stable_percent: $StablePct
- middle_percent: $MiddlePct
- residual_percent: $ResidualPct

## Structural band

stable [$StablePct%] | middle [$MiddlePct%] | residual [$ResidualPct%]

## Boundary

This card visualizes already-surfaced structural observables.

It does not infer incidents, severity, cause, anomaly, importance, or action.

## One-line hold

Fast terrain shape; no operational claim.
"@

$Html = @"
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>LOG_STRUCTURE_TERRAIN_CARD_V0</title>
<style>
body { font-family: Segoe UI, Arial, sans-serif; margin: 32px; max-width: 900px; }
.card { border: 1px solid #ccc; border-radius: 12px; padding: 24px; }
h1 { margin-top: 0; }
.meta { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 18px 0; }
.box { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
.band { display: flex; height: 34px; border: 1px solid #999; border-radius: 8px; overflow: hidden; margin-top: 12px; }
.stable { width: $StableWidth%; background: #d9ead3; }
.middle { width: $MiddleWidth%; background: #fff2cc; }
.residual { width: $ResidualWidth%; background: #f4cccc; }
.legend { display: flex; gap: 18px; margin-top: 10px; font-size: 14px; }
.boundary { margin-top: 24px; font-size: 14px; color: #444; }
</style>
</head>
<body>
<div class="card">
<h1>Log Structure Terrain Card</h1>
<h2>$TerrainName</h2>

<div class="meta">
<div class="box"><b>Lines indexed</b><br>$LinesIndexed</div>
<div class="box"><b>Templates</b><br>$Templates</div>
<div class="box"><b>Surface</b><br>stable / middle / residual</div>
</div>

<h3>Structural band</h3>
<div class="band">
<div class="stable" title="stable $StablePct%"></div>
<div class="middle" title="middle $MiddlePct%"></div>
<div class="residual" title="residual $ResidualPct%"></div>
</div>

<div class="legend">
<div>Stable: $StablePct%</div>
<div>Middle: $MiddlePct%</div>
<div>Residual: $ResidualPct%</div>
</div>

<div class="boundary">
<p><b>Boundary:</b> This card visualizes already-surfaced structural observables. It does not infer incidents, severity, cause, anomaly, importance, or action.</p>
<p><b>One-line hold:</b> Fast terrain shape; no operational claim.</p>
</div>
</div>
</body>
</html>
"@

Write-AtomicText -Path $MdPath -Text $Md
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== TERRAIN CARD COMPLETE ==="
Write-Host $HtmlPath
