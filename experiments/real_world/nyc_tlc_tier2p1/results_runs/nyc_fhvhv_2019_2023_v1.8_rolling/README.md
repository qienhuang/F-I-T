# NYC TLC (FHVHV) v1.8 Rolling Window Diagnostic (repo-safe artifacts)

This archive contains **small, repo-safe artifacts** for the v1.8 rolling-window diagnostic run on **NYC TLC FHVHV (2019–2023)**.

## What v1.8 tests

Compared to v1.7 (pre/post-COVID), v1.8 checks whether window-scoped coherence is stable across **smaller, overlapping blocks**:

- window length: 365 days
- stride: 90 days
- gate: Spearman rho on the cost-family constraint pair

Interpretation rule (EST):

- if any rolling window fails the coherence gate, the run is `ESTIMATOR_UNSTABLE` at this scope (no regime interpretation).

## Where to look

- Coherence outcome and per-window breakdown: `outputs/coherence_report.json`
- Human-readable report: `outputs/regime_report.md`
- Summary figure: `outputs/tradeoff_onepage.png` (or `.pdf`)
- Change points (diagnostic only when coherence fails): `outputs/change_points.json`

