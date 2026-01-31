#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${HERE}/.." && pwd)"

mkdir -p "${CASE_DIR}/data"

python "${CASE_DIR}/scripts/make_synthetic_metrics.py" --out "${CASE_DIR}/data/synthetic_metrics.csv" --n 1500 --seed 7 --missing_pae_rate 0.25 --missing_msa_rate 0.25

cd "${CASE_DIR}"
pip -q install -r requirements.txt

python -m src.run --prereg PREREG_SMOKE.yaml --run_id SMOKE

echo "Smoke run complete. See: ${CASE_DIR}/out_smoke/SMOKE/"
