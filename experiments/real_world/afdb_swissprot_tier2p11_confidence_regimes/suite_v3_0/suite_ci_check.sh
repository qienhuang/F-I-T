#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASE_DIR="$(cd "${HERE}/.." && pwd)"
SUBCASES_DIR="${CASE_DIR}/subcases"

echo "=== AFDB Non-LLM Small-Models Suite (v3.0) ==="
echo "Case dir: ${CASE_DIR}"
echo ""

run_one () {
  local name="$1"
  local dir="${SUBCASES_DIR}/${name}"
  echo ""
  echo "---- running subcase: ${name} ----"
  if [ ! -d "${dir}" ]; then
    echo "Missing subcase dir: ${dir}"
    exit 1
  fi
  if [ ! -f "${dir}/scripts/ci_check.sh" ]; then
    echo "Missing ci_check.sh for subcase: ${name}"
    exit 1
  fi
  (cd "${dir}" && bash scripts/ci_check.sh)
}

run_one "pae_proxy_alarm"
run_one "msa_deficit_proxy"
run_one "dual_oracle_active_acquisition"

echo ""
echo "SUITE CI PASSED."
