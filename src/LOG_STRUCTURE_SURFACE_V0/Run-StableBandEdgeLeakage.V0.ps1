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

  $Parts = @($Template -split ' ' | Where-Object { $_ -ne "" })

  if ($Parts.Count -le 4) {
    return ($Parts -join ' ')
  }

  return (($Parts | Select-Object -First 4) -join ' ')
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\stable_band_edge_leakage_v0"
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

$SurfaceRows = @()

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

    if ($CurrentRegime -eq "stable") {
      continue
    }

    $PrevRegime = "boundary"
    $NextRegime = "boundary"

    if ($i -gt 0) {
      $PrevRegime = $Regimes[$Forms[$i - 1]]
    }

    if ($i -lt ($Forms.Count - 1)) {
      $NextRegime = $Regimes[$Forms[$i + 1]]
    }

    $StableTouches = 0

    if ($PrevRegime -eq "stable") {
      $StableTouches += 1
    }

    if ($NextRegime -eq "stable") {
      $StableTouches += 1
    }

    if ($StableTouches -eq 0) {
      continue
    }

    $EdgeType = "one_sided_stable_edge"

    if ($StableTouches -eq 2) {
      $EdgeType = "stable_bracketed"
    }

    $SurfaceRows += [pscustomobject]@{
      file = $File.Name
      current_regime = $CurrentRegime
      edge_type = $EdgeType
      previous_regime = $PrevRegime
      next_regime = $NextRegime
      rough_family = Get-RoughFamily $Current
      exact_template = $Current
    }
  }
}

$SurfaceCsv = Join-Path $OutDir "stable_band_edge_leakage_surface.csv"
$SurfaceRows | Export-Csv $SurfaceCsv -NoTypeInformation -Encoding UTF8

$SummaryRows = @(
  $SurfaceRows |
    Group-Object file,current_regime,edge_type,rough_family |
    ForEach-Object {
      $Parts = $_.Name -split ', ', 4

      [pscustomobject]@{
        file = $Parts[0]
        current_regime = $Parts[1]
        edge_type = $Parts[2]
        rough_family = $Parts[3]
        occurrences = $_.Count
        exact_template_count = @($_.Group | Select-Object -ExpandProperty exact_template -Unique).Count
      }
    } |
    Sort-Object file,current_regime,edge_type,occurrences -Descending
)

$SummaryCsv = Join-Path $OutDir "stable_band_edge_leakage_summary.csv"
$SummaryRows | Export-Csv $SummaryCsv -NoTypeInformation -Encoding UTF8

$CompactRows = @(
  $SurfaceRows |
    Group-Object file,current_regime,edge_type |
    ForEach-Object {
      $Parts = $_.Name -split ', ', 3
      $Group = @($_.Group)

      [pscustomobject]@{
        file = $Parts[0]
        current_regime = $Parts[1]
        edge_type = $Parts[2]
        occurrences = $Group.Count
        rough_family_count = @($Group | Select-Object -ExpandProperty rough_family -Unique).Count
        exact_template_count = @($Group | Select-Object -ExpandProperty exact_template -Unique).Count
      }
    } |
    Sort-Object file,current_regime,edge_type
)

$CompactCsv = Join-Path $OutDir "stable_band_edge_leakage_compact.csv"
$CompactRows | Export-Csv $CompactCsv -NoTypeInformation -Encoding UTF8

$CompactHtml = foreach ($R in $CompactRows) {
@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.current_regime)</td>
  <td>$($R.edge_type)</td>
  <td>$($R.occurrences)</td>
  <td>$($R.rough_family_count)</td>
  <td>$($R.exact_template_count)</td>
</tr>
"@
}

$TopHtml = foreach ($R in ($SummaryRows | Select-Object -First 100)) {
@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.current_regime)</td>
  <td>$($R.edge_type)</td>
  <td><code>$($R.rough_family)</code></td>
  <td>$($R.occurrences)</td>
  <td>$($R.exact_template_count)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Stable-Band Edge Leakage V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:28px; }
.card { max-width:1250px; margin:auto; background:#111820; border:1px solid #2c3945; border-radius:14px; padding:24px; }
h1 { margin-top:0; }
.note { color:#aaa; line-height:1.6; margin-bottom:22px; }
table { width:100%; border-collapse:collapse; margin:18px 0; font-size:13px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; }
td { border-bottom:1px solid #27313a; padding:8px; vertical-align:top; }
code { color:#cfe9ff; }
.boundary { color:#999; margin-top:24px; border-top:1px solid #2c3945; padding-top:18px; line-height:1.6; }
</style>
</head>
<body>
<div class='card'>

<h1>Stable-Band Edge Leakage V0</h1>

<div class='note'>
Observer-only local edge surface. This asks which non-stable forms occur directly beside stable forms.
It does not infer promotion, decay, anomaly, cause, importance, or lifecycle direction.
</div>

<h2>Compact stable-edge summary</h2>

<table>
<tr>
  <th>file</th>
  <th>current regime</th>
  <th>edge type</th>
  <th>occurrences</th>
  <th>rough families</th>
  <th>exact templates</th>
</tr>
$($CompactHtml -join "`r`n")
</table>

<h2>Top stable-edge rough families</h2>

<table>
<tr>
  <th>file</th>
  <th>regime</th>
  <th>edge type</th>
  <th>rough family</th>
  <th>occurrences</th>
  <th>exact templates</th>
</tr>
$($TopHtml -join "`r`n")
</table>

<div class='boundary'>
Boundary: Stable-band edge leakage means non-stable forms occur adjacent to stable forms.
It does not mean they belong to stable structure or are moving toward stability.
<br><br>
One-line hold: Observe edge variation near stable basins without turning adjacency into promotion.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "STABLE_BAND_EDGE_LEAKAGE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== STABLE-BAND EDGE LEAKAGE COMPLETE ==="
Write-Host $HtmlPath
