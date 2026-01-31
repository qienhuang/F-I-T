# NYC TLC (FHVHV) v1.9 Rolling Sensitivity (repo-safe artifacts)

This archive contains **small, repo-safe artifacts** for the v1.9 rolling sensitivity run on **NYC TLC FHVHV (2019–2023)**.

## What v1.9 tests

v1.9 uses finer rolling windows than v1.8:

- window length: 180 days
- stride: 60 days

This checks whether the v1.8 failure pattern (pandemic-era windows) is robust to window granularity.

## Where to look

- Windowed coherence + pooled summary: `outputs/coherence_report.json`
- Auto-exported FAIL-window index: `outputs/fail_windows.md`
- Human-readable report: `outputs/regime_report.md`
- Summary figure: `outputs/tradeoff_onepage.png` (or `.pdf`)

