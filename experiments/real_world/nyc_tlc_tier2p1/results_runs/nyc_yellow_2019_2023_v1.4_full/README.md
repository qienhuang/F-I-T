# NYC TLC (Yellow) 2019-2023 Run (v1.4) — Pooled Coherence Failure

This archive corresponds to `EST_PREREG_v1.4.yaml`.

## Summary

- Boundary: Yellow taxi, daily aggregation, 2019-01-01 .. 2023-12-31
- Constraint family (cost-family): `C_congestion` and `C_price_pressure`
- Coherence (pooled): rho = 0.543 (threshold = 0.6) → `ESTIMATOR_UNSTABLE`

Interpretation: diagnostics only. The same pair can be coherent within sub-windows but fail when pooling due to level shifts (see v1.5 year-windowed coherence).

## Artifacts

- `EST_PREREG_v1.4.yaml`
- `coherence_report.json`
- `regime_report.md`
- `change_points.json`
- `metrics_log.parquet`
- `tradeoff_onepage.pdf` / `tradeoff_onepage.png`

