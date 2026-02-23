Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

python scripts/prepare_long_table.py
python scripts/validate_schema.py --input data/multiscale_long.parquet --out results/schema_validation.json
python scripts/saturation_gate.py --input data/multiscale_long.parquet --out_csv results/saturation_matrix.csv --out_json results/saturation_summary.json
python scripts/fit_scale_invariants.py --input data/multiscale_long.parquet --saturation_csv results/saturation_matrix.csv --results_dir results --bootstrap_resamples 200

Write-Host "Full Path-4 run complete."

