param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Link-IfExists {
  param(
    [string]$Label,
    [string]$Path,
    [string]$Note
  )

  if (Test-Path $Path) {
    return "<tr><td><a href='file:///$Path'>$Label</a></td><td>available</td><td>$Note</td></tr>"
  }

  return "<tr><td>$Label</td><td>not yet generated</td><td>$Note</td></tr>"
}

$OutDir = Join-Path $TerrainRoot "_surface_work\structural_read_layer_index_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Profile = Join-Path $TerrainRoot "_surface_work\structural_read_profile_sheet_v0\STRUCTURAL_READ_PROFILE_SHEET_V0.html"
$Stable = Join-Path $TerrainRoot "_surface_work\stable_topology_prototype_v0\STABLE_TOPOLOGY_PROTOTYPE_V0.html"
$Middle = Join-Path $TerrainRoot "_surface_work\middle_topology_prototype_v0\MIDDLE_TOPOLOGY_PROTOTYPE_V0.html"
$Transition = Join-Path $TerrainRoot "_surface_work\middle_transition_prototype_v0\MIDDLE_TRANSITION_PROTOTYPE_V0.html"
$Reuse = Join-Path $TerrainRoot "_surface_work\middle_reuse_geometry_html_v0\MIDDLE_REUSE_GEOMETRY_V0.html"

$Rows = @()
$Rows += Link-IfExists "Profile sheet" $Profile "Entry surface: receive, reduce, profile, export."
$Rows += Link-IfExists "Stable topology" $Stable "Stable recurrence cartography: shape, mass, concentration."
$Rows += Link-IfExists "Middle topology" $Middle "Weak recurrence ecology: count buckets 4 / 3 / 2."
$Rows += Link-IfExists "Middle transition" $Transition "Windowed recurrence movement, not lifecycle truth."
$Rows += Link-IfExists "Middle reuse geometry" $Reuse "Contextual reuse topology across middle buckets."

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Structural Read Layer Index V0</title>
<style>
body { background:#111; color:#eee; font-family:Segoe UI, Arial; padding:32px; }
.card { max-width:1120px; margin:auto; background:#1b1b1b; border-radius:18px; padding:28px; }
a { color:#8fd8f4; text-decoration:none; }
a:hover { text-decoration:underline; }
.note { color:#aaa; line-height:1.6; margin-bottom:24px; }
table { width:100%; border-collapse:collapse; margin-top:18px; }
th,td { border-bottom:1px solid #333; padding:10px; text-align:left; vertical-align:top; }
th { color:#aaa; }
.boundary { margin-top:30px; color:#999; font-size:12px; line-height:1.7; border-top:1px solid #333; padding-top:18px; }
</style>
</head>
<body>
<div class='card'>
<h1>Structural Read Layer Index V0</h1>

<div class='note'>
This index connects generated observer surfaces without adding interpretation.
Stable shows recurrence terrain. Middle shows weak recurrence ecology and contextual reuse topology.
Transition shows candidate movement between recurrence postures. Residual remains sparse edge structure.
</div>

<table>
<tr><th>surface</th><th>status</th><th>role</th></tr>
$($Rows -join "`r`n")
</table>

<div class='boundary'>
Boundary: This index does not infer anomaly, severity, cause, importance, lifecycle, semantic family, or recommended action.
<br><br>
One-line hold: Preserve orientation across layers without collapsing structure into authority.
</div>
</div>
</body>
</html>
"@

$OutPath = Join-Path $OutDir "STRUCTURAL_READ_LAYER_INDEX_V0.html"
$Tmp = "$OutPath.tmp"
$Html | Set-Content $Tmp -Encoding UTF8
Move-Item -Force $Tmp $OutPath

Write-Host ""
Write-Host "=== STRUCTURAL READ LAYER INDEX COMPLETE ==="
Write-Host $OutPath
