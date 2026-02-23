Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$repo = Split-Path -Parent (Split-Path -Parent $root)
$semigroup = Join-Path $repo "experiments\renormalization\gol_rg_lens_v0_1\src\semigroup_scale_map_test.py"
$input = Join-Path $repo "experiments\renormalization\gol_rg_lens_v0_1\out\multiscale_scheme_audit.csv"

if (-not (Test-Path $semigroup)) {
  throw "Missing dependency script: $semigroup"
}
if (-not (Test-Path $input)) {
  throw "Missing source input: $input"
}

Set-Location $root

python $semigroup --input $input --scheme majority --estimator C_frozen --outdir "results/closure/majority_C_frozen" --scales 1 2 4 8 --test_fraction 0.3 --random_state 20260216 --sat_near_bound_threshold 0.1 --sat_fraction_gate 0.9 --min_non_saturated_pairs 2
python $semigroup --input $input --scheme majority --estimator H --outdir "results/closure/majority_H" --scales 1 2 4 8 --test_fraction 0.3 --random_state 20260216 --sat_near_bound_threshold 0.1 --sat_fraction_gate 0.9 --min_non_saturated_pairs 2

Write-Host "Semigroup start runs complete."
