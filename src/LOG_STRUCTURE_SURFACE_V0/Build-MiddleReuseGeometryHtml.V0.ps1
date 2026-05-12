param(
  [Parameter(Mandatory=$true)]
  [string]$TerrainRoot
)

$ErrorActionPreference = "Stop"

$SourceCsv = Join-Path $TerrainRoot "_surface_work\reuse_geometry_distribution_v0\reuse_geometry_distribution_surface.csv"

if (-not (Test-Path $SourceCsv)) {
  throw "Missing reuse geometry distribution surface: $SourceCsv"
}

$OutDir = Join-Path $TerrainRoot "_surface_work\middle_reuse_geometry_html_v0"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Rows = @(Import-Csv $SourceCsv)

if ($Rows.Count -eq 0) {
  throw "No rows found in reuse geometry distribution surface."
}

$Files = $Rows.file | Sort-Object -Unique

function Get-BarHtml {
  param(
    [double]$Pct
  )

  $Width = [math]::Round($Pct,2)

  return "<div style='display:inline-block;height:18px;width:${Width}%;background:#4a6fa5;border-right:1px solid #ffffff22;'></div>"
}

$Html = @()

$Html += "<html>"
$Html += "<head>"
$Html += "<title>MIDDLE_REUSE_GEOMETRY_V0</title>"
$Html += "<style>"
$Html += "body { font-family: Segoe UI; background:#111; color:#ddd; padding:24px; }"
$Html += "h1,h2,h3 { color:#fff; }"
$Html += ".terrain { margin-bottom:48px; padding-bottom:24px; border-bottom:1px solid #333; }"
$Html += ".bucket { margin-top:20px; margin-bottom:28px; }"
$Html += ".strip { width:900px; background:#222; border:1px solid #444; }"
$Html += ".legend-row { margin-top:6px; font-size:13px; }"
$Html += "table { border-collapse:collapse; margin-top:10px; }"
$Html += "th,td { border:1px solid #444; padding:6px 10px; text-align:left; }"
$Html += "th { background:#222; }"
$Html += ".note { margin-top:40px; color:#aaa; max-width:1000px; line-height:1.5; }"
$Html += "</style>"
$Html += "</head>"
$Html += "<body>"

$Html += "<h1>MIDDLE REUSE GEOMETRY V0</h1>"

$Html += "<div class='note'>"
$Html += "Sandbox observer surface only. This page shows normalized reuse-topology composition across recurrence buckets."
$Html += "<br/><br/>"
$Html += "Pattern signatures preserve neighborhood reuse geometry directly."
$Html += "<br/><br/>"
$Html += "Examples:"
$Html += "<br/>"
$Html += "2 = full reuse across two occurrences"
$Html += "<br/>"
$Html += "1-1 = fully circulating two-occurrence topology"
$Html += "<br/>"
$Html += "2-1-1 = partial reuse across four occurrences"
$Html += "<br/>"
$Html += "1-1-1-1 = fully circulating four-occurrence topology"
$Html += "<br/><br/>"
$Html += "Boundary: This surface does not infer anomaly, lifecycle, semantic family, severity, cause, or operational meaning."
$Html += "</div>"

foreach ($File in $Files) {

  $Html += "<div class='terrain'>"
  $Html += "<h2>$File</h2>"

  foreach ($Bucket in @(2,3,4)) {

    $BucketRows = @(
      $Rows |
        Where-Object {
          $_.file -eq $File -and
          [int]$_.bucket -eq $Bucket
        } |
        Sort-Object {[double]$_.pct_of_bucket} -Descending
    )

    if ($BucketRows.Count -eq 0) {
      continue
    }

    $Html += "<div class='bucket'>"
    $Html += "<h3>Bucket $Bucket</h3>"

    $Html += "<div class='strip'>"

    foreach ($R in $BucketRows) {
      $Html += Get-BarHtml -Pct ([double]$R.pct_of_bucket)
    }

    $Html += "</div>"

    $Html += "<table>"
    $Html += "<tr>"
    $Html += "<th>pattern</th>"
    $Html += "<th>forms</th>"
    $Html += "<th>pct_of_bucket</th>"
    $Html += "</tr>"

    foreach ($R in $BucketRows) {

      $Pct = "{0:N2}" -f ([double]$R.pct_of_bucket)

      $Html += "<tr>"
      $Html += "<td>$($R.pattern_signature)</td>"
      $Html += "<td>$($R.forms)</td>"
      $Html += "<td>$Pct%</td>"
      $Html += "</tr>"
    }

    $Html += "</table>"
    $Html += "</div>"
  }

  $Html += "</div>"
}

$Html += "<div class='note'>"
$Html += "<b>One-line hold:</b>"
$Html += "<br/><br/>"
$Html += "Middle recurrence ecology preserves recurrence persistence and contextual reuse topology as independent observational axes."
$Html += "</div>"

$Html += "</body>"
$Html += "</html>"

$OutPath = Join-Path $OutDir "MIDDLE_REUSE_GEOMETRY_V0.html"

$Tmp = "$OutPath.tmp"

$Html -join "`r`n" | Set-Content $Tmp -Encoding UTF8

Move-Item -Force $Tmp $OutPath

Write-Host ""
Write-Host "=== MIDDLE REUSE GEOMETRY HTML COMPLETE ==="
Write-Host $OutPath
