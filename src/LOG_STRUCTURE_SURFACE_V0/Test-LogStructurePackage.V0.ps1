$ErrorActionPreference = "Stop"

$Files = @(
  "START_HERE_LOG_STRUCTURE_V0.md",
  "LOG_STRUCTURE_PRODUCT_BOUNDARY_V0.md",
  "Run-LogStructureSurface.V0.ps1",
  "Run-LogStructure.Drop.bat",
  "Run-LogStructurePanelSummary.V0.ps1",
  "Run-LogStructureTerrainCard.V0.ps1",
  "Run-LogStructureZoomCard.V0.ps1",
  "Run-LogStructureBandTextureCard.V0.ps1",
  "START_HERE_FOR_OUTSIDERS.md",
  "STRUCTURAL_READ_EIGHT_STAGE_CONTRACT_V0.md"
)

$Rows = foreach ($f in $Files) {
  $exists = Test-Path $f
  $status = "missing"
  $note = ""

  if ($exists) {
    if ($f -like "*.ps1") {
      $errors = $null
      $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $f -Raw), [ref]$errors)
      if ($errors -and $errors.Count -gt 0) {
        $status = "parse_error"
        $note = ($errors | Select-Object -First 1).Message
      } else {
        $status = "ok"
      }
    } else {
      $status = "text_present"
    }
  }

  [pscustomobject]@{
    file = $f
    exists = $exists
    status = $status
    note = $note
  }
}

Write-Host "=== LOG STRUCTURE V0 SELF CHECK ==="
$Rows | Format-Table -AutoSize

$Rows | Export-Csv ".\LOG_STRUCTURE_V0_SELF_CHECK.csv" -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Wrote:"
Write-Host ".\LOG_STRUCTURE_V0_SELF_CHECK.csv"





