# ONE_PAGE_TRADEOFF — MSA Deficit Proxy (v0.1)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager forces the “proxy channel” story to remain **auditable**.

---

## Panel A — Regression calibration (test)

- Scatter plot: true  $ C3 $  vs predicted  $ \widehat{C3} $  on test.
- Annotate: MAE, RMSE, Spearman,  $ R^2 $ .

---

## Panel B — Residual distribution (test)

- Histogram of residuals:  $ (C3 - \widehat{C3}) $ .
- Purpose: reveal bias/heavy tails.

---

## Panel C — Alarm usability curve (test)

Define event:

- `E_msa_sparse`: `msa_depth <= tau_msa_depth`

Use score =  $ \widehat{C3} $ . Plot:

- TPR vs FPR sweep (ROC style) on test.
- Mark operating points at target FPR caps.

---

## Panel D — Budget view at target FPR

At each target FPR cap, show:

- flagged per 10k (predicted positives per 10k)
- missed per 10k (false negatives per 10k)

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_msa_depth
- tau_pae not applicable
- split seed string
- feature whitelist hash
