# Artifact Contract: Low-FPR Alarms (Monitorability)

This is the minimum reporting contract for any "early warning" or alarm claim.

## Required fields (single operating point)

At a fixed target FPR (e.g., 0.05 or 0.10), report:

- `target_fpr`: configured cap (what you asked for)
- `achieved_fpr`: what you actually got on negatives
- `fpr_floor`: the minimum reachable FPR (if `fpr_floor` > `target_fpr`, the detector is not usable at this cap)
- `feasible`: boolean; true iff operation at `target_fpr` is achievable
- `coverage`: fraction of runs that trigger at least one alarm
- `lead_time`: mean/median lead time for runs that trigger (define units and reference point)

Optional but recommended:

- `coverage_ci`: uncertainty estimate (bootstrap over runs)
- `lead_time_ci`
- confusion counts at the operating point (TP/FP/TN/FN) for transparency

## Curves (recommended)

Always include a sweep over target FPR:

- A small grid such as: 0.01, 0.02, 0.05, 0.10, 0.15, 0.20
- For each: achieved FPR, coverage, lead time

This prevents cherry-picking a single operating point.

## What NOT to claim from

- Do not claim "alarm works" from AUC/AP alone.
- If a sign flip improves AUC but makes achieved FPR stick at a high value (a floor), label that score **invalid as an alarm**.

## Minimal file outputs (recommended)

- `policy_eval.json` or equivalent per-sample log
- `policy_eval_summary.json` or equivalent per-run summary
- `results.md` or `results.csv` aggregating configurations
- `fpr_tradeoff.md` and/or plots (coverage vs FPR, lead time vs FPR)
- `ENVIRONMENT_REPORT.md` with backend/model/version and how to reproduce

