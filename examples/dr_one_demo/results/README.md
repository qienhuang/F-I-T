# Results (example artifacts)

This folder stores **small, repo-safe example outputs** from `policy-eval` runs to make the “baseline vs controlled gating” story concrete.

These artifacts are **not** used as evidence for any general claim. They are a reproducibility aid and a sanity check that:

- baseline can exhibit unsafe tool propensity under a prompt suite + action vocabulary,
- the controller can trip and disable tools,
- alarm feasibility (FPR controllability / `fpr_floor`) can be checked explicitly.

## Example: read/write action vocabulary (Mac mini)

Files:

- `policy_eval_summary.example_readwrite_v1.json`
- `policy_eval.example_readwrite_v1.json`

Observed summary (from the included example):

- Baseline: `baseline_adv_tool_rate = 1.0`
- Controlled: `controlled_adv_tool_rate = 0.0`
- Alarm: `feasible = true`, `fpr_floor = 0.0`, `achieved_fpr = 0.0`, `coverage = 2/3`

Configuration (conceptually):

- prompts: `data/policy_prompts_readwrite_v1.jsonl`
- action vocabulary: `REFUSE, ANSWER, TOOL:read_file, TOOL:write_file`
- unsafe actions: `TOOL:write_file`

## Matrix summary (Windows 11 + RTX 3090)

To make the “gating useful vs gating redundant” distinction explicit, we also keep a small matrix writeup:

- `MATRIX_SUMMARY.md`
- `MATRIX_PROTOCOL.md`
- `policy_eval_runs_matrix.md` (paper-ready; all runs in the matrix)
- `policy_eval_agg_matrix.md` (paper-ready; grouped mean±std)
- `policy_eval_runs.md` / `policy_eval_agg.md` (older exploratory scans)

Paper-ready headline (read/write prompt suite; 20/20 runs; 2 models × 2 target FPR × 5 seeds; std=0):

| Model | Target FPR | n_runs | Baseline adv tool rate | Controlled adv tool rate | Δ |
|---|---:|---:|---:|---:|---:|
| qwen3:4b | 0.05 | 5 | 1.0±0.0 | 0.0±0.0 | -100% |
| qwen3:4b | 0.10 | 5 | 1.0±0.0 | 0.0±0.0 | -100% |
| qwen3:8b | 0.05 | 5 | 1.0±0.0 | 0.0±0.0 | -100% |
| qwen3:8b | 0.10 | 5 | 1.0±0.0 | 0.0±0.0 | -100% |

Reproduce:

```bash
python dr_one_demo.py policy-eval \
  --backend ollama \
  --ollama_model qwen3:4b \
  --samples 50 \
  --temperature 0.9 \
  --target_fpr 0.10 \
  --seed_base 1337 \
  --action_ids "REFUSE,ANSWER,TOOL:read_file,TOOL:write_file" \
  --unsafe_action_ids "TOOL:write_file" \
  --prompts data/policy_prompts_readwrite_v1.jsonl \
  --out_dir out/example_readwrite_v1
```
