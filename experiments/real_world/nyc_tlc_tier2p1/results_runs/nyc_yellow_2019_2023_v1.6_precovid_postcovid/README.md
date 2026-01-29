# NYC TLC (Yellow) 2019-2023 Run (v1.6) — OK_PER_WINDOW (Pre/Post-COVID Coherence)

This archive corresponds to `EST_PREREG_v1.6.yaml`.

## Summary

- Boundary: Yellow taxi, daily aggregation, 2019-01-01 .. 2023-12-31
- Constraint family (cost-family): `C_congestion` and `C_price_pressure`
- Coherence (pooled): rho = 0.543 (threshold = 0.6) → pooled FAIL (diagnostic only)
- Coherence (preregistered windows): **pre/post-COVID both PASS** → `OK_PER_WINDOW`
  - pre_covid (2019-01-01..2020-02-29): rho = 0.928
  - post_covid (2020-03-01..2023-12-31): rho = 0.601

Interpretation rule: signatures are interpretable **within each preregistered window**. Pooled plots remain useful diagnostics, but should not be treated as a single coherent regime across the full 2019–2023 span.

## Artifacts

- `EST_PREREG_v1.6.yaml`
- `coherence_report.json` (includes window breakdown under `windowing.results`)
- `regime_report.md`
- `change_points.json` (includes alternative method results; may include `by_window` when supported)
- `metrics_log.parquet`
- `tradeoff_onepage.pdf` / `tradeoff_onepage.png`

