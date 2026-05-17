param(
    [string]$PacketRoot = ".\src\LOG_STRUCTURE_SURFACE_V0\product_packets\operator_workbench_v1_001"
)

$SurfaceRoot = ".\src\LOG_STRUCTURE_SURFACE_V0"

$Items = @(
    "$PacketRoot\operator_workbench_v1_manifest.json",
    "$PacketRoot\OPERATOR_WORKBENCH_V1_FRAME_001.md",
    "$PacketRoot\FIRST_TRAVERSAL_LOOP_001.md",
    "$PacketRoot\FIRST_USER_TRAVERSAL_TEST_001.md",
    "$SurfaceRoot\comparison_packets\master_comparative_field_001\master_comparative_field_v0.svg"
)

foreach ($Item in $Items) {
    if (Test-Path $Item) {
        Invoke-Item $Item
    } else {
        Write-Host "MISSING: $Item"
    }
}
