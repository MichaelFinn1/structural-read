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

$OutDir = Join-Path $TerrainRoot "_surface_work\stable_topology_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$Profiles = @()

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

  $Stable = @(
    $Counts.GetEnumerator() |
      Where-Object { $_.Value -ge 5 } |
      ForEach-Object {
        [pscustomobject]@{
          template = $_.Key
          count = [int]$_.Value
        }
      } |
      Sort-Object count -Descending
  )

  $StableLines = ($Stable | Measure-Object -Property count -Sum).Sum
  if (-not $StableLines) { $StableLines = 0 }

  $MaxCount = ($Stable | Measure-Object -Property count -Maximum).Maximum
  if (-not $MaxCount) { $MaxCount = 1 }

  $Top1Lines = ($Stable | Select-Object -First 1 | Measure-Object -Property count -Sum).Sum
  $Top5Lines = ($Stable | Select-Object -First 5 | Measure-Object -Property count -Sum).Sum
  $Top10Lines = ($Stable | Select-Object -First 10 | Measure-Object -Property count -Sum).Sum

  if (-not $Top1Lines) { $Top1Lines = 0 }
  if (-not $Top5Lines) { $Top5Lines = 0 }
  if (-not $Top10Lines) { $Top10Lines = 0 }

  $Top1StableShare = if ($StableLines -gt 0) {
    [math]::Round(($Top1Lines / $StableLines) * 100, 1)
  } else {
    0
  }

  $Top5StableShare = if ($StableLines -gt 0) {
    [math]::Round(($Top5Lines / $StableLines) * 100, 1)
  } else {
    0
  }

  $Top10StableShare = if ($StableLines -gt 0) {
    [math]::Round(($Top10Lines / $StableLines) * 100, 1)
  } else {
    0
  }

  $StableCountValues = @($Stable | ForEach-Object { $_.count } | Sort-Object)
  $MedianStableCount = 0

  if ($StableCountValues.Count -gt 0) {
    $Mid = [math]::Floor($StableCountValues.Count / 2)

    if (($StableCountValues.Count % 2) -eq 0) {
      $MedianStableCount = [math]::Round((($StableCountValues[$Mid - 1] + $StableCountValues[$Mid]) / 2), 1)
    } else {
      $MedianStableCount = $StableCountValues[$Mid]
    }
  }

  $Rank50 = 0
  $Rank80 = 0
  $RankByPct = @{}
  $RunningStable = 0
  $RankIndex = 0

  foreach ($StableRow in $Stable) {
    $RankIndex += 1
    $RunningStable += $StableRow.count

    foreach ($Pct in @(10,20,30,40,50,60,70,80,90)) {
      if (-not $RankByPct.ContainsKey($Pct) -and $StableLines -gt 0 -and (($RunningStable / $StableLines) -ge ($Pct / 100))) {
        $RankByPct[$Pct] = $RankIndex
      }
    }

    if ($Rank50 -eq 0 -and $StableLines -gt 0 -and (($RunningStable / $StableLines) -ge 0.5)) {
      $Rank50 = $RankIndex
    }

    if ($Rank80 -eq 0 -and $StableLines -gt 0 -and (($RunningStable / $StableLines) -ge 0.8)) {
      $Rank80 = $RankIndex
    }
  }

  $Profiles += [pscustomobject]@{
    file = $File.Name
    stable_count = $Stable.Count
    stable_lines = $StableLines
    max_count = $MaxCount
    top1_stable_share = $Top1StableShare
    top5_stable_share = $Top5StableShare
    top10_stable_share = $Top10StableShare
    rank50 = $Rank50
    rank80 = $Rank80
    rank_by_pct = $RankByPct
    median_stable_count = $MedianStableCount
    stable = $Stable
  }
}

$GlobalMax = ($Profiles | Measure-Object -Property max_count -Maximum).Maximum
if (-not $GlobalMax -or $GlobalMax -eq 0) { $GlobalMax = 1 }

$GlobalStableLinesMax = ($Profiles | Measure-Object -Property stable_lines -Maximum).Maximum
if (-not $GlobalStableLinesMax -or $GlobalStableLinesMax -eq 0) { $GlobalStableLinesMax = 1 }

$ComparisonRows = foreach ($P in $Profiles) {
@"
<tr>
  <td>$($P.file)</td>
  <td>$($P.stable_count)</td>
  <td>$($P.stable_lines)</td>
  <td>$($P.max_count)</td>
  <td>$($P.median_stable_count)</td>
  <td>$($P.top1_stable_share)%</td>
  <td>$($P.top5_stable_share)%</td>
  <td>$($P.top10_stable_share)%</td>
  <td>$($P.rank50)</td>
  <td>$($P.rank80)</td>
</tr>
"@
}

