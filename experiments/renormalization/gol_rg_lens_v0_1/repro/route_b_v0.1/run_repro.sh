#!/usr/bin/env bash
set -euo pipefail

bundle_root="$(cd "$(dirname "$0")" && pwd)"
exp_root="$(cd "$bundle_root/../.." && pwd)"
cd "$exp_root"

SCHEMES=(majority threshold_low threshold_high average)
ESTIMATORS=(C_frozen C_activity H)

python src/generate_multiscale_dataset.py \
  --seeds 10 \
  --steps 2000 \
  --grid 128 \
  --burn_in 100 \
  --measure_interval 10 \
  --window 50 \
  --scales 1 2 4 8 \
  --schemes "${SCHEMES[@]}" \
  --out_csv out/multiscale_scheme_audit.csv \
  --summary_json out/run_summary.json

for s in "${SCHEMES[@]}"; do
  for e in "${ESTIMATORS[@]}"; do
    python src/semigroup_scale_map_test.py \
      --input out/multiscale_scheme_audit.csv \
      --scheme "$s" \
      --estimator "$e" \
      --outdir "out/scheme_audit_full/${s}_${e}" \
      --scales 1 2 4 8 \
      --test_fraction 0.33 \
      --random_state 0 \
      --sat_near_bound_threshold 0.1 \
      --sat_fraction_gate 0.9 \
      --min_non_saturated_pairs 2
  done
done

python src/build_scheme_matrix.py \
  --out_root out/scheme_audit_full \
  --schemes "${SCHEMES[@]}" \
  --estimators "${ESTIMATORS[@]}" \
  --out_csv out/scheme_matrix_v0_1.csv \
  --out_md out/scheme_matrix_v0_1.md

python src/summarize_route_b.py \
  --matrix_csv out/scheme_matrix_v0_1.csv \
  --out_json out/route_b_hard_gate_summary.json \
  --out_md out/route_b_hard_gate_summary.md \
  --rmse_threshold 0.05 \
  --near_bound_threshold 0.1 \
  --saturation_fraction_gate 0.9 \
  --min_non_saturated_pairs 2

mkdir -p "$bundle_root/artifacts"
cp -f out/scheme_matrix_v0_1.csv "$bundle_root/artifacts/scheme_matrix_v0_1.csv"
cp -f out/scheme_matrix_v0_1.md "$bundle_root/artifacts/scheme_matrix_v0_1.md"
cp -f out/route_b_hard_gate_summary.json "$bundle_root/artifacts/route_b_hard_gate_summary.json"
cp -f out/route_b_hard_gate_summary.md "$bundle_root/artifacts/route_b_hard_gate_summary.md"
cp -f PREREG.yaml "$bundle_root/artifacts/PREREG.locked.yaml"

echo "Done. See repro/route_b_v0.1/artifacts/"
