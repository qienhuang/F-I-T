# NYC TLC (Yellow) v1.9 Rolling Sensitivity (repo-safe artifacts)

This archive contains **small, repo-safe artifacts** for the v1.9 rolling sensitivity run on **NYC TLC Yellow Taxi (2019–2023)**.

## What v1.9 tests

v1.9 changes only the rolling window granularity (relative to v1.8):

- window length: 180 days
- stride: 60 days

This probes whether v1.8 failures are broad regime breaks or localized boundary sensitivity.

## Where to look

- Windowed coherence + pooled summary: `outputs/coherence_report.json`
- Auto-exported FAIL-window index: `outputs/fail_windows.md`
- Human-readable report: `outputs/regime_report.md`
- Summary figure: `outputs/tradeoff_onepage.png` (or `.pdf`)

