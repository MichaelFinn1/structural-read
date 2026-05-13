param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Html-Encode {
  param([string]$Text)
  return [System.Net.WebUtility]::HtmlEncode($Text)
}

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Normalize-Template {
  param([string]$Line)

  $t = $Line
  $RequestShape = $null

  if ($t -match '"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+([^"\s]+)') {
    $Method = $Matches[1]
    $Target = $Matches[2]

    $Target = $Target -replace '\?.*','?<query>'
    $Target = $Target -replace '/\d+','/<num>'

    $RequestShape = "$Method $Target"
  }

  $t = $t -replace '\b\d{1,3}(\.\d{1,3}){3}\b','<ip>'
  $t = $t -replace '[A-Fa-f0-9]{8,}','<hex>'
  $t = $t -replace '\b\d+\b','<num>'
  $t = $t -replace '\s+',' '
  $t = $t.Trim()

  if ($RequestShape) {
    return "$RequestShape || $t"
  }

  return $t
}
function Get-PrefixFamily {
  param([string]$Template)

  if ($Template -match "^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+[^|]+") {
    return $Matches[0].Trim()
  }

  $Tokens = @($Template -split '\s+' | Where-Object { $_ -ne "" })

  if ($Tokens.Count -eq 0) {
    return "<empty>"
  }

  # Apache/request-like shape:
  # preserve HTTP method + request target when present.
  $Methods = @("GET","POST","PUT","PATCH","DELETE","HEAD","OPTIONS")

  for ($i = 0; $i -lt $Tokens.Count; $i++) {
    if ($Methods -contains $Tokens[$i]) {

      $Method = $Tokens[$i]

      $Target = "<none>"
      if ($i + 1 -lt $Tokens.Count) {
        $Target = $Tokens[$i + 1]
      }

      # Normalize long query strings lightly
      $Target = $Target -replace '\?.*','?<query>'

      # Collapse repeated numeric path segments
      $Target = $Target -replace '/\d+','/<num>'

      return "$Method $Target"
    }
  }

  # sshd-like shape: skip generic timestamp prefix if present.
  if ($Tokens.Count -ge 6 -and $Tokens[0] -match "^[A-Z][a-z][a-z]$" -and $Tokens[1] -eq "<num>") {
    return (($Tokens | Select-Object -Skip 2 -First 4) -join " ")
  }

  # Apache/error timestamp-like shape: keep a little more than date prefix.
  if ($Tokens.Count -ge 5 -and $Tokens[0] -match "^\[[A-Z][a-z][a-z]$") {
    return (($Tokens | Select-Object -First 5) -join " ")
  }

  # Default: first 4 tokens, not first 2, to avoid giant umbrella families.
  return (($Tokens | Select-Object -First ([math]::Min(4, $Tokens.Count))) -join " ")
}

function Get-TokenShapeBand {
  param([int]$TokenCount)

  if ($TokenCount -le 5) {
    return "short"
  }

  if ($TokenCount -le 14) {
    return "medium"
  }

  return "long"
}

function Get-ClassForCount {
  param([int]$Count)

  if ($Count -ge 5) {
    return "stable"
  }

  if ($Count -ge 2) {
    return "middle"
  }

  return "residual"
}

function Get-AttachmentType {
  param(
    [string]$PrevClass,
    [string]$NextClass
  )

  $NeighborClasses = @()
  if ($PrevClass -and $PrevClass -ne "boundary") { $NeighborClasses += $PrevClass }
  if ($NextClass -and $NextClass -ne "boundary") { $NeighborClasses += $NextClass }

  if ($NeighborClasses.Count -eq 0) {
    return "boundary"
  }

  $HasStable = $NeighborClasses -contains "stable"
  $HasMiddle = $NeighborClasses -contains "middle"
  $HasResidual = $NeighborClasses -contains "residual"

  if (($HasStable -and $HasMiddle) -or ($HasStable -and $HasResidual) -or ($HasMiddle -and $HasResidual)) {
    return "mixed"
  }

  if ($HasStable) {
    return "near_stable"
  }

  if ($HasMiddle) {
    return "near_middle"
  }

  if ($HasResidual) {
    return "near_residual"
  }

  return "boundary"
}

