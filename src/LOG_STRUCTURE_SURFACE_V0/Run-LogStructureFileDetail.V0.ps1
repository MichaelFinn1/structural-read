param(
  [Parameter(Mandatory=$true)]
  [string]$Path,

  [int]$MaxStable = 20,
  [int]$MaxMiddle = 16,
  [int]$MaxResidual = 24
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
  return ($Name -replace '[^A-Za-z0-9_.-]', '_')
}

function Make-TemplateRows {
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

$LogFiles = @(
  Get-ChildItem $Path -Recurse -File |
    Where-Object { $_.Extension -match '\.(log|txt)$' }
)

if ($LogFiles.Count -eq 0) {
  throw "No log-like files found."
}

$OutDir = Join-Path $Path "_surface_work\log_structure_file_detail_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$BackPath = Join-Path $Path "_surface_work\structural_read_profile_sheet_v0\STRUCTURAL_READ_PROFILE_SHEET_V0.html"

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

  $MaxStableCount = ($StableRows | Measure-Object -Property count -Maximum).Maximum
  if (-not $MaxStableCount -or $MaxStableCount -eq 0) { $MaxStableCount = 1 }

  $GlobalStableMax = $MaxStableCount
  foreach ($OtherFile in $LogFiles) {
    $OtherCounts = @{}
    $OtherLines = Get-Content $OtherFile.FullName -ErrorAction SilentlyContinue

    foreach ($OtherLine in $OtherLines) {
      if ([string]::IsNullOrWhiteSpace($OtherLine)) { continue }
      $OtherTemplate = Normalize-Template $OtherLine

      if (-not $OtherCounts.ContainsKey($OtherTemplate)) {
        $OtherCounts[$OtherTemplate] = 0
      }

      $OtherCounts[$OtherTemplate] += 1
    }

    $OtherMax = ($OtherCounts.Values | Measure-Object -Maximum).Maximum
    if ($OtherMax -and $OtherMax -gt $GlobalStableMax) {
      $GlobalStableMax = $OtherMax
    }
  }

  $StableVisual = foreach ($r in ($StableRows | Select-Object -First $MaxStable)) {
    $w = [math]::Max(3, [math]::Round(($r.count / $MaxStableCount) * 100))
    $relief = [math]::Max(0.12, ($r.count / $GlobalStableMax))
    $glow = [math]::Round(0.25 + ($relief * 0.65), 3)
    $shade = [math]::Round(45 + ($relief * 145))
    $blur = [math]::Round($relief * 12)

@"
<div class='stable-row'>
  <div class='stable-count'>$($r.count)</div>
  <div class='stable-track'>
    <div class='stable-fill' style='width:$w%; opacity:$glow; background:linear-gradient(to right, rgb(35,$shade,255), rgb(110,245,255)); box-shadow:0 0 ${blur}px rgba(90,220,255,$glow);'></div>
  </div>
  <div class='stable-text'><code>$($r.template)</code></div>
</div>
"@
  }

  $MiddleBucketObjects = @(
    [pscustomobject]@{ name = "2"; rows = @($MiddleRows | Where-Object { $_.count -eq 2 }) },
    [pscustomobject]@{ name = "3_to_4"; rows = @($MiddleRows | Where-Object { $_.count -ge 3 -and $_.count -le 4 }) }
  )

  $MiddleBucketHtml = foreach ($b in $MiddleBucketObjects) {
    if ($b.rows.Count -gt 0) {
      $lines = ($b.rows | Measure-Object -Property count -Sum).Sum
      $share = if ($MiddleLines -gt 0) { [math]::Round(($lines / $MiddleLines) * 100,1) } else { 0 }
      $width = [math]::Max(4, $share)
@"
<div class='bucket-row'>
  <div class='bucket-name'>$($b.name)</div>
  <div class='bucket-track'><div class='bucket-fill' style='width:$width%'></div></div>
  <div class='bucket-meta'>$($b.rows.Count) templates / $lines lines / $share%</div>
</div>
"@
    }
  }

  $MiddleSampleHtml = foreach ($r in ($MiddleRows | Select-Object -First $MaxMiddle)) {
@"
<div class='sample-line'><span>$($r.count)</span><code>$($r.template)</code></div>
"@
  }

  $ResidualDots = foreach ($r in ($ResidualRows | Select-Object -First $MaxResidual)) {
@"
<div class='res-dot' title='$($r.template)'></div>
"@
  }

  $ResidualSampleHtml = foreach ($r in ($ResidualRows | Select-Object -First $MaxResidual)) {
@"
<div class='sample-line'><span>$($r.count)</span><code>$($r.template)</code></div>
"@
  }

  $StableHtml = Make-TemplateRows -Rows $StableRows -Take $MaxStable
  $MiddleHtml = Make-TemplateRows -Rows $MiddleRows -Take $MaxMiddle
  $ResidualHtml = Make-TemplateRows -Rows $ResidualRows -Take $MaxResidual

  $Safe = Safe-Name $f.Name
  $CsvPath = Join-Path $OutDir ("file_detail_" + $Safe + ".csv")
  $Templates | Export-Csv $CsvPath -NoTypeInformation -Encoding UTF8

  $HtmlPath = Join-Path $OutDir ("LOG_STRUCTURE_FILE_DETAIL_" + $Safe + ".html")

  $Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>File Detail - $($f.Name)</title>
<style>
body { background:#111; color:#eee; font-family:Segoe UI, Arial; margin:0; padding:30px; }
.card { max-width:1180px; margin:auto; background:#1b1b1b; border-radius:16px; padding:28px; }
a { color:#8fd8f4; text-decoration:none; }
a:hover { text-decoration:underline; }
h1 { margin-top:0; }
.metahead { color:#aaa; margin-bottom:22px; }
.metrics { display:grid; grid-template-columns: repeat(6, 1fr); gap:10px; margin-bottom:24px; }
.metric { background:#202020; border-radius:10px; padding:12px; }
.metric div { color:#999; font-size:11px; }
.metric strong { font-size:22px; }
.band { width:100%; height:30px; display:flex; overflow:hidden; border-radius:8px; background:#222; margin:18px 0 8px 0; }
.stable { background:#5bc0eb; width:$StablePct%; }
.middle { background:#9bc53d; width:$MiddlePct%; }
.residual { background:#e55934; width:$ResidualPct%; }
.shares { color:#aaa; font-size:12px; margin-bottom:26px; }
.section { margin-top:32px; }
.visual-note { color:#aaa; font-size:12px; margin-bottom:14px; }

.stable-row { display:grid; grid-template-columns:70px 170px 1fr; gap:10px; align-items:center; margin-bottom:8px; }
.stable-count { color:#aaa; font-size:12px; }
.stable-track {
  height:12px;
  background:linear-gradient(to right, rgba(28,38,68,0.95), rgba(16,22,38,0.92));
  border-radius:8px;
  overflow:hidden;
}
.stable-fill {
  height:100%;
  border-radius:8px;
}
.stable-text { font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

.bucket-row { display:grid; grid-template-columns:70px 220px 1fr; gap:10px; align-items:center; margin-bottom:10px; }
.bucket-name { color:#aaa; font-size:12px; }
.bucket-track { height:18px; background:#252525; border-radius:8px; overflow:hidden; }
.bucket-fill { height:100%; background:repeating-linear-gradient(90deg,#9bc53d 0px,#9bc53d 7px,#b7da64 7px,#b7da64 10px); }
.bucket-meta { color:#bbb; font-size:12px; }

.res-field { display:flex; flex-wrap:wrap; gap:7px; max-width:650px; margin-bottom:16px; }
.res-dot { width:10px; height:10px; background:#e55934; border-radius:50%; opacity:.75; }

.sample-line { display:grid; grid-template-columns:40px 1fr; gap:10px; margin-bottom:6px; font-size:12px; }
.sample-line span { color:#aaa; }
.sample-line code { color:#ddd; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

table { width:100%; border-collapse:collapse; margin-top:10px; font-size:12px; }
th { color:#aaa; text-align:left; border-bottom:1px solid #444; padding:8px; }
td { border-bottom:1px solid #333; padding:8px; vertical-align:top; }
code { color:#ddd; white-space:normal; }
details { margin-top:16px; }
summary { cursor:pointer; color:#8fd8f4; margin-bottom:8px; }
.boundary { margin-top:34px; color:#999; font-size:12px; line-height:1.7; border-top:1px solid #333; padding-top:18px; }
</style>
</head>
<body>
<div class='card'>

<p><a href='file:///$BackPath'>← Back to Structural Read Profile Sheet</a></p>

<h1>File Detail Surface</h1>
<div class='metahead'>$($f.Name)</div>

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

<div class='section' id='stable'>
  <h2>Stable structures</h2>
  <div class='visual-note'>Ranked recurrence magnitude. Longer lines indicate stronger repetition inside this file; brighter relief indicates strength relative to the terrain-wide stable field.</div>
  $($StableVisual -join "`r`n")

  <details>
    <summary>Open stable table</summary>
    <table>
      <tr><th>count</th><th>template</th></tr>
      $StableHtml
    </table>
  </details>
</div>

<div class='section' id='middle'>
  <h2>Middle recurrence texture</h2>
  <div class='visual-note'>Bucket texture for low-count recurrence. “2” means templates occurring twice; “3_to_4” means templates occurring three or four times. This shows distribution texture, not importance.</div>
  $($MiddleBucketHtml -join "`r`n")

  <div class='visual-note'>Representative middle samples</div>
  $($MiddleSampleHtml -join "`r`n")

  <details>
    <summary>Open middle table</summary>
    <table>
      <tr><th>count</th><th>template</th></tr>
      $MiddleHtml
    </table>
  </details>
</div>

<div class='section' id='residual'>
  <h2>Residual samples</h2>
  <div class='visual-note'>Sparse edge field. Each dot represents one displayed residual sample; residual templates occur once in this file.</div>
  <div class='res-field'>
    $($ResidualDots -join "`r`n")
  </div>

  $($ResidualSampleHtml -join "`r`n")

  <details>
    <summary>Open residual table</summary>
    <table>
      <tr><th>count</th><th>template</th></tr>
      $ResidualHtml
    </table>
  </details>
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


