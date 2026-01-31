# MTA Subway Hourly Ridership (Tier-2 / P11, EST-gated)

This is a repo-ready real-world Tier-2 case built on **MTA subway hourly ridership** data.

Goal: demonstrate an auditable, EST-disciplined workflow for **windowed coherence** and **monitorability** in a non-stationary system with obvious regime shifts (pandemic shock, recovery, policy/seasonal structure).

This case is intentionally conservative:
- it treats coherence failure as a first-class outcome (interpretation is gated),
- it records pooled-vs-windowed outcomes without forcing a single narrative.

## Current status (repo results)

This case has a completed daily run (2023-2024) archived under `results_runs/` and summarized in `RESULTS.md`.
The key outcome is a coherence FAIL with a stable negative rho for the preregistered constraint pair (`C_load` vs `C_concentration`), i.e., a sign-mismatch under the preregistered family semantics.

## What you get (artifacts)

Running the pipeline produces:

- `outputs/metrics_log.parquet` (canonical time series: state + estimators)
- `outputs/coherence_report.json` (machine-readable EST gate outcome)
- `outputs/fail_windows.md` (index of failed windows, if windowing is enabled)
- `outputs/change_points.json` and `outputs/regime_report.md` (diagnostic; interpretation is coherence-gated)
- `outputs/tradeoff_onepage.pdf` (+ `.png`)

For repo-safe publishing, copy outputs into `results_runs/<run_id>/` and commit only that folder.

## Boundary (data + schema)

Place raw data files under:

- `data/raw/`

Supported raw formats:
- `.csv` (recommended for MTA exports)
- `.parquet`

Required columns (aliases supported):
- timestamp: `transit_timestamp`, `timestamp`, `datetime`, `date_time`
- station id: `station_complex_id`, `complex_id`, `station_id`, `station`
- ridership: `ridership`, `entries`, `total`, `count`

If schema changes, treat it as **boundary drift** and prereg a new mapping.

## Quick start (smoke test)

This uses a tiny synthetic fixture (no external downloads) and verifies the end-to-end pipeline.

```bash
python -m tests.generate_fixtures --out_dir data/raw/_fixture
python run_pipeline.py --prereg EST_PREREG_v0.1_hourly.yaml --raw_glob "data/raw/_fixture/*.csv" --out_root _smoke_out/hourly
```

## Running on real data

1) Put the MTA hourly ridership export(s) into `data/raw/`.
2) Run:

```bash
python run_pipeline.py --prereg EST_PREREG_v0.1_hourly.yaml
```

Optional overrides:

```bash
python run_pipeline.py --prereg EST_PREREG_v0.1_hourly.yaml --raw_glob "data/raw/subway_hourly*.csv"
python run_pipeline.py --prereg EST_PREREG_v0.1_hourly.yaml --max_files 2 --out_root _smoke_out/hourly
```

## Hourly -> Daily variant

Once hourly is working, you can run the daily-aggregated variant (a separate prereg):

```bash
python run_pipeline.py --prereg EST_PREREG_v0.2_daily.yaml --out_root _smoke_out/daily
```

## Failure semantics (EST)

- If coherence FAILS at the chosen scope: status is `ESTIMATOR_UNSTABLE` and regime interpretation is forbidden.
- If pooled FAILS but all preregistered windows PASS: status is `OK_PER_WINDOW` (interpret within-window only).
- If pooled PASS but some windows FAIL: status is `STRUCTURE_MISMATCH` (diagnostic of estimator-family mismatch at that scope).

## Files

- `EST_PREREG_v0.1_hourly.yaml` (hourly; windowing supported)
- `EST_PREREG_v0.2_daily.yaml` (daily aggregation; same estimator family)
- `EST_PREREG_v0.3_daily_2023_2024.yaml` (daily; preregistered date ranges for 2023/2024; current archived run)
- `run_pipeline.py` (wrapper)
- `src/` (deterministic engine)
- `tests/` (fixture + schema smoke test)
- `RESULTS.md` (repo-safe results summary)
