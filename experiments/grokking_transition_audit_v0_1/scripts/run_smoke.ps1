Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python scripts/make_smoke_data.py
python src/run_pipeline.py --prereg EST_PREREG.smoke.yaml

Write-Host "Smoke run complete. Check outputs/smoke/summary.json and outputs/smoke/report.md"

