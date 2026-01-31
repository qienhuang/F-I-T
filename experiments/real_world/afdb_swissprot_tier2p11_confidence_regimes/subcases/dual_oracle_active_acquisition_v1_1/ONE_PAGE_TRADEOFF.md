# ONE_PAGE_TRADEOFF — Dual‑Oracle + Δ‑Lag + Leakage Audit (v1.1)

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

## Panel D — Δ‑lag visualization (floor‑clear → joint‑usable)

For each policy (sorted by earliest joint usability), place markers:

- `r_floor_pae`  (PAE floor resolved round)
- `r_floor_msa`  (MSA floor resolved round)
- `r_joint`      (joint usable round)

Also draw a horizontal line segment from:

- `r_floor = max(r_floor_pae, r_floor_msa)`  to  `r_joint`

The segment length is  $ \Delta = r\_{joint} - r\_{floor} $ .

Interpretation:

- small segment: floor clears and joint usability arrives quickly
- long segment: floor clears early, but usability is delayed
- negative segment: audit warning (should not occur)

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae, tau_msa_depth
- primary FPR cap
- seed string
- feature whitelist hash
