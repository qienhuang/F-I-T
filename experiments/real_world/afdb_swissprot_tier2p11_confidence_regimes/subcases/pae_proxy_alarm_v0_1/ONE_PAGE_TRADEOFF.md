# ONE_PAGE_TRADEOFF — PAE Proxy Alarm (v0.1)

**Output:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

This one‑pager is designed to force a **monitorability‑first** interpretation.

---

## Panel A — ROC curve + operating points

- Plot ROC (TPR vs FPR) on the **test** split.
- Mark each target FPR in `monitorability.fpr_targets` using the threshold selected on the **validation** split.

---

## Panel B — Coverage vs FPR (alarm usability curve)

- Plot TPR as a function of FPR across thresholds on the **test** split.
- Annotate whether each target FPR yields **TPR > 0**.
- If TPR is 0 at a target FPR, label that operating point as **UNUSABLE**.

---

## Panel C — Score distributions (neg vs pos)

- Show predicted probability (or score) histogram / KDE:
  - negatives (no PAE event)
  - positives (PAE event)
- Purpose: make the “FPR floor / overlap” visually obvious.

---

## Panel D — Budget view (flagged volume vs missed events)

At each target FPR operating point, report:

- `flagged_per_10k`
- `missed_events_per_10k` (false negatives per 10k)
- achieved FPR / TPR / precision

This panel is the “engineering trade‑off” representation.

---

## Footer (mandatory)

Include:
- subcase id + run id
- parent case id
- tau_pae
- split seed string
- feature whitelist hash
