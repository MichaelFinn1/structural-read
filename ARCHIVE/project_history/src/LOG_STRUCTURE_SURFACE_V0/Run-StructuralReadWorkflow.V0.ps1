param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot,

  [string]$PanelRoot = ""
)

$ErrorActionPreference = "Stop"

function Test-LocalScript {
  param([string]$Name)

  $Path = Join-Path $PSScriptRoot $Name

  if (-not (Test-Path $Path)) {
    throw "Missing required script: $Name"
  }

  return $Path
}

$ReduceScript = Test-LocalScript "Run-LogStructureSurface.V0.ps1"
$TextureScript = Test-LocalScript "Run-LogStructureFileTextureBars.V0.ps1"
$ProfileSheetScript = Test-LocalScript "Run-StructuralReadProfileSheet.V0.ps1"

$CompareScript = Join-Path $PSScriptRoot "Run-StructuralReadTerrainComparison.V0.ps1"

Write-Host ""
Write-Host "=== STRUCTURAL READ WORKFLOW V0 ==="
Write-Host "Terrain:"
Write-Host $TerrainRoot

Write-Host ""
Write-Host "1. RECEIVE"
Write-Host "Bounded local terrain accepted."

Write-Host ""
Write-Host "2. REDUCE"
& $ReduceScript -Path $TerrainRoot

Write-Host ""
Write-Host "3. PROFILE"
& $TextureScript -Path $TerrainRoot

Write-Host ""
Write-Host "4/5/6/7. MAP / TRAVERSE / EXPORT"
& $ProfileSheetScript -TerrainRoot $TerrainRoot

if ($PanelRoot -ne "") {
  if (Test-Path $CompareScript) {
    Write-Host ""
    Write-Host "4. COMPARE"
    & $CompareScript -PanelRoot $PanelRoot
  }
}

Write-Host ""
Write-Host "8. STOP"
Write-Host "No incident, anomaly, severity, cause, recommendation, or operational meaning inferred."

$ProfileSheet = Join-Path $TerrainRoot "_surface_work\structural_read_profile_sheet_v0\STRUCTURAL_READ_PROFILE_SHEET_V0.html"

Write-Host ""
Write-Host "=== WORKFLOW COMPLETE ==="
Write-Host "Open:"
Write-Host $ProfileSheet

if (Test-Path $ProfileSheet) {
  Invoke-Item $ProfileSheet
}
