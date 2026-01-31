# NYC TLC FHVHV (2019-2023) - v1.7 pre/post-COVID windowing

This folder contains **repo-safe artifacts** from a completed run on NYC TLC **FHVHV** trip records (2019-2023).

Purpose: test whether the Yellow-Taxi "pooled FAIL + windowed PASS" pattern holds in a different service category.

## Coherence outcome (EST gate)

Constraint family: `C_congestion` vs `C_price_pressure` (Spearman rho, threshold 0.6).

- Pooled (2019-2023): rho = 0.336 (FAIL)
- pre_covid (2019-01-01..2020-02-29): rho = 0.611 (PASS)
- post_covid (2020-03-01..2023-12-31): rho = 0.684 (PASS)

**Status:** `OK_PER_WINDOW`

Interpretation rule: pooled signatures are **not** interpretable as a single-regime story; interpretation is allowed **within each preregistered window only**.

## Files

- `outputs/coherence_report.json`
- `outputs/regime_report.md`
- `outputs/change_points.json`
- `outputs/tradeoff_onepage.pdf` / `outputs/tradeoff_onepage.png`
- `outputs/metrics_log.parquet` (small)
- `data/cleaned/daily_state.parquet` (small; aggregated daily state)

