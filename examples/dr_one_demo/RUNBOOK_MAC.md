# Dr.One demo: Mac runbook (Ollama + policy-eval)

This runbook is optimized for a Mac mini workflow where Ollama runs locally (Metal acceleration), while training happens elsewhere.

## 0) Go to the demo

```bash
cd '/Users/qienhuang/Downloads/FIT Lab/github/F-I-T/examples/dr_one_demo'
```

## 1) Confirm Ollama is running

```bash
ollama list
```

If needed:

```bash
ollama pull qwen3:8b
```

## 2) Smoke test (fast)

```bash
python3 dr_one_demo.py policy-eval \
  --backend ollama \
  --ollama_model qwen3:8b \
  --samples 5 \
  --temperature 0.7 \
  --target_fpr 0.10 \
  --seed_base 1337 \
  --out_dir out/qwen3_8b_smoke
```

Expected: writes `out/qwen3_8b_smoke/policy_eval_summary.json`.

If you see `Remote end closed connection without response`, try:

- use IPv4 explicitly: `--ollama_url http://127.0.0.1:11434`
- keep `--ollama_use_seed` **off** (default)

## 3) Main run (recommended matrix)

The suite uses `data/policy_prompts.jsonl` (currently 6 prompts), so total model calls are approximately:

`calls ≈ 2 * 6 * samples`  (baseline + controlled)

With `samples=20`, that is ~240 short calls.

```bash
chmod +x run_policy_eval_matrix.sh
bash run_policy_eval_matrix.sh qwen3:8b
```

If baseline tool usage is always 0, try the stronger prompt suite:

```bash
PROMPTS_FILE=data/policy_prompts_v2.jsonl bash run_policy_eval_matrix.sh qwen3:4b
```

If you want to test “safer” tool names (read/write), override the action vocabulary:

```bash
ACTION_IDS="REFUSE,ANSWER,TOOL:read_file,TOOL:write_file" \
UNSAFE_ACTION_IDS="TOOL:write_file" \
PROMPTS_FILE=data/policy_prompts_readwrite_v1.jsonl \
bash run_policy_eval_matrix.sh qwen3:4b
```

To expand the sweep (more time):

```bash
FPRS="0.05 0.10 0.20" SEEDS="1337 2337 3337" SAMPLES=50 bash run_policy_eval_matrix.sh qwen3:8b
```

## 4) Optional: sweep models

```bash
bash run_policy_eval_matrix.sh qwen3:8b
bash run_policy_eval_matrix.sh llama3.2:3b
```
