**Li^2 Cross-M Summary (quick findings)**

- **Goal:** Estimate `r_crit` (training-set ratio at which `p_grok` transitions `0 -> 1`) across Ms and produce a short, reproducible cross-M summary for repo benchmarking.

- **Data used:**
  - M=71: experiments/li2_scaling_law/results/beta_multiseed_v5/M71/beta_analysis/beta_transition_analysis.json
  - M=159: experiments/li2_scaling_law/results/beta_multiseed_v5_extra/M159/beta_analysis/beta_transition_analysis.json

- **Results:**
  - **M = 71:** r_crit = 0.415 (fit valid; 3 points used; exp_fit reported). See file above for fit params.
  - **M = 159:** r_crit ~ 0.335. Dense low-ratio sweep (0.20-0.34) shows `p_grok = 0` for ratios `<= 0.32` and `p_grok > 0` at `0.34` (`p_grok ~ 0.67` across seeds); analysis file reports `r_crit = 0.335` (fit invalid due to few points above `r_crit`). Interval implied by the grid: `r_crit in (0.32, 0.34)`.

- **Interpretation:** `r_crit` decreases with larger M (example: `0.415 -> ~0.335` between `M=71 -> M=159`). With only these two validated Ms we cannot robustly fit a scaling law; more Ms (and denser sampling around the transition) would enable a parametric fit. The M159 low-ratio sweep tightened the `r_crit` estimate to ~0.335 (between 0.32 and 0.34).

- **Files to inspect / reproduce:**
  - `experiments/li2_scaling_law/results/beta_multiseed_v5/M71/beta_analysis/beta_transition_analysis.json`
  - `experiments/li2_scaling_law/results/beta_multiseed_v5_extra/M159/beta_analysis/beta_transition_analysis.json`
  - PT/MSS phase plots under each M's `pt_mss_plots/` directory.
  - Summary report: `experiments/li2_scaling_law/results/beta_multiseed_v5_extra/M159/fit_validation_summary.md`.

- **Recommended next steps (high-leverage):**
  - If a single, compact figure/table is desired for paper benchmarks: produce a small table with (M, r_crit, lower_ratio, upper_ratio, notes) for each M included and a short caption.
  - Only expand seeds if you need narrower uncertainty around r_crit for a single M; otherwise add additional M values to map the trend.

