param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot,

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

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\rough_family_continuity_v0"
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
$FamilyRows = @()

foreach ($File in $LogFiles) {

  Write-Host "Reading $($File.Name)..."

  $RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)
  $CleanLines = @($RawLines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

  $WindowCount = [math]::Ceiling($CleanLines.Count / $WindowSize)

  for ($w = 0; $w -lt $WindowCount; $w++) {

    $Start = $w * $WindowSize
    $End = [math]::Min($Start + $WindowSize - 1, $CleanLines.Count - 1)

    if ($Start -gt $End) { continue }

    $Slice = @($CleanLines[$Start..$End])

    foreach ($Line in $Slice) {

      $Template = Normalize-Template $Line
      $Family = Get-RoughFamily $Template

      $SurfaceRows += [pscustomobject]@{
        file = $File.Name
        window_index = $w
        rough_family = $Family
        exact_template = $Template
      }
    }
  }
}

$SurfaceCsv = Join-Path $OutDir "rough_family_window_surface.csv"
$SurfaceRows | Export-Csv $SurfaceCsv -NoTypeInformation -Encoding UTF8

$FamilyRows = @(
  $SurfaceRows |
    Group-Object file,rough_family |
    ForEach-Object {
      $Parts = $_.Name -split ', ', 2
      $FileName = $Parts[0]
      $Family = $Parts[1]
      $Group = @($_.Group)

      $Windows = @($Group | Select-Object -ExpandProperty window_index -Unique)
      $ExactTemplates = @($Group | Select-Object -ExpandProperty exact_template -Unique)

      [pscustomobject]@{
        file = $FileName
        rough_family = $Family
        total_occurrences = $Group.Count
        window_count = $Windows.Count
        exact_template_count = $ExactTemplates.Count
        continuity_ratio = [math]::Round(($Windows.Count / (($SurfaceRows | Where-Object { $_.file -eq $FileName } | Select-Object -ExpandProperty window_index -Unique).Count)), 3)
        exact_variation_ratio = [math]::Round(($ExactTemplates.Count / $Group.Count), 3)
      }
    } |
    Sort-Object file,window_count,total_occurrences -Descending
)

$FamilyCsv = Join-Path $OutDir "rough_family_continuity_summary.csv"
$FamilyRows | Export-Csv $FamilyCsv -NoTypeInformation -Encoding UTF8

$HtmlRows = foreach ($R in ($FamilyRows | Select-Object -First 120)) {
@"
<tr>
  <td>$($R.file)</td>
  <td><code>$($R.rough_family)</code></td>
  <td>$($R.total_occurrences)</td>
  <td>$($R.window_count)</td>
  <td>$($R.exact_template_count)</td>
  <td>$($R.continuity_ratio)</td>
  <td>$($R.exact_variation_ratio)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Rough-Family Continuity V0</title>
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

<h1>Rough-Family Continuity V0</h1>

<div class='note'>
Observer-only window surface. This asks whether rough-shape families persist across windows even when exact templates vary.
It does not infer identity, anomaly, lifecycle, causality, or importance.
</div>

<table>
<tr>
  <th>file</th>
  <th>rough family</th>
  <th>occurrences</th>
  <th>windows present</th>
  <th>exact templates</th>
  <th>continuity ratio</th>
  <th>exact variation ratio</th>
</tr>
$($HtmlRows -join "`r`n")
</table>

<div class='boundary'>
Boundary: Rough-family continuity is not semantic identity. It only means shallow normalized leading structure persisted across windows.
<br><br>
One-line hold: Observe persistence above exact-template identity without converting it into meaning.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "ROUGH_FAMILY_CONTINUITY_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== ROUGH-FAMILY CONTINUITY COMPLETE ==="
Write-Host $HtmlPath
