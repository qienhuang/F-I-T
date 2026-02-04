# NYC TLC Tier-2 / P11 - Results Summary (EST-gated)

This file summarizes the repo-safe Tier-2 results for NYC TLC Yellow Taxi (2019-2023) under EST discipline.
It is a pointer-rich results page: quick conclusion first, then auditable artifacts.

Key rule: **interpretation is gated by coherence**. Pooled failure is preserved as a first-class outcome.

Note: select prereg files include v2.5 demo fields (e.g., `expected_sign`, `coherence_radius_spec`, `boundary_warmup_spec`) to illustrate prereg structure. These fields do not change any archived results or failure labels in this document.

## One-sentence result

The cost-family constraint estimators are coherent **within preregistered windows** (yearly or pre/post-COVID) but not coherent when pooled across 2019-2023; therefore, P11 signatures are interpretable **only within phase-consistent windows**. This pattern replicates across Yellow, Green, and FHVHV datasets with one notable exception: Green shows a pre-COVID coherence failure, demonstrating that windowing does not universally rescue coherence. Rolling window analysis (v1.8) reveals that even pre/post-COVID windowing may be too coarse: all three datasets fail the stricter rolling coherence test, indicating localized instability periods that fixed windows miss.

## Objective (what this result does and does not try to do)

This Tier-2 case evaluates a narrow question:

> Under what explicit temporal scopes does a constraint-estimator family remain coherent in a non-stationary real-world system?

The goal is not to maximize pass rates or to "fit" a story to the data. Under EST, coherence failure is a first-class, auditable outcome: if coherence fails, interpretation is forbidden at that scope.

## Boundary (what is in scope)

- System: NYC TLC Yellow Taxi operations
- Time: 2019-01-01 .. 2023-12-31 (daily aggregation)
- Outputs: structural signatures only (no causal attribution; no forecasting claims)

## Result table (coherence outcomes)

### Yellow Taxi (primary)

| Run | Prereg | Windowing | Status | Pooled rho | Notes |
|-----|--------|-----------|--------|------------|-------|
| v1.4 full | `EST_PREREG_v1.4.yaml` | none (pooled) | `ESTIMATOR_UNSTABLE` | < 0.6 | Pooled-only diagnostic run |
| v1.5 yearly | `EST_PREREG_v1.5.yaml` | yearly | `OK_PER_YEAR` | 0.543 | All years PASS; pooled FAIL via level shifts / Simpson-style aggregation failure |
| v1.6 pre/post | `EST_PREREG_v1.6.yaml` | date_ranges | `OK_PER_WINDOW` | 0.543 | pre/post-COVID both PASS; pooled FAIL via level shifts |

### v1.7 Cross-Dataset Replication (Green / FHVHV)

| Dataset | Prereg | Pooled rho | Pre-COVID rho | Post-COVID rho | Status | Notes |
|---------|--------|------------|---------------|----------------|--------|-------|
| Yellow | v1.6 | 0.543 (FAIL) | 0.928 (PASS) | 0.601 (PASS) | `OK_PER_WINDOW` | Reference baseline |
| Green | v1.7_green | 0.631 (PASS) | 0.461 (FAIL) | 0.779 (PASS) | `ESTIMATOR_UNSTABLE` | **Reversed pattern**: pre-COVID FAIL |
| FHVHV | v1.7_fhvhv | 0.336 (FAIL) | 0.611 (PASS) | 0.684 (PASS) | `OK_PER_WINDOW` | Similar to Yellow |

**Key finding**: Windowing rescues Yellow and FHVHV but fails for Green (pre-COVID window). This demonstrates that windowed coherence is dataset-dependent and cannot be assumed to hold universally.

### v1.8 Rolling Window Diagnostic (Stricter Test)

v1.8 applies 17 overlapping 365-day rolling windows (90-day stride) to detect localized coherence failures that pre/post-COVID windowing may miss.

| Dataset | Prereg | Pooled rho | Windows PASS | Windows FAIL | Status | Pattern |
|---------|--------|------------|--------------|--------------|--------|---------|
| Yellow | v1.8_rolling | 0.543 (FAIL) | 14/17 | 3/17 | `ESTIMATOR_UNSTABLE` | Late-period failures (2022-03 to 2023-09) |
| Green | v1.8_rolling_green | 0.631 (PASS) | 8/17 | 9/17 | `ESTIMATOR_UNSTABLE` | Early + late failures (scattered) |
| FHVHV | v1.8_rolling_fhvhv | 0.336 (FAIL) | 10/17 | 7/17 | `ESTIMATOR_UNSTABLE` | Mid-period failures (2019-06 to 2021-12) |

