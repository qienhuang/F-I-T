$ErrorActionPreference = "Stop"

$bundleRoot = $PSScriptRoot
$expRoot = (Resolve-Path (Join-Path $bundleRoot "..\..\")).Path
Set-Location $expRoot

$python = "python"

$schemes = @("majority","threshold_low","threshold_high","average")
$estimators = @("C_frozen","C_activity","H")

& $python "src/generate_multiscale_dataset.py" `
  --seeds 10 `
  --steps 2000 `
  --grid 128 `
  --burn_in 100 `
  --measure_interval 10 `
  --window 50 `
  --scales 1 2 4 8 `
  --schemes $schemes `
  --out_csv "out/multiscale_scheme_audit.csv" `
  --summary_json "out/run_summary.json"

foreach ($s in $schemes) {
  foreach ($e in $estimators) {
    & $python "src/semigroup_scale_map_test.py" `
      --input "out/multiscale_scheme_audit.csv" `
      --scheme $s `
      --estimator $e `
      --outdir ("out/scheme_audit_full/{0}_{1}" -f $s, $e) `
      --scales 1 2 4 8 `
      --test_fraction 0.33 `
      --random_state 0 `
      --sat_near_bound_threshold 0.1 `
      --sat_fraction_gate 0.9 `
      --min_non_saturated_pairs 2
  }
}

& $python "src/build_scheme_matrix.py" `
  --out_root "out/scheme_audit_full" `
  --schemes $schemes `
  --estimators $estimators `
  --out_csv "out/scheme_matrix_v0_1.csv" `
  --out_md "out/scheme_matrix_v0_1.md"

& $python "src/summarize_route_b.py" `
  --matrix_csv "out/scheme_matrix_v0_1.csv" `
  --out_json "out/route_b_hard_gate_summary.json" `
  --out_md "out/route_b_hard_gate_summary.md" `
  --rmse_threshold 0.05 `
  --near_bound_threshold 0.1 `
  --saturation_fraction_gate 0.9 `
  --min_non_saturated_pairs 2

$artifactDir = Join-Path $bundleRoot "artifacts"
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
Copy-Item "out/scheme_matrix_v0_1.csv" (Join-Path $artifactDir "scheme_matrix_v0_1.csv") -Force
Copy-Item "out/scheme_matrix_v0_1.md" (Join-Path $artifactDir "scheme_matrix_v0_1.md") -Force
Copy-Item "out/route_b_hard_gate_summary.json" (Join-Path $artifactDir "route_b_hard_gate_summary.json") -Force
Copy-Item "out/route_b_hard_gate_summary.md" (Join-Path $artifactDir "route_b_hard_gate_summary.md") -Force
Copy-Item "PREREG.yaml" (Join-Path $artifactDir "PREREG.locked.yaml") -Force

Write-Host "Done. See repro/route_b_v0.1/artifacts/" -ForegroundColor Green
