param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
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

function Write-AtomicCsv {
  param(
    [string]$Path,
    [object[]]$Rows
  )

  $Tmp = "$Path.tmp"
  $Rows | Export-Csv $Tmp -NoTypeInformation -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Get-PatternSignature {
  param([int[]]$Counts)

  $Sorted = @($Counts | Sort-Object -Descending)
  return ($Sorted -join "-")
}

$OutDir = Join-Path $TerrainRoot "_surface_work\local_middle_relation_decomposition_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$FormRows = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $RawLines = @(
    Get-Content $File.FullName -ErrorAction SilentlyContinue |
      Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
  )

  $TemplatesByLine = @()

  foreach ($Line in $RawLines) {
    $TemplatesByLine += Normalize-Template $Line
  }

  $Counts = @{}

  foreach ($Template in $TemplatesByLine) {
    if (-not $Counts.ContainsKey($Template)) {
      $Counts[$Template] = 0
    }

    $Counts[$Template] += 1
  }

  $PositionsByTemplate = @{}

  for ($i = 0; $i -lt $TemplatesByLine.Count; $i++) {
    $Template = $TemplatesByLine[$i]
    $Count = [int]$Counts[$Template]

    if ($Count -ge 2 -and $Count -le 4) {
      if (-not $PositionsByTemplate.ContainsKey($Template)) {
        $PositionsByTemplate[$Template] = @()
      }

      $PositionsByTemplate[$Template] += $i
    }
  }

  foreach ($Template in $PositionsByTemplate.Keys) {
    $OccurrenceCount = [int]$Counts[$Template]
    $NeighborhoodCounts = @{}

    foreach ($Pos in $PositionsByTemplate[$Template]) {
      $Prev = "<start>"
      $Next = "<end>"

      if ($Pos -gt 0) {
        $Prev = $TemplatesByLine[$Pos - 1]
      }

      if ($Pos -lt ($TemplatesByLine.Count - 1)) {
        $Next = $TemplatesByLine[$Pos + 1]
      }

      $Neighborhood = "$Prev || $Template || $Next"

      if (-not $NeighborhoodCounts.ContainsKey($Neighborhood)) {
        $NeighborhoodCounts[$Neighborhood] = 0
      }

      $NeighborhoodCounts[$Neighborhood] += 1
    }

    $ReuseCounts = @(
      $NeighborhoodCounts.Values |
        ForEach-Object { [int]$_ } |
        Sort-Object -Descending
    )

    $DistinctNeighborhoodCount = $ReuseCounts.Count
    $MaxNeighborhoodReuse = 0

    if ($ReuseCounts.Count -gt 0) {
      $MaxNeighborhoodReuse = $ReuseCounts[0]
    }

    $SharedNeighborhoodRatio = 0
    if ($OccurrenceCount -gt 0) {
      $SharedNeighborhoodRatio = [math]::Round(($MaxNeighborhoodReuse / $OccurrenceCount), 4)
    }

    $ContextReuseRatio = 0
    if ($OccurrenceCount -gt 1) {
      $ContextReuseRatio = [math]::Round((($OccurrenceCount - $DistinctNeighborhoodCount) / ($OccurrenceCount - 1)), 4)
    }

    $PatternSignature = Get-PatternSignature -Counts $ReuseCounts

    $FormRows += [pscustomobject]@{
      file = $File.Name
      bucket = $OccurrenceCount
      middle_form = $Template
      occurrence_count = $OccurrenceCount
      distinct_neighborhood_count = $DistinctNeighborhoodCount
      max_neighborhood_reuse = $MaxNeighborhoodReuse
      shared_neighborhood_ratio = $SharedNeighborhoodRatio
      context_reuse_ratio = $ContextReuseRatio
      neighborhood_pattern_signature = $PatternSignature
    }
  }
}

$DistributionRows = @(
  $FormRows |
    Group-Object file,bucket,neighborhood_pattern_signature |
    ForEach-Object {
      $Parts = $_.Name -split ", "

      [pscustomobject]@{
        file = $Parts[0]
        bucket = [int]$Parts[1]
        pattern_signature = $Parts[2]
        forms = $_.Count
      }
    } |
    Sort-Object file,bucket,pattern_signature
)

$SurfacePath = Join-Path $OutDir "local_middle_relation_decomposition_surface.csv"
$DistributionPath = Join-Path $OutDir "local_middle_relation_distribution.csv"

Write-AtomicCsv -Path $SurfacePath -Rows ($FormRows | Sort-Object file,bucket,neighborhood_pattern_signature,middle_form)
Write-AtomicCsv -Path $DistributionPath -Rows $DistributionRows

Write-Host ""
Write-Host "=== LOCAL MIDDLE RELATION DECOMPOSITION COMPLETE ==="
Write-Host $SurfacePath
Write-Host $DistributionPath
