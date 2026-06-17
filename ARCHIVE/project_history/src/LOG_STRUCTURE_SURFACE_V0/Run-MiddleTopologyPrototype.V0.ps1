param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot,

  [int]$MaxExamplesPerBucket = 12
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

function Write-AtomicText {
  param([string]$Path,[string]$Text)

  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Make-BucketRows {
  param(
    [object[]]$Rows,
    [int]$Take
  )

  $Out = foreach ($r in ($Rows | Select-Object -First $Take)) {
@"
<tr>
  <td>$($r.count)</td>
  <td><code>$($r.template)</code></td>
</tr>
"@
  }

  return ($Out -join "`r`n")
}

$OutDir = Join-Path $TerrainRoot "_surface_work\middle_topology_prototype_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$LogFiles = @(
  Get-ChildItem $TerrainRoot -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$Profiles = @()

foreach ($File in $LogFiles) {
  Write-Host "Reading $($File.Name)..."

  $Counts = @{}
  $Lines = Get-Content $File.FullName -ErrorAction SilentlyContinue

  foreach ($Line in $Lines) {
    if ([string]::IsNullOrWhiteSpace($Line)) { continue }

    $Template = Normalize-Template $Line

    if (-not $Counts.ContainsKey($Template)) {
      $Counts[$Template] = 0
    }

    $Counts[$Template] += 1
  }

  $Templates = @(
    $Counts.GetEnumerator() |
      ForEach-Object {
        [pscustomobject]@{
          template = $_.Key
          count = [int]$_.Value
        }
      }
  )

  $Bucket2 = @($Templates | Where-Object { $_.count -eq 2 } | Sort-Object template)
  $Bucket3 = @($Templates | Where-Object { $_.count -eq 3 } | Sort-Object template)
  $Bucket4 = @($Templates | Where-Object { $_.count -eq 4 } | Sort-Object template)

  $MiddleTemplates = $Bucket2.Count + $Bucket3.Count + $Bucket4.Count
  $Lines2 = ($Bucket2 | Measure-Object -Property count -Sum).Sum
  $Lines3 = ($Bucket3 | Measure-Object -Property count -Sum).Sum
  $Lines4 = ($Bucket4 | Measure-Object -Property count -Sum).Sum

  if (-not $Lines2) { $Lines2 = 0 }
  if (-not $Lines3) { $Lines3 = 0 }
  if (-not $Lines4) { $Lines4 = 0 }

  $MiddleLines = $Lines2 + $Lines3 + $Lines4

  $Profiles += [pscustomobject]@{
    file = $File.Name
    middle_templates = $MiddleTemplates
    middle_lines = $MiddleLines
    count2_templates = $Bucket2.Count
    count3_templates = $Bucket3.Count
    count4_templates = $Bucket4.Count
    count2_lines = $Lines2
    count3_lines = $Lines3
    count4_lines = $Lines4
    bucket2 = $Bucket2
    bucket3 = $Bucket3
    bucket4 = $Bucket4
  }
}

$ComparisonRows = foreach ($P in $Profiles) {
@"
<tr>
  <td>$($P.file)</td>
  <td>$($P.middle_templates)</td>
  <td>$($P.middle_lines)</td>
  <td>$($P.count2_templates)</td>
  <td>$($P.count3_templates)</td>
  <td>$($P.count4_templates)</td>
  <td>$($P.count2_lines)</td>
  <td>$($P.count3_lines)</td>
  <td>$($P.count4_lines)</td>
</tr>
"@
}

$RowsHtml = foreach ($P in $Profiles) {
  $TotalMiddleTemplates = $P.middle_templates
  if ($TotalMiddleTemplates -eq 0) { $TotalMiddleTemplates = 1 }

  $W2 = [math]::Round(($P.count2_templates / $TotalMiddleTemplates) * 100, 2)
  $W3 = [math]::Round(($P.count3_templates / $TotalMiddleTemplates) * 100, 2)
  $W4 = [math]::Round(($P.count4_templates / $TotalMiddleTemplates) * 100, 2)

  if ($P.middle_templates -eq 0) {
    $W2 = 0
    $W3 = 0
    $W4 = 0
  }

  $Rows2 = Make-BucketRows -Rows $P.bucket2 -Take $MaxExamplesPerBucket
  $Rows3 = Make-BucketRows -Rows $P.bucket3 -Take $MaxExamplesPerBucket
  $Rows4 = Make-BucketRows -Rows $P.bucket4 -Take $MaxExamplesPerBucket

@"
<div class='file-card'>
  <h2>$($P.file)</h2>

  <div class='metrics'>
    <div><span>middle templates</span><strong>$($P.middle_templates)</strong></div>
    <div><span>middle lines</span><strong>$($P.middle_lines)</strong></div>
    <div><span>count=2 templates</span><strong>$($P.count2_templates)</strong></div>
    <div><span>count=3 templates</span><strong>$($P.count3_templates)</strong></div>
    <div><span>count=4 templates</span><strong>$($P.count4_templates)</strong></div>
  </div>

  <div class='label'>middle bucket ecology strip</div>
  <div class='note small-note'>
    Width shows template population share inside the middle layer. Count=2 is residual-near; count=4 is stable-near. This is a structural guide, not a lifecycle claim.
  </div>

  <div class='middle-strip'>
    <div class='bucket b2' style='width:$W2%'>
      <span>2</span>
    </div>
    <div class='bucket b3' style='width:$W3%'>
      <span>3</span>
    </div>
    <div class='bucket b4' style='width:$W4%'>
      <span>4</span>
    </div>
  </div>

  <div class='bucket-grid'>
    <div class='bucket-card'>
      <h3>count=2</h3>
      <div class='bucket-meta'>$($P.count2_templates) templates / $($P.count2_lines) lines</div>
      <details open>
        <summary>Representative templates</summary>
        <table>
          <tr><th>count</th><th>template</th></tr>
          $Rows2
        </table>
      </details>
    </div>

    <div class='bucket-card'>
      <h3>count=3</h3>
      <div class='bucket-meta'>$($P.count3_templates) templates / $($P.count3_lines) lines</div>
      <details open>
        <summary>Representative templates</summary>
        <table>
          <tr><th>count</th><th>template</th></tr>
          $Rows3
        </table>
      </details>
    </div>

    <div class='bucket-card'>
      <h3>count=4</h3>
      <div class='bucket-meta'>$($P.count4_templates) templates / $($P.count4_lines) lines</div>
      <details open>
        <summary>Representative templates</summary>
        <table>
          <tr><th>count</th><th>template</th></tr>
          $Rows4
        </table>
      </details>
    </div>
  </div>
</div>
"@
}

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Middle Topology Prototype V0</title>
<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  padding:32px;
}

