#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${HERE}/.." && pwd)"

echo "[1/3] generate synthetic metrics"
mkdir -p "${CASE_DIR}/data"
python "${CASE_DIR}/scripts/make_synthetic_metrics.py" \
  --out "${CASE_DIR}/data/synthetic_metrics.csv" \
  --n 650 \
  --seed 7 \
  --missing_pae_rate 0.25 \
  --missing_msa_rate 0.25

echo "[2/3] run smoke"
python "${CASE_DIR}/run_case.py" --prereg "${CASE_DIR}/PREREG_SMOKE.yaml" --run_id MAIN

echo "[3/3] check artifacts"
python "${CASE_DIR}/scripts/check_artifacts.py" --run_dir "${CASE_DIR}/out_smoke/MAIN"

echo "CI-style check PASSED."
