param(
  [Parameter(Mandatory=$true)]
  [string]$Path,

  [int]$MaxStable = 20,
  [int]$MaxMiddle = 16,
  [int]$MaxResidual = 16
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)
  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

function Normalize-Template {
  param([string]$Line)

  $t = $Line
  $t = $t -replace '\b\d{1,3}(\.\d{1,3}){3}\b','<ip>'
  $t = $t -replace '[A-Fa-f0-9]{8,}','<hex>'
  $t = $t -replace '\b\d+\b','<num>'
  $t = $t -replace '\s+',' '

  return $t.Trim()
}

function Safe-Name {
  param([string]$Name)

  $s = $Name -replace '[^A-Za-z0-9_.-]', '_'
  return $s
}

$LogFiles = @(
  Get-ChildItem $Path -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$OutDir = Join-Path $Path "_surface_work\log_structure_file_detail_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$BackPath = Join-Path $Path "_surface_work\log_structure_file_texture_v0\LOG_STRUCTURE_FILE_TEXTURE_PROFILE_BARS_V0.html"

$IndexRows = @()

foreach ($f in $LogFiles) {
  Write-Host "Building detail for $($f.Name)..."

  $Counts = @{}
  $Lines = Get-Content $f.FullName -ErrorAction SilentlyContinue

  foreach ($line in $Lines) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }

    $t = Normalize-Template $line

    if (-not $Counts.ContainsKey($t)) {
      $Counts[$t] = 0
    }

    $Counts[$t] += 1
  }

  $TotalLines = ($Counts.Values | Measure-Object -Sum).Sum
  if (-not $TotalLines) { $TotalLines = 0 }

  $Templates = @(
    $Counts.GetEnumerator() |
      ForEach-Object {
        $class =
          if ($_.Value -ge 5) { "stable" }
          elseif ($_.Value -ge 2) { "middle" }
          else { "residual" }

        [pscustomobject]@{
          template = $_.Key
          count = [int]$_.Value
          class = $class
        }
      } |
      Sort-Object count -Descending
  )

  $StableRows = @($Templates | Where-Object { $_.class -eq "stable" })
  $MiddleRows = @($Templates | Where-Object { $_.class -eq "middle" })
  $ResidualRows = @($Templates | Where-Object { $_.class -eq "residual" })

  $StableLines = ($StableRows | Measure-Object -Property count -Sum).Sum
  $MiddleLines = ($MiddleRows | Measure-Object -Property count -Sum).Sum
  $ResidualLines = ($ResidualRows | Measure-Object -Property count -Sum).Sum

  if (-not $StableLines) { $StableLines = 0 }
  if (-not $MiddleLines) { $MiddleLines = 0 }
  if (-not $ResidualLines) { $ResidualLines = 0 }

  $TemplateCount = $Templates.Count

  $Top10Lines = ($Templates | Select-Object -First 10 | Measure-Object -Property count -Sum).Sum
  if (-not $Top10Lines) { $Top10Lines = 0 }

  $StablePct = if ($TotalLines -gt 0) { [math]::Round(($StableLines / $TotalLines) * 100,1) } else { 0 }
  $MiddlePct = if ($TotalLines -gt 0) { [math]::Round(($MiddleLines / $TotalLines) * 100,1) } else { 0 }
  $ResidualPct = if ($TotalLines -gt 0) { [math]::Round(($ResidualLines / $TotalLines) * 100,1) } else { 0 }
  $Top10Share = if ($TotalLines -gt 0) { [math]::Round(($Top10Lines / $TotalLines) * 100,1) } else { 0 }
  $Density = if ($TotalLines -gt 0) { [math]::Round(($TemplateCount / $TotalLines) * 1000,1) } else { 0 }

  $Safe = Safe-Name $f.Name
  $CsvPath = Join-Path $OutDir ("file_detail_" + $Safe + ".csv")
  $Templates | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

  function Make-Rows {
    param(
      [object[]]$Rows,
      [int]$Take
    )

    $out = foreach ($r in ($Rows | Select-Object -First $Take)) {
@"
<tr>
  <td>$($r.count)</td>
  <td><code>$($r.template)</code></td>
</tr>
"@
    }

    return ($out -join "`r`n")
  }

  $StableHtml = Make-Rows -Rows $StableRows -Take $MaxStable
  $MiddleHtml = Make-Rows -Rows $MiddleRows -Take $MaxMiddle
  $ResidualHtml = Make-Rows -Rows $ResidualRows -Take $MaxResidual

  $HtmlPath = Join-Path $OutDir ("LOG_STRUCTURE_FILE_DETAIL_" + $Safe + ".html")

  $Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>File Detail - $($f.Name)</title>
