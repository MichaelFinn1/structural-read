param(
  [Parameter(Mandatory=$true)]
  [string]$FilePath,

  [int]$WindowSize = 500
)

$ErrorActionPreference = "Stop"

function Normalize-Template {
  param([string]$Line)

  $t = $Line
  $t = $t -replace '\b\d{1,3}(\.\d{1,3}){3}\b','<ip>'
  $t = $t -replace '[A-Fa-f0-9]{8,}','<hex>'
  $t = $t -replace '\b\d+\b','<num>'
  $t = $t -replace '\s+',' '

  return $t.Trim()
}

function Get-RoughFamily {
  param([string]$Template)

  $Parts = @($Template -split ' ' | Where-Object { $_ -ne "" })

  if ($Parts.Count -le 4) {
    return ($Parts -join ' ')
  }

  return (($Parts | Select-Object -First 4) -join ' ')
}

function Get-Regime {
  param([int]$Count)

  if ($Count -ge 5) { return "stable" }
  if ($Count -ge 2) { return "middle" }
  return "residual"
}

$File = Get-Item $FilePath
$TerrainRoot = $File.Directory.FullName

$OutDir = Join-Path $TerrainRoot "_surface_work\temporal_strata_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)
$Forms = @()

foreach ($Line in $RawLines) {
  if ([string]::IsNullOrWhiteSpace($Line)) { continue }
  $Forms += Normalize-Template $Line
}

$GlobalCounts = @{}
foreach ($F in $Forms) {
  if (-not $GlobalCounts.ContainsKey($F)) { $GlobalCounts[$F] = 0 }
  $GlobalCounts[$F] += 1
}

$GlobalRegime = @{}
foreach ($K in $GlobalCounts.Keys) {
  $GlobalRegime[$K] = Get-Regime $GlobalCounts[$K]
}

$PreviousFamilies = @{}
$Rows = @()

$WindowIndex = 0

for ($Start = 0; $Start -lt $Forms.Count; $Start += $WindowSize) {

  $WindowIndex += 1

  $End = [Math]::Min($Start + $WindowSize - 1, $Forms.Count - 1)
  $Slice = @($Forms[$Start..$End])

  $StableCount = 0
  $MiddleCount = 0
  $ResidualCount = 0
  $StableEdgeForms = 0

  $CurrentFamilies = @{}

  for ($i = 0; $i -lt $Slice.Count; $i++) {

    $AbsoluteIndex = $Start + $i
    $Current = $Forms[$AbsoluteIndex]
    $Regime = $GlobalRegime[$Current]
    $Family = Get-RoughFamily $Current

    if (-not $CurrentFamilies.ContainsKey($Family)) {
      $CurrentFamilies[$Family] = $true
    }

    if ($Regime -eq "stable") { $StableCount += 1 }
    elseif ($Regime -eq "middle") { $MiddleCount += 1 }
    else { $ResidualCount += 1 }

    if ($Regime -ne "stable") {
      $PrevRegime = "boundary"
      $NextRegime = "boundary"

      if ($AbsoluteIndex -gt 0) {
        $PrevRegime = $GlobalRegime[$Forms[$AbsoluteIndex - 1]]
      }

      if ($AbsoluteIndex -lt ($Forms.Count - 1)) {
        $NextRegime = $GlobalRegime[$Forms[$AbsoluteIndex + 1]]
      }

      if ($PrevRegime -eq "stable" -or $NextRegime -eq "stable") {
        $StableEdgeForms += 1
      }
    }
  }

  $NewFamilies = 0
  $ReturningFamilies = 0

  foreach ($Fam in $CurrentFamilies.Keys) {
    if ($PreviousFamilies.ContainsKey($Fam)) {
      $ReturningFamilies += 1
    } else {
      $NewFamilies += 1
    }
  }

  $DisappearingFamilies = 0

  foreach ($Fam in $PreviousFamilies.Keys) {
    if (-not $CurrentFamilies.ContainsKey($Fam)) {
      $DisappearingFamilies += 1
    }
  }

  $Rows += [pscustomobject]@{
    window = "window_$("{0:D3}" -f $WindowIndex)"
    stable_count = $StableCount
    middle_count = $MiddleCount
    residual_count = $ResidualCount
    new_rough_families = $NewFamilies
    returning_rough_families = $ReturningFamilies
    disappearing_rough_families = $DisappearingFamilies
    stable_edge_forms = $StableEdgeForms
  }

  $PreviousFamilies = $CurrentFamilies.Clone()
}

$Csv = Join-Path $OutDir "temporal_strata_surface.csv"
$Rows | Export-Csv $Csv -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "=== TEMPORAL STRATA CSV COMPLETE ==="
Write-Host $Csv
