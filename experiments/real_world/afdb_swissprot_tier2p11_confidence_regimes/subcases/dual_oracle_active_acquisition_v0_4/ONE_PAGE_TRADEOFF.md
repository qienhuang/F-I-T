# ONE_PAGE_TRADEOFF — Dual‑Oracle Active Acquisition + Joint Gate (v0.4)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager makes the dual‑oracle strategy **operational** and comparable, while exposing the **joint gate**.

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

## Panel C — MSA proxy channel quality (budgeted regression)

Target:



$$
C3 := -\log(1 + \texttt{msa\_depth})
$$



- X axis: cumulative **MSA** labels queried
- Y axis: MAE of  $ \widehat{C3} $  on the MSA holdout
- One curve per policy.

---

## Panel D — Joint gate frontier (policy summary)

Define `joint_usable_round(policy)`:

- the earliest round where **both** PAE and MSA alarms are usable at the primary cap, i.e.:
  - achieved FPR ≤ cap (within eps) and
  - TPR > 0

Plot each policy as a point:

- X axis: `joint_usable_round` (lower is better; if never achieved, set to `rounds+1`)
- Y axis: final MAE of  $ \widehat{C3} $  (lower is better)

Purpose: a single picture of “how fast the system becomes operational” vs “how good the proxy channel becomes”.

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae, tau_msa_depth
- primary FPR cap
- split seed string
- feature whitelist hash
