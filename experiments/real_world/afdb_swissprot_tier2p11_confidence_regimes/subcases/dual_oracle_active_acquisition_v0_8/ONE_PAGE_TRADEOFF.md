# ONE_PAGE_TRADEOFF — Dual‑Oracle + Candidate‑Pool Ablation (v0.8)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

---

## Panel A — PAE alarm learning curve (reporting holdout)

- X axis: cumulative **PAE** labels queried
- Y axis: TPR on PAE holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel B — MSA alarm learning curve (reporting holdout)

- X axis: cumulative **MSA** labels queried
- Y axis: TPR on MSA holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel C — Allocation over time

- X axis: round
- Y axis: fraction of this round’s queries allocated to PAE
- One curve per policy.

---

## Panel D — Joint gate frontier (event‑aware summary)

Define `joint_usable_round(policy)`:

- the earliest round where **both** alarms are usable on the **holdout** at the primary cap:
  - achieved FPR ≤ cap (within eps) and
  - TPR ≥ `tpr_min_for_usable`

Plot each policy as a point:

- X axis: `joint_usable_round` (lower is better; if never achieved, set to `rounds+1`)
- Y axis: final MAE of  $ \widehat{C3} $  on the MSA holdout (lower is better)

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae, tau_msa_depth
- primary FPR cap
- seed string
- feature whitelist hash