$RowsHtml = foreach ($P in $Profiles) {
  $DecayTicks = foreach ($S in ($P.stable | Select-Object -First 80)) {
    $Rel = [math]::Max(0.04, ($S.count / $GlobalMax))
    $Height = [math]::Round(8 + ($Rel * 82))
    $Opacity = [math]::Round(0.22 + ($Rel * 0.78), 3)

    "<span class='decay-tick' style='height:${Height}px; opacity:${Opacity}'></span>"
  }

  $ReliefCells = foreach ($S in ($P.stable | Select-Object -First 160)) {
    $Rel = [math]::Max(0.04, ($S.count / $GlobalMax))
    $Shade = [math]::Round(40 + ($Rel * 210))
    $Opacity = [math]::Round(0.22 + ($Rel * 0.7), 3)

    "<span class='relief-cell' style='background:rgb(20,$Shade,255); opacity:${Opacity}'></span>"
  }

  $PctMarkers = foreach ($Pct in @(50,80,100)) {
    $Rank = 0
    if ($Pct -eq 100) {
      $Rank = $P.stable_count
    } elseif ($P.rank_by_pct.ContainsKey($Pct)) {
      $Rank = $P.rank_by_pct[$Pct]
    }

    $Left = 0
    if ($P.stable_count -gt 0) {
      $Left = [math]::Min(100, [math]::Round(($Rank / $P.stable_count) * 100, 2))
    }

@"
    <div class='pct-marker' style='left:$Left%'>
      <div class='pct-line'></div>
      <div class='pct-label'>$Pct%</div>
    </div>
"@
  }

  $CurvePoints = @()
  $CurveRunning = 0
  $CurveRank = 0

  foreach ($StableRow in $P.stable) {
    $CurveRank += 1
    $CurveRunning += $StableRow.count

    $X = 0
    if ($P.stable_count -gt 1) {
      $X = [math]::Round((($CurveRank - 1) / ($P.stable_count - 1)) * 100, 2)
    }

    $Y = 0
    if ($P.stable_lines -gt 0) {
      $Y = [math]::Round(($CurveRunning / $P.stable_lines) * 100, 2)
    }

    $CurvePoints += [pscustomobject]@{
      x = $X
      y = $Y
    }
  }

  $CurvePointString = ($CurvePoints | ForEach-Object {
    "$($_.x),$(100 - $_.y)"
  }) -join " "

  $DensityWidth = [math]::Max(6, [math]::Round(($P.stable_lines / $GlobalStableLinesMax) * 100, 2))

  $DensityCells = foreach ($StableRow in $P.stable) {
    $Rel = [math]::Max(0.04, ($StableRow.count / $GlobalMax))
    $Opacity = [math]::Round(0.12 + ($Rel * 0.88), 3)

    "<span class='density-cell' style='opacity:${Opacity}'></span>"
  }

  $TopRows = foreach ($S in ($P.stable | Select-Object -First 16)) {
@"
<tr>
  <td>$($S.count)</td>
  <td><code>$($S.template)</code></td>
</tr>
"@
  }

@"
<div class='file-card'>
  <h2>$($P.file)</h2>

  <div class='metrics'>
    <div><span>stable templates</span><strong>$($P.stable_count)</strong></div>
    <div><span>stable lines</span><strong>$($P.stable_lines)</strong></div>
    <div><span>max recurrence</span><strong>$($P.max_count)</strong></div>
    <div><span>median count</span><strong>$($P.median_stable_count)</strong></div>
    <div><span>top5 stable share</span><strong>$($P.top5_stable_share)%</strong></div>
    <div><span>templates to 80%</span><strong>$($P.rank80)</strong></div>
  </div>

  <div class='label'>cumulative stable mass curve</div>
  <div class='curve-note'>Shows how quickly stable recurrence mass accumulates as templates are added from highest count downward. Fast rise = stable mass carried by few templates. Slow rise = stable mass spread across many templates.</div>
  <div class='curve-field'>
    <div class='grid-line y20'></div>
    <div class='grid-line y40'></div>
    <div class='grid-line y60'></div>
    <div class='grid-line y80'></div>
    <svg class="curve-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polyline points="$CurvePointString" />
    </svg>
    $($PctMarkers -join "`r`n")
  </div>

  <div class='label'>rank density strip</div>
  <div class='curve-note'>Strip length shows stable recurrence mass relative to other files. Brightness shows rank concentration inside this file.</div>
  <div class='density-frame'>
    <div class='density-field' style='width:$DensityWidth%'>
      $($DensityCells -join "`r`n")
    </div>
  </div>

  <details>
    <summary>Open top stable templates</summary>
    <table>
      <tr><th>count</th><th>template</th></tr>
      $($TopRows -join "`r`n")
    </table>
  </details>
</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Stable Topology Prototype V0</title>
<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:32px;
}

.card {
  max-width:1220px;
  margin:auto;
  background:#1b1b1b;
  border-radius:18px;
  padding:28px;
}

h1 { margin-top:0; }
h2 { margin-bottom:12px; }

.note {
  color:#aaa;
  line-height:1.6;
  margin-bottom:26px;
}

.small-note {
  font-size:12px;
  margin-bottom:12px;
}

.comparison-block {
  background:#202020;
  border:1px solid #333;
  border-radius:16px;
  padding:22px;
  margin:24px 0;
}

.file-card {
  background:#202020;
  border:1px solid #333;
  border-radius:16px;
  padding:22px;
  margin:24px 0;
}

