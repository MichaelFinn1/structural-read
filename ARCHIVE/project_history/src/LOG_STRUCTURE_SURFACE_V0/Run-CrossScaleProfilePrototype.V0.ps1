param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Normalize-Template {
  param([string]$Line)

  $t = $Line
  $t = $t -replace '\b\d{1,3}(\.\d{1,3}){3}\b','<ip>'
  $t = $t -replace '[A-Fa-f0-9]{8,}','<hex>'
  $t = $t -replace '\b\d+\b','<num>'
  $t = $t -replace '\s+',' '

  return $t.Trim()
}

function Html-Encode {
  param([string]$Text)
  return [System.Net.WebUtility]::HtmlEncode($Text)
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\cross_scale_profile_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$ReuseCsv = Join-Path $TerrainRoot "_surface_work\reuse_geometry_distribution_v0\reuse_geometry_distribution_surface.csv"
$ReuseRows = @()

if (Test-Path $ReuseCsv) {
  $ReuseRows = @(Import-Csv $ReuseCsv)
}

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' -and $_.FullName -notmatch '\\_surface_work\\' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$Profiles = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $Counts = @{}
  $Lines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)

  foreach ($Line in $Lines) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }

    $T = Normalize-Template $Line

    if (-not $Counts.ContainsKey($T)) {
      $Counts[$T] = 0
    }

    $Counts[$T] += 1
  }

  $Templates = @(
    $Counts.GetEnumerator() |
      ForEach-Object {
        [pscustomobject]@{
          template = $_.Key
          count = [int]$_.Value
        }
      }
  )

  $Stable = @($Templates | Where-Object { $_.count -ge 5 } | Sort-Object count -Descending)
  $Middle = @($Templates | Where-Object { $_.count -ge 2 -and $_.count -le 4 })
  $Residual = @($Templates | Where-Object { $_.count -eq 1 })

  $StableLines = ($Stable | Measure-Object -Property count -Sum).Sum
  $MiddleLines = ($Middle | Measure-Object -Property count -Sum).Sum
  $ResidualLines = ($Residual | Measure-Object -Property count -Sum).Sum

  if (-not $StableLines) { $StableLines = 0 }
  if (-not $MiddleLines) { $MiddleLines = 0 }
  if (-not $ResidualLines) { $ResidualLines = 0 }

  $Profiles += [pscustomobject]@{
    file = $File.Name
    total_lines = $Lines.Count
    unique_templates = $Templates.Count
    stable_templates = $Stable.Count
    middle_templates = $Middle.Count
    residual_templates = $Residual.Count
    stable = $Stable
    stable_lines = $StableLines
    middle_lines = $MiddleLines
    residual_lines = $ResidualLines
  }
}

