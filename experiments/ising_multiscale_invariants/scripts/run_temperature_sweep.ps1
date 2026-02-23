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

# Lightweight pilot sweep to diagnose saturation-vs-instability under same gates.
$temps = @("2.10", "2.269", "2.40")
$seedStart = 14000

foreach ($temp in $temps) {
  $tag = $temp.Replace(".", "p")
  $dataDir = "data/temp_sweep/T$tag"
  $resDir = "results/temp_sweep/T$tag"
  New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
  New-Item -ItemType Directory -Force -Path $resDir | Out-Null

  Invoke-Py "python scripts/generate_multiscale_long_dataset.py --seeds 3 --seed_start $seedStart --steps 2500 --burn_in 400 --measure_interval 20 --window 30 --grid_size 128 --temperature $temp --out_parquet $dataDir/multiscale_long.parquet --out_csv $dataDir/multiscale_long.csv --summary_json $dataDir/run_summary.json --manifest_json $dataDir/MANIFEST.json"
  Invoke-Py "python scripts/validate_schema.py --input $dataDir/multiscale_long.parquet --out $resDir/schema_validation.json"
  Invoke-Py "python scripts/saturation_gate.py --input $dataDir/multiscale_long.parquet --out_csv $resDir/saturation_matrix.csv --out_json $resDir/saturation_summary.json"
  Invoke-Py "python scripts/fit_scale_invariants.py --input $dataDir/multiscale_long.parquet --saturation_csv $resDir/saturation_matrix.csv --results_dir $resDir --bootstrap_resamples 80"
  Invoke-Py "python scripts/render_invariant_matrix_md.py --input_csv $resDir/invariant_matrix.csv --output_md $resDir/invariant_matrix.md"

  $seedStart += 100
}

Invoke-Py "python scripts/summarize_temperature_sweep.py --root results/temp_sweep --out_csv results/temp_sweep/temperature_sweep_summary.csv --out_md results/temp_sweep/temperature_sweep_summary.md"

Write-Host "Ising temperature sweep pilot complete."
