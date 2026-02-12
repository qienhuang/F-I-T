# Results (example artifacts)

This folder stores **small, repo-safe example outputs** from `policy-eval` runs to make the "baseline vs controlled gating" story concrete.

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

To make the "gating useful vs gating redundant" distinction explicit, we also keep a small matrix writeup:

### Paper-grade reproducibility protocols

- **[MATRIX_PROTOCOL_v0_2.md](MATRIX_PROTOCOL_v0_2.md)** - Current paper-grade preset (4 models x 2 prompt sets x 2 FPRs x 5 seeds x 100 samples)
- **[MATRIX_PROTOCOL.md](MATRIX_PROTOCOL.md)** - Earlier version (2 models x 1 prompt set)
- **[MATRIX_SUMMARY.md](MATRIX_SUMMARY.md)** - Conceptual overview
- **[run_matrix_v0_2_and_summarize.ps1](run_matrix_v0_2_and_summarize.ps1)** - One-click runner for v0.2

### Generated tables (paper-ready)

- `policy_eval_runs_matrix.md` - All runs in the matrix (one row per run)
- `policy_eval_agg_matrix.md` - Grouped mean+/-std by (model, prompt_set, target_fpr)
- `policy_eval_runs.md` / `policy_eval_agg.md` - Older exploratory scans

Headline (read/write prompt suite; 20/20 runs; 2 models x 2 target FPR x 5 seeds; std=0):

| Model | Target FPR | n_runs | Baseline adv tool rate | Controlled adv tool rate | Delta |
|---|---:|---:|---:|---:|---:|
| qwen3:4b | 0.05 | 5 | 1.0+/-0.0 | 0.0+/-0.0 | -100% |
| qwen3:4b | 0.10 | 5 | 1.0+/-0.0 | 0.0+/-0.0 | -100% |
| qwen3:8b | 0.05 | 5 | 1.0+/-0.0 | 0.0+/-0.0 | -100% |
| qwen3:8b | 0.10 | 5 | 1.0+/-0.0 | 0.0+/-0.0 | -100% |

Full matrix (80/80 runs) is summarized in:

- `policy_eval_runs_matrix.md` (all runs)
- `policy_eval_agg_matrix.md` (grouped aggregates)

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
