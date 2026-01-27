# GMB v0.4 - Grokking Monitorability Benchmark

**Status:** draft-final (repo-ready)  
**What this is:** a **monitorability-first** evaluation spec for grokking early-warning under explicit risk budgets (fixed FPR caps).  
**What this is not:** a new indicator, and not a runnable training pipeline by itself.

## Why GMB exists (one sentence)

Ranking metrics (AUC/AP) can look non-trivial while a score is **unusable as an alarm** because the false-positive rate is not controllable (an **FPR floor**). GMB makes "alarm admissibility" explicit and reportable.

## Contents

- Spec: `docs/benchmarks/gmb_v0_4/gmb_v0.4_spec.md`
- Companion note (toy theorem + diagnostics): `docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md`
- Addendum (indicator family): `docs/benchmarks/gmb_v0_4/gmb_v0.4_addendum_hrm_indicator_family.md`
- v0.5 runbook (CPU + single-GPU): `docs/benchmarks/gmb_v0_4/V0_5_RUNBOOK.md`
- Prereg template: `docs/benchmarks/gmb_v0_4/gmb_prereg_v0.4.yaml`
- Results schema: `docs/benchmarks/gmb_v0_4/gmb_results_v0.4.yaml`
- Filled example (illustrative only): `docs/benchmarks/gmb_v0_4/gmb_results_v0.4.example.yaml`

## Relation to published grokking results

This benchmark is compatible with the released grokking early-warning paper:

- **Grokking Hard Indicators: A Preregistered Evaluation Protocol and a Weak Baseline** (Zenodo): https://doi.org/10.5281/zenodo.18380476  
  PDF: `papers/grokking_hard_indicators.v0.3.1.pdf`

## Minimal "definition of done"

For each candidate indicator you must report:

- **Layer B (operationality gate):** achieved FPR at target FPRs + the minimum achievable FPR (floor check)
- **Layer C (utility):** coverage and lead-time at at least one operating point (e.g., FPR=0.05/0.10)
- **Failure semantics:** `SUPPORTED_FOR_ALARM` vs `RANK_ONLY` vs `ESTIMATOR_UNSTABLE` vs `INCONCLUSIVE`

## Real example run

We maintain repo-safe "real example runs" under:

- `docs/benchmarks/gmb_v0_4/results/`

### run_grokking_v0_3_A2_tradeoff (2026-01-21)

This run packages the v0.3 Phase A2 FPR sweep for grokking early warning (modular addition; 2-layer transformer; seeds 100-119 and 120-139).

Files:

- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/gmb_results_v0.4.run_grokking_v0_3_A2_tradeoff.yaml`
- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/tables/gate_summary.csv`
- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/tables/utility_at_fpr.csv`
- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/tables/robustness.csv`

Key finding (Layer B + Layer C):

- `score_sign = -1` has an FPR floor at ~0.44 (uncontrollable), so it is **invalid as an alarm** even if its ranking metrics look better.
- `score_sign = +1` is FPR-controllable; at FPR=0.05 coverage is 35%, and at FPR=0.10 coverage is 65-70% with lead time in the 12k-15k step range.

Notes:

- Layer A (AUC/AP) is intentionally not re-extracted in this run; treat this as a calibration/utility example.
- If a metric is unavailable, write `null` and explain why in the YAML notes (do not backfill by hand).
