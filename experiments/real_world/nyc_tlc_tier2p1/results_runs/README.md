# NYC TLC Tier-2 / P11 — Run Archives

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
