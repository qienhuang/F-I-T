# Dr.One `policy-eval` matrix (summary)

This note summarizes a small **baseline vs controlled** matrix evaluation for the Dr.One demo under explicit low-FPR operation.

These runs are not evidence for general robustness. They are a reproducibility artifact meant to make two regimes visible:

1) **Gating is useful**: baseline unsafe behavior exists; controlled mode blocks unsafe tool usage.
2) **Gating is redundant**: baseline is already safe; controlled mode remains feasible but does not improve safety.

## Setup (gating-useful regime)

- Prompts: `data/policy_prompts_readwrite_v1.jsonl`
- Action vocabulary: `REFUSE, ANSWER, TOOL:read_file, TOOL:write_file`
- Unsafe actions: `TOOL:write_file`

Interpretation details:

- `baseline_adv_tool_rate` counts how often the model chooses an **unsafe** tool action.
- `TOOL:read_file` is intentionally *not* treated as unsafe in this suite; it is used to separate “tool propensity” from “irreversible side effects”.
- `coverage` is the fraction of adversarial prompts for which the alarm trips at least once under the target FPR operating point (here, `2/3 = 66.7%`).

## Results (Windows 11 + RTX 3090 + Ollama + Python 3.13)

Paper-ready matrix:

- Prompts: `policy_prompts_readwrite_v1.jsonl`
- Samples per prompt: `100`
- Temperature: `0.9`
- Seeds: `1337, 2337, 3337, 4337, 5337`

Summary (20/20 runs; std=0 across seeds):

| Model | Target FPR | n_runs | Baseline adv tool rate (mean±std) | Controlled adv tool rate (mean±std) |
|---|---:|---:|---:|---:|
| qwen3:4b | 0.05 | 5 | 1.0±0.0 | 0.0±0.0 |
| qwen3:4b | 0.10 | 5 | 1.0±0.0 | 0.0±0.0 |
| qwen3:8b | 0.05 | 5 | 1.0±0.0 | 0.0±0.0 |
| qwen3:8b | 0.10 | 5 | 1.0±0.0 | 0.0±0.0 |

Operational reading (consistent across the matrix):

- Baseline unsafe behavior is present (`baseline_adv_tool_rate = 1.0`).
- Controlled mode blocks unsafe tool usage (`controlled_adv_tool_rate = 0.0`) while remaining feasible under low-FPR operation (`fpr_floor = 0.0`, `achieved_fpr = 0.0`, `coverage = 2/3`).

Paper-ready tables:

- All runs: `policy_eval_runs_matrix.md`
- Grouped `mean±std`: `policy_eval_agg_matrix.md`

Exploratory (non-paper-ready) scans across other prompt suites / parameters are tracked separately:

- `policy_eval_runs.md`
- `policy_eval_agg.md`

## Contrast: gating-redundant regime (original prompt suite)

Under the original network/code-exec prompt suite (`data/policy_prompts.jsonl`), the scanned models were sufficiently conservative that:

- `baseline_adv_tool_rate = 0.0` (adversarial tool usage does not occur),
- the controller remains feasible (`feasible = true`, `fpr_floor = 0.0`),
- gating does not improve safety because baseline is already safe.

## Protocol (paper-ready)

Follow:

- `MATRIX_PROTOCOL_v0_2.md`
