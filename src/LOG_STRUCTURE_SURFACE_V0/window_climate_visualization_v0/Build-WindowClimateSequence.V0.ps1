param(
  [Parameter(Mandatory=$true)]
  [string]$ParticipationPathCsv,

  [Parameter(Mandatory=$true)]
  [int]$WindowSize,

  [Parameter(Mandatory=$true)]
  [string]$OutCsv
)

$Rows = Import-Csv $ParticipationPathCsv

$Out = @()

foreach ($R in $Rows) {

  $WindowIndex =
    [int]($R.window -replace 'window_','')

  $LineStart =
    (($WindowIndex - 1) * $WindowSize) + 1

  $LineEnd =
    ($WindowIndex * $WindowSize)

  $Bracketed =
    [double]$R.stable_bracketed / [double]$R.family_occurrences

  $Edge =
    [double]$R.stable_edge / [double]$R.family_occurrences

  $Middle =
    [double]$R.middle_attached / [double]$R.family_occurrences

  $Residual =
    [double]$R.residual_clustered / [double]$R.family_occurrences

  $Diversity =
    [double]$R.exact_template_count / [double]$R.family_occurrences

  $EdgeMargin =
    [math]::Round(($Edge - $Bracketed), 3)

  $EdgeRatio = 0

  if ($Bracketed -gt 0) {
    $EdgeRatio =
      [math]::Round(($Edge / $Bracketed), 3)
  }

  $Climate = "quietly_consolidated"

  if ($Edge -gt $Bracketed) {
    $Climate = "permeability_coupled"
  }
  elseif ($Bracketed -lt 0.75) {
    $Climate = "enclosure_dominant"
  }

  $Topology = "ordinary"

  if (
    $Edge -gt $Bracketed -and
    $Middle -gt 0.12
  ) {
    $Topology = "localized_inversion_basin"
  }

  $Out += [pscustomobject]@{
    window_size = $WindowSize
    window_index = $WindowIndex
    line_start = $LineStart
    line_end = $LineEnd
    climate = $Climate
    enclosure_share = [math]::Round($Bracketed,3)
    edge_share = [math]::Round($Edge,3)
    middle_share = [math]::Round($Middle,3)
    residual_share = [math]::Round($Residual,3)
    diversity_share = [math]::Round($Diversity,3)
    edge_margin = $EdgeMargin
    edge_to_bracketed_ratio = $EdgeRatio
    local_topology = $Topology
  }
}

$Out |
  Export-Csv `
    $OutCsv `
    -NoTypeInformation `
    -Encoding UTF8

Write-Host ""
Write-Host "=== WINDOW CLIMATE SEQUENCE COMPLETE ==="
Write-Host $OutCsv
