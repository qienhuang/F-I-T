# ONE_PAGE_TRADEOFF — Dual‑Oracle + Δ‑Lag + Joint Coverage Jump + Cost (v1.9)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager is the “policy comparison surface” for FIT readers:

- Panels A/B: **monitorability** under a low‑FPR cap (TPR@cap)
- Panel C: **boundary acquisition** behavior (how cost is allocated)
- Panel D: **phase-like event markers** (Δ‑lag + joint coverage jump)

---

## Panel A — PAE learning curve (holdout)

- X axis: cumulative **PAE cost** ( `pae_queried * pae_unit_cost` )
- Y axis: TPR on PAE holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel B — MSA learning curve (holdout)

- X axis: cumulative **MSA cost** ( `msa_queried * msa_unit_cost` )
- Y axis: TPR on MSA holdout at the **primary FPR cap**
- One curve per policy.

---

## Panel C — Allocation over time (cost share to PAE)

- X axis: round index
- Y axis: fraction of **per-round cost** allocated to PAE

This replaces “fraction of queries” when oracle unit costs differ.

---

## Panel D — Event timeline (round-index)

Markers (per policy):

- PAE floor resolved
- MSA floor resolved
- joint usable@cap
- `E_covjump_joint` (joint coverage jump)

And a segment drawn from:

- `r_floor_max` (max of the two floor‑resolved rounds)
to
- `r_joint_usable`

This segment length is the Δ‑lag in rounds.

---

## Interpretation rule (do not violate)

Treat this page as *evidence* only under the locked prereg boundary:

- If leakage audit fails → refuse to interpret.
- If FPR floors persist → alarms are not deployable, even if AUC is high.
- If `E_covjump_joint` never occurs → report **NOT EVALUABLE UNDER BOUNDARY** for jump-style claims.
