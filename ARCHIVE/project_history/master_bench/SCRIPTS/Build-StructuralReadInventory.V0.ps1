param(
    [string]$Root = ".",
    [string]$OutPath = ".\master_bench\STATUS\STRUCTURAL_READ_INVENTORY_V0.md"
)

$ErrorActionPreference = "Stop"

$RootPath = (Resolve-Path $Root).Path
$OutFull = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutPath)
$OutDir = Split-Path -Parent $OutFull

if (-not (Test-Path $OutDir)) {
    New-Item -ItemType Directory -Force $OutDir | Out-Null
}

$ExcludeDirs = @(
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "env"
)

$Files = Get-ChildItem -Path $RootPath -Recurse -File |
    Where-Object {
        $full = $_.FullName
        $keep = $true
        foreach ($d in $ExcludeDirs) {
            if ($full -like "*\$d\*") {
                $keep = $false
            }
        }
        $keep
    } |
    Sort-Object FullName

function Get-RelPath {
    param([string]$FullName)
    return $FullName.Substring($RootPath.Length).TrimStart("\")
}

function Select-Files {
    param(
        [string[]]$Patterns
    )

    $selected = @()
    foreach ($f in $Files) {
        $rel = Get-RelPath $f.FullName
        foreach ($p in $Patterns) {
            if ($rel -like $p) {
                $selected += $f
                break
            }
        }
    }
    return $selected | Sort-Object FullName -Unique
}

$Scripts = Select-Files @("*.ps1", "*.py", "*.rs")
$Docs = Select-Files @("*.md", "*.txt")
$Csvs = Select-Files @("*.csv")
$Html = Select-Files @("*.html", "*.htm")
$BenchFiles = Select-Files @("master_bench\*")
$SurfaceFiles = Select-Files @("*surface*", "*STRUCTURAL*", "*LOG_STRUCTURE*", "*inventory*", "*receipt*", "*packet*")

$Lines = New-Object System.Collections.Generic.List[string]

$Lines.Add("# STRUCTURAL_READ_INVENTORY_V0")
$Lines.Add("")
$Lines.Add("Status: BUILD")
$Lines.Add("")
$Lines.Add("Root:")
$Lines.Add("")
$Lines.Add($RootPath)
$Lines.Add("")
$Lines.Add("Generated:")
$Lines.Add("")
$Lines.Add((Get-Date).ToString("yyyy-MM-dd HH:mm:ss"))
$Lines.Add("")
$Lines.Add("## Counts")
$Lines.Add("")
$Lines.Add("- Total files: $($Files.Count)")
$Lines.Add("- Scripts: $($Scripts.Count)")
$Lines.Add("- Markdown/text docs: $($Docs.Count)")
$Lines.Add("- CSV files: $($Csvs.Count)")
$Lines.Add("- HTML files: $($Html.Count)")
$Lines.Add("- Master Bench files: $($BenchFiles.Count)")
$Lines.Add("- Surface-related files: $($SurfaceFiles.Count)")
$Lines.Add("")
$Lines.Add("## Master Bench files")
$Lines.Add("")

foreach ($f in $BenchFiles) {
    $Lines.Add("- " + (Get-RelPath $f.FullName))
}

$Lines.Add("")
$Lines.Add("## Surface-related files")
$Lines.Add("")

foreach ($f in $SurfaceFiles | Select-Object -First 200) {
    $Lines.Add("- " + (Get-RelPath $f.FullName))
}

if ($SurfaceFiles.Count -gt 200) {
    $Lines.Add("")
    $Lines.Add("Surface-related list truncated at 200 files.")
}

$Lines.Add("")
$Lines.Add("## Scripts")
$Lines.Add("")

foreach ($f in $Scripts | Select-Object -First 200) {
    $Lines.Add("- " + (Get-RelPath $f.FullName))
}

if ($Scripts.Count -gt 200) {
    $Lines.Add("")
    $Lines.Add("Script list truncated at 200 files.")
}

$Lines.Add("")
$Lines.Add("## Boundary")
$Lines.Add("")
$Lines.Add("This inventory is an orientation surface, not an interpretation layer.")
$Lines.Add("It lists files and counts only.")
$Lines.Add("It does not decide importance, meaning, status, or next action.")

$Tmp = "$OutFull.tmp"
$Lines | Set-Content $Tmp -Encoding UTF8
Move-Item -Force $Tmp $OutFull
