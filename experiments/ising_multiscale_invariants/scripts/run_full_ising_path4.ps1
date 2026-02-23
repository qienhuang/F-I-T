Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

function Invoke-Py([string]$cmd) {
  Write-Host ">> $cmd"
  Invoke-Expression $cmd
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code ${LASTEXITCODE}: $cmd"
  }
}

Invoke-Py "python scripts/generate_multiscale_long_dataset.py --seeds 6 --seed_start 13000 --steps 4000 --burn_in 500 --measure_interval 20 --window 40 --grid_size 128 --temperature 2.269"
Invoke-Py "python scripts/validate_schema.py --input data/multiscale_long.parquet --out results/schema_validation.json"
Invoke-Py "python scripts/saturation_gate.py --input data/multiscale_long.parquet --out_csv results/saturation_matrix.csv --out_json results/saturation_summary.json"
Invoke-Py "python scripts/fit_scale_invariants.py --input data/multiscale_long.parquet --saturation_csv results/saturation_matrix.csv --results_dir results --bootstrap_resamples 200"
Invoke-Py "python scripts/render_invariant_matrix_md.py --input_csv results/invariant_matrix.csv --output_md results/invariant_matrix.md"
Invoke-Py "python scripts/plot_path4_figures.py --input data/multiscale_long.parquet --fixed_points_json results/fixed_points.json --saturation_csv results/saturation_matrix.csv --invariant_csv results/invariant_matrix.csv --out_dir results/figures"

Write-Host "Ising Path-4 full run complete."
