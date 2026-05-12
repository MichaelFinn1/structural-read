param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicCsv {
  param(
    [string]$Path,
    [object[]]$Rows
  )

  $Tmp = "$Path.tmp"
  $Rows | Export-Csv $Tmp -NoTypeInformation -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$SourceDir = Join-Path $TerrainRoot "_surface_work\local_middle_relation_decomposition_v0"
$SourceCsv = Join-Path $SourceDir "local_middle_relation_distribution.csv"

if (-not (Test-Path $SourceCsv)) {
  throw "Missing source distribution CSV. Run Run-LocalMiddleRelationDecomposition.V0.ps1 first: $SourceCsv"
}

$OutDir = Join-Path $TerrainRoot "_surface_work\reuse_geometry_distribution_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Rows = @(Import-Csv $SourceCsv)

if ($Rows.Count -eq 0) {
  throw "Source distribution CSV is empty: $SourceCsv"
}

$BucketTotals = @{}
$FileTotals = @{}

foreach ($R in $Rows) {
  $File = [string]$R.file
  $Bucket = [string]$R.bucket
  $Forms = [int]$R.forms

  $BucketKey = "$File||$Bucket"

  if (-not $BucketTotals.ContainsKey($BucketKey)) {
    $BucketTotals[$BucketKey] = 0
  }

  if (-not $FileTotals.ContainsKey($File)) {
    $FileTotals[$File] = 0
  }

  $BucketTotals[$BucketKey] += $Forms
  $FileTotals[$File] += $Forms
}

$OutRows = foreach ($R in $Rows) {
  $File = [string]$R.file
  $Bucket = [string]$R.bucket
  $Forms = [int]$R.forms
  $Pattern = [string]$R.pattern_signature
  $BucketKey = "$File||$Bucket"

  $BucketTotal = [int]$BucketTotals[$BucketKey]
  $FileTotal = [int]$FileTotals[$File]

  $PctBucket = 0
  $PctFile = 0

  if ($BucketTotal -gt 0) {
    $PctBucket = [math]::Round(($Forms / $BucketTotal) * 100, 2)
  }

  if ($FileTotal -gt 0) {
    $PctFile = [math]::Round(($Forms / $FileTotal) * 100, 2)
  }

  [pscustomobject]@{
    file = $File
    bucket = [int]$Bucket
    pattern_signature = $Pattern
    forms = $Forms
    bucket_total_forms = $BucketTotal
    file_total_middle_forms = $FileTotal
    pct_of_bucket = $PctBucket
    pct_of_file_middle = $PctFile
  }
}

$OutPath = Join-Path $OutDir "reuse_geometry_distribution_surface.csv"

Write-AtomicCsv -Path $OutPath -Rows (
  $OutRows |
    Sort-Object file,bucket,pattern_signature
)

Write-Host ""
Write-Host "=== REUSE GEOMETRY DISTRIBUTION SURFACE COMPLETE ==="
Write-Host $OutPath