.card {
  max-width:1260px;
  margin:auto;
  background:#1b1b1b;
  border-radius:18px;
  padding:28px;
}

h1 { margin-top:0; }
h2 { margin-bottom:12px; }
h3 { margin:0 0 8px 0; }

.note {
  color:#aaa;
  line-height:1.6;
  margin-bottom:26px;
}

.small-note {
  font-size:12px;
  margin-bottom:12px;
}

.comparison-block {
  background:#202020;
  border:1px solid #333;
  border-radius:16px;
  padding:22px;
  margin:24px 0;
}

.file-card {
  background:#202020;
  border:1px solid #333;
  border-radius:16px;
  padding:22px;
  margin:24px 0;
}

.metrics {
  display:grid;
  grid-template-columns:repeat(5, 1fr);
  gap:10px;
  margin-bottom:18px;
}

.metrics div {
  background:#171717;
  border-radius:10px;
  padding:12px;
}

.metrics span {
  display:block;
  color:#999;
  font-size:11px;
}

.metrics strong {
  font-size:22px;
}

.label {
  color:#aaa;
  font-size:12px;
  margin:18px 0 8px 0;
}

.middle-strip {
  height:46px;
  display:flex;
  overflow:hidden;
  border-radius:14px;
  background:#14200e;
  border:1px solid #2f4a20;
  margin-bottom:20px;
}

