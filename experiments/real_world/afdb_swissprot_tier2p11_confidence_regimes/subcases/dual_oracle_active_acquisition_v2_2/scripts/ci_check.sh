#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${HERE}/.." && pwd)"

echo "[1/6] generate synthetic metrics"
mkdir -p "${CASE_DIR}/data"
python "${CASE_DIR}/scripts/make_synthetic_metrics.py" \
  --out "${CASE_DIR}/data/synthetic_metrics.csv" \
  --n 700 \
  --seed 7 \
  --missing_pae_rate 0.25 \
  --missing_msa_rate 0.25

echo "[2/6] run baseline grid (small)"
python "${CASE_DIR}/scripts/run_baseline_grid.py" --prereg "${CASE_DIR}/PREREG_SMOKE.yaml" --out_root "${CASE_DIR}/out_smoke_baseline"

echo "[3/6] run policy grid (small; limited policies)"
python "${CASE_DIR}/scripts/run_policy_grid.py" --prereg "${CASE_DIR}/PREREG_SMOKE.yaml" --out_root "${CASE_DIR}/out_smoke_policy" --max_policies 2

echo "[4/6] run main (single representative run)"
python -m src.run --prereg PREREG_SMOKE.yaml --run_id MAIN

echo "[5/6] aggregate v2.2 (baseline band + policy band + policy-robust frontier + jump distribution)"
python "${CASE_DIR}/scripts/aggregate_v2_2.py" --main_run "${CASE_DIR}/out_smoke/MAIN" --baseline_root "${CASE_DIR}/out_smoke_baseline" --policy_root "${CASE_DIR}/out_smoke_policy"

echo "[6/6] generate claims + validate artifacts"
python "${CASE_DIR}/scripts/generate_claims.py" --run_dir "${CASE_DIR}/out_smoke/MAIN"
python "${CASE_DIR}/scripts/check_artifacts.py" --run_dir "${CASE_DIR}/out_smoke/MAIN"

echo "CI-style check PASSED (v2.2)."
