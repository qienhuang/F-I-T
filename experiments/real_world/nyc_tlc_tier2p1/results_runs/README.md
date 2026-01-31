# NYC TLC Tier-2 / P11 - Run Archives

This folder contains **small, repo-safe artifacts** from completed runs (reports + JSON + small parquet), intended to make EST outcomes auditable without publishing raw TLC data.

## Archives

- `nyc_yellow_2019_2023_v1/`  
  v1.2-style constraint family (`C_congestion`, `C_scarcity`, `C_concentration`): coherence fails (`ESTIMATOR_UNSTABLE`). Diagnostics only.

- `nyc_yellow_2019_2023_v1.4_full/`  
  Cost-family (`C_congestion`, `C_price_pressure`): pooled coherence fails (rho < threshold). Diagnostics only.

- `nyc_yellow_2019_2023_v1.5_yearly/`  
  Same cost-family, but **year-windowed coherence**: `OK_PER_YEAR` (per-year PASS, pooled FAIL due to level shifts / Simpson's paradox). Interpretable **within-year**.

- `nyc_yellow_2019_2023_v1.6_precovid_postcovid/`  
  Same cost-family, but **pre/post-COVID date windows**: `OK_PER_WINDOW` (both windows PASS, pooled FAIL due to level shifts). Interpretable **within-window**.

- `nyc_green_2019_2023_v1.7_precovid_postcovid/`  
  Green Taxi replication (v1.7 pre/post-COVID): pooled PASS but pre-COVID window FAIL, so coherence is `ESTIMATOR_UNSTABLE`. This is a valid negative result: windowing does not universally rescue coherence.

- `nyc_fhvhv_2019_2023_v1.7_precovid_postcovid/`  
  FHVHV replication (v1.7 pre/post-COVID): pooled FAIL but both windows PASS, so `OK_PER_WINDOW`. Interpretable **within-window**.

- `nyc_yellow_2019_2023_v1.8_rolling/`  
  Yellow rolling-window diagnostic (v1.8): pooled FAIL; some rolling windows FAIL, so `ESTIMATOR_UNSTABLE` at this finer scope.

- `nyc_green_2019_2023_v1.8_rolling/`  
  Green rolling-window diagnostic (v1.8): pooled PASS but many rolling windows FAIL, so `ESTIMATOR_UNSTABLE` (windowing is diagnostic, not a universal fix).

- `nyc_fhvhv_2019_2023_v1.8_rolling/`  
  FHVHV rolling-window diagnostic (v1.8): pooled FAIL; some rolling windows FAIL, so `ESTIMATOR_UNSTABLE` at this finer scope.

- `nyc_yellow_2019_2023_v1.9_rolling_180_60/`  
  Yellow rolling sensitivity (v1.9; 180-day windows / 60-day stride): still `ESTIMATOR_UNSTABLE`, but failures are highly localized (late 2022).

- `nyc_green_2019_2023_v1.9_rolling_180_60/`  
  Green rolling sensitivity (v1.9; 180/60): `ESTIMATOR_UNSTABLE` with pervasive window failures (demonstrates strong window-size sensitivity).

- `nyc_fhvhv_2019_2023_v1.9_rolling_180_60/`  
  FHVHV rolling sensitivity (v1.9; 180/60): `ESTIMATOR_UNSTABLE`; failure pattern remains concentrated in the pandemic-era block (scale-stable).
