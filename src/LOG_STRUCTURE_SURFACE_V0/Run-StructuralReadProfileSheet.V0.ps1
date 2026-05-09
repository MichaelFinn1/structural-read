param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

function Write-AtomicText {
  param([string]$Path,[string]$Text)
  $Tmp = "$Path.tmp"
  $Text | Set-Content $Tmp -Encoding UTF8
  Move-Item -Force $Tmp $Path
}

$LogSurfaceRoot = Join-Path $TerrainRoot "_surface_work\log_structure_v0"
$FileTextureRoot = Join-Path $TerrainRoot "_surface_work\log_structure_file_texture_v0"
$FileProfileRoot = Join-Path $TerrainRoot "_surface_work\log_structure_file_profiles_v0"

$ReadPath = Join-Path $LogSurfaceRoot "LOG_STRUCTURE_READ_V0.md"
$ClassSummaryPath = Join-Path $LogSurfaceRoot "log_class_summary.csv"
$TemplateSurfacePath = Join-Path $LogSurfaceRoot "log_template_surface.csv"
$TextureCsvPath = Join-Path $FileTextureRoot "log_file_texture_profile.csv"
$ProfileCsvPath = Join-Path $FileProfileRoot "log_file_profile_surface.csv"
$TextureHtmlPath = Join-Path $FileTextureRoot "LOG_STRUCTURE_FILE_TEXTURE_PROFILE_BARS_V0.html"

if (-not (Test-Path $ReadPath)) {
  throw "Missing LOG_STRUCTURE_READ_V0.md. Run Run-LogStructureSurface.V0.ps1 first."
}

if (-not (Test-Path $TextureCsvPath)) {
  throw "Missing log_file_texture_profile.csv. Run Run-LogStructureFileTextureBars.V0.ps1 first."
}

$ReadLines = Get-Content $ReadPath

function Read-Field {
  param([string]$Name)

  $pattern = "^- " + [regex]::Escape($Name) + ": "
  $line = $ReadLines | Where-Object { $_ -match $pattern } | Select-Object -First 1

  if (-not $line) { return "" }

  return ($line -replace $pattern, "").Trim()
}

$LogFilesSeen = Read-Field "log_files_seen"
$LinesIndexed = Read-Field "lines_indexed"
$StableLines = Read-Field "stable_line_count"
$MiddleLines = Read-Field "middle_line_count"
$ResidualLines = Read-Field "residual_line_count"
$TemplateCount = Read-Field "template_count"

$FileRows = Import-Csv $TextureCsvPath
$FileCount = $FileRows.Count

$TopVolume = $FileRows | Sort-Object {[int]$_.lines} -Descending | Select-Object -First 1
$TopResidual = $FileRows | Sort-Object {[double]$_.residual_pct} -Descending | Select-Object -First 1
$TopDensity = $FileRows | Sort-Object {[double]$_.templates_per_1000_lines} -Descending | Select-Object -First 1
$TopConcentration = $FileRows | Sort-Object {[double]$_.top10_share_pct} -Descending | Select-Object -First 1

$FileSummaryRows = foreach ($f in ($FileRows | Sort-Object {[int]$_.lines} -Descending)) {
@"
<tr>
  <td>$($f.file_name)</td>
  <td>$($f.lines)</td>
  <td>$($f.templates)</td>
  <td>$($f.stable_pct)%</td>
  <td>$($f.middle_pct)%</td>
  <td>$($f.residual_pct)%</td>
  <td>$($f.top10_share_pct)%</td>
  <td>$($f.templates_per_1000_lines)</td>
</tr>
"@
}

$OutDir = Join-Path $TerrainRoot "_surface_work\structural_read_profile_sheet_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$HtmlPath = Join-Path $OutDir "STRUCTURAL_READ_PROFILE_SHEET_V0.html"

$TextureRelNote =
  if (Test-Path $TextureHtmlPath) {
    "Available: $TextureHtmlPath"
  } else {
    "Not available"
  }

$Html = @"
<html>
<head>
<meta charset='utf-8'>
<title>Structural Read Profile Sheet</title>

<style>
body {
  background:#111;
  color:#eee;
  font-family:Segoe UI, Arial;
  margin:0;
  padding:30px;
}

.sheet {
  max-width:1180px;
  margin:auto;
  background:#1b1b1b;
  border-radius:16px;
  padding:28px;
}

h1 {
  margin-top:0;
  margin-bottom:8px;
}

.subtitle {
  color:#aaa;
  margin-bottom:28px;
}

.flow {
  display:grid;
  grid-template-columns: repeat(4, 1fr);
  gap:14px;
  margin-bottom:30px;
}

.step {
  background:#242424;
  border-radius:12px;
  padding:16px;
  min-height:145px;
}

.step h2 {
  font-size:16px;
  margin:0 0 10px 0;
}

.step p {
  color:#bbb;
  font-size:13px;
  line-height:1.5;
}

.metrics {
  display:grid;
  grid-template-columns: repeat(6, 1fr);
  gap:10px;
  margin-bottom:30px;
}