$OutDir = Join-Path $TerrainRoot "_surface_work\residual_shape_ecology_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' -and $_.FullName -notmatch '\\_surface_work\\' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$AllResidualRows = @()
$FileSummaries = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $RawLines = @(Get-Content $File.FullName -ErrorAction SilentlyContinue)
  $NormalizedLines = @()

  foreach ($Line in $RawLines) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }
    $NormalizedLines += (Normalize-Template $Line)
  }

  $Counts = @{}
  foreach ($T in $NormalizedLines) {
    if (-not $Counts.ContainsKey($T)) {
      $Counts[$T] = 0
    }

    $Counts[$T] += 1
  }

  $ResidualTemplates = @(
    $Counts.GetEnumerator() |
      Where-Object { [int]$_.Value -eq 1 } |
      ForEach-Object { $_.Key }
  )

  $ResidualSet = @{}
  foreach ($R in $ResidualTemplates) {
    $ResidualSet[$R] = $true
  }

  $ResidualRows = @()

  for ($i = 0; $i -lt $NormalizedLines.Count; $i++) {
    $Current = $NormalizedLines[$i]

    if (-not $ResidualSet.ContainsKey($Current)) {
      continue
    }

    $Prev = if ($i -gt 0) { $NormalizedLines[$i - 1] } else { "" }
    $Next = if ($i -lt ($NormalizedLines.Count - 1)) { $NormalizedLines[$i + 1] } else { "" }

    $PrevClass = if ($Prev -eq "") { "boundary" } else { Get-ClassForCount -Count ([int]$Counts[$Prev]) }
    $NextClass = if ($Next -eq "") { "boundary" } else { Get-ClassForCount -Count ([int]$Counts[$Next]) }

    $AttachmentType = Get-AttachmentType -PrevClass $PrevClass -NextClass $NextClass
    $TokenCount = @($Current -split '\s+' | Where-Object { $_ -ne "" }).Count
    $PrefixFamily = Get-PrefixFamily -Template $Current
    $TokenShapeBand = Get-TokenShapeBand -TokenCount $TokenCount

    $ResidualRows += [pscustomobject]@{
      file = $File.Name
      residual_form = $Current
      residual_prefix_family = $PrefixFamily
      token_count = $TokenCount
      token_shape_band = $TokenShapeBand
      prev_class = $PrevClass
      next_class = $NextClass
      residual_attachment_type = $AttachmentType
    }
  }

  $FamilySizes = @{}
  foreach ($R in $ResidualRows) {
    $K = $R.residual_prefix_family

    if (-not $FamilySizes.ContainsKey($K)) {
      $FamilySizes[$K] = 0
    }

    $FamilySizes[$K] += 1
  }

  $ResidualRowsWithSize = foreach ($R in $ResidualRows) {
    [pscustomobject]@{
      file = $R.file
      residual_form = $R.residual_form
      residual_prefix_family = $R.residual_prefix_family
      residual_prefix_family_size = $FamilySizes[$R.residual_prefix_family]
      token_count = $R.token_count
      token_shape_band = $R.token_shape_band
      prev_class = $R.prev_class
      next_class = $R.next_class
      residual_attachment_type = $R.residual_attachment_type
    }
  }

  $AllResidualRows += $ResidualRowsWithSize

  $ResidualCount = $ResidualRowsWithSize.Count
  $FamilyCount = @($FamilySizes.Keys).Count
  $LargestFamilySize = 0

  if ($FamilySizes.Count -gt 0) {
    $LargestFamilySize = ($FamilySizes.Values | Measure-Object -Maximum).Maximum
  }

  $LargestFamilyShare = if ($ResidualCount -gt 0) {
    [math]::Round(($LargestFamilySize / $ResidualCount) * 100, 1)
  } else {
    0
  }

  $AttachedCount = @(
    $ResidualRowsWithSize |
      Where-Object { $_.residual_attachment_type -in @("near_stable","near_middle","mixed") }
  ).Count

  $AttachmentRatio = if ($ResidualCount -gt 0) {
    [math]::Round(($AttachedCount / $ResidualCount) * 100, 1)
  } else {
    0
  }

  $FileSummaries += [pscustomobject]@{
    file = $File.Name
    residual_count = $ResidualCount
    residual_prefix_family_count = $FamilyCount
    largest_residual_family_size = $LargestFamilySize
    largest_residual_family_share = $LargestFamilyShare
    residual_attachment_ratio = $AttachmentRatio
  }
}

$SurfaceCsv = Join-Path $OutDir "residual_shape_surface.csv"
$DistributionCsv = Join-Path $OutDir "residual_shape_distribution.csv"
$SummaryCsv = Join-Path $OutDir "residual_shape_summary.csv"

$AllResidualRows |
  Sort-Object file,residual_prefix_family,residual_attachment_type |
  Export-Csv $SurfaceCsv -NoTypeInformation -Encoding UTF8

$DistributionRows = @()

$Groups = $AllResidualRows |
  Group-Object file,residual_prefix_family,token_shape_band,residual_attachment_type

foreach ($G in $Groups) {
  $First = $G.Group | Select-Object -First 1
  $FileCount = @($AllResidualRows | Where-Object { $_.file -eq $First.file }).Count

  $PctOfFileResidual = if ($FileCount -gt 0) {
    [math]::Round(($G.Count / $FileCount) * 100, 2)
  } else {
    0
  }

  $DistributionRows += [pscustomobject]@{
    file = $First.file
    residual_prefix_family = $First.residual_prefix_family
    token_shape_band = $First.token_shape_band
    residual_attachment_type = $First.residual_attachment_type
    forms = $G.Count
    pct_of_file_residual = $PctOfFileResidual
  }
}

$DistributionRows |
  Sort-Object file,@{Expression="forms";Descending=$true} |
  Export-Csv $DistributionCsv -NoTypeInformation -Encoding UTF8

