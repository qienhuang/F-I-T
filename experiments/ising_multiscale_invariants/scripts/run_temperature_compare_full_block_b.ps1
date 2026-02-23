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

# Full-budget two-temperature comparison with an independent seed block.
$temps = @("2.10", "2.269")
$seedStart = 17000
$seeds = 6
$steps = 4000
$burnIn = 500
$measureInterval = 20
$window = 40
$gridSize = 128
$bootstrap = 200

foreach ($temp in $temps) {
  $tag = $temp.Replace(".", "p")
  $dataDir = "data/temp_compare_full_block_b/T$tag"
  $resDir = "results/temp_compare_full_block_b/T$tag"
  New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
  New-Item -ItemType Directory -Force -Path $resDir | Out-Null

  Invoke-Py "python scripts/generate_multiscale_long_dataset.py --seeds $seeds --seed_start $seedStart --steps $steps --burn_in $burnIn --measure_interval $measureInterval --window $window --grid_size $gridSize --temperature $temp --out_parquet $dataDir/multiscale_long.parquet --out_csv $dataDir/multiscale_long.csv --summary_json $dataDir/run_summary.json --manifest_json $dataDir/MANIFEST.json"
  Invoke-Py "python scripts/validate_schema.py --input $dataDir/multiscale_long.parquet --out $resDir/schema_validation.json"
  Invoke-Py "python scripts/saturation_gate.py --input $dataDir/multiscale_long.parquet --out_csv $resDir/saturation_matrix.csv --out_json $resDir/saturation_summary.json"
  Invoke-Py "python scripts/fit_scale_invariants.py --input $dataDir/multiscale_long.parquet --saturation_csv $resDir/saturation_matrix.csv --results_dir $resDir --bootstrap_resamples $bootstrap"
  Invoke-Py "python scripts/render_invariant_matrix_md.py --input_csv $resDir/invariant_matrix.csv --output_md $resDir/invariant_matrix.md"
}

Invoke-Py "python scripts/summarize_temperature_sweep.py --root results/temp_compare_full_block_b --out_csv results/temp_compare_full_block_b/temperature_compare_full_block_b_summary.csv --out_md results/temp_compare_full_block_b/temperature_compare_full_block_b_summary.md --title 'Ising Two-Temperature Full Compare Summary (Block B)' --note_tail 'This is a paired full-compare audit on an independent fixed seed block 17000..17005, not yet a multi-block pooled claim.'"

Write-Host "Ising full two-temperature comparison (block B) complete."
