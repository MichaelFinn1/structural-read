param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function New-SurfaceRow {
  param(
    [string]$Name,
    [string]$Layer,
    [string]$Purpose,
    [string]$Path
  )

  $Exists = Test-Path $Path
  $Status = if ($Exists) { "available" } else { "not generated" }
  $Stamp = ""

  if ($Exists) {
    $Stamp = (Get-Item $Path).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
    $Link = "<a href='file:///$Path'>open</a>"
  } else {
    $Link = ""
  }

  return [pscustomobject]@{
    name = $Name
    layer = $Layer
    purpose = $Purpose
    status = $Status
    generated = $Stamp
    link = $Link
  }
}

$OutDir = Join-Path $TerrainRoot "_surface_work\structural_read_overview_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Surfaces = @()

$Surfaces += New-SurfaceRow "Profile sheet" "profile" "Entry profile: files, recurrence bands, exports." (Join-Path $TerrainRoot "_surface_work\structural_read_profile_sheet_v0\STRUCTURAL_READ_PROFILE_SHEET_V0.html")
$Surfaces += New-SurfaceRow "File texture bars" "traversal" "Visual file bars and file-level descent." (Join-Path $TerrainRoot "_surface_work\log_structure_file_texture_v0\LOG_STRUCTURE_FILE_TEXTURE_PROFILE_BARS_V0.html")
$Surfaces += New-SurfaceRow "Stable topology" "stable" "Stable recurrence cartography: shape, mass, concentration." (Join-Path $TerrainRoot "_surface_work\stable_topology_prototype_v0\STABLE_TOPOLOGY_PROTOTYPE_V0.html")
$Surfaces += New-SurfaceRow "Middle topology" "middle" "Weak recurrence ecology: count buckets 4 / 3 / 2." (Join-Path $TerrainRoot "_surface_work\middle_topology_prototype_v0\MIDDLE_TOPOLOGY_PROTOTYPE_V0.html")
$Surfaces += New-SurfaceRow "Middle transition" "middle" "Windowed recurrence movement, not lifecycle truth." (Join-Path $TerrainRoot "_surface_work\middle_transition_prototype_v0\MIDDLE_TRANSITION_PROTOTYPE_V0.html")
$Surfaces += New-SurfaceRow "Middle reuse geometry" "middle" "Contextual reuse topology across middle buckets." (Join-Path $TerrainRoot "_surface_work\middle_reuse_geometry_html_v0\MIDDLE_REUSE_GEOMETRY_V0.html")
$Surfaces += New-SurfaceRow "Layer index" "meta" "Layer model bridge across generated observer surfaces." (Join-Path $TerrainRoot "_surface_work\structural_read_layer_index_v0\STRUCTURAL_READ_LAYER_INDEX_V0.html")
$Surfaces += New-SurfaceRow "Log read markdown" "export" "Plain markdown structural read export." (Join-Path $TerrainRoot "_surface_work\log_structure_v0\LOG_STRUCTURE_READ_V0.md")
$Surfaces += New-SurfaceRow "Template surface CSV" "export" "Template recurrence CSV export." (Join-Path $TerrainRoot "_surface_work\log_structure_v0\log_template_surface.csv")

$Rows = foreach ($S in $Surfaces) {
@"
<tr>
  <td>$($S.name)</td>
  <td><span class='tag'>$($S.layer)</span></td>
  <td>$($S.purpose)</td>
  <td>$($S.status)</td>
  <td>$($S.generated)</td>
  <td>$($S.link)</td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Structural Read Overview V0</title>
<style>
body { background:#111; color:#eee; font-family:Segoe UI, Arial; padding:32px; }
.card { max-width:1180px; margin:auto; background:#1b1b1b; border-radius:18px; padding:28px; }
h1 { margin-top:0; }
.note { color:#aaa; line-height:1.6; margin-bottom:24px; max-width:960px; }
table { width:100%; border-collapse:collapse; margin-top:18px; }
th,td { border-bottom:1px solid #333; padding:10px; text-align:left; vertical-align:top; }
th { color:#aaa; }
a { color:#8fd8f4; text-decoration:none; }
a:hover { text-decoration:underline; }
.tag { display:inline-block; background:#252525; border:1px solid #444; border-radius:999px; padding:3px 9px; color:#ccc; font-size:12px; }
.boundary { margin-top:30px; color:#999; font-size:12px; line-height:1.7; border-top:1px solid #333; padding-top:18px; }
</style>
</head>
<body>
<div class='card'>

<h1>Structural Read Overview V0</h1>

<div class='note'>
This overview is a navigation membrane for earned surfaces. It discovers generated outputs and links to them without recomputing, ranking, previewing, or interpreting.
</div>

<table>
<tr>
  <th>surface</th>
  <th>layer</th>
  <th>purpose</th>
  <th>status</th>
  <th>generated</th>
  <th>open</th>
</tr>
$($Rows -join "`r`n")
</table>

<div class='boundary'>
Boundary: This overview does not infer anomaly, severity, cause, importance, lifecycle, semantic family, priority, or recommended action.
<br><br>
One-line hold: Build a map of earned surfaces, not a dashboard of conclusions.
</div>

</div>
</body>
</html>
"@

$OutPath = Join-Path $OutDir "STRUCTURAL_READ_OVERVIEW_V0.html"
$Tmp = "$OutPath.tmp"
$Html | Set-Content $Tmp -Encoding UTF8
Move-Item -Force $Tmp $OutPath

Write-Host ""
Write-Host "=== STRUCTURAL READ OVERVIEW COMPLETE ==="
Write-Host $OutPath
