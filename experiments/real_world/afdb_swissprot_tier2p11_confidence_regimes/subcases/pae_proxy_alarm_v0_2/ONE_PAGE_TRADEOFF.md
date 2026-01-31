# ONE_PAGE_TRADEOFF — Active Acquisition (PAE Proxy Alarm v0.2)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager makes the acquisition story **operational** (budgeted learning), not narrative.

---

## Panel A — Coverage at low FPR vs oracle budget

- X axis: total labels queried (including init set)
- Y axis: TPR on holdout at the **primary FPR cap**
- One curve per policy.

Purpose: “How quickly do we get usable coverage under budget”

---

## Panel B — Constraint satisfaction (achieved FPR vs budget)

- X axis: total labels queried
- Y axis: achieved FPR on holdout at the operating threshold selected on labeled‑val
- Show the primary FPR cap as a horizontal reference.

Purpose: verify that policies are compared under the same false‑positive constraint.

---

## Panel C — Positive discovery rate in queried batches

- X axis: acquisition round
- Y axis: fraction of queried batch that are positive events (PAE event)

Purpose: visualize whether a policy efficiently finds rare positives.

---

## Panel D — Efficiency summary (AUTC bar)

Compute AUTC = area under the curve of Panel A (TPR vs queried labels) up to the final budget.

Plot one bar per policy.

Purpose: a single comparable “learning efficiency” scalar.

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae
- primary FPR cap
- split seed string
- feature whitelist hash
