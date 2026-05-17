param(
    [string]$BookmarkPath = ".\src\LOG_STRUCTURE_SURFACE_V0\product_packets\operator_workbench_v1_001\bookmark_apache_netsparker_orientation_001.json"
)

if (-not (Test-Path $BookmarkPath)) {
    Write-Host ""
    Write-Host "BOOKMARK NOT FOUND"
    Write-Host $BookmarkPath
    Write-Host ""
    exit
}

$Bookmark = Get-Content $BookmarkPath -Raw | ConvertFrom-Json

$SurfaceRoot = ".\src\LOG_STRUCTURE_SURFACE_V0"

$FieldSurface = Join-Path `
    $SurfaceRoot `
    $Bookmark.field_surface

$DescentSurface = Join-Path `
    $SurfaceRoot `
    $Bookmark.descent_surface

$ReturnRead = Join-Path `
    $SurfaceRoot `
    $Bookmark.return_read

Write-Host ""
Write-Host "RESTORING ORIENTATION STATE"
Write-Host ""
Write-Host "Selected Region:" $Bookmark.selected_region
Write-Host "Stance Scales:" ($Bookmark.stance_scales -join ", ")
Write-Host ""

Invoke-Item $FieldSurface
Invoke-Item $DescentSurface
Invoke-Item $ReturnRead