.metrics {
  display:grid;
  grid-template-columns:repeat(4, 1fr);
  gap:10px;
  margin-bottom:18px;
}

.metrics div {
  background:#171717;
  border-radius:10px;
  padding:12px;
}

.metrics span {
  display:block;
  color:#999;
  font-size:11px;
}

.metrics strong {
  font-size:22px;
}

.label {
  color:#aaa;
  font-size:12px;
  margin:18px 0 8px 0;
}

.curve-note {
  color:#999;
  font-size:12px;
  margin-bottom:8px;
}

.curve-field {
  height:150px;
  position:relative;
  background:linear-gradient(to bottom, #101a2b, #07101d);
  border-radius:12px;
  padding:8px;
  overflow:hidden;
  border:1px solid #25344a;
}

.curve-svg {
  position:absolute;
  left:0;
  top:0;
  width:100%;
  height:100%;
  overflow:visible;
}

.curve-svg polyline {
  fill:none;
  stroke:#51eaff;
  stroke-width:2.4;
  stroke-linecap:round;
  stroke-linejoin:round;
  vector-effect:non-scaling-stroke;
  filter:drop-shadow(0 0 5px rgba(90,220,255,.55));
}

.grid-line {
  position:absolute;
  left:0;
  right:0;
  height:1px;
  background:rgba(255,255,255,.08);
}

.y20 { top:80%; }
.y40 { top:60%; }
.y60 { top:40%; }
.y80 { top:20%; }

.pct-marker {
  position:absolute;
  top:0;
  bottom:0;
  width:1px;
}



.pct-line {
  height:100%;
  border-left:1px dashed rgba(255,255,255,.16);
}

.pct-label {
  position:absolute;
  top:4px;
  left:4px;
  color:#8fd8f4;
  font-size:10px;
}

.density-frame {
  height:34px;
  background:linear-gradient(to bottom, #101a2b, #07101d);
  border-radius:12px;
  padding:8px;
  overflow:hidden;
  border:1px solid #25344a;
}

.density-field {
  height:100%;
  display:flex;
  border-radius:8px;
  overflow:hidden;
  background:rgba(40,120,210,.16);
}

.density-cell {
  flex:1;
  min-width:1px;
  background:linear-gradient(to bottom, #51eaff, #10345d);
  box-shadow:0 0 5px rgba(90,220,255,.22);
}

.decay-field {
  height:104px;
  display:flex;
  align-items:flex-end;
  gap:3px;
  background:linear-gradient(to bottom, #101a2b, #07101d);
  border-radius:12px;
  padding:8px;
  overflow:hidden;
}

.decay-tick {
  width:8px;
  background:linear-gradient(to top, #10345d, #51eaff);
  border-radius:6px 6px 0 0;
  box-shadow:0 0 7px rgba(90,220,255,.3);
}

.relief-field {
  min-height:80px;
  display:flex;
  flex-wrap:wrap;
  gap:3px;
  background:linear-gradient(to bottom, #101a2b, #07101d);
  border-radius:12px;
  padding:8px;
  overflow:hidden;
}

.relief-cell {
  width:13px;
  height:13px;
  border-radius:4px;
  box-shadow:0 0 5px rgba(90,220,255,.22);
}

details {
  margin-top:16px;
}

summary {
  cursor:pointer;
  color:#8fd8f4;
}

table {
  width:100%;
  border-collapse:collapse;
  margin-top:10px;
  font-size:12px;
}

th {
  color:#aaa;
  text-align:left;
  border-bottom:1px solid #444;
  padding:8px;
}

td {
  border-bottom:1px solid #333;
  padding:8px;
  vertical-align:top;
}

code {
  color:#ddd;
  white-space:normal;
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

<h1>Stable Topology Prototype V0</h1>

<div class='note'>
Sandbox prototype only. This page studies stable recurrence topology before compressing it into the overview terrain strip.
Stable means templates occurring five or more times: recurring enough to have shape. Stable does not mean normal, safe, boring, ignorable, or explained.
This page shows recurrence posture, not importance.
</div>

<div class='comparison-block'>
  <h2>Stable mass comparison</h2>
  <div class='note small-note'>
    Comparison table for recurrence mass only. Lower template counts to 50% / 80% indicate concentrated stable mass; higher counts indicate broader stable mass.
  </div>
  <table>
    <tr>
      <th>file</th>
      <th>stable templates</th>
      <th>stable lines</th>
      <th>max count</th>
      <th>median count</th>
      <th>top1</th>
      <th>top5</th>
      <th>top10</th>
      <th>templates to 50%</th>
      <th>templates to 80%</th>
    </tr>
    $($ComparisonRows -join "`r`n")
  </table>
</div>

$($RowsHtml -join "`r`n")

<div class='boundary'>
Boundary: This prototype does not infer anomaly, severity, importance, cause, incident status, or recommended action.
<br><br>
One-line hold: Stabilize local stable terrain before compressing upward.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "STABLE_TOPOLOGY_PROTOTYPE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== STABLE TOPOLOGY PROTOTYPE COMPLETE ==="
Write-Host $HtmlPath









