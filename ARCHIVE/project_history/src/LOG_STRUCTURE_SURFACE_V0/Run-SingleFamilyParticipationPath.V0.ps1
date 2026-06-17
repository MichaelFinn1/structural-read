param(
  [Parameter(Mandatory=$true)]
  [string]$FilePath,

  [Parameter(Mandatory=$true)]
  [string]$RoughFamily,

  [int]$WindowSize = 500
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

function Get-RoughFamily {
  param([string]$Template)

  $Parts = @($Template -split ' ' | Where-Object { $_ -ne "" })

  if ($Parts.Count -le 4) {
    return ($Parts -join ' ')
  }

  return (($Parts | Select-Object -First 4) -join ' ')
}

function Get-Regime {
  param([int]$Count)

  if ($Count -ge 5) { return "stable" }
  if ($Count -ge 2) { return "middle" }
  return "residual"
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$File = Get-Item $FilePath
$TerrainRoot = $File.Directory.FullName

$OutDir = Join-Path $TerrainRoot "_surface_work\single_family_participation_path_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)

$Forms = @()
$FamilySurface = @{}

foreach ($Line in $RawLines) {

  if ([string]::IsNullOrWhiteSpace($Line)) {
    continue
  }

  $Normalized = Normalize-Template $Line
  $Forms += $Normalized

  $Family = Get-RoughFamily $Normalized

  if (-not $FamilySurface.ContainsKey($Family)) {
    $FamilySurface[$Family] = 0
  }

  $FamilySurface[$Family] += 1
}

$FamilyDebugPath = Join-Path $OutDir "rough_family_surface_debug.txt"

(
  $FamilySurface.GetEnumerator() |
    Sort-Object Value -Descending |
    Select-Object -First 80 |
    ForEach-Object {
      "{0}`t{1}" -f $_.Key, $_.Value
    }
) | Set-Content $FamilyDebugPath -Encoding UTF8

$Counts = @{}

foreach ($F in $Forms) {
  if (-not $Counts.ContainsKey($F)) { $Counts[$F] = 0 }
  $Counts[$F] += 1
}

$Regimes = @{}

foreach ($K in $Counts.Keys) {
  $Regimes[$K] = Get-Regime $Counts[$K]
}

$Rows = @()
$WindowIndex = 0

for ($Start = 0; $Start -lt $Forms.Count; $Start += $WindowSize) {

  $WindowIndex += 1

  $End = [Math]::Min($Start + $WindowSize - 1, $Forms.Count - 1)

  $FamilyHits = 0
  $StableBracketed = 0
  $StableEdge = 0
  $MiddleAttached = 0
  $ResidualClustered = 0
  $Mixed = 0
  $ExactTemplates = @{}

  for ($i = $Start; $i -le $End; $i++) {

    $Current = $Forms[$i]
    $CurrentFamily = Get-RoughFamily $Current

    if ($CurrentFamily -ne $RoughFamily) {
      continue
    }

    $FamilyHits += 1
    $ExactTemplates[$Current] = $true

    $PrevRegime = "boundary"
    $NextRegime = "boundary"

    if ($i -gt 0) {
      $PrevRegime = $Regimes[$Forms[$i - 1]]
    }

    if ($i -lt ($Forms.Count - 1)) {
      $NextRegime = $Regimes[$Forms[$i + 1]]
    }

    if ($PrevRegime -eq "stable" -and $NextRegime -eq "stable") {
      $StableBracketed += 1
    }
    elseif ($PrevRegime -eq "stable" -or $NextRegime -eq "stable") {
      $StableEdge += 1
    }
    elseif ($PrevRegime -eq "middle" -or $NextRegime -eq "middle") {
      $MiddleAttached += 1
    }
    elseif ($PrevRegime -eq "residual" -and $NextRegime -eq "residual") {
      $ResidualClustered += 1
    }
    else {
      $Mixed += 1
    }
  }

  $DominantPosture = "absent"

  if ($FamilyHits -gt 0) {
    $PostureCounts = @(
      [pscustomobject]@{ posture="stable_bracketed"; count=$StableBracketed },
      [pscustomobject]@{ posture="stable_edge"; count=$StableEdge },
      [pscustomobject]@{ posture="middle_attached"; count=$MiddleAttached },
      [pscustomobject]@{ posture="residual_clustered"; count=$ResidualClustered },
      [pscustomobject]@{ posture="mixed"; count=$Mixed }
    )

    $DominantPosture = (
      $PostureCounts |
        Sort-Object count -Descending |
        Select-Object -First 1
    ).posture
  }

  $Rows += [pscustomobject]@{
    window = "window_$("{0:D3}" -f $WindowIndex)"
    present = if ($FamilyHits -gt 0) { "yes" } else { "no" }
    family_occurrences = $FamilyHits
    exact_template_count = $ExactTemplates.Count
    dominant_posture = $DominantPosture
    stable_bracketed = $StableBracketed
    stable_edge = $StableEdge
    middle_attached = $MiddleAttached
    residual_clustered = $ResidualClustered
    mixed = $Mixed
  }
}

$CsvPath = Join-Path $OutDir "single_family_participation_path.csv"
$Rows | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$HtmlRows = foreach ($R in $Rows) {
@"
<tr class='$($R.dominant_posture)'>
  <td>$($R.window)</td>
  <td>$($R.present)</td>
  <td>$($R.family_occurrences)</td>
  <td>$($R.exact_template_count)</td>
  <td>$($R.dominant_posture)</td>
  <td>$($R.stable_bracketed)</td>
  <td>$($R.stable_edge)</td>
  <td>$($R.middle_attached)</td>
  <td>$($R.residual_clustered)</td>
  <td>$($R.mixed)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Single-Family Participation Path V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:28px; }
.card { max-width:1250px; margin:auto; background:#111820; border:1px solid #2c3945; border-radius:14px; padding:24px; }
.note { color:#aaa; line-height:1.6; margin-bottom:22px; }
table { width:100%; border-collapse:collapse; margin-top:18px; font-size:13px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; }
td { border-bottom:1px solid #27313a; padding:8px; }
.stable_bracketed { background:rgba(90,169,230,.12); }
.stable_edge { background:rgba(90,169,230,.07); }
.middle_attached { background:rgba(155,197,61,.10); }
.residual_clustered { background:rgba(229,89,52,.10); }
.mixed { background:rgba(180,180,180,.06); }
.absent { color:#777; }
.boundary { color:#999; margin-top:24px; border-top:1px solid #2c3945; padding-top:18px; line-height:1.6; }
code { color:#cfe9ff; }
</style>
</head>
<body>
<div class='card'>

<h1>Single-Family Participation Path V0</h1>

<div class='note'>
Observer-only window path for one rough family.
This does not infer entity identity, causality, lifecycle, prediction, importance, or anomaly.
<br><br>
Requested rough family:
<code>$RoughFamily</code>
<br><br>
Debug output:
<code>$FamilyDebugPath</code>
</div>

<table>
<tr>
  <th>window</th>
  <th>present</th>
  <th>occurrences</th>
  <th>exact templates</th>
  <th>dominant posture</th>
  <th>stable bracketed</th>
  <th>stable edge</th>
  <th>middle attached</th>
  <th>residual clustered</th>
  <th>mixed</th>
</tr>
$($HtmlRows -join "`r`n")
</table>

<div class='boundary'>
Boundary: This is a path of emitted participation posture for one rough family.
It is not a claim that one entity persists or evolves.
<br><br>
One-line hold: Follow one participation shape across strata without turning continuity into identity.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "SINGLE_FAMILY_PARTICIPATION_PATH_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== SINGLE-FAMILY PARTICIPATION PATH COMPLETE ==="
Write-Host $HtmlPath
Write-Host ""
Write-Host "Debug rough-family surface:"
Write-Host $FamilyDebugPath
