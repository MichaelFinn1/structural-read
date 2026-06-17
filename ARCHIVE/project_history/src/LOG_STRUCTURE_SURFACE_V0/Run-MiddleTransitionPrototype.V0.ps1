param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot,

  [int]$WindowCount = 10
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

function Get-Band {
  param([int]$Count)

  if ($Count -ge 5) { return "stable" }
  if ($Count -ge 2) { return "middle" }
  if ($Count -eq 1) { return "residual" }
  return "absent"
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\middle_transition_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

$AllRows = @()
$Cards = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $Lines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  $Total = $Lines.Count

  if ($Total -eq 0) { continue }

  $WindowSize = [math]::Ceiling($Total / $WindowCount)

  $WindowMaps = @()

  for ($w = 0; $w -lt $WindowCount; $w++) {
    $Start = $w * $WindowSize
    $End = [math]::Min($Start + $WindowSize - 1, $Total - 1)

    $Counts = @{}

    if ($Start -le $End) {
      foreach ($Line in $Lines[$Start..$End]) {
        $Template = Normalize-Template $Line

        if (-not $Counts.ContainsKey($Template)) {
          $Counts[$Template] = 0
        }

        $Counts[$Template] += 1
      }
    }

    $WindowMaps += $Counts
  }

  $AllTemplates = @{}
  foreach ($Map in $WindowMaps) {
    foreach ($Key in $Map.Keys) {
      $AllTemplates[$Key] = $true
    }
  }

  $Transitions = @{}

  foreach ($Template in $AllTemplates.Keys) {
    $Bands = @()

    for ($w = 0; $w -lt $WindowCount; $w++) {
      $Count = 0
      if ($WindowMaps[$w].ContainsKey($Template)) {
        $Count = [int]$WindowMaps[$w][$Template]
      }

      $Bands += Get-Band -Count $Count
    }

    for ($w = 0; $w -lt ($WindowCount - 1); $w++) {
      $From = $Bands[$w]
      $To = $Bands[$w + 1]
      $Key = "$From->$To"

      if (-not $Transitions.ContainsKey($Key)) {
        $Transitions[$Key] = 0
      }

      $Transitions[$Key] += 1
    }
  }

  $Interesting = @(
    "residual->middle",
    "middle->stable",
    "stable->middle",
    "middle->residual",
    "residual->stable",
    "stable->residual",
    "middle->middle",
    "stable->stable",
    "residual->residual",
    "absent->residual",
    "residual->absent"
  )

  foreach ($K in $Interesting) {
    if (-not $Transitions.ContainsKey($K)) {
      $Transitions[$K] = 0
    }
  }

  $Formation = $Transitions["residual->middle"] + $Transitions["middle->stable"] + $Transitions["residual->stable"]
  $Dissolution = $Transitions["stable->middle"] + $Transitions["middle->residual"] + $Transitions["stable->residual"]
  $Persistence = $Transitions["middle->middle"] + $Transitions["stable->stable"] + $Transitions["residual->residual"]

  $AllRows += [pscustomobject]@{
    file = $File.Name
    windows = $WindowCount
    lines = $Total
    formation_candidates = $Formation
    dissolution_candidates = $Dissolution
    persistence_candidates = $Persistence
    residual_to_middle = $Transitions["residual->middle"]
    middle_to_stable = $Transitions["middle->stable"]
    stable_to_middle = $Transitions["stable->middle"]
    middle_to_residual = $Transitions["middle->residual"]
    absent_to_residual = $Transitions["absent->residual"]
    residual_to_absent = $Transitions["residual->absent"]
  }

  $MaxMovement = (@($Formation,$Dissolution,$Persistence) | Measure-Object -Maximum).Maximum
  if (-not $MaxMovement -or $MaxMovement -lt 1) { $MaxMovement = 1 }

  $FormationW = [math]::Round(($Formation / $MaxMovement) * 100, 1)
  $DissolutionW = [math]::Round(($Dissolution / $MaxMovement) * 100, 1)
  $PersistenceW = [math]::Round(($Persistence / $MaxMovement) * 100, 1)

  $Cards += @"
<div class='file-card'>
  <h2>$($File.Name)</h2>

  <div class='metrics'>
    <div><span>lines</span><strong>$Total</strong></div>
    <div><span>windows</span><strong>$WindowCount</strong></div>
    <div><span>formation candidates</span><strong>$Formation</strong></div>
    <div><span>dissolution candidates</span><strong>$Dissolution</strong></div>
    <div><span>persistence candidates</span><strong>$Persistence</strong></div>
  </div>

  <div class='label'>candidate movement balance</div>
  <div class='movement-row'>
    <div class='move-label'>formation</div>
    <div class='move-track'><div class='move-fill formation' style='width:$FormationW%'></div></div>
    <div class='move-count'>$Formation</div>
  </div>
  <div class='movement-row'>
    <div class='move-label'>dissolution</div>
    <div class='move-track'><div class='move-fill dissolution' style='width:$DissolutionW%'></div></div>
    <div class='move-count'>$Dissolution</div>
  </div>
  <div class='movement-row'>
    <div class='move-label'>persistence</div>
    <div class='move-track'><div class='move-fill persistence' style='width:$PersistenceW%'></div></div>
    <div class='move-count'>$Persistence</div>
  </div>

  <div class='label'>selected transitions</div>
  <table>
    <tr><th>transition</th><th>count</th></tr>
    <tr><td>residual → middle</td><td>$($Transitions["residual->middle"])</td></tr>
    <tr><td>middle → stable</td><td>$($Transitions["middle->stable"])</td></tr>
    <tr><td>stable → middle</td><td>$($Transitions["stable->middle"])</td></tr>
    <tr><td>middle → residual</td><td>$($Transitions["middle->residual"])</td></tr>
    <tr><td>absent → residual</td><td>$($Transitions["absent->residual"])</td></tr>
    <tr><td>residual → absent</td><td>$($Transitions["residual->absent"])</td></tr>
  </table>
</div>
"@
}