**Key finding**: Rolling window analysis is strictly more sensitive than pre/post-COVID windowing. All three datasets show `ESTIMATOR_UNSTABLE` under rolling analysis, even when v1.7 pre/post-COVID windowing passed.

**Rolling window failure patterns:**
- **Yellow**: Coherence is stable through 2022, then degrades in windows covering late 2022-2023 (win_013-015 fail)
- **Green**: Most volatile; failures distributed across early and late windows with no clear phase boundary
- **FHVHV**: Failures concentrated in pandemic-era windows (mid-2019 through late 2021), then recovers in 2022-2023

### v1.9 Rolling Sensitivity (180-day / 60-day stride)

v1.9 applies finer-grained 28 overlapping 180-day rolling windows (60-day stride) to assess sensitivity to window size.

| Dataset | Prereg | Pooled rho | Windows PASS | Windows FAIL | Status | Comparison to v1.8 |
|---------|--------|------------|--------------|--------------|--------|-------------------|
| Yellow | v1.9_rolling_180_60_yellow | 0.543 (FAIL) | 26/28 | 2/28 | `ESTIMATOR_UNSTABLE` | **Improves**: only 2 windows fail (late 2022) |
| Green | v1.9_rolling_180_60_green | 0.631 (PASS) | 11/28 | 17/28 | `ESTIMATOR_UNSTABLE` | **Degrades**: 17 windows fail (early + late) |
| FHVHV | v1.9_rolling_180_60_fhvhv | 0.336 (FAIL) | 19/28 | 9/28 | `ESTIMATOR_UNSTABLE` | Similar: pandemic-era failures |

**Key finding**: Finer windows reveal dataset-specific sensitivity patterns:
- **Yellow** is actually more stable with 180-day windows (2/28 fail vs 3/17 in v1.8) — failures are highly localized to late 2022 (win_022: 2022-08-13..2023-02-09, win_023: 2022-10-12..2023-04-10)
- **Green** degrades significantly (17/28 fail vs 9/17 in v1.8) — coherence is unstable across nearly the entire time series
- **FHVHV** shows similar pattern: failures concentrated in pandemic period (late 2019 through mid-2021)

### v1.10 Rolling Sensitivity (90-day / 30-day stride)

v1.10 applies the finest preregistered granularity: 58 overlapping 90-day rolling windows (30-day stride).

| Dataset | Prereg | Pooled rho | Windows PASS | Windows FAIL | Status | Comparison to v1.9 |
|---------|--------|------------|--------------|--------------|--------|-------------------|
| Yellow | v1.10_rolling_90_30_yellow | 0.543 (FAIL) | 56/58 | 2/58 | `ESTIMATOR_UNSTABLE` | **Stable**: same 2 late-2022 failures |
| Green | v1.10_rolling_90_30_green | 0.631 (PASS) | 26/58 | 32/58 | `ESTIMATOR_UNSTABLE` | **Degrades**: 32 windows fail (55%) |
| FHVHV | v1.10_rolling_90_30_fhvhv | 0.336 (FAIL) | 45/58 | 13/58 | `ESTIMATOR_UNSTABLE` | Similar: pandemic-era failures |

**Key finding**: Window-size sensitivity grid completed. Conclusions:
- **Yellow** exhibits remarkable stability across all window sizes (2 failures at all scales, consistently in late 2022: win_046-047 = 2022-10-12..2023-02-09)
- **Green** indicates a constraint-family mismatch at this scope: failure rates remain high across granularities (9/17 -> 17/28 -> 32/58), so increasing window granularity does not rescue coherence
- **FHVHV** shows a localized pandemic-era instability (mid-2020 to late 2021) that is consistent across window sizes

### v1.11 Rolling Sensitivity (120-day / 30-day stride)

v1.11 tests an intermediate window size (120-day) with fine stride (30-day) to explore the granularity trade-off between v1.9 and v1.10.

