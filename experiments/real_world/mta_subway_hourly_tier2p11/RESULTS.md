# MTA Subway Hourly Ridership (Tier-2 / P11) — Results (EST-gated)

This file summarizes repo-safe Tier-2 artifacts for MTA subway ridership under EST discipline.

Hard rule: **interpretation is gated by coherence**. Negative results are preserved as first-class outcomes.

Note: the prereg file includes v2.5 demo fields (e.g., `expected_sign`, `coherence_radius_spec`, `boundary_warmup_spec`) to illustrate prereg structure. These fields do not change any archived results or failure labels in this document.

## One-sentence result

The coherence gate FAILS because the preregistered constraint pair (`C_load`, `C_concentration`) exhibits a **stable negative correlation** (rho ~= -0.5) rather than the preregistered positive coupling. This is not estimator instability; it is a **sign-mismatch under the preregistered constraint-family semantics**.

## Key finding: stable anti-correlation (sign-mismatch)

| Scope | Period | `C_load` vs `C_concentration` | Note |
|---|---|---:|---|
| Pooled | 2023-2024 | rho = **-0.480** | Inverse coupling |
| H1_2023 window | 2023 | rho = **-0.521** | Consistent within-year |
| H2_2024 window | 2024 | n = 23 | DATA_MISSING (insufficient samples) |

**Mechanism sketch (bounded)**: in transit dynamics, total ridership and spatial concentration plausibly move inversely:

- High ridership days (weekday commutes) -> dispersed travel across many stations -> lower top-k share.
- Low ridership days (weekends/holidays) -> travel concentrates at a smaller set of hubs -> higher top-k share.

This can be coherent (stable), while still being a mismatch for a constraint family that presumes positive co-movement.

## Boundary (what is in scope)

- Dataset: MTA Subway Hourly Ridership (NY Open Data export)
- Time: 2023-01-01 to 2024-07-08 (as processed in the archived run)
- Aggregation: daily (`bucket: D`, `America/New_York`)

Note: if the raw export / schema changes, treat it as boundary drift and preregister a new mapping.

## Coherence gate outcome (preregistered v0.3)

| Metric | Value | Threshold | Status |
|---|---:|---:|---|
| Pooled (`C_load` vs `C_concentration`) | -0.480 | >= 0.6 | FAIL |
| H1_2023 window | -0.521 | >= 0.6 | FAIL |
| H2_2024 window | N/A | - | DATA_MISSING |
| Overall | - | - | **ESTIMATOR_UNSTABLE** (gate failure at preregistered sign/threshold) |

Interpretation note: the status label reflects preregistered failure semantics. The data behavior is consistent; what fails is the preregistered notion of a "constraint family" for this domain.

## Regime detection (diagnostic only)

Change points and regime diagnostics are generated, but **regime interpretation is forbidden** under EST when the coherence gate fails.

## Follow-ups (must be new preregistrations)

These are optional, but "next obvious" if you want to reuse MTA as a Tier-2/P11 case:

1) **Sign-aware coherence (v0.4)**:
   - preregister whether the family is intended to be positively coupled, negatively coupled, or "magnitude-only" (abs rho), and
   - treat the sign as an explicit part of the boundary/semantics, not a post-hoc patch.

2) **Alternative constraint family (v0.4)**:
   - replace `C_concentration` with a different proxy (or add a third proxy) and re-run the same EST gates.

## Archived artifacts (repo-safe)

Primary run:

- `results_runs/mta_daily_v0.3/outputs/metrics_log.parquet`
- `results_runs/mta_daily_v0.3/outputs/coherence_report.json`
- `results_runs/mta_daily_v0.3/outputs/fail_windows.md`
- `results_runs/mta_daily_v0.3/outputs/regime_report.md`
- `results_runs/mta_daily_v0.3/outputs/tradeoff_onepage.pdf` (+ `.png`)

## Reproduce (local)

```bash
cd experiments/real_world/mta_subway_hourly_tier2p11

# Download data (writes to data/raw/; do not commit raw downloads)
python scripts/download_mta_data.py --outdir data/raw

# Run daily pipeline (v0.3)
python run_pipeline.py --prereg EST_PREREG_v0.3_daily_2023_2024.yaml --out_root results_runs/mta_daily_v0.3
```
