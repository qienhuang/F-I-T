**Li^2 Cross-M Summary - Five-point r_crit benchmark (M199 pilot)**

- **Goal:** Estimate `r_crit` (training-set ratio at which `p_grok` transitions `0 -> 1`) across moduli M and produce a reproducible cross-M benchmark for the repo.

- **Data sources:**
  - M=71: `experiments/li2_scaling_law/results/beta_multiseed_v5/M71/beta_analysis/beta_transition_analysis.json`
  - M=97: `experiments/li2_scaling_law/results/beta_multiseed_v4/M97/beta_analysis/beta_transition_analysis.json`
  - M=127: `experiments/li2_scaling_law/results/beta_multiseed_v4/M127/beta_analysis/beta_transition_analysis.json`
  - M=159 (boundary): `experiments/li2_scaling_law/results/beta_multiseed_v5_extra/M159/beta_analysis/beta_transition_analysis.json`
  - M=159 (speed-fit): `experiments/li2_scaling_law/results/beta_multiseed_v5_M159_speedfit/M159/experiments/` (18 runs: 3 seeds x 6 ratios 0.34-0.44)

- **Results table:**

| M   | r_crit | Fit Valid | Num Points | Lower Bound | Upper Bound | Notes |
|-----|--------|-----------|------------|-------------|-------------|-------|
| 71  | 0.415  | yes       | 3          | 0.40        | 0.44        | Exp fit: beta=29.59, R^2=0.996 |
| 97  | 0.385  | yes       | 5          | 0.36        | 0.40        | Exp fit: beta=45.11, R^2=0.974 |
| 127 | 0.350  | yes       | 7          | 0.34        | 0.36        | Exp fit: beta (see json), R^2>0.97 |
| 159 | 0.335  | yes       | 6          | 0.32        | 0.34        | Exp fit: beta=47.14, R^2=0.934 (speed-fit supplemental points) |
| 199 | ~0.31  | pilot     | 2          | 0.30        | 0.32        | Pilot: 0/2@0.30, 2/2@0.32; extends monotonic trend |

- **Interpretation:** `r_crit` decreases monotonically with M (0.415 -> 0.385 -> 0.350 -> 0.335 -> ~0.31). The trend is consistent across five moduli spanning 71-199. M71/M97/M127/M159 have validated exponential fits for grok speed vs (r - r_crit). M199 is a pilot confirmation of the monotonic trend.

- **Files to inspect / reproduce:**
  - Beta transition analyses: see data sources above for each M's `beta_transition_analysis.json`
  - PT/MSS phase plots: `pt_mss_plots/` under each M's output directory
  - Grok speed fits: `grok_speed/grok_speed_fit_delay.json` under each M's output directory
  - Full validation summaries: `fit_validation_summary.md` files in each M's results root

- **Citation-ready benchmark:** This five-point r_crit(M) curve (M199 pilot) demonstrates the scaling of grokking phase transition boundaries across modular arithmetic tasks. Suitable for inclusion in papers requiring reproducible grokking benchmarks.
