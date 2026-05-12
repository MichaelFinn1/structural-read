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

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\visual_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$FileProfiles = @()

foreach ($File in $LogFiles) {
  $Counts = @{}
  $Lines = Get-Content $File.FullName -ErrorAction SilentlyContinue

  foreach ($Line in $Lines) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }

    $Template = Normalize-Template $Line

    if (-not $Counts.ContainsKey($Template)) {
      $Counts[$Template] = 0
    }

    $Counts[$Template] += 1
  }

  $Templates = @(
    $Counts.GetEnumerator() |
      ForEach-Object {
        $Class =
          if ($_.Value -ge 5) { "stable" }
          elseif ($_.Value -ge 2) { "middle" }
          else { "residual" }

        [pscustomobject]@{
          template = $_.Key
          count = [int]$_.Value
          class = $Class
        }
      } |
      Sort-Object count -Descending
  )

  $Stable = @($Templates | Where-Object { $_.class -eq "stable" })
  $Middle = @($Templates | Where-Object { $_.class -eq "middle" })
  $Residual = @($Templates | Where-Object { $_.class -eq "residual" })

  $StableLines = ($Stable | Measure-Object -Property count -Sum).Sum
  $MiddleLines = ($Middle | Measure-Object -Property count -Sum).Sum
  $ResidualLines = ($Residual | Measure-Object -Property count -Sum).Sum

  if (-not $StableLines) { $StableLines = 0 }
  if (-not $MiddleLines) { $MiddleLines = 0 }
  if (-not $ResidualLines) { $ResidualLines = 0 }

  $TotalLines = $StableLines + $MiddleLines + $ResidualLines
  if ($TotalLines -eq 0) { $TotalLines = 1 }

  $FileProfiles += [pscustomobject]@{
    file = $File.Name
    total_lines = $TotalLines
    stable_lines = $StableLines
    middle_lines = $MiddleLines
    residual_lines = $ResidualLines
    stable = $Stable
    middle = $Middle
    residual = $Residual
  }
}

$GlobalStableMax = 1
foreach ($P in $FileProfiles) {
  $M = ($P.stable | Measure-Object -Property count -Maximum).Maximum
  if ($M -and $M -gt $GlobalStableMax) {
    $GlobalStableMax = $M
  }
}

$RowsHtml = foreach ($P in $FileProfiles) {
  $StablePct = [math]::Round(($P.stable_lines / $P.total_lines) * 100, 2)
  $MiddlePct = [math]::Round(($P.middle_lines / $P.total_lines) * 100, 2)
  $ResidualPct = [math]::Round(($P.residual_lines / $P.total_lines) * 100, 2)

  $StableTicks = foreach ($S in ($P.stable | Select-Object -First 18)) {
    $Relief = [math]::Max(0.12, ($S.count / $GlobalStableMax))
    $Height = [math]::Round(22 + ($Relief * 34))
    $Opacity = [math]::Round(0.25 + ($Relief * 0.7), 3)
    "<span class='stable-tick' style='height:${Height}px; opacity:${Opacity}'></span>"
  }

  $Middle2 = @($P.middle | Where-Object { $_.count -eq 2 })
  $Middle3to4 = @($P.middle | Where-Object { $_.count -ge 3 -and $_.count -le 4 })

  $MiddleTotal = $Middle2.Count + $Middle3to4.Count
  if ($MiddleTotal -eq 0) { $MiddleTotal = 1 }

  $M2Width = [math]::Round(($Middle2.Count / $MiddleTotal) * 100, 2)
  $M34Width = [math]::Round(($Middle3to4.Count / $MiddleTotal) * 100, 2)

  $ResidualPackets = foreach ($R in 1..([math]::Min(18, $P.residual.Count))) {
    "<span class='res-dot'></span>"
  }

@"
<div class='file-row'>
  <div class='file-name'>$($P.file)</div>

  <div class='terrain-strip'>

    <div class='seg stable-seg' style='width:$StablePct%'>
      <div class='stable-relief'>
        $($StableTicks -join "`r`n")
      </div>
    </div>

    <div class='seg middle-seg' style='width:$MiddlePct%'>
      <div class='middle-ecology'>
        <div class='middle-two' style='width:$M2Width%'></div>
        <div class='middle-threefour' style='width:$M34Width%'></div>
      </div>
    </div>

    <div class='seg residual-seg' style='width:$ResidualPct%'>
      <div class='res-packets'>
        $($ResidualPackets -join "`r`n")
      </div>
    </div>

  </div>

  <div class='meta'>
    stable=$StablePct% / middle=$MiddlePct% / residual=$ResidualPct%
  </div>
</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Structural Terrain Strip Prototype V0</title>
<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:32px;
}

