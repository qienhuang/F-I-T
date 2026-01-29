# NYC TLC (Yellow) 2019-2023 Run (v1.5) — OK_PER_YEAR (Windowed Coherence)

This archive corresponds to `EST_PREREG_v1.5.yaml`.

## Summary

- Boundary: Yellow taxi, daily aggregation, 2019-01-01 .. 2023-12-31
- Constraint family (cost-family): `C_congestion` and `C_price_pressure`
- Coherence (pooled): rho = 0.543 (threshold = 0.6) → pooled FAIL
- Coherence (year-windowed): **2019–2023 all PASS** → `OK_PER_YEAR`

Interpretation rule: signatures are interpretable **within each year**. Pooled plots and pooled change points remain useful diagnostics, but should not be treated as a single coherent regime across the full 5-year span.

## Artifacts

- `EST_PREREG_v1.5.yaml`
- `coherence_report.json` (includes per-year breakdown under `windowing.results`)
- `regime_report.md` (includes per-year coherence table)
- `change_points.json` (includes `by_year`)
- `metrics_log.parquet`
- `tradeoff_onepage.pdf` / `tradeoff_onepage.png`