$CsvPath = Join-Path $OutDir "middle_transition_summary.csv"
$AllRows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Middle Transition Prototype V0</title>
<style>
body { background:#111; color:#eee; font-family:Segoe UI, Arial; padding:32px; }
.card { max-width:1220px; margin:auto; background:#1b1b1b; border-radius:18px; padding:28px; }
h1 { margin-top:0; }
.note { color:#aaa; line-height:1.6; margin-bottom:24px; }
.file-card { background:#202020; border:1px solid #333; border-radius:16px; padding:22px; margin:24px 0; }
.metrics { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:18px; }
.metrics div { background:#171717; border-radius:10px; padding:12px; }
.metrics span { display:block; color:#999; font-size:11px; }
.metrics strong { font-size:22px; }
.label { color:#aaa; font-size:12px; margin:18px 0 8px 0; }
.movement-row { display:grid; grid-template-columns:110px 1fr 90px; gap:10px; align-items:center; margin-bottom:9px; }
.move-label { color:#bbb; font-size:12px; }
.move-track { height:18px; background:#171717; border-radius:10px; overflow:hidden; border:1px solid #333; }
.move-fill { height:100%; }
.formation { background:#b7da64; }
.dissolution { background:#e6a04f; }
.persistence { background:#5bc0eb; }
.move-count { color:#aaa; font-size:12px; }
table { width:100%; border-collapse:collapse; margin-top:10px; font-size:12px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; }
td { border-bottom:1px solid #333; padding:8px; }
.boundary { margin-top:34px; border-top:1px solid #333; padding-top:18px; color:#999; font-size:12px; line-height:1.7; }
</style>
</head>
<body>
<div class='card'>

<h1>Middle Transition Prototype V0</h1>

<div class='note'>
Sandbox prototype only. This page slices each file into sequential windows and tracks candidate movement between recurrence bands.
Residual = count 1 in a window. Middle = count 2–4. Stable = count 5 or more. Absent = not present in that window.
These are candidate movement counts, not lifecycle truth.
</div>

$($Cards -join "`r`n")

<div class='boundary'>
Boundary: This prototype does not infer causality, lifecycle, anomaly, severity, importance, semantic family, or recommended action.
<br><br>
One-line hold: Middle directionality is explored only as windowed recurrence movement.
<br><br>
CSV: $CsvPath
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "MIDDLE_TRANSITION_PROTOTYPE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== MIDDLE TRANSITION PROTOTYPE COMPLETE ==="
Write-Host $HtmlPath
Write-Host $CsvPath

