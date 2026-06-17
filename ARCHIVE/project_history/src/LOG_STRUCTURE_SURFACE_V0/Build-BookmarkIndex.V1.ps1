$PacketRoot = ".\src\LOG_STRUCTURE_SURFACE_V0\product_packets\operator_workbench_v1_001"

$Bookmarks = Get-ChildItem `
    $PacketRoot `
    -Filter "bookmark_*.json" `
    -File

$Rows = @()

foreach ($BookmarkFile in $Bookmarks) {
    $Bookmark = Get-Content $BookmarkFile.FullName -Raw | ConvertFrom-Json

    $Rows += [pscustomobject]@{
        bookmark_id     = $Bookmark.bookmark_id
        selected_region = $Bookmark.selected_region
        stance_scales   = ($Bookmark.stance_scales -join "|")
        status          = $Bookmark.status
        path            = $BookmarkFile.FullName
    }
}

$Out = Join-Path $PacketRoot "bookmark_index_v1.csv"

$Rows | Export-Csv `
    $Out `
    -NoTypeInformation `
    -Encoding UTF8

Write-Host ""
Write-Host "WROTE BOOKMARK INDEX"
Write-Host $Out
Write-Host ""
