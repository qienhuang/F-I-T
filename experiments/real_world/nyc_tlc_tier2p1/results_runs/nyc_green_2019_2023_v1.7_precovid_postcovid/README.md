# NYC TLC Green Taxi (2019-2023) - v1.7 pre/post-COVID windowing

This folder contains **repo-safe artifacts** from a completed run on NYC TLC **Green Taxi** trip records (2019-2023).

Purpose: replicate (or falsify) the Yellow-Taxi pattern "pooled FAIL + windowed PASS" under the same EST discipline.

## Coherence outcome (EST gate)

Constraint family: `C_congestion` vs `C_price_pressure` (Spearman rho, threshold 0.6).

- Pooled (2019-2023): rho = 0.631 (PASS)
- pre_covid (2019-01-01..2020-02-29): rho = 0.461 (FAIL)
- post_covid (2020-03-01..2023-12-31): rho = 0.779 (PASS)

**Status:** `ESTIMATOR_UNSTABLE`

Interpretation rule: because at least one preregistered window fails the coherence gate, **no regime interpretation is permitted** for this run under the v1.7 scope.

This is an intended kind of Tier-2 outcome: it demonstrates that windowing does not universally "rescue" coherence.

## Files

- `outputs/coherence_report.json`
- `outputs/regime_report.md` (diagnostic only when coherence fails)
- `outputs/change_points.json`
- `outputs/tradeoff_onepage.pdf` / `outputs/tradeoff_onepage.png`
- `outputs/metrics_log.parquet` (small)
- `data/cleaned/daily_state.parquet` (small; aggregated daily state)

