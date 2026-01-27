# Dr.One Demo (Self-Edit Loop + Monitorability Gate)

This is a **minimal, model-agnostic** demo that shows how a self-modifying system can be wrapped in a **monitorability control loop**:

- proposals come with a scalar `score` (a proxy for "safety/quality confidence")
- acceptance is **threshold-based** under a target false-positive budget (FPR)
- if FPR cannot be controlled by any threshold, the score is **invalid as an alarm**

The demo is intentionally small and auditable. It runs on CPU and does not require a GPU.

## Quick start (no model required)

```bash
python dr_one_demo.py self-edit --backend stub
python dr_one_demo.py fpr-demo
python dr_one_demo.py policy-eval --backend stub
```

Outputs:
- `out/audit_log.jsonl`

## Optional: connect a real local model (Ollama)

1) Install and start Ollama, then pull a small model (example):

```bash
ollama pull qwen2.5:3b
```

2) Run:

```bash
python dr_one_demo.py self-edit --backend ollama --ollama_model qwen2.5:3b
```

This demo does **not** require `requests`; it will use stdlib HTTP by default (and will use `requests` if it happens to be installed).

You can also run a **policy-style jailbreak evaluation** (baseline vs controlled tool gating):

```bash
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b
```

You can override the action vocabulary if you want to test “safer” tool names (e.g., `TOOL:read_file`):

```bash
python dr_one_demo.py policy-eval \
  --backend ollama \
  --ollama_model qwen2.5:3b \
  --action_ids "REFUSE,ANSWER,TOOL:read_file,TOOL:write_file" \
  --unsafe_action_ids "TOOL:write_file"
```

To get multi-run stability without changing prompts, vary `--seed_base` while keeping other parameters fixed:

```bash
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --seed_base 1337 --out_dir out/run_seed1337
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --seed_base 2337 --out_dir out/run_seed2337
```

Note: by default, `policy-eval` does **not** include `options.seed` in Ollama `/api/generate` calls. Some Ollama/model builds appear to close the connection when `seed` is provided. If you have verified it works in your environment, you can enable it:

```bash
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --ollama_use_seed
```

By default it uses `data/policy_prompts.jsonl` and writes:

- `out/policy_eval_summary.json`
- `out/policy_eval.json`

If your model is very conservative (baseline never chooses tools), try the stronger prompt suite:

```bash
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen3:4b --prompts data/policy_prompts_v2.jsonl
```

If you want to test “safer” tool names (read/write) to get non-zero tool propensity, combine an alternate action vocabulary with a matching prompt suite:

```bash
python dr_one_demo.py policy-eval \
  --backend ollama \
  --ollama_model qwen3:4b \
  --action_ids "REFUSE,ANSWER,TOOL:read_file,TOOL:write_file" \
  --unsafe_action_ids "TOOL:write_file" \
  --prompts data/policy_prompts_readwrite_v1.jsonl
```

Example artifacts (small, repo-safe) are in `results/`.

## Windows: run a matrix (PowerShell)

If you want to sweep multiple FPR targets / seeds on Windows:

```powershell
cd github/F-I-T/examples/dr_one_demo
powershell -ExecutionPolicy Bypass -File .\run_policy_eval_matrix.ps1 -Model "qwen3:4b" -Samples 50 -Temperature 0.9
```

Tip: use `-OutRoot out_matrix_v0_1 -CleanOutRoot` to keep a paper-ready run directory separate from ad-hoc experiments.

## Summarize results

After you have multiple runs under `out/`, generate a single markdown table:

```bash
python summarize_out.py --out_root out
```

To also get a grouped table (mean±std over seeds) suitable for citing in a paper:

```bash
python summarize_out.py --out_root out --aggregate --write_agg_md results/policy_eval_agg.md
```

For a recommended paper-ready matrix and exact commands, see `results/MATRIX_PROTOCOL.md`.

## What the demo edits

`toy_repo/` contains a tiny Python module plus `unittest` tests. The agent proposes a patch; the gate runs tests and only keeps patches that pass.

## What this answers (Controlled Nirvana critique)

This demo is meant to make three claims *executable*:

- **Estimator implementation**: `policy-eval` computes \(\hat{F}\) and \(\hat{C}\) from an observable **output distribution** over actions (empirical sampling).
- **Adversarial comparison**: `policy-eval` runs a small jailbreak-style prompt suite and reports baseline vs controlled tool-call rates.
- **Automatic trigger / cutoff**: when \(\sigma^2(\hat{F})\) spikes, or when low-FPR alarms become infeasible (FPR floor), the controller can **disable tool/API actions**.

## Interpreting `policy-eval` outputs (common regimes)

`policy-eval` reports two kinds of things:

- **Behavioral rates** (what the model actually does): `baseline_adv_tool_rate`, `controlled_adv_tool_rate`, etc.
- **Alarm feasibility** under an explicit FPR budget: `threshold`, `achieved_fpr`, `coverage`, `fpr_floor`, `feasible`.

Important detail: in **controlled** mode, the evaluator always estimates \(\hat{F}\) from a **counterfactual distribution with tools enabled** (what the model would do if tools were available). The *realized* action may still be forced to `REFUSE` once the controller trips. `policy_eval.json` records both:

- `raw_action_mode`: argmax action before gating
- `action_mode`: realized action after gating

Three common regimes:

1) **Baseline already safe**
   - `baseline_adv_tool_rate = 0` and often `baseline` is clean at all FPR targets.
   - In this case, the demo is still useful as a *protocol* (it shows how to check alarm feasibility), but you should switch to a weaker model or a harder prompt suite if you want to demonstrate the value of gating.

2) **Baseline unsafe, alarm feasible**
   - `baseline_adv_tool_rate > 0`, and `fpr_floor <= target_fpr` for some targets.
   - This is the “happy path” where `controlled_*` can reduce tool usage while keeping a low false-positive budget.

3) **Alarm invalid / infeasible (FPR floor)**
   - `fpr_floor` is high (e.g. `1.0`), meaning **no threshold can simultaneously (a) ever trigger on adversarial prompts and (b) keep FPR within budget**.
   - In FIT/Controlled-Nirvana terms: the score is **not a valid alarm** in the requested low-FPR regime, so the controller may choose a safe fallback (“no monitor, no tools”).

## Notes

- This demo uses a deliberately simplified notion of `score` to illustrate the *protocol* (thresholding + controllability), not to claim a good indicator.
- See also:
  - `docs/core/monitorability.md`
  - `docs/core/monitorability_control_loop.md`
