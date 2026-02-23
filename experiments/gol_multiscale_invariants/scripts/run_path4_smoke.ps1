Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

python scripts/prepare_long_table.py
python scripts/validate_schema.py --input data/multiscale_long.parquet --out results/schema_validation.json
python scripts/saturation_gate.py --input data/multiscale_long.parquet --out_csv results/saturation_matrix.csv --out_json results/saturation_summary.json

Write-Host "Path-4 smoke completed. Outputs under data/ and results/."

