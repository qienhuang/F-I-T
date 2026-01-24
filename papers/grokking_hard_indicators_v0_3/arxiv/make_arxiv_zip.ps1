param(
  [string]$Version = "v0.3"
)

$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$base = "grokking_hard_indicators_arxiv_$Version"
$zipName = "$base.zip"

$files = @(
  "main.tex",
  "abstract.tex",
  "content.tex"
)

foreach ($f in $files) {
  if (-not (Test-Path $f)) {
    throw "Missing required file: $f"
  }
}

function New-Zip([string]$outZip) {
  if (Test-Path $outZip) { Remove-Item $outZip -Force }
  Compress-Archive -Path $files -DestinationPath $outZip
  Write-Host "Wrote: $outZip"
}

try {
  New-Zip $zipName
} catch {
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $alt = "${base}_${stamp}.zip"
  New-Zip $alt
}

