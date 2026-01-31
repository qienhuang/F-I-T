# ONE_PAGE_TRADEOFF — Dual‑Oracle + Regime Diagnostics (v1.0)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

---

## Panel A — PAE learning curve (reporting holdout)

- X axis: cumulative **PAE** labels queried
- Y axis: TPR on PAE holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel B — MSA learning curve (reporting holdout)

- X axis: cumulative **MSA** labels queried
- Y axis: TPR on MSA holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel C — Allocation over time

- X axis: round
- Y axis: fraction of this round’s queries allocated to PAE
- One curve per policy.

---

## Panel D — Regime event markers (phase‑like audit)

For each policy (sorted by earliest joint usability), place three markers on a horizontal row:

- marker 1: `E_floor_resolved_pae_round`  
- marker 2: `E_floor_resolved_msa_round`  
- marker 3: `E_joint_usable_round`

Interpretation:

- early floor resolution without joint usability implies “floor fixed, but still not usable”
- joint usability without floor resolution should not occur (flag as audit failure)

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae, tau_msa_depth
- primary FPR cap
- seed string
- feature whitelist hash
