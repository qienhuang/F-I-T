# ONE_PAGE_TRADEOFF — Dual‑Oracle Active Acquisition (v0.3)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager makes the dual‑oracle strategy **operational** and comparable.

---

## Panel A — PAE alarm learning curve (budgeted)

- X axis: cumulative **PAE** labels queried
- Y axis: TPR on PAE holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel B — MSA alarm learning curve (budgeted)

- X axis: cumulative **MSA** labels queried
- Y axis: TPR on MSA holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel C — Oracle allocation over time

- X axis: acquisition round
- Y axis: fraction of queries allocated to PAE in that round:



$$
\texttt{frac\_pae} = \frac{q_{pae}}{q_{pae} + q_{msa}}
$$



Plot one line per policy.

Purpose: make “boundary switch strategy” visible, not narrative.

---

## Panel D — Efficiency summary (stacked AUTC)

Compute:

- AUTC_PAE = area under Panel A curve  
- AUTC_MSA = area under Panel B curve  

Plot per policy a stacked bar:

- bottom: AUTC_PAE
- top: AUTC_MSA

Purpose: one comparable budgeted learning efficiency score (and whether one oracle dominates).

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae, tau_msa_depth
- primary FPR cap
- split seed string
- feature whitelist hash
