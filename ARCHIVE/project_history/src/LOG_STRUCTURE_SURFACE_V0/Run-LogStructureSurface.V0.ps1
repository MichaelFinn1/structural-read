param(
  [Parameter(Mandatory=$true)]
  [string]$Path,

  [int]$MaxLines = 50000,

  [int]$StableThreshold = 5,

  [int]$MiddleThreshold = 2
)

$ErrorActionPreference = "Stop"

function Write-AtomicCsv {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [object[]]$Rows
  )

  $tmp = "$Path.tmp"

  if ($null -eq $Rows -or @($Rows).Count -eq 0) {
    "" | Set-Content $tmp -Encoding UTF8
  } else {
    @($Rows) | Export-Csv $tmp -NoTypeInformation -Encoding UTF8
  }

  Move-Item -Force $tmp $Path
}

function Write-AtomicText {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Text
  )

  $tmp = "$Path.tmp"
  $Text | Set-Content $tmp -Encoding UTF8
  Move-Item -Force $tmp $Path
}

function Normalize-LogLine {
  param([string]$Line)

  if ($null -eq $Line) {
    return "<blank>"
  }

  $s = $Line.Trim()

  $s = [regex]::Replace($s, '\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?Z?\b', '<timestamp>')
  $s = [regex]::Replace($s, '\b\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\b', '<timestamp>')
  $s = [regex]::Replace($s, '\b\d{1,3}(\.\d{1,3}){3}\b', '<ip>')
  $s = [regex]::Replace($s, '\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', '<guid>')
  $s = [regex]::Replace($s, '\b0x[0-9a-fA-F]+\b', '<hex>')
  $s = [regex]::Replace($s, '\b\d+\b', '<num>')
  $s = [regex]::Replace($s, '\s+', ' ')

  if ([string]::IsNullOrWhiteSpace($s)) {
    $s = "<blank>"
  }

  return $s
}

if (-not (Test-Path -LiteralPath $Path)) {
  throw "Path not found: $Path"
}

$Target = Get-Item -LiteralPath $Path

if ($Target.PSIsContainer) {
  $RootPath = $Target.FullName
  $LogFiles = @(
    Get-ChildItem -LiteralPath $RootPath -File -Recurse -Force |
      Where-Object {
        $_.FullName -notmatch '[\\/]_surface_work([\\/]|$)' -and
        ($_.Extension.ToLowerInvariant() -eq ".log" -or $_.Extension.ToLowerInvariant() -eq ".txt")
      } |
      Sort-Object FullName
  )

  $OutRoot = Join-Path $RootPath "_surface_work\log_structure_v0"
} else {
  $RootPath = Split-Path -Parent $Target.FullName
  $LogFiles = @($Target)
  $SafeName = [IO.Path]::GetFileNameWithoutExtension($Target.Name)
  $OutRoot = Join-Path $RootPath ("_surface_work\log_structure_v0\" + $SafeName)
}

New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

$LineRows = @()
$GlobalLine = 0

foreach ($file in $LogFiles) {
  $SourceRel = $file.FullName

  if ($SourceRel.StartsWith($RootPath)) {
    $SourceRel = $SourceRel.Substring($RootPath.Length).TrimStart("\")
  }

  $LocalLine = 0

  foreach ($line in [System.IO.File]::ReadLines($file.FullName)) {
    $GlobalLine += 1
    $LocalLine += 1

    if ($GlobalLine -gt $MaxLines) {
      break
    }

    $Template = Normalize-LogLine -Line $line

    $LineRows += [pscustomobject]@{
      global_line_number = $GlobalLine
      source_file = $SourceRel
      local_line_number = $LocalLine
      template = $Template
      raw_sample = $line
    }
  }

  if ($GlobalLine -gt $MaxLines) {
    break
  }
}

$TemplateRows = @(
  @($LineRows) |
    Group-Object template |
    ForEach-Object {
      $Count = [int]$_.Count

      $Class = "residual"
      if ($Count -ge $StableThreshold) {
        $Class = "stable"
      } elseif ($Count -ge $MiddleThreshold) {
        $Class = "middle"
      }

      $Sample = ""
      $First = @($_.Group) | Select-Object -First 1
      if ($First) {
        $Sample = $First.raw_sample
      }

      [pscustomobject]@{
        template = $_.Name
        count = $Count
        class = $Class
        sample = $Sample
      }
    } |
    Sort-Object count -Descending
)

$ClassRows = @(
  @($TemplateRows) |
    Group-Object class |
    ForEach-Object {
      $LineCount = 0
      foreach ($r in @($_.Group)) {
        $LineCount += [int]$r.count
      }

      [pscustomobject]@{
        class = $_.Name
        template_count = [int]$_.Count
        line_count = $LineCount
      }
    } |
    Sort-Object class
)

Write-AtomicCsv -Path (Join-Path $OutRoot "log_line_template_index.csv") -Rows @($LineRows)
Write-AtomicCsv -Path (Join-Path $OutRoot "log_template_surface.csv") -Rows @($TemplateRows)
Write-AtomicCsv -Path (Join-Path $OutRoot "log_class_summary.csv") -Rows @($ClassRows)

$StableCount = 0
$MiddleCount = 0
$ResidualCount = 0

foreach ($r in @($ClassRows)) {
  if ($r.class -eq "stable") { $StableCount = [int]$r.line_count }
  if ($r.class -eq "middle") { $MiddleCount = [int]$r.line_count }
  if ($r.class -eq "residual") { $ResidualCount = [int]$r.line_count }
}

$TopTemplates = @($TemplateRows | Select-Object -First 10)

$TopLines = @()
foreach ($t in $TopTemplates) {
  $TopLines += "- [$($t.class)] count=$($t.count) :: $($t.template)"
}

if ($TopLines.Count -eq 0) {
  $TopLines += "- none surfaced"
}

$Read = @"
# LOG_STRUCTURE_READ_V0

Status: log_structure_surface_v0

## Input

$Path

## Scope

- log_files_seen: $($LogFiles.Count)
- lines_indexed: $(@($LineRows).Count)
- max_lines: $MaxLines

## Reduction surface

- stable_line_count: $StableCount
- middle_line_count: $MiddleCount
- residual_line_count: $ResidualCount
- template_count: $(@($TemplateRows).Count)

## Top repeated templates

$($TopLines -join "`r`n")

## Outputs

- log_line_template_index.csv
- log_template_surface.csv
- log_class_summary.csv
- LOG_STRUCTURE_READ_V0.md

## Boundary

This read exposes repeated line structure, middle recurrence, and residual lines.

It does not:
- infer cause
- detect incidents
- rank severity
- recommend action
- assign operational meaning
- claim anomaly status

## One-line hold

Reduce log noise into structure; human keeps judgment.
"@

Write-AtomicText -Path (Join-Path $OutRoot "LOG_STRUCTURE_READ_V0.md") -Text $Read

Write-Host ""
Write-Host "=== LOG STRUCTURE SURFACE COMPLETE ==="
Write-Host "Input:"
Write-Host $Path
Write-Host ""
Write-Host "Output:"
Write-Host $OutRoot
Write-Host ""
Write-Host "Open:"
Write-Host (Join-Path $OutRoot "LOG_STRUCTURE_READ_V0.md")
