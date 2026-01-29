# NYC TLC (Yellow) 2019-2023 Run (v1) — Negative Result Under EST

This folder archives a **completed** end-to-end run of the NYC TLC Tier-2 / P11 pipeline on **NYC Yellow Taxi** trip records (2019-01 to 2023-12).

It is a **successful negative result** under EST discipline: the pipeline ran and produced artifacts, and the preregistered constraint family failed the coherence gate.

## Run Snapshot

- Dataset: NYC TLC Yellow Taxi (Parquet months 2019-01 .. 2023-12)
- Files processed: 60
- Days aggregated: 1,826
- Trip records (sum of daily `trip_count`): 214,117,057
- Time range: 2019-01-01 .. 2023-12-31
- Prereg: `../../EST_PREREG.yaml` (v1.2, 2026-01-28)

## Coherence Gate (EST)

Status: `ESTIMATOR_UNSTABLE` (no regime interpretation allowed)

- `C_congestion` vs `C_scarcity`: rho = -0.677 (n=1826) [FAIL]
- `C_congestion` vs `C_concentration`: rho = -0.009 (n=1826) [FAIL]

Interpretation (diagnostic only): the current `C_scarcity = -log(trip_count)` behaves like an activity/demand proxy, and can be anticorrelated with congestion, making it unsuitable as a member of a coherent "constraint" family for this boundary.

## Artifacts (archived)

- `coherence_report.json`
- `regime_report.md` (contains change points; explicitly marked NOT interpretable under EST)
- `change_points.json`

## How to reproduce (local data required)

From `github/F-I-T/experiments/real_world/nyc_tlc_tier2p1/`:

```bash
python -m src.clean --prereg EST_PREREG.yaml
python -m src.estimators --prereg EST_PREREG.yaml
python -m src.regimes --prereg EST_PREREG.yaml
python -m src.plots --prereg EST_PREREG.yaml
```

Or run the wrapper:

```bash
python run_pipeline.py --prereg EST_PREREG.yaml
```

