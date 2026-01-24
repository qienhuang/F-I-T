# ONE_PAGE_TRADEOFF — Dual‑Oracle Active Acquisition (v0.5)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

Purpose: compare **allocation + within‑oracle ranking** policies under fixed budgets, while preserving EST boundary discipline.

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

- X axis: round index
- Y axis: fraction of this round’s queries allocated to PAE:



$$
\texttt{frac\_pae}(r) := \frac{q_{pae}(r)}{q_{pae}(r) + q_{msa}(r)}
$$



This makes allocation policies visible (fixed split vs adaptive).

---

## Panel D — Joint gate frontier (speed vs proxy quality)

Define `joint_usable_round(policy)`:

- the earliest round where **both** PAE and MSA alarms are usable at the primary cap, i.e.:
  - achieved FPR ≤ cap (within eps) and
  - TPR > 0

Plot each policy as a point:

- X axis: `joint_usable_round` (lower is better; if never achieved, set to `rounds+1`)
- Y axis: final MAE on MSA holdout for  $ \widehat{C3} $  where



$$
C3 := -\log(1 + \texttt{msa\_depth})
$$



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