| Dataset | Prereg | Pooled rho | Windows PASS | Windows FAIL | Status | Comparison to v1.10 |
|---------|--------|------------|--------------|--------------|--------|-------------------|
| Yellow | v1.11_rolling_120_30_yellow | 0.543 (FAIL) | 54/57 | 3/57 | `ESTIMATOR_UNSTABLE` | **Similar**: 3 late-2022 failures (win_045-047: 2022-09-12..2023-03-11) |
| Green | v1.11_rolling_120_30_green | 0.631 (PASS) | 27/57 | 30/57 | `ESTIMATOR_UNSTABLE` | **Similar**: 30 windows fail (53%), scattered early + late |
| FHVHV | v1.11_rolling_120_30_fhvhv | 0.336 (FAIL) | 40/57 | 17/57 | `ESTIMATOR_UNSTABLE` | **Similar**: pandemic-era failures (2020-01..2022-01) |

**Key finding**: The 120-day window confirms the patterns observed in v1.8–v1.10:
- **Yellow** remains remarkably stable (3/57 fail = 5%), with failures highly localized to late 2022
- **Green** shows persistent constraint-family mismatch (30/57 = 53% fail), scattered across 2019 early + 2020 pandemic + 2022-2023 late period
- **FHVHV** confirms pandemic-era instability (17/57 = 30% fail), concentrated in 2020-01 through 2021-12

### Window-Size Sensitivity Summary

| Dataset | v1.8 (365/90) | v1.9 (180/60) | v1.10 (90/30) | v1.11 (120/30) | Pattern |
|---------|---------------|---------------|---------------|----------------|---------|
| Yellow | 3/17 fail (18%) | 2/28 fail (7%) | 2/58 fail (3%) | 3/57 fail (5%) | **Stable** — failures localized to late 2022 |
| Green | 9/17 fail (53%) | 17/28 fail (61%) | 32/58 fail (55%) | 30/57 fail (53%) | **Constraint-family mismatch** — pervasive failures |
| FHVHV | 7/17 fail (41%) | 9/28 fail (32%) | 13/58 fail (22%) | 17/57 fail (30%) | **Improving** — pandemic-era only |

## Estimator family (the hard contract)

The core result above is about the cost-family constraint pair used in v1.4-v1.6:

- `C_congestion = log1p(minutes_per_mile)`
- `C_price_pressure = log1p(fare_per_mile)`

The information estimator in these runs is `I_entropy_pu` (pickup-zone entropy), used downstream for P11-style ratio diagnostics, but interpretation remains coherence-gated.

## Archived artifacts (repo-safe)

All artifacts below are small and auditable without shipping raw TLC data.

### Yellow Taxi
- v1.4 pooled: `results_runs/nyc_yellow_2019_2023_v1.4_full/`
- v1.5 yearly: `results_runs/nyc_yellow_2019_2023_v1.5_yearly/`
- v1.6 pre/post: `results_runs/nyc_yellow_2019_2023_v1.6_precovid_postcovid/`

### v1.7 Cross-Dataset
- Green: `results_runs/nyc_green_2019_2023_v1.7_precovid_postcovid/`
- FHVHV: `results_runs/nyc_fhvhv_2019_2023_v1.7_precovid_postcovid/`

### v1.8 Rolling Window
- Yellow: `results_runs/nyc_yellow_2019_2023_v1.8_rolling/`
- Green: `results_runs/nyc_green_2019_2023_v1.8_rolling/`
- FHVHV: `results_runs/nyc_fhvhv_2019_2023_v1.8_rolling/`

### v1.9 Rolling Sensitivity (180-day / 60-day)
- Yellow: `results_runs/nyc_yellow_2019_2023_v1.9_rolling_180_60/`
- Green: `results_runs/nyc_green_2019_2023_v1.9_rolling_180_60/`
- FHVHV: `results_runs/nyc_fhvhv_2019_2023_v1.9_rolling_180_60/`

### v1.10 Rolling Sensitivity (90-day / 30-day)
- Yellow: `results_runs/nyc_yellow_2019_2023_v1.10_rolling_90_30/`
- Green: `results_runs/nyc_green_2019_2023_v1.10_rolling_90_30/`
- FHVHV: `results_runs/nyc_fhvhv_2019_2023_v1.10_rolling_90_30/`

### v1.11 Rolling Sensitivity (120-day / 30-day)
- Yellow: `results_runs/nyc_yellow_2019_2023_v1.11_rolling_120_30/`
- Green: `results_runs/nyc_green_2019_2023_v1.11_rolling_120_30/`
- FHVHV: `results_runs/nyc_fhvhv_2019_2023_v1.11_rolling_120_30/`