$RowsHtml = foreach ($P in $Profiles) {
  $CurvePoints = @()
  $Running = 0
  $Rank = 0

  foreach ($S in $P.stable) {
    $Rank += 1
    $Running += $S.count

    if ($P.stable.Count -gt 1) {
      $X = [math]::Round((($Rank - 1) / ($P.stable.Count - 1)) * 100, 2)
    } else {
      $X = 100
    }

    if ($P.stable_lines -gt 0) {
      $Y = [math]::Round(($Running / $P.stable_lines) * 100, 2)
    } else {
      $Y = 0
    }

    $CurvePoints += "$X,$(100 - $Y)"
  }

  if ($CurvePoints.Count -eq 0) {
    $CurvePoints += "0,100"
    $CurvePoints += "100,100"
  }

  $CurvePointString = $CurvePoints -join " "

  $MiddleRows = @(
    $ReuseRows |
      Where-Object { $_.file -eq $P.file } |
      Sort-Object bucket,pattern_signature
  )

  $MiddleTotal = 0
  foreach ($R in $MiddleRows | Where-Object { [int]$_.bucket -in @(2,3,4) }) {
    $MiddleTotal += [int]$R.forms
  }

  $MiddleHtml = foreach ($Bucket in @(2,3,4)) {
    $BucketRows = @(
      $MiddleRows |
        Where-Object { [int]$_.bucket -eq $Bucket } |
        Sort-Object {[double]$_.pct_of_bucket} -Descending
    )

    if ($BucketRows.Count -eq 0) { continue }

    $BucketTotal = ($BucketRows | Select-Object -First 1).bucket_total_forms
    $BucketTotalInt = [int]$BucketTotal

    $Segments = foreach ($R in $BucketRows) {
      $Width = [math]::Round([double]$R.pct_of_bucket, 2)
      $Dark = [math]::Min(0.95, [math]::Max(0.25, ([double]$R.pct_of_bucket / 100)))
      $Pattern = Html-Encode $R.pattern_signature

      "<span class='mid-seg' style='width:${Width}%; opacity:$Dark' title='bucket $Bucket / $Pattern / $Width%'></span>"
    }

    $BucketShare = if ($MiddleTotal -gt 0) {
      [math]::Round(($BucketTotalInt / $MiddleTotal) * 100, 1)
    } else {
      0
    }

@"
<div class='middle-bucket'>
  <div class='bucket-label'>
    <strong>$Bucket</strong>
    <span>($BucketTotalInt)</span>
  </div>
  <div class='middle-strip-frame'>
    <div class='middle-strip' style='width:$BucketShare%'>$($Segments -join "")</div>
  </div>
  <div class='bucket-share'>$BucketShare%</div>
</div>
"@
  }

  $ResidualMacroCount = [math]::Ceiling($P.residual_templates / 100)
  $VisibleMacroBlocks = [math]::Min($ResidualMacroCount, 8)

  $Boxes = foreach ($m in 1..$VisibleMacroBlocks) {
    $MacroStart = ($m - 1) * 100

    $SubBoxes = foreach ($s in 1..4) {
      $SubStart = $MacroStart + (($s - 1) * 25)
      $Remaining = $P.residual_templates - $SubStart
      $DotsInBox = [math]::Max(0, [math]::Min(25, $Remaining))

      $Dots = foreach ($i in 1..25) {
        if ($i -le $DotsInBox) {
          "<span class='res-dot on'></span>"
        } else {
          "<span class='res-dot off'></span>"
        }
      }

      "<div class='res-box'>$($Dots -join '')</div>"
    }

    "<div class='res-macro'>$($SubBoxes -join '')</div>"
  }

  $SafeFile = Html-Encode $P.file

@"
<div class='profile-row'>
  <div class='file-panel'>
    <div class='file-name'>$SafeFile</div>
    <div class='meta'>lines: $($P.total_lines)</div>
    <div class='meta'>unique forms: $($P.unique_templates)</div>
    <div class='meta'>stable (>=5): $($P.stable_templates)</div>
    <div class='meta'>middle (2-4): $($P.middle_templates)</div>
    <div class='meta'>residual (=1): $($P.residual_templates)</div>
  </div>

  <div class='region stable-region'>
    <div class='region-title'>stable shape</div>
    <svg viewBox='0 0 100 100' preserveAspectRatio='none' class='stable-svg'>
      <line x1='0' y1='90' x2='100' y2='90' class='guide'></line>
      <line x1='0' y1='50' x2='100' y2='50' class='guide'></line>
      <line x1='0' y1='0' x2='100' y2='0' class='guide soft'></line>
      <polyline points='$CurvePointString'></polyline>
    </svg>
    <div class='axis-note'>cumulative stable recurrence</div>
  </div>

  <div class='region middle-region'>
    <div class='region-title'>middle reuse topology</div>
    <div class='region-subnote'>row length = bucket share of middle; shade = pattern dominance</div>
    $($MiddleHtml -join "`r`n")
  </div>

  <div class='region residual-region'>
    <div class='region-title'>residual field</div>
    <div class='region-subnote'>each macro block = 100 singleton forms; each small box = 25</div>
    <div class='res-wrap'>$($Boxes -join "")</div>
    <div class='res-total'>$($P.residual_templates) residuals / $ResidualMacroCount hundred-blocks</div>
  </div>
</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Cross Scale Profile Prototype V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:24px; }
.card { max-width:1500px; margin:auto; }
h1 { margin:0 0 8px 0; }
.note { color:#aaa; line-height:1.55; max-width:1120px; margin-bottom:22px; }
.profile-row { display:grid; grid-template-columns:180px 1.25fr 1.25fr 1.05fr; gap:12px; align-items:stretch; margin:12px 0; }
.file-panel,.region { background:#111820; border:1px solid #2b3a46; border-radius:9px; padding:12px; min-height:150px; }
.file-panel { display:flex; flex-direction:column; justify-content:center; }
.file-name { font-weight:700; color:#fff; font-size:18px; margin-bottom:12px; }
.meta { color:#c7c7c7; font-size:13px; margin:3px 0; }
.region-title { color:#aaa; font-size:13px; margin-bottom:8px; }
.region-subnote { color:#aaa; font-size:11px; margin-bottom:8px; }
.stable-svg { width:100%; height:112px; background:linear-gradient(to bottom,#0d2234,#07101d); border-radius:7px; }
.stable-svg polyline { fill:none; stroke:#65e6ff; stroke-width:2.3; vector-effect:non-scaling-stroke; filter:drop-shadow(0 0 4px rgba(101,230,255,.6)); }
.stable-svg .guide { stroke:rgba(210,230,255,.34); stroke-width:.65; stroke-dasharray:2 2; vector-effect:non-scaling-stroke; }
.stable-svg .soft { stroke:rgba(210,230,255,.18); }
.axis-note { color:#aaa; font-size:11px; text-align:center; margin-top:5px; }
.middle-bucket { display:grid; grid-template-columns:54px 1fr 52px; gap:8px; align-items:center; margin:10px 0; }
.bucket-label strong { font-size:18px; display:block; color:#eee; }
.bucket-label span { font-size:12px; color:#bbb; }
.middle-strip-frame { height:22px; background:#0c1b12; border:1px solid #263a28; border-radius:7px; overflow:hidden; }
.middle-strip { height:100%; background:rgba(120,220,80,.12); white-space:nowrap; border-radius:6px; overflow:hidden; }
.mid-seg { display:inline-block; height:100%; background:#8bd85c; border-right:1px solid rgba(0,0,0,.35); }
.bucket-share { color:#93e66a; font-weight:700; text-align:right; }
.res-wrap { display:flex; flex-wrap:wrap; gap:12px; align-content:start; }
.res-macro { display:grid; grid-template-columns:repeat(2, 42px); grid-template-rows:repeat(2, 42px); gap:6px; padding:6px; border:1px solid #3b4650; border-radius:8px; background:#10151b; }
.res-box { width:42px; height:42px; border:1px solid #3b4650; border-radius:6px; display:grid; grid-template-columns:repeat(5, 1fr); grid-template-rows:repeat(5, 1fr); gap:2px; padding:5px; background:#151b22; }
.res-dot { width:5px; height:5px; border-radius:50%; align-self:center; justify-self:center; }
.res-dot.on { background:#ef5138; opacity:.9; }
.res-dot.off { background:transparent; }
.res-total { color:#ff654c; font-size:13px; margin-top:10px; }
.boundary { margin-top:24px; color:#999; font-size:12px; line-height:1.7; border-top:1px solid #333; padding-top:16px; }
</style>
</head>
<body>
<div class='card'>
<h1>Cross Scale Profile Prototype V0</h1>

<div class='note'>
Sandbox compression test only. This page asks whether lower-level structural surfaces can survive upward into one cross-scale profile row. Stable, middle, and residual remain separate grammars. No ranking, anomaly, severity, lifecycle, cause, priority, or recommendation is inferred.
</div>

$($RowsHtml -join "`r`n")

<div class='boundary'>
Boundary: This prototype does not replace the profile sheet. It tests whether bottom-up structural detail can compress upward without collapsing stable, middle, and residual into one metric.
<br><br>
One-line hold: The top surface should become a compressed trace of lower surfaces, not a summary imposed from above.
</div>

</div>
</body>
</html>
"@

$OutPath = Join-Path $OutDir "CROSS_SCALE_PROFILE_PROTOTYPE_V0.html"
Write-AtomicText -Path $OutPath -Text $Html

Write-Host ""
Write-Host "=== CROSS SCALE PROFILE PROTOTYPE COMPLETE ==="
Write-Host $OutPath
