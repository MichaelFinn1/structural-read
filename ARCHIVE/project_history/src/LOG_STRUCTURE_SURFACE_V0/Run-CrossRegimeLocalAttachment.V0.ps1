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

$OutDir = Join-Path $TerrainRoot "_surface_work\cross_regime_local_attachment_v0"
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

$Rows = @()
$SummaryRows = @()

foreach ($File in $LogFiles) {

  Write-Host "Reading $($File.Name)..."

  $RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)

  $Forms = @()
  foreach ($Line in $RawLines) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }
    $Forms += Normalize-Template $Line
  }

  $Counts = @{}
  foreach ($F in $Forms) {
    if (-not $Counts.ContainsKey($F)) { $Counts[$F] = 0 }
    $Counts[$F] += 1
  }

  $Regimes = @{}
  foreach ($K in $Counts.Keys) {
    $C = [int]$Counts[$K]

    if ($C -ge 5) {
      $Regimes[$K] = "stable"
    } elseif ($C -ge 2) {
      $Regimes[$K] = "middle"
    } else {
      $Regimes[$K] = "residual"
    }
  }

  for ($i = 0; $i -lt $Forms.Count; $i++) {

    $Current = $Forms[$i]
    $CurrentRegime = $Regimes[$Current]

    $PrevRegime = "boundary"
    $NextRegime = "boundary"

    if ($i -gt 0) {
      $PrevRegime = $Regimes[$Forms[$i - 1]]
    }

    if ($i -lt ($Forms.Count - 1)) {
      $NextRegime = $Regimes[$Forms[$i + 1]]
    }

    $Neighborhood = "$PrevRegime-$CurrentRegime-$NextRegime"

    $Rows += [pscustomobject]@{
      file = $File.Name
      current_regime = $CurrentRegime
      previous_regime = $PrevRegime
      next_regime = $NextRegime
      neighborhood_signature = $Neighborhood
      current_form = $Current
    }
  }
}

$SurfaceCsv = Join-Path $OutDir "cross_regime_local_attachment_surface.csv"
$Rows | Export-Csv $SurfaceCsv -NoTypeInformation -Encoding UTF8

$SummaryRows = @(
  $Rows |
    Group-Object file,current_regime,previous_regime,next_regime,neighborhood_signature |
    ForEach-Object {
      $Parts = $_.Name -split ', '

      [pscustomobject]@{
        file = $Parts[0]
        current_regime = $Parts[1]
        previous_regime = $Parts[2]
        next_regime = $Parts[3]
        neighborhood_signature = $Parts[4]
        occurrences = $_.Count
      }
    } |
    Sort-Object file,current_regime,occurrences -Descending
)

$SummaryCsv = Join-Path $OutDir "cross_regime_local_attachment_summary.csv"
$SummaryRows | Export-Csv $SummaryCsv -NoTypeInformation -Encoding UTF8

$CompactRows = @(
  $Rows |
    Group-Object file,current_regime |
    ForEach-Object {
      $Parts = $_.Name -split ', '
      $FileName = $Parts[0]
      $Regime = $Parts[1]
      $Subset = @($_.Group)

      $Total = $Subset.Count
      if ($Total -eq 0) { $Total = 1 }

      $NearStable = @($Subset | Where-Object {
        $_.previous_regime -eq "stable" -or $_.next_regime -eq "stable"
      }).Count

      $NearMiddle = @($Subset | Where-Object {
        $_.previous_regime -eq "middle" -or $_.next_regime -eq "middle"
      }).Count

      $NearResidual = @($Subset | Where-Object {
        $_.previous_regime -eq "residual" -or $_.next_regime -eq "residual"
      }).Count

      [pscustomobject]@{
        file = $FileName
        current_regime = $Regime
        occurrences = $Subset.Count
        near_stable_pct = [math]::Round(($NearStable / $Total) * 100, 1)
        near_middle_pct = [math]::Round(($NearMiddle / $Total) * 100, 1)
        near_residual_pct = [math]::Round(($NearResidual / $Total) * 100, 1)
      }
    } |
    Sort-Object file,current_regime
)

$CompactCsv = Join-Path $OutDir "cross_regime_local_attachment_compact.csv"
$CompactRows | Export-Csv $CompactCsv -NoTypeInformation -Encoding UTF8

$HtmlRows = foreach ($R in $CompactRows) {
@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.current_regime)</td>
  <td>$($R.occurrences)</td>
  <td>$($R.near_stable_pct)%</td>
  <td>$($R.near_middle_pct)%</td>
  <td>$($R.near_residual_pct)%</td>
</tr>
"@
}

$TopRows = foreach ($R in ($SummaryRows | Select-Object -First 80)) {
@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.neighborhood_signature)</td>
  <td>$($R.occurrences)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Cross-Regime Local Attachment V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:28px; }
.card { max-width:1200px; margin:auto; background:#111820; border:1px solid #2c3945; border-radius:14px; padding:24px; }
h1 { margin-top:0; }
.note { color:#aaa; line-height:1.6; margin-bottom:22px; }
table { width:100%; border-collapse:collapse; margin:18px 0; font-size:13px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; }
td { border-bottom:1px solid #27313a; padding:8px; vertical-align:top; }
.boundary { color:#999; margin-top:24px; border-top:1px solid #2c3945; padding-top:18px; line-height:1.6; }
</style>
</head>
<body>
<div class='card'>

<h1>Cross-Regime Local Attachment V0</h1>

<div class='note'>
Observer-only local adjacency surface. This asks what persistence regimes locally surround stable, middle, and residual forms.
It does not infer membership, cause, lifecycle progression, anomaly, severity, or importance.
</div>

<h2>Compact regime-neighbor summary</h2>

<table>
<tr>
  <th>file</th>
  <th>current regime</th>
  <th>occurrences</th>
  <th>near stable</th>
  <th>near middle</th>
  <th>near residual</th>
</tr>
$($HtmlRows -join "`r`n")
</table>

<h2>Top local regime neighborhoods</h2>

<table>
<tr>
  <th>file</th>
  <th>neighborhood signature</th>
  <th>occurrences</th>
</tr>
$($TopRows -join "`r`n")
</table>

<div class='boundary'>
Boundary: This is static/postural local adjacency only. It does not describe movement across windows.
<br><br>
One-line hold: Observe how persistence regimes locally touch without turning adjacency into belonging or lifecycle.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "CROSS_REGIME_LOCAL_ATTACHMENT_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== CROSS-REGIME LOCAL ATTACHMENT COMPLETE ==="
Write-Host $HtmlPath