$FileSummaries |
  Sort-Object file |
  Export-Csv $SummaryCsv -NoTypeInformation -Encoding UTF8

$SummaryRowsHtml = foreach ($S in ($FileSummaries | Sort-Object file)) {
@"
<tr>
  <td>$($S.file)</td>
  <td>$($S.residual_count)</td>
  <td>$($S.residual_prefix_family_count)</td>
  <td>$($S.largest_residual_family_size)</td>
  <td>$($S.largest_residual_family_share)%</td>
  <td>$($S.residual_attachment_ratio)%</td>
</tr>
"@
}

$FileCardsHtml = foreach ($S in ($FileSummaries | Sort-Object file)) {
  $TopFamilies = @(
    $DistributionRows |
      Where-Object { $_.file -eq $S.file } |
      Sort-Object {[int]$_.forms} -Descending |
      Select-Object -First 8
  )

  $FamilyRows = foreach ($F in $TopFamilies) {
    $Fam = Html-Encode $F.residual_prefix_family
@"
<tr>
  <td><code>$Fam</code></td>
  <td>$($F.token_shape_band)</td>
  <td>$($F.residual_attachment_type)</td>
  <td>$($F.forms)</td>
  <td>$($F.pct_of_file_residual)%</td>
</tr>
"@
  }

@"
<div class='file-card'>
  <h2>$($S.file)</h2>

  <div class='mini-metrics'>
    <div><span>residual forms</span><strong>$($S.residual_count)</strong></div>
    <div><span>rough prefix families</span><strong>$($S.residual_prefix_family_count)</strong></div>
    <div><span>largest family share</span><strong>$($S.largest_residual_family_share)%</strong></div>
    <div><span>attached ratio</span><strong>$($S.residual_attachment_ratio)%</strong></div>
  </div>

  <div class='subnote'>
    Top rough residual shape families. Grouping uses only normalized leading tokens and adjacency posture.
  </div>

  <table>
    <tr>
      <th>rough prefix family</th>
      <th>token band</th>
      <th>attachment</th>
      <th>forms</th>
      <th>share</th>
    </tr>
    $($FamilyRows -join "`r`n")
  </table>
</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Residual Shape Ecology V0</title>
<style>
body { background:#0b0f14; color:#eee; font-family:Segoe UI, Arial; padding:28px; }
.card { max-width:1300px; margin:auto; }
h1 { margin:0 0 8px 0; }
.note { color:#aaa; line-height:1.6; max-width:1080px; margin-bottom:22px; }
.file-card,.summary-card { background:#111820; border:1px solid #2b3a46; border-radius:12px; padding:18px; margin:18px 0; }
h2 { margin:0 0 14px 0; }
.mini-metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:14px; }
.mini-metrics div { background:#0d131a; border:1px solid #22313d; border-radius:9px; padding:12px; }
.mini-metrics span { display:block; color:#999; font-size:11px; }
.mini-metrics strong { font-size:22px; }
.subnote { color:#aaa; font-size:12px; margin:10px 0; }
table { width:100%; border-collapse:collapse; font-size:12px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #3a4650; padding:8px; }
td { border-bottom:1px solid #24313a; padding:8px; vertical-align:top; }
code { color:#ddd; white-space:normal; }
a { color:#8fd8f4; text-decoration:none; }
a:hover { text-decoration:underline; }
.boundary { margin-top:24px; color:#999; font-size:12px; line-height:1.7; border-top:1px solid #333; padding-top:16px; }
</style>
</head>
<body>
<div class='card'>

<h1>Residual Shape Ecology V0</h1>

<div class='note'>
Sandbox-only residual edge-field surface. This page asks whether singleton forms exhibit lightweight structural resemblance and local attachment behavior without recurrence persistence. It does not infer anomaly, severity, importance, cause, priority, or recommended action.
</div>

<div class='summary-card'>
  <h2>Residual ecology summary</h2>
  <table>
    <tr>
      <th>file</th>
      <th>residual forms</th>
      <th>rough prefix families</th>
      <th>largest family size</th>
      <th>largest family share</th>
      <th>attached ratio</th>
    </tr>
    $($SummaryRowsHtml -join "`r`n")
  </table>
</div>

$($FileCardsHtml -join "`r`n")

<div class='boundary'>
Boundary: Residual here means singleton forms only. Rough family grouping uses shallow normalized prefix structure and immediate-neighborhood attachment only. No semantic grouping, anomaly claim, severity claim, clustering, or action recommendation is made.
<br><br>
One-line hold: Residual becomes useful when it shows the shape of rarity, not just the amount of rarity.
<br><br>
Exports:
<ul>
  <li><a href='file:///$SurfaceCsv'>residual_shape_surface.csv</a></li>
  <li><a href='file:///$DistributionCsv'>residual_shape_distribution.csv</a></li>
  <li><a href='file:///$SummaryCsv'>residual_shape_summary.csv</a></li>
</ul>
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "RESIDUAL_SHAPE_ECOLOGY_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== RESIDUAL SHAPE ECOLOGY COMPLETE ==="
Write-Host $HtmlPath