<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  margin:0;
  padding:30px;
}
.card {
  max-width:1180px;
  margin:auto;
  background:#1b1b1b;
  border-radius:16px;
  padding:28px;
}
a { color:#8fd8f4; text-decoration:none; }
a:hover { text-decoration:underline; }
h1 { margin-top:0; }
.metahead { color:#aaa; margin-bottom:22px; }
.metrics {
  display:grid;
  grid-template-columns: repeat(6, 1fr);
  gap:10px;
  margin-bottom:24px;
}
.metric {
  background:#202020;
  border-radius:10px;
  padding:12px;
}
.metric div { color:#999; font-size:11px; }
.metric strong { font-size:22px; }
.band {
  width:100%;
  height:30px;
  display:flex;
  overflow:hidden;
  border-radius:8px;
  background:#222;
  margin:18px 0 8px 0;
}
.stable { background:#5bc0eb; width:$StablePct%; }
.middle { background:#9bc53d; width:$MiddlePct%; }
.residual { background:#e55934; width:$ResidualPct%; }
.shares { color:#aaa; font-size:12px; margin-bottom:26px; }
.section {
  margin-top:28px;
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
  color:#999;
  font-size:12px;
  line-height:1.7;
  border-top:1px solid #333;
  padding-top:18px;
}
</style>
</head>
<body>
<div class='card'>

<p><a href='file:///$BackPath'>← Back to file profile bars</a></p>

<h1>File Detail Surface</h1>

<div class='metahead'>
$f
</div>

<div class='metrics'>
  <div class='metric'><div>Lines</div><strong>$TotalLines</strong></div>
  <div class='metric'><div>Templates</div><strong>$TemplateCount</strong></div>
  <div class='metric'><div>Stable</div><strong>$StablePct%</strong></div>
  <div class='metric'><div>Middle</div><strong>$MiddlePct%</strong></div>
  <div class='metric'><div>Residual</div><strong>$ResidualPct%</strong></div>
  <div class='metric'><div>Top10</div><strong>$Top10Share%</strong></div>
</div>

<div class='band'>
  <div class='stable'></div>
  <div class='middle'></div>
  <div class='residual'></div>
</div>

<div class='shares'>
stable=$StablePct% / middle=$MiddlePct% / residual=$ResidualPct% / templates per 1k lines=$Density
</div>

<div class='section'>
  <h2>Stable structures</h2>
  <table>
    <tr><th>count</th><th>template</th></tr>
    $StableHtml
  </table>
</div>

<div class='section'>
  <h2>Middle recurrence texture</h2>
  <table>
    <tr><th>count</th><th>template</th></tr>
    $MiddleHtml
  </table>
</div>

<div class='section'>
  <h2>Residual samples</h2>
  <table>
    <tr><th>count</th><th>template</th></tr>
    $ResidualHtml
  </table>
</div>

<div class='section'>
  <h2>Exports</h2>
  <p><a href='file:///$CsvPath'>Open file detail CSV</a></p>
</div>

<div class='boundary'>
Boundary: This file detail surface presents local recurrence structure for one file. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.
<br><br>
One-line hold: Enter local structure, preserve global orientation, return without interpretation.
</div>

</div>
</body>
</html>
"@

  Write-AtomicText -Path $HtmlPath -Text $Html

  $IndexRows += [pscustomobject]@{
    file_name = $f.Name
    detail_html = $HtmlPath
    detail_csv = $CsvPath
  }
}

$IndexPath = Join-Path $OutDir "file_detail_index.csv"
$IndexRows | Export-Csv $IndexPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "=== FILE DETAIL SURFACES COMPLETE ==="
Write-Host $OutDir
