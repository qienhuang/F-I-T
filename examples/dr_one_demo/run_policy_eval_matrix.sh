#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-qwen3:8b}"
SAMPLES="${SAMPLES:-20}"
TEMPERATURE="${TEMPERATURE:-0.7}"
OLLAMA_URL="${OLLAMA_URL:-}"
OLLAMA_USE_SEED="${OLLAMA_USE_SEED:-0}"
PROMPTS_FILE="${PROMPTS_FILE:-}"
ACTION_IDS="${ACTION_IDS:-}"
UNSAFE_ACTION_IDS="${UNSAFE_ACTION_IDS:-}"

if [[ -n "${FPRS:-}" ]]; then
  read -r -a FPRS_ARR <<< "${FPRS}"
else
  FPRS_ARR=("0.05" "0.10")
fi

if [[ -n "${SEEDS:-}" ]]; then
  read -r -a SEEDS_ARR <<< "${SEEDS}"
else
  SEEDS_ARR=(1337 2337)
fi

mkdir -p out

for fpr in "${FPRS_ARR[@]}"; do
  for seed in "${SEEDS_ARR[@]}"; do
    safe_model="$(echo "$MODEL" | tr ':/' '__')"
    tag="${safe_model}_fpr$(echo "$fpr" | tr -d '.')_seed${seed}_s${SAMPLES}"
    out_dir="out/${tag}"

    echo "== policy-eval model=${MODEL} fpr=${fpr} seed_base=${seed} samples=${SAMPLES}"
    extra_args=()
    if [[ -n "${OLLAMA_URL}" ]]; then
      extra_args+=(--ollama_url "${OLLAMA_URL}")
    fi
    if [[ "${OLLAMA_USE_SEED}" != "0" ]]; then
      extra_args+=(--ollama_use_seed)
    fi
    if [[ -n "${PROMPTS_FILE}" ]]; then
      extra_args+=(--prompts "${PROMPTS_FILE}")
    fi
    if [[ -n "${ACTION_IDS}" ]]; then
      extra_args+=(--action_ids "${ACTION_IDS}")
    fi
    if [[ -n "${UNSAFE_ACTION_IDS}" ]]; then
      extra_args+=(--unsafe_action_ids "${UNSAFE_ACTION_IDS}")
    fi
    python3 dr_one_demo.py policy-eval \
      --backend ollama \
      --ollama_model "${MODEL}" \
      --samples "${SAMPLES}" \
      --temperature "${TEMPERATURE}" \
      --target_fpr "${fpr}" \
      --seed_base "${seed}" \
      --out_dir "${out_dir}" \
      "${extra_args[@]}"
  done
done

echo "Done. Summaries are under out/*/policy_eval_summary.json"
