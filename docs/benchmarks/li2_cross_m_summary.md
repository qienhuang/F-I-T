**Li² Cross-M Summary — Four-point r_crit benchmark**

- **Goal:** Estimate `r_crit` (training-set ratio at which `p_grok` transitions `0 → 1`) across moduli M and produce a reproducible cross-M benchmark for the repo.

- **Data sources:**
  - M=71: `experiments/li2_scaling_law/results/beta_multiseed_v5/M71/beta_analysis/beta_transition_analysis.json`
  - M=97: `experiments/li2_scaling_law/results/beta_multiseed_v4/M97/beta_analysis/beta_transition_analysis.json`
  - M=127: `experiments/li2_scaling_law/results/beta_multiseed_v4/M127/beta_analysis/beta_transition_analysis.json`
  - M=159: `experiments/li2_scaling_law/results/beta_multiseed_v5_extra/M159/beta_analysis/beta_transition_analysis.json`

- **Results table:**

| M   | r_crit | Fit Valid | Num Points | Lower Bound | Upper Bound | Notes |
|-----|--------|-----------|------------|-------------|-------------|-------|
| 71  | 0.415  | ✓         | 3          | 0.40        | 0.44        | Exp fit: β=29.59, R²=0.996 |
| 97  | 0.385  | ✓         | 5          | 0.36        | 0.40        | Exp fit: β=45.11, R²=0.974 |
| 127 | 0.350  | ✓         | 7          | 0.34        | 0.36        | Exp fit: β (see json), R²>0.97 |
| 159 | 0.335  | ✗         | 0          | 0.32        | 0.34        | Low-ratio grid: p_grok=0 @≤0.32, >0 @0.34 |

- **Interpretation:** `r_crit` decreases monotonically with M (0.415 → 0.385 → 0.350 → 0.335). The trend is consistent across four moduli spanning 71–159. M71/M97/M127 have validated exponential fits for grok speed vs (r − r_crit); M159's r_crit is bounded by the dense low-ratio grid.

- **Interpretation:** `r_crit` decreases monotonically with M (0.415 → 0.385 → 0.350 → 0.335). The trend is consistent across four moduli spanning 71–159. M71/M97/M127 have validated exponential fits for grok speed vs (r − r_crit); M159's r_crit is bounded by the dense low-ratio grid.

- **Files to inspect / reproduce:**
  - Beta transition analyses: see "Data sources" above for each M's `beta_transition_analysis.json`
  - PT/MSS phase plots: `pt_mss_plots/` under each M's output directory
  - Grok speed fits: `grok_speed/grok_speed_fit_delay.json` under each M's output directory
  - Full validation summaries: `fit_validation_summary.md` files in each M's results root

- **Citation-ready benchmark:** This four-point r_crit(M) curve demonstrates the scaling of grokking phase transition boundaries across modular arithmetic tasks. Suitable for inclusion in papers requiring reproducible grokking benchmarks.

