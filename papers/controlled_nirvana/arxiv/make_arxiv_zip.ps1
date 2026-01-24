$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path

$outZip = Join-Path $here "controlled_nirvana_arxiv_v1.5.zip"
if (Test-Path $outZip) {
    try {
        Remove-Item $outZip -Force -ErrorAction Stop
    } catch {
        $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $outZip = Join-Path $here "controlled_nirvana_arxiv_v1.5_$stamp.zip"
    }
}

$tmp = Join-Path $here "_arxiv_tmp"
if (-not (Test-Path $tmp)) {
    New-Item -ItemType Directory -Path $tmp | Out-Null
}

Copy-Item (Join-Path $here "main.tex") (Join-Path $tmp "main.tex") -Force
Copy-Item (Join-Path $here "abstract.tex") (Join-Path $tmp "abstract.tex") -Force
Copy-Item (Join-Path $here "content.tex") (Join-Path $tmp "content.tex") -Force

Compress-Archive -Path (Join-Path $tmp "*") -DestinationPath $outZip
try {
    Remove-Item $tmp -Recurse -Force -ErrorAction Stop
} catch {
    Write-Host "Note: could not remove temporary folder: $tmp"
}

Write-Host "Wrote: $outZip"
