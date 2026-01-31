# GMB v0.5 hold-out run (seeds 140-179)

This folder packages a **repo-ready** GMB v0.5 hold-out evaluation run for grokking (40 seeds).

Key point: this run is about **alarm usability under explicit FPR control** (Layer B/C), not just ranking metrics.

## Summary (paper-ready)

**Seeds:** 140-179 (40 runs; 39 runs with an evaluable event)  
**Event:** jump (E1)

### Score sign = +1 (alarm-usable candidate)

- FPR is controllable (achieved ≈ target).
- Coverage is limited at strict low-FPR:
  - FPR=0.05 → coverage=41% (16/39), abstain=59%, lead≈12.8k steps
  - FPR=0.10 → coverage=56% (22/39), abstain=44%, lead≈11.3k steps
  - FPR=0.20 → coverage=74% (29/39), abstain=26%, lead≈12.0k steps

### Score sign = -1 (invalid as an alarm score)

- Achieved FPR saturates at ~0.438 independent of target → **FPR floor**.
- This is therefore **not alarm-usable**, even if ranking metrics look better.

### Diagnostics (effective-n collapse)

- sign=+1: `n_eff_ratio = 0.152 ± 0.004`, `k_eff = 1.140 ± 0.009`, `tie_dom = 0.036 ± 0.004`
- sign=-1: `n_eff_ratio = 0.152 ± 0.004`, `k_eff = 1.140 ± 0.009`, `tie_dom = 1.000 ± 0.000` (pathological ties)

## Files

- Machine-readable summary: `gmb_results_v0.4.run_grokking_v0_5_holdout_140_179.yaml`
- Tables:
  - `tables/gate_summary.csv`
  - `tables/utility_at_fpr.csv`
  - `tables/robustness.csv`
  - `tables/tradeoff_with_abstain.sign_plus1.csv`
  - `tables/tradeoff_with_abstain.sign_minus1.csv`
  - `tables/diagnostics_per_run.sign_plus1.csv`
  - `tables/diagnostics_per_run.sign_minus1.csv`

## Provenance

Source outputs copied from the local grokking workspace:

- `grokking/results/v0_5_holdout/sign_plus1/`
- `grokking/results/v0_5_holdout/sign_minus1/`
