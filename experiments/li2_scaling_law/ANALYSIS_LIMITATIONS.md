# Analysis Limitations (Public)

This note summarizes limitations of the current grok-speed analysis in `experiments/li2_scaling_law/` without internal discussion details.

## 1) Too few points to identify a functional form

In the `band_sweep` dataset used for the initial Li² boundary verification, each M typically has only **two** ratio points strictly above `r_crit` that reliably grok (often 3/3 seeds).

With only two points, any 2-parameter model can appear to fit perfectly after log-linearization, e.g.:
- Exponential: `T = A * exp(-beta * (r - r_crit))`
- Power law: `T = K * (r - r_crit)^(-gamma)`

Therefore:
- **R² = 1.0 is not evidence** in this regime.
- We can state “time-to-grok drops sharply above `r_crit`”, but not “it is exponential”.

## 2) Avoid conflating “fast grok” with “early generalization”

When the training ratio is sufficiently above `r_crit`, a run may generalize early without a long memorization plateau. This can make `t_grok` small, but it is not necessarily the same phenomenon as delayed grokking.

For that reason, we recommend tracking:
- `grok_epoch`: first epoch where test accuracy crosses the threshold
- `mem_epoch`: first epoch where train accuracy reaches near-1.0 (e.g. ≥ 0.99)
- `grok_delay = grok_epoch - mem_epoch`

## 3) What data would upgrade this to a publishable “second law”

To distinguish exponential vs power-law vs piecewise behavior, each M should have at least **5–8 points above `r_crit`** (e.g. `r_crit + 0.01` … `r_crit + 0.10`).

Scripts to support this:
- `grok_speed_sweep.py` (builds a dense ratio grid above `r_crit`)
- `analyze_grok_speed.py` (compares exponential vs power-law in log space; requires `min_points >= 3`)

