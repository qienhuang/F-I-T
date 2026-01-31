# NYC TLC (Yellow) v1.8 Rolling Window Diagnostic (repo-safe artifacts)

This archive contains **small, repo-safe artifacts** for the v1.8 rolling-window diagnostic run on **NYC TLC Yellow Taxi (2019–2023)**.

## What v1.8 tests

Compared to v1.6 (pre/post-COVID), v1.8 uses **overlapping rolling windows** to detect localized coherence degradation:

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

## Notes

This run is intentionally strict. It can fail even when coarser preregistered windowing (yearly or pre/post-COVID) passes.

