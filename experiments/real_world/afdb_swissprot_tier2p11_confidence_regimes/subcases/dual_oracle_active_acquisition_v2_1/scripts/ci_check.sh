#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${HERE}/.." && pwd)"

echo "[1/4] generate synthetic metrics"
mkdir -p "${CASE_DIR}/data"
python "${CASE_DIR}/scripts/make_synthetic_metrics.py" \
  --out "${CASE_DIR}/data/synthetic_metrics.csv" \
  --n 800 \
  --seed 7 \
  --missing_pae_rate 0.25 \
  --missing_msa_rate 0.25

echo "[2/4] run baseline grid (small)"
python "${CASE_DIR}/scripts/run_baseline_grid.py" --prereg "${CASE_DIR}/PREREG_SMOKE.yaml" --out_root "${CASE_DIR}/out_smoke_baseline"

echo "[3/4] run main (smoke)"
python -m src.run --prereg PREREG_SMOKE.yaml --run_id MAIN

echo "[4/4] aggregate v2.0 + validate artifacts"
python "${CASE_DIR}/scripts/aggregate_v2_0.py" --main_run "${CASE_DIR}/out_smoke/MAIN" --baseline_root "${CASE_DIR}/out_smoke_baseline"
python "${CASE_DIR}/scripts/generate_claims.py" --run_dir "${CASE_DIR}/out_smoke/MAIN"
python "${CASE_DIR}/scripts/check_artifacts.py" --run_dir "${CASE_DIR}/out_smoke/MAIN"

echo "CI-style check PASSED (v2.0)."