.card {
  max-width:1180px;
  margin:auto;
  background:#1b1b1b;
  border-radius:18px;
  padding:28px;
}

h1 { margin-top:0; }

.note {
  color:#aaa;
  line-height:1.6;
  margin-bottom:26px;
}

.file-row {
  margin:26px 0 34px 0;
}

.file-name {
  font-size:18px;
  margin-bottom:8px;
}

.terrain-strip {
  width:100%;
  height:74px;
  display:flex;
  overflow:hidden;
  border-radius:14px;
  background:#222;
  border:1px solid #333;
}

.seg {
  height:100%;
  position:relative;
  overflow:hidden;
}

.stable-seg {
  background:linear-gradient(to bottom, #10243f, #071222);
}

.middle-seg {
  background:linear-gradient(to bottom, #263816, #15220d);
}

.residual-seg {
  background:linear-gradient(to bottom, #3a1710, #1e0c08);
}

.stable-relief {
  height:100%;
  display:flex;
  align-items:flex-end;
  gap:3px;
  padding:8px;
}

.stable-tick {
  width:8px;
  background:linear-gradient(to top, #164a78, #54e8ff);
  border-radius:6px 6px 0 0;
  box-shadow:0 0 8px rgba(90,220,255,.35);
}

.middle-ecology {
  height:100%;
  display:flex;
}

.middle-two {
  height:100%;
  background:repeating-linear-gradient(
    90deg,
    rgba(155,197,61,.42) 0px,
    rgba(155,197,61,.42) 5px,
    rgba(20,35,12,.3) 5px,
    rgba(20,35,12,.3) 11px
  );
}

.middle-threefour {
  height:100%;
  background:repeating-linear-gradient(
    90deg,
    rgba(190,230,95,.78) 0px,
    rgba(190,230,95,.78) 9px,
    rgba(35,55,18,.35) 9px,
    rgba(35,55,18,.35) 13px
  );
}

.res-packets {
  display:flex;
  flex-wrap:wrap;
  gap:5px;
  padding:9px;
  align-content:flex-start;
}

.res-dot {
  width:7px;
  height:7px;
  border-radius:50%;
  background:#e55934;
  opacity:.72;
}

.meta {
  color:#aaa;
  font-size:12px;
  margin-top:8px;
}

.boundary {
  margin-top:34px;
  border-top:1px solid #333;
  padding-top:18px;
  color:#999;
  font-size:12px;
  line-height:1.7;
}
</style>
</head>
<body>
<div class='card'>

<h1>Structural Terrain Strip Prototype V0</h1>

<div class='note'>
Sandbox prototype only. One row per file. Width shows stable / middle / residual share.
Internal texture shows recurrence posture: stable relief, middle bucket ecology, residual packet field.
This page does not infer anomaly, severity, importance, cause, or recommended action.
</div>

$($RowsHtml -join "`r`n")

<div class='boundary'>
Boundary: This prototype tests whether recurrence posture survives zoom-out. It is not part of the product workflow yet.
<br><br>
One-line hold: Preserve recurrence shape as scale changes.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "STRUCTURAL_TERRAIN_STRIP_PROTOTYPE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== STRUCTURAL TERRAIN STRIP PROTOTYPE COMPLETE ==="
Write-Host $HtmlPath
