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

function Get-RoughFamily {
  param([string]$Template)

  $Parts = @(
    $Template -split ' ' |
      Where-Object { $_ -ne "" }
  )

  if ($Parts.Count -le 4) {
    return ($Parts -join ' ')
  }

  return (($Parts | Select-Object -First 4) -join ' ')
}

function Get-Regime {
  param([int]$Count)

  if ($Count -ge 5) {
    return "stable"
  }

  if ($Count -ge 2) {
    return "middle"
  }

  return "residual"
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"

  $Text | Set-Content $Tmp -Encoding UTF8

  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path `
  $TerrainRoot `
  "_surface_work\contextual_posture_continuity_v0"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object {
      $_.Extension -match '\.(log|txt)$' -and
      $_.FullName -notmatch '\\_surface_work\\'
    }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$WindowSize = 500

$SurfaceRows = @()

foreach ($File in $LogFiles) {

  Write-Host "Reading $($File.Name)..."

  $RawLines = @(
    Get-Content $File.FullName -ErrorAction SilentlyContinue
  )

  $Forms = @()

  foreach ($Line in $RawLines) {

    if ([string]::IsNullOrWhiteSpace($Line)) {
      continue
    }

    $Forms += Normalize-Template $Line
  }

  if ($Forms.Count -eq 0) {
    continue
  }

  $Counts = @{}

  foreach ($F in $Forms) {

    if (-not $Counts.ContainsKey($F)) {
      $Counts[$F] = 0
    }

    $Counts[$F] += 1
  }

  $Regimes = @{}

  foreach ($K in $Counts.Keys) {
    $Regimes[$K] = Get-Regime $Counts[$K]
  }

  $WindowIndex = 0

  for ($Start = 0; $Start -lt $Forms.Count; $Start += $WindowSize) {

    $End = [Math]::Min(
      $Start + $WindowSize - 1,
      $Forms.Count - 1
    )

    $WindowIndex += 1

    for ($i = $Start; $i -le $End; $i++) {

      $Current = $Forms[$i]
      $Family = Get-RoughFamily $Current

      $PrevRegime = "boundary"
      $NextRegime = "boundary"

      if ($i -gt 0) {
        $PrevRegime = $Regimes[$Forms[$i - 1]]
      }

      if ($i -lt ($Forms.Count - 1)) {
        $NextRegime = $Regimes[$Forms[$i + 1]]
      }

      $Posture = "mixed"

      if (
        $PrevRegime -eq "stable" -and
        $NextRegime -eq "stable"
      ) {
        $Posture = "stable_bracketed"
      }
      elseif (
        $PrevRegime -eq "stable" -or
        $NextRegime -eq "stable"
      ) {
        $Posture = "stable_edge"
      }
      elseif (
        $PrevRegime -eq "middle" -or
        $NextRegime -eq "middle"
      ) {
        $Posture = "middle_attached"
      }
      elseif (
        $PrevRegime -eq "residual" -and
        $NextRegime -eq "residual"
      ) {
        $Posture = "residual_clustered"
      }

      $SurfaceRows += [pscustomobject]@{
        file = $File.Name
        window = $WindowIndex
        rough_family = $Family
        posture = $Posture
      }
    }
  }
}

$SummaryRows = @(
  $SurfaceRows |
    Group-Object file,rough_family,posture |
    ForEach-Object {

      $Parts = $_.Name -split ', ', 3

      [pscustomobject]@{
        file = $Parts[0]
        rough_family = $Parts[1]
        posture = $Parts[2]
        occurrences = $_.Count
        windows_present = @(
          $_.Group |
            Select-Object -ExpandProperty window -Unique
        ).Count
      }
    } |
    Sort-Object file,windows_present,occurrences -Descending
)

$SummaryCsv = Join-Path `
  $OutDir `
  "contextual_posture_continuity_summary.csv"

$SummaryRows |
  Export-Csv `
    $SummaryCsv `
    -NoTypeInformation `
    -Encoding UTF8

$CompactRows = @(
  $SurfaceRows |
    Group-Object file,rough_family |
    ForEach-Object {

      $Parts = $_.Name -split ', ', 2

      $Postures = @(
        $_.Group |
          Select-Object -ExpandProperty posture -Unique
      )

      [pscustomobject]@{
        file = $Parts[0]
        rough_family = $Parts[1]
        windows_present = @(
          $_.Group |
            Select-Object -ExpandProperty window -Unique
        ).Count
        dominant_posture = (
          $_.Group |
            Group-Object posture |
            Sort-Object Count -Descending |
            Select-Object -First 1
        ).Name
        posture_variability = $Postures.Count
      }
    } |
    Sort-Object file,windows_present -Descending
)

$CompactCsv = Join-Path `
  $OutDir `
  "contextual_posture_continuity_compact.csv"

$CompactRows |
  Export-Csv `
    $CompactCsv `
    -NoTypeInformation `
    -Encoding UTF8

$CompactHtml = foreach ($R in ($CompactRows | Select-Object -First 100)) {

@"
<tr>
  <td>$($R.file)</td>
  <td><code>$($R.rough_family)</code></td>
  <td>$($R.windows_present)</td>
  <td>$($R.dominant_posture)</td>
  <td>$($R.posture_variability)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Contextual Posture Continuity V0</title>

<style>

body {
  background:#0b0f14;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:28px;
}

.card {
  max-width:1200px;
  margin:auto;
  background:#111820;
  border:1px solid #2c3945;
  border-radius:14px;
  padding:24px;
}

.note {
  color:#aaa;
  line-height:1.6;
  margin-bottom:22px;
}

table {
  width:100%;
  border-collapse:collapse;
  margin-top:18px;
}

th {
  color:#aaa;
  text-align:left;
  border-bottom:1px solid #444;
  padding:8px;
}

td {
  border-bottom:1px solid #27313a;
  padding:8px;
}

code {
  color:#cfe9ff;
}

.boundary {
  color:#999;
  margin-top:24px;
  border-top:1px solid #2c3945;
  padding-top:18px;
  line-height:1.6;
}

</style>
</head>

<body>

<div class='card'>

<h1>Contextual Posture Continuity V0</h1>

<div class='note'>

Observer-only cross-window posture surface.

This asks whether rough families repeatedly inhabit
similar local persistence neighborhoods across windows.

It does NOT infer:
identity,
promotion,
importance,
or lifecycle trajectory.

</div>

<table>

<tr>
  <th>file</th>
  <th>rough family</th>
  <th>windows present</th>
  <th>dominant posture</th>
  <th>posture variability</th>
</tr>

$($CompactHtml -join "`r`n")

</table>

<div class='boundary'>

Boundary:
Contextual posture continuity means a rough family
repeatedly appeared in similar local persistence contexts.

It does NOT mean:
the same entity persisted,
or that the structure is evolving toward stability.

<br><br>

One-line hold:
Observe persistent participation posture
without turning continuity into identity or destiny.

</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path `
  $OutDir `
  "CONTEXTUAL_POSTURE_CONTINUITY_V0.html"

Write-AtomicText `
  -Path $HtmlPath `
  -Text $Html

Write-Host ""
Write-Host "=== CONTEXTUAL POSTURE CONTINUITY COMPLETE ==="
Write-Host $HtmlPath
