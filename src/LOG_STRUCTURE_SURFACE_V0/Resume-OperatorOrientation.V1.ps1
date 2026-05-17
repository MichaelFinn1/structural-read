param(
    [string]$BookmarkPath = ".\src\LOG_STRUCTURE_SURFACE_V0\product_packets\operator_workbench_v1_001\bookmark_apache_netsparker_orientation_001.json"
)

$SurfaceRoot = ".\src\LOG_STRUCTURE_SURFACE_V0"

& "$SurfaceRoot\Restore-OrientationState.V1.ps1" `
    -BookmarkPath $BookmarkPath

& "$SurfaceRoot\Write-OrientationReturnReceipt.V1.ps1" `
    -BookmarkPath $BookmarkPath
