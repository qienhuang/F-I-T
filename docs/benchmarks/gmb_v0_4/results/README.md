# GMB v0.4 results (real runs)

This folder is for **real (non-example) benchmark outputs** produced under the GMB v0.4 spec.

## What belongs here

For each run, create a subfolder:

- `docs/benchmarks/gmb_v0_4/results/<run_id>/`

And include:

- `gmb_results_v0.4.<run_id>.yaml` (filled schema; machine-readable)
- `tables/gate_summary.csv`
- `tables/utility_at_fpr.csv`
- `tables/robustness.csv`

## Rules

- Do not copy private datasets or internal drafts into this repo.
- If a metric is unavailable, write `null` and explain why in the YAML notes.
- Prefer reporting `INCONCLUSIVE` over inventing a number.

## Current runs

- `run_grokking_v0_3_A2_tradeoff/` (2026-01-21) - grokking v0.3 Phase A2 FPR sweep packaged as a real GMB v0.4 run.

