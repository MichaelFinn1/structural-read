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

$PacketRoot = Split-Path $BookmarkPath -Parent
$ReceiptDir = Join-Path $PacketRoot "return_receipts"

New-Item `
    -ItemType Directory `
    -Force `
    $ReceiptDir | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"

$ReceiptPath = Join-Path `
    $ReceiptDir `
    "return_receipt_$Stamp.md"

@"
# RETURN_RECEIPT_$Stamp

Status:
orientation_return_receipt

## Restored bookmark

$($Bookmark.bookmark_id)

## Selected region

$($Bookmark.selected_region)

## Stance scales

$($Bookmark.stance_scales -join ", ")

## Restored surfaces

- $($Bookmark.field_surface)
- $($Bookmark.descent_surface)
- $($Bookmark.return_read)

## Return note

Orientation state restored.

The bookmark preserved:

- selected region
- stance scales
- field surface
- descent surface
- return read

## Boundary

This receipt records return continuity only.

It does not add interpretation.
"@ | Set-Content `
    $ReceiptPath `
    -Encoding UTF8

Write-Host ""
Write-Host "WROTE RETURN RECEIPT"
Write-Host $ReceiptPath
Write-Host ""