.bucket {
  height:100%;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  min-width:0;
}

.bucket span {
  font-size:13px;
  color:#10200a;
  font-weight:700;
}

.b2 {
  background:repeating-linear-gradient(
    90deg,
    rgba(155,197,61,.38) 0px,
    rgba(155,197,61,.38) 6px,
    rgba(35,55,18,.25) 6px,
    rgba(35,55,18,.25) 13px
  );
}

.b3 {
  background:repeating-linear-gradient(
    90deg,
    rgba(170,215,70,.62) 0px,
    rgba(170,215,70,.62) 9px,
    rgba(35,55,18,.28) 9px,
    rgba(35,55,18,.28) 14px
  );
}

.b4 {
  background:repeating-linear-gradient(
    90deg,
    rgba(200,240,95,.86) 0px,
    rgba(200,240,95,.86) 12px,
    rgba(45,75,20,.32) 12px,
    rgba(45,75,20,.32) 16px
  );
}

.bucket-grid {
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:14px;
}

.bucket-card {
  background:#171717;
  border:1px solid #303828;
  border-radius:14px;
  padding:14px;
  min-width:0;
}

.bucket-meta {
  color:#aaa;
  font-size:12px;
  margin-bottom:10px;
}

details {
  margin-top:10px;
}

summary {
  cursor:pointer;
  color:#b7da64;
  margin-bottom:8px;
}

table {
  width:100%;
  border-collapse:collapse;
  margin-top:10px;
  font-size:12px;
}

th {
  color:#aaa;
  text-align:left;
  border-bottom:1px solid #444;
  padding:8px;
}

td {
  border-bottom:1px solid #333;
  padding:8px;
  vertical-align:top;
}

code {
  color:#ddd;
  white-space:normal;
}

.boundary {
  margin-top:34px;
  border-top:1px solid #333;
  padding-top:18px;
  color:#999;
  font-size:12px;
  line-height:1.7;
}
</style>
</head>
<body>
<div class='card'>

<h1>Middle Topology Prototype V0</h1>

<div class='note'>
Sandbox prototype only. This page studies weak recurrence ecology before any clustering, semantic grouping, or compression upward.
Middle means templates occurring two, three, or four times. Count=2 is closest to residual; count=4 is closest to stable under the current threshold.
This page shows recurrence population structure, not meaning.
</div>

<div class='comparison-block'>
  <h2>Middle bucket comparison</h2>
  <div class='note small-note'>
    Comparison table for weak recurrence population only. These are structural measures: bucket population and line mass.
  </div>
  <table>
    <tr>
      <th>file</th>
      <th>middle templates</th>
      <th>middle lines</th>
      <th>count2 templates</th>
      <th>count3 templates</th>
      <th>count4 templates</th>
      <th>count2 lines</th>
      <th>count3 lines</th>
      <th>count4 lines</th>
    </tr>
    $($ComparisonRows -join "`r`n")
  </table>
</div>

$($RowsHtml -join "`r`n")

<div class='boundary'>
Boundary: This prototype does not infer anomaly, severity, importance, cause, lifecycle transition, semantic family, or recommended action.
<br><br>
One-line hold: Stable revealed recurrence cartography; middle opens weak recurrence ecology.
</div>

</div>
</body>
</html>
"@

$HtmlPath = Join-Path $OutDir "MIDDLE_TOPOLOGY_PROTOTYPE_V0.html"
Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== MIDDLE TOPOLOGY PROTOTYPE COMPLETE ==="
Write-Host $HtmlPath
