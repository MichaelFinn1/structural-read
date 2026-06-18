$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$InputDir = Join-Path $Here "INPUT"
$OutputDir = Join-Path $Here "OUTPUT"
$TraversalCsv = Join-Path $OutputDir "traversal_windows_v0.csv"
$HtmlPath = Join-Path $OutputDir "structural_read_output.html"
$ReceiptPath = Join-Path $OutputDir "LOCAL_UPLOAD_RECEIPT_V0.md"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$Errors = ""
$TraversalGenerated = "no"
$HtmlGenerated = "no"
$InputFilePath = ""
$InputLines = 0

try {
    $Files = Get-ChildItem -Path $InputDir -File

    if ($Files.Count -ne 1) {
        throw "Expected exactly one file in INPUT; found $($Files.Count)."
    }

    $InputFile = $Files[0]
    $InputFilePath = $InputFile.FullName

    $Lines = Get-Content $InputFilePath
    $InputLines = $Lines.Count

    $Rows = New-Object System.Collections.Generic.List[string]
    $Rows.Add("window_id,start_line,end_line,line_count,text_preview")

    $WindowSize = 20
    $WindowId = 0

    for ($i = 0; $i -lt $Lines.Count; $i += $WindowSize) {
        $WindowId += 1
        $StartLine = $i + 1
        $EndLine = [Math]::Min($i + $WindowSize, $Lines.Count)
        $Slice = $Lines[$i..($EndLine - 1)]
        $Preview = (($Slice -join " ") -replace '"','""')
        if ($Preview.Length -gt 220) {
            $Preview = $Preview.Substring(0,220)
        }
        $Rows.Add("$WindowId,$StartLine,$EndLine,$($EndLine - $StartLine + 1),`"$Preview`"")
    }

    Set-Content -Path $TraversalCsv -Value $Rows -Encoding UTF8
    $TraversalGenerated = "yes"

    $EscapedTitle = [System.Net.WebUtility]::HtmlEncode($InputFile.Name)
    $HtmlRows = Get-Content $TraversalCsv | Select-Object -Skip 1 | ForEach-Object {
        $Parts = $_ -split ",",5
        "<tr><td>$($Parts[0])</td><td>$($Parts[1])</td><td>$($Parts[2])</td><td>$($Parts[3])</td><td>$([System.Net.WebUtility]::HtmlEncode($Parts[4]))</td></tr>"
    }

    $Html = @"
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Structural Read Local Output</title>
<style>
body { font-family: Arial, sans-serif; margin: 32px; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 1px solid #ccc; padding: 6px; vertical-align: top; }
th { background: #eee; }
</style>
</head>
<body>
<h1>Structural Read Local Output</h1>
<p>Input file: $EscapedTitle</p>
<table>
<tr><th>window_id</th><th>start_line</th><th>end_line</th><th>line_count</th><th>text_preview</th></tr>
$($HtmlRows -join "`n")
</table>
</body>
</html>
"@

    Set-Content -Path $HtmlPath -Value $Html -Encoding UTF8
    $HtmlGenerated = "yes"
}
catch {
    $Errors = $_.Exception.Message
}

$Receipt = @"
# LOCAL_UPLOAD_RECEIPT_V0

input_file = $InputFilePath
input_lines = $InputLines
traversal_windows_generated = $TraversalGenerated
html_generated = $HtmlGenerated
html_output_path = $HtmlPath
errors = $Errors
"@

Set-Content -Path $ReceiptPath -Value $Receipt -Encoding UTF8
Get-Content $ReceiptPath

if ($HtmlGenerated -eq "yes") {
    Write-Host ""
    Write-Host "Open:"
    Write-Host $HtmlPath
}
