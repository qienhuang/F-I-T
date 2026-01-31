# PROMPT_GUIDE — local CLI assistant (v0.6)

---

## Prompt 0 — guardrails (boundary + claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Use decision trace + one‑pager as primary evidence.
5) If achieved FPR violates the cap materially, label that operating point invalid.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv
- out/<run_id>/round_metrics.json

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- one table: per policy final PAE TPR@cap, final MSA TPR@cap, joint_usable_round, final MAE(C3_hat)

---

## Prompt 1 — decision trace audit (EST hygiene)

Audit `decision_trace.csv`:

- deterministic ordering (same seed → same trace)
- no label leaks (labels only appear after queried)
- per‑oracle budgets respected
- no repeated (accession, oracle_type)
- `composite_batch_ff` actually shows increasing novelty within the batch (sanity check)

Output: pass/fail checklist.

---

## Prompt 2 — joint gate outcome

Using `round_metrics.json`, compute for each policy:

- `joint_usable_round` (first round both alarms usable at cap and TPR ≥ tpr_min)
- if never achieved, report “NOT OPERATIONAL under this boundary + budget”.

No speculation; numbers only.

---

## Prompt 3 — batch diversity check

For each policy where ranking is `composite_batch_ff`:

- compute mean novelty of selected points per round per oracle
- compare to `uncertainty` ranking

Goal: demonstrate diversity is not just a label; it is a measured behavior in the decision trace.
