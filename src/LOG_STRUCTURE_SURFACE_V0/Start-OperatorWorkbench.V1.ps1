$PacketRoot = ".\src\LOG_STRUCTURE_SURFACE_V0\product_packets\operator_workbench_v1_001"

$IndexPath = Join-Path `
    $PacketRoot `
    "bookmark_index_v1.csv"

if (-not (Test-Path $IndexPath)) {

    Write-Host ""
    Write-Host "BOOKMARK INDEX NOT FOUND"
    Write-Host ""
    exit
}

$Bookmarks = Import-Csv $IndexPath

Write-Host ""
Write-Host "AVAILABLE ORIENTATION STATES"
Write-Host ""

for ($i = 0; $i -lt $Bookmarks.Count; $i++) {

    $Row = $Bookmarks[$i]

    Write-Host "[$i]"
    Write-Host " bookmark_id    :" $Row.bookmark_id
    Write-Host " selected_region:" $Row.selected_region
    Write-Host " stance_scales :" $Row.stance_scales
    Write-Host ""
}

if ($Bookmarks.Count -eq 1) {

    Write-Host "ONLY ONE BOOKMARK AVAILABLE"
    Write-Host "AUTO-SELECTING [0]"
    Write-Host ""

    $ChoiceInt = 0

} else {

    $Choice = Read-Host "Select bookmark index"

    if ($Choice -notmatch '^\d+$') {

        Write-Host ""
        Write-Host "INVALID SELECTION"
        Write-Host ""
        exit
    }

    $ChoiceInt = [int]$Choice

    if ($ChoiceInt -ge $Bookmarks.Count) {

        Write-Host ""
        Write-Host "SELECTION OUT OF RANGE"
        Write-Host ""
        exit
    }
}

$Selected = $Bookmarks[$ChoiceInt]

Write-Host ""
Write-Host "RESTORING"
Write-Host $Selected.bookmark_id
Write-Host ""

& ".\src\LOG_STRUCTURE_SURFACE_V0\Resume-OperatorOrientation.V1.ps1" `
    -BookmarkPath $Selected.path