.metric {
  background:#202020;
  border-radius:10px;
  padding:12px;
}

.metric div {
  color:#999;
  font-size:11px;
}

.metric strong {
  font-size:22px;
}

.section {
  margin-top:30px;
}

.callouts {
  display:grid;
  grid-template-columns: repeat(4, 1fr);
  gap:12px;
  margin-top:12px;
}

.callout {
  background:#202020;
  border-radius:10px;
  padding:12px;
}

.callout div {
  color:#999;
  font-size:11px;
  margin-bottom:5px;
}

.callout strong {
  font-size:14px;
}

a {
  color:#8fd8f4;
  text-decoration:none;
}

a:hover {
  text-decoration:underline;
}

table {
  width:100%;
  border-collapse:collapse;
  margin-top:14px;
  font-size:13px;
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
}

.exports {
  background:#202020;
  border-radius:10px;
  padding:14px;
  color:#bbb;
  font-size:13px;
  line-height:1.7;
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
<div class='sheet'>

<h1>Structural Read Profile Sheet</h1>

<div class='subtitle'>
Receive → Reduce → Profile → Export
</div>

<div class='flow'>

  <div class='step'>
    <h2>1. Receive</h2>
    <p>Input terrain is a local folder. Files are read locally. No upload, no cloud dependency, no interpretation.</p>
  </div>

  <div class='step'>
    <h2>2. Reduce</h2>
    <p>Log lines are reduced into recurrence templates and surfaced as stable, middle, and residual structure.</p>
  </div>

  <div class='step'>
    <h2>3. Profile</h2>
    <p>Files become structural profiles: volume, recurrence bands, template density, concentration, and residual pressure.</p>
  </div>

  <div class='step'>
    <h2>4. Export</h2>
    <p>Outputs remain usable outside the tool: CSV, Markdown, and HTML surfaces for Excel, Python, R, SPSS, or manual review.</p>
  </div>

</div>

<div class='metrics'>
  <div class='metric'><div>Files seen</div><strong>$LogFilesSeen</strong></div>
  <div class='metric'><div>File profiles</div><strong>$FileCount</strong></div>
  <div class='metric'><div>Lines indexed</div><strong>$LinesIndexed</strong></div>
  <div class='metric'><div>Templates</div><strong>$TemplateCount</strong></div>
  <div class='metric'><div>Stable lines</div><strong>$StableLines</strong></div>
  <div class='metric'><div>Residual lines</div><strong>$ResidualLines</strong></div>
</div>

<div class='section'>
  <h2>Profile callouts</h2>

  <div class='callouts'>
    <div class='callout'>
      <div>Largest file</div>
      <strong>$($TopVolume.file_name)</strong><br>
      $($TopVolume.lines) lines
    </div>

    <div class='callout'>
      <div>Highest residual share</div>
      <strong>$($TopResidual.file_name)</strong><br>
      $($TopResidual.residual_pct)%
    </div>

    <div class='callout'>
      <div>Highest template density</div>
      <strong>$($TopDensity.file_name)</strong><br>
      $($TopDensity.templates_per_1000_lines) / 1k lines
    </div>

    <div class='callout'>
      <div>Highest top10 concentration</div>
      <strong>$($TopConcentration.file_name)</strong><br>
      $($TopConcentration.top10_share_pct)%
    </div>
  </div>
</div>

<div class='section'>
  <h2>Visual file profiles</h2>
  <p class='subtitle'>Each file profile can be opened as a visual texture bar surface.</p>
  <div class='exports'>
    <a href="file:///$TextureHtmlPath">Open file texture profile bars</a>
  </div>
</div>

<div class='section'>
  <h2>File profile table</h2>

  <table>
    <tr>
      <th>file</th>
      <th>lines</th>
      <th>templates</th>
      <th>stable</th>
      <th>middle</th>
      <th>residual</th>
      <th>top10</th>
      <th>templates/1k</th>
    </tr>
    $($FileSummaryRows -join "`r`n")
  </table>
</div>

<div class='section'>
  <h2>Exports</h2>

  <div class='exports'>
    Log read: $ReadPath<br>
    Template surface: $TemplateSurfacePath<br>
    Class summary: $ClassSummaryPath<br>
    File texture CSV: $TextureCsvPath<br>
    File texture HTML: $TextureRelNote<br>
    Profile sheet: $HtmlPath
  </div>
</div>

<div class='boundary'>
Boundary: This profile sheet organizes structural observables into a receive / reduce / profile / export flow. It does not infer incidents, severity, anomaly, cause, operational importance, or recommended action.
<br><br>
One-line hold: Receive the terrain, reduce recurrence, profile structure, export usable surfaces.
</div>

</div>
</body>
</html>
"@

Write-AtomicText -Path $HtmlPath -Text $Html

Write-Host ""
Write-Host "=== STRUCTURAL READ PROFILE SHEET COMPLETE ==="
Write-Host $HtmlPath

