param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot,

  [int]$MaxRows = 120
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

function Short-Hash {
  param([string]$Text)

  $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
  $Sha = [System.Security.Cryptography.SHA256]::Create()
  $Hash = $Sha.ComputeHash($Bytes)
  return (($Hash[0..5] | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$OutDir = Join-Path $TerrainRoot "_surface_work\local_middle_relation_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

$Rows = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
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
    $Bucket = [int]$Counts[$Template]
    $Neighborhoods = @{}

    foreach ($Pos in $PositionsByTemplate[$Template]) {
      $Prev = "<start>"
      $Next = "<end>"

      if ($Pos -gt 0) {
        $Prev = $TemplatesByLine[$Pos - 1]
      }

      if ($Pos -lt ($TemplatesByLine.Count - 1)) {
        $Next = $TemplatesByLine[$Pos + 1]
      }

      $SignatureRaw = "$Prev || $Template || $Next"
      $Sig = Short-Hash $SignatureRaw

      if (-not $Neighborhoods.ContainsKey($Sig)) {
        $Neighborhoods[$Sig] = [pscustomobject]@{
          signature = $Sig
          count = 0
          prev = $Prev
          current = $Template
          next = $Next
        }
      }

      $Neighborhoods[$Sig].count += 1
    }

    $NeighborhoodList = @($Neighborhoods.Values | Sort-Object count -Descending)
    $TopNeighborhood = $NeighborhoodList | Select-Object -First 1
    $RepeatedContextCount = 0

    foreach ($N in $NeighborhoodList) {
      if ($N.count -gt 1) {
        $RepeatedContextCount += 1
      }
    }

    $Rows += [pscustomobject]@{
      file = $File.Name
      bucket = $Bucket
      form_count = $Bucket
      neighborhood_variants = $NeighborhoodList.Count
      repeated_neighborhoods = $RepeatedContextCount
      top_neighborhood_count = $TopNeighborhood.count
      top_neighborhood_signature = $TopNeighborhood.signature
      template = $Template
      top_prev = $TopNeighborhood.prev
      top_next = $TopNeighborhood.next
    }
  }
}

$RowsTyped = foreach ($R in $Rows) {
  $RelationType = "context-mixed"

  if ($R.neighborhood_variants -eq 1 -and $R.repeated_neighborhoods -ge 1) {
    $RelationType = "context-locked"
  } elseif ($R.neighborhood_variants -gt 1 -and $R.repeated_neighborhoods -eq 0) {
    $RelationType = "context-split"
  } elseif ($R.neighborhood_variants -gt 1 -and $R.repeated_neighborhoods -gt 0) {
    $RelationType = "context-partial"
  }

  $R | Add-Member -NotePropertyName relation_type -NotePropertyValue $RelationType -Force
  $R
}

$CsvPath = Join-Path $OutDir "local_middle_relation_surface.csv"
$RowsTyped | Sort-Object file,bucket,relation_type,neighborhood_variants,template | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

$SummaryRows = @(
  $RowsTyped |
    Group-Object file,bucket,relation_type |
    ForEach-Object {
      $Parts = $_.Name -split ", "
      [pscustomobject]@{
        file = $Parts[0]
        bucket = $Parts[1]
        relation_type = $Parts[2]
        forms = $_.Count
      }
    } |
    Sort-Object file,bucket,relation_type
)

$SummaryHtmlRows = foreach ($S in $SummaryRows) {
@"
<tr>
  <td>$($S.file)</td>
  <td>$($S.bucket)</td>
  <td>$($S.relation_type)</td>
  <td>$($S.forms)</td>
</tr>
"@
}

$DisplayRows = @(
  $RowsTyped |
    Sort-Object file,bucket,relation_type,neighborhood_variants,top_neighborhood_count |
    Select-Object -First $MaxRows
)

$HtmlRows = foreach ($R in $DisplayRows) {
@"
<tr>
  <td>$($R.file)</td>
  <td>$($R.bucket)</td>
  <td>$($R.neighborhood_variants)</td>
  <td>$($R.repeated_neighborhoods)</td>
  <td>$($R.relation_type)</td>
  <td>$($R.top_neighborhood_count)</td>
  <td><code>$($R.template)</code></td>
  <td><code>$($R.top_prev)</code></td>
  <td><code>$($R.top_next)</code></td>
</tr>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Local Middle Relation Prototype V0</title>
<style>
body { background:#111; color:#eee; font-family:Segoe UI, Arial; padding:32px; }
.card { max-width:1280px; margin:auto; background:#1b1b1b; border-radius:18px; padding:28px; }
h1 { margin-top:0; }
.note { color:#aaa; line-height:1.6; margin-bottom:24px; }
table { width:100%; border-collapse:collapse; margin-top:14px; font-size:12px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; position:sticky; top:0; background:#1b1b1b; }
td { border-bottom:1px solid #333; padding:8px; vertical-align:top; }
code { color:#ddd; white-space:normal; }
.boundary { margin-top:34px; border-top:1px solid #333; padding-top:18px; color:#999; font-size:12px; line-height:1.7; }
</style>
</head>
<body>
<div class='card'>

<h1>Local Middle Relation Prototype V0</h1>

<div class='note'>
Sandbox prototype only. This page inspects local neighborhoods around weakly recurring forms.
Middle forms are templates occurring two, three, or four times in the file.
Neighborhood = previous normalized form + current middle form + next normalized form.
This exposes local structural relation only. It does not cluster, interpret, rank importance, infer anomaly, or claim lifecycle direction.
</div>

<h2>Local relation summary</h2>

<div class='note'>
Context-locked means the weakly recurring form repeats in the same local neighborhood.
Context-split means the same form repeats in different local neighborhoods.
Context-partial means mixed evidence.
These are structural relation types, not semantic categories.
</div>

<table>
  <tr>
    <th>file</th>
    <th>bucket</th>
    <th>relation type</th>
    <th>forms</th>
  </tr>
  $($SummaryHtmlRows -join "`r`n")
</table>

<h2>Representative local middle forms</h2>

<table>
  <tr>
    <th>file</th>
    <th>bucket</th>
    <th>neighborhood variants</th>
    <th>repeated neighborhoods</th>
    <th>relation type</th>
    <th>top neighborhood count</th>
    <th>middle form</th>
    <th>top previous form</th>
    <th>top next form</th>
  </tr>
  $($HtmlRows -join "`r`n")
</table>

<div class='boundary'>
Boundary: This prototype does not infer semantic family, anomaly, severity, importance, lifecycle, cause, or recommended action.
<br><br>
One-line hold: Weak recurrence is inspected through local neighborhoods before any grouping or compression upward.
<br><br>
CSV: $CsvPath
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "LOCAL_MIDDLE_RELATION_PROTOTYPE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== LOCAL MIDDLE RELATION PROTOTYPE COMPLETE ==="
Write-Host $HtmlPath
Write-Host $CsvPath

