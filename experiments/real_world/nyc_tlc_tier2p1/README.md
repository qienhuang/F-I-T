# NYC TLC Tier-2 P11 Case Study

**Regime-Shift Signatures in I/C with EST Coherence Gates**

## Quick Start

```bash
# 1. Download TLC data (see Data section below)

# 2. Run pipeline
python -m src.clean --prereg EST_PREREG.yaml
python -m src.estimators --prereg EST_PREREG.yaml
python -m src.regimes --prereg EST_PREREG.yaml
python -m src.plots --prereg EST_PREREG.yaml
```

Latest full-run archives (2019-2023; EST-gated):

- [results_runs/nyc_yellow_2019_2023_v1/](results_runs/nyc_yellow_2019_2023_v1/)
- [results_runs/nyc_yellow_2019_2023_v1.4_full/](results_runs/nyc_yellow_2019_2023_v1.4_full/) (v1.4 pooled coherence fails)
- [results_runs/nyc_yellow_2019_2023_v1.5_yearly/](results_runs/nyc_yellow_2019_2023_v1.5_yearly/) (v1.5 `OK_PER_YEAR`: per-year PASS, pooled FAIL via level shifts / Simpson's paradox)
- [results_runs/nyc_yellow_2019_2023_v1.6_precovid_postcovid/](results_runs/nyc_yellow_2019_2023_v1.6_precovid_postcovid/) (v1.6 `OK_PER_WINDOW`: pre/post-COVID PASS, pooled FAIL via level shifts)

Convenience wrapper (same steps; easier to batch):

```bash
python run_pipeline.py --prereg EST_PREREG.yaml
```

Run v1.5 (year-windowed coherence):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.5.yaml
```

Optional v1.6 (pre/post-COVID date windows; treats the macro boundary as a preregistered window split):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.6.yaml
```

Optional v1.8 (rolling windowing; diagnostic-only unless all windows pass):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling.yaml
```

Optional v1.8 (rolling diagnostic on Green / FHVHV; may reveal finer instability even when v1.7 passes):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling_green.yaml
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling_fhvhv.yaml --raw_glob "data/raw/fhvhv_tripdata_*.parquet"
```

Optional v1.9 (rolling sensitivity: 180-day windows / 60-day stride):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_yellow.yaml
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_green.yaml
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_fhvhv.yaml --raw_glob "data/raw/fhvhv_tripdata_*.parquet"
```

v1.7 cross-dataset replications (Green / FHVHV):

```powershell
# Download helper (optional). Data is local-only under data/raw/ and is gitignored.
pwsh ./download_tripdata.ps1 -Dataset green -YearStart 2019 -YearEnd 2023
pwsh ./download_tripdata.ps1 -Dataset fhvhv -YearStart 2019 -YearEnd 2023
```

Quick smoke (limit files; CPU-friendly):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.7_green.yaml --max_files 2 --out_root _smoke_out/green_v1.7
python run_pipeline.py --prereg EST_PREREG_v1.7_fhvhv.yaml --max_files 2 --out_root _smoke_out/fhvhv_v1.7
```

Full runs (write into a run folder; do not commit raw data or `outputs/`):

```bash
python run_pipeline.py --prereg EST_PREREG_v1.7_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.7_precovid_postcovid
python run_pipeline.py --prereg EST_PREREG_v1.7_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.7_precovid_postcovid
```

Batching tip: override the raw glob without editing the prereg file:

```bash
# Example: run only year 2021
python run_pipeline.py --prereg EST_PREREG.yaml --raw_glob "data/raw/yellow_tripdata_2021-*.parquet"
```

Smoke test (CPU-friendly): run on a small prefix of files first

```bash
python -m src.clean --prereg EST_PREREG.yaml --max_files 2
python -m src.estimators --prereg EST_PREREG.yaml
python -m src.regimes --prereg EST_PREREG.yaml
python -m src.plots --prereg EST_PREREG.yaml
```

Or with the wrapper:

```bash
python run_pipeline.py --prereg EST_PREREG.yaml --max_files 2
```

No-download smoke run (fixtures; NOT evidence): runs end-to-end using `tests/fixtures/*.parquet`

```bash
python -m src.clean --prereg EST_PREREG.fixture.yaml --output data/cleaned_fixture/daily_state.parquet
python -m src.estimators --prereg EST_PREREG.fixture.yaml --input data/cleaned_fixture/daily_state.parquet --output outputs_fixture/metrics_log.parquet
python -m src.regimes --prereg EST_PREREG.fixture.yaml --input outputs_fixture/metrics_log.parquet --coherence outputs_fixture/coherence_report.json --output outputs_fixture/regime_report.md
python -m src.plots --prereg EST_PREREG.fixture.yaml --input outputs_fixture/metrics_log.parquet --coherence outputs_fixture/coherence_report.json --change-points outputs_fixture/change_points.json --output outputs_fixture/tradeoff_onepage.pdf
```

Extended fixture run (coherence gate actually runs; NOT evidence):

```bash
python tests/generate_fixtures.py --n_rows 3000 --start 2023-01-15 --n_days 45 --name_suffix _45d
python -m src.clean --prereg EST_PREREG.fixture_coherence.yaml --output data/cleaned_fixture_45d/daily_state.parquet
python -m src.estimators --prereg EST_PREREG.fixture_coherence.yaml --input data/cleaned_fixture_45d/daily_state.parquet --output outputs_fixture_45d/metrics_log.parquet
python -m src.regimes --prereg EST_PREREG.fixture_coherence.yaml --input outputs_fixture_45d/metrics_log.parquet --coherence outputs_fixture_45d/coherence_report.json --output outputs_fixture_45d/regime_report.md
python -m src.plots --prereg EST_PREREG.fixture_coherence.yaml --input outputs_fixture_45d/metrics_log.parquet --coherence outputs_fixture_45d/coherence_report.json --change-points outputs_fixture_45d/change_points.json --output outputs_fixture_45d/tradeoff_onepage.pdf
```

## What This Is

This is a **Tier-2 real-world case study** demonstrating FIT/EST principles on NYC Taxi & Limousine Commission (TLC) trip data.

**Primary focus: P11** - Regime-change signatures in the Information/Constraint ratio

**Key question:** Can we detect statistically robust regime shifts in urban mobility patterns using FIT estimators?

## EST Discipline

This case follows strict EST (Estimator Selection Theory) discipline:

1. **Pre-registration required** - All estimator definitions locked in `EST_PREREG.yaml`
2. **Coherence gate** - Constraint estimators must correlate (Spearman rho >= 0.6)
3. **Failure labels**:
   - If coherence fails -> `ESTIMATOR_UNSTABLE` (no interpretation allowed)
   - If all yearly windows pass but pooled coherence fails under prereg windowing -> `OK_PER_YEAR` (interpret within-year only)
   - If all preregistered date windows pass but pooled coherence fails -> `OK_PER_WINDOW` (interpret within-window only)

## Data

### Source

NYC TLC Trip Record Data: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

### Download Instructions

1. Go to TLC data portal
2. Download Yellow Taxi Trip Records (Parquet format)
3. Select months from 2019-01 to 2023-12
4. Place files in `data/raw/`

Example:
```
data/raw/
├── yellow_tripdata_2019-01.parquet
├── yellow_tripdata_2019-02.parquet
├── ...
└── yellow_tripdata_2023-12.parquet
```

### Data Size

- ~60 files, ~3-4 GB total
- Each month: ~7M trips (pre-pandemic) to ~3M trips (2020)

Note: `src.clean` aggregates per file and avoids loading the full trip table into memory at once. CPU runs are feasible, but a full 2019–2023 sweep can still take time (hours, depending on disk speed).

## Estimators

### Information (I)

| ID | Definition | Interpretation |
|----|------------|----------------|
| `I_entropy_pu` | Shannon entropy of pickup zone distribution | Spatial diversity of trips |

### Constraint (C)

| ID | Definition | Interpretation |
|----|------------|----------------|
| `C_congestion` | `log1p(minutes_per_mile)` | Travel friction proxy |
| `C_price_pressure` | `log1p(fare_per_mile)` | Fare pressure proxy |

### Force (F)

| ID | Definition | Interpretation |
|----|------------|----------------|
| `F_fare_drift` | Rolling diff of fare/mile | Price pressure |
| `F_congestion_drift` | Rolling diff of congestion | Friction trend |

## Outputs

| File | Description |
|------|-------------|
| `outputs/metrics_log.parquet` | Daily estimator values |
| `outputs/coherence_report.json` | Constraint family coherence test |
| `outputs/regime_report.md` | Change point analysis |
| `outputs/change_points.json` | Detected change points |
| `outputs/tradeoff_onepage.pdf` | Four-panel visualization |

## One-Page Figure

The trade-off figure has four normative panels:

- **(A) Information** - I_entropy over time
- **(B) Constraints** - C_congestion and C_scarcity agreement
- **(C) P11 Core** - R=I/C ratio and dR/dt with change points
- **(D) Trade-off** - Feasible region scatter (C vs I)

## Interpretation Rules

1. **Check coherence first** - If ESTIMATOR_UNSTABLE, stop interpretation
2. **Change points are signatures** - Not causal claims
3. **Event annotation is optional** - COVID, holidays, etc. are metadata, not explanation
4. **Robustness required** - Run sensitivity checks on window size

## Requirements

```
pandas>=2.0
numpy>=1.24
scipy>=1.10
matplotlib>=3.7
pyyaml>=6.0
pyarrow>=12.0
```

Optional sanity check (no big data needed): run unit tests on small parquet fixtures:

```bash
python -m pip install -r requirements.txt
pytest -q
```

## Case Study Documents

- [Case Study v1.1](nyc_tlc_tier2p11_case_study_v1.1.md) - Refined EST alignment

## Known Limitations

- Constraint proxies are internal (no external traffic data)
- Daily aggregation may miss intra-day patterns

## Next Steps

- Prefer v1.6 if you want a preregistered macro boundary (pre/post-COVID): `EST_PREREG_v1.6.yaml`
- Prefer v1.5 if you want calendar-year windowing: `EST_PREREG_v1.5.yaml`
- Use v1.8 as a strict rolling-window diagnostic (may fail even when v1.5/v1.6 pass): `EST_PREREG_v1.8_rolling.yaml`
- Run v1.7 replications (Green / FHVHV) to test whether "pooled FAIL + windowed PASS" generalizes beyond Yellow:
  - `EST_PREREG_v1.7_green.yaml`
  - `EST_PREREG_v1.7_fhvhv.yaml`

- Try a preregistered constraint-family repair (v1.3 candidate): `EST_PREREG.v1_3_price_pressure.yaml`
  - Run: `python run_pipeline.py --prereg EST_PREREG.v1_3_price_pressure.yaml`
- Add hourly bucket as separate boundary
- Implement Bayesian online CPD alternative
- Cross-plot with NYC 311 signatures (Tier-3)
