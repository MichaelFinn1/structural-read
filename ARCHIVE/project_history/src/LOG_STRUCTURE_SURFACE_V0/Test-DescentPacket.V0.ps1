param(
    [Parameter(Mandatory=$true)]
    [string]$PacketPath,

    [string]$ManifestPath = ".\DESCENT_MANIFEST_V0.csv"
)

$ErrorActionPreference = "Stop"

$allowedStatus = @(
    "open",
    "banked_reread",
    "revised",
    "stopped",
    "invalidated"
)

$result = [ordered]@{
    packet_path = $PacketPath
    packet_id = Split-Path $PacketPath -Leaf
    valid = $true
    issues = @()
}

function Add-Issue {
    param([string]$Message)
    $result.valid = $false
    $result.issues += $Message
}

if (-not (Test-Path $PacketPath)) {
    Add-Issue "packet folder missing"
} else {
    $readme = Join-Path $PacketPath "README.md"
    $return = Join-Path $PacketPath "RETURN_READ.md"

    if (-not (Test-Path $readme)) {
        Add-Issue "README.md missing"
    } else {
        $readmeText = Get-Content $readme -Raw
        if ($readmeText -notmatch "Source read:") { Add-Issue "README missing Source read" }
        if ($readmeText -notmatch "Boundary:") { Add-Issue "README missing Boundary" }
        if ($readmeText -notmatch "Structural question:") { Add-Issue "README missing Structural question" }
    }

    if (-not (Test-Path $return)) {
        Add-Issue "RETURN_READ.md missing"
    } else {
        $returnText = Get-Content $return -Raw
        if ($returnText -notmatch "## Evidence touched") { Add-Issue "RETURN_READ missing Evidence touched" }
        if ($returnText -notmatch "## What held\?") { Add-Issue "RETURN_READ missing What held" }
        if ($returnText -notmatch "## What weakened\?") { Add-Issue "RETURN_READ missing What weakened" }
        if ($returnText -notmatch "## What remains unresolved\?") { Add-Issue "RETURN_READ missing unresolved section" }
        if ($returnText -notmatch "## Boundary") { Add-Issue "RETURN_READ missing Boundary" }
    }

    $evidenceFiles = Get-ChildItem $PacketPath -File | Where-Object {
        $_.Name -notin @("README.md", "RETURN_READ.md")
    }

    if ($evidenceFiles.Count -lt 1) {
        Add-Issue "no evidence files present"
    }
}

if (-not (Test-Path $ManifestPath)) {
    Add-Issue "manifest missing"
} else {
    $manifest = Import-Csv $ManifestPath
    $row = $manifest | Where-Object { $_.packet_id -eq $result.packet_id }

    if (-not $row) {
        Add-Issue "packet not found in manifest"
    } else {
        if (-not $row.source_read_id) { Add-Issue "manifest missing source_read_id" }
        if (-not $row.packet_type) { Add-Issue "manifest missing packet_type" }
        if (-not $row.boundary) { Add-Issue "manifest missing boundary" }
if (
    $row.status -in @("banked_reread","revised")
) {
    if (-not $row.unresolved_scale_behavior) {
        Add-Issue "missing unresolved_scale_behavior"
    }

    if (-not $row.unresolved_attachment_structure) {
        Add-Issue "missing unresolved_attachment_structure"
    }

    if (-not $row.unresolved_middle_distribution) {
        Add-Issue "missing unresolved_middle_distribution"
    }
}

        if ($allowedStatus -notcontains $row.status) {
            Add-Issue "manifest status not allowed: $($row.status)"
        }
    }
}


if ($result.valid) {
    Write-Host ""
    Write-Host "DESCENT PACKET VALID"
    Write-Host $result.packet_id
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "DESCENT PACKET HAS ISSUES"
    Write-Host $result.packet_id
    Write-Host ""
    foreach ($issue in $result.issues) {
        Write-Host "- $issue"
    }
    Write-Host ""
}