Each archive contains:

- `coherence_report.json` (machine-readable status + window breakdown)
- `fail_windows.md` (auto-exported index of rolling FAIL windows, if rolling windowing is used)
- `regime_report.md`
- `change_points.json`
- `tradeoff_onepage.pdf` / `tradeoff_onepage.png`

## Windowed coherence snapshot (v1.6)

- Pooled: rho = 0.543 (FAIL at threshold 0.6)
- pre_covid (2019-01-01..2020-02-29): rho = 0.928 (PASS)
- post_covid (2020-03-01..2023-12-31): rho = 0.601 (PASS)

## Interpretation rules (EST-compliant)

- If pooled coherence fails, do not interpret pooled change points as a single-regime story.
- If `OK_PER_YEAR` / `OK_PER_WINDOW` holds, interpretation is allowed only within the corresponding windows.
- "Pooled FAIL" is preserved as a diagnostic signal of regime heterogeneity (level shifts / aggregation failure), not erased by windowing.

## Suggested figure (optional, for readers)

If you want a lightweight visual summary, use:

- `results_runs/figures/nyc_tlc_windowed_coherence_summary.svg`

This is not a "result" by itself; it is a diagrammatic index of the coherence outcomes already archived above.

## Reproduce (local)

This produces local artifacts under `outputs/` (not committed). Use `results_runs/` for repo-safe artifacts.

```bash
# Yellow (v1.5/v1.6)
python run_pipeline.py --prereg EST_PREREG_v1.5.yaml
python run_pipeline.py --prereg EST_PREREG_v1.6.yaml

# v1.7 cross-dataset (requires downloading Green/FHVHV data first)
pwsh ./download_tripdata.ps1 -Dataset green -YearStart 2019 -YearEnd 2023
pwsh ./download_tripdata.ps1 -Dataset fhvhv -YearStart 2019 -YearEnd 2023

python run_pipeline.py --prereg EST_PREREG_v1.7_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.7_precovid_postcovid
python run_pipeline.py --prereg EST_PREREG_v1.7_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.7_precovid_postcovid --raw_glob "data/raw/fhvhv_tripdata_*.parquet"

# v1.8 rolling window (stricter diagnostic)
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling.yaml --out_root results_runs/nyc_yellow_2019_2023_v1.8_rolling
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.8_rolling
python run_pipeline.py --prereg EST_PREREG_v1.8_rolling_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.8_rolling --raw_glob "data/raw/fhvhv_tripdata_*.parquet"

# v1.9 rolling sensitivity (180-day / 60-day stride)
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_yellow.yaml --out_root results_runs/nyc_yellow_2019_2023_v1.9_rolling_180_60
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.9_rolling_180_60
python run_pipeline.py --prereg EST_PREREG_v1.9_rolling_180_60_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.9_rolling_180_60 --raw_glob "data/raw/fhvhv_tripdata_*.parquet"

# v1.10 rolling sensitivity (90-day / 30-day stride)
python run_pipeline.py --prereg EST_PREREG_v1.10_rolling_90_30_yellow.yaml --out_root results_runs/nyc_yellow_2019_2023_v1.10_rolling_90_30
python run_pipeline.py --prereg EST_PREREG_v1.10_rolling_90_30_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.10_rolling_90_30
python run_pipeline.py --prereg EST_PREREG_v1.10_rolling_90_30_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.10_rolling_90_30 --raw_glob "data/raw/fhvhv_tripdata_*.parquet"

# v1.11 rolling sensitivity (120-day / 30-day stride)
python run_pipeline.py --prereg EST_PREREG_v1.11_rolling_120_30_yellow.yaml --out_root results_runs/nyc_yellow_2019_2023_v1.11_rolling_120_30
python run_pipeline.py --prereg EST_PREREG_v1.11_rolling_120_30_green.yaml --out_root results_runs/nyc_green_2019_2023_v1.11_rolling_120_30
python run_pipeline.py --prereg EST_PREREG_v1.11_rolling_120_30_fhvhv.yaml --out_root results_runs/nyc_fhvhv_2019_2023_v1.11_rolling_120_30 --raw_glob "data/raw/fhvhv_tripdata_*.parquet"
```
