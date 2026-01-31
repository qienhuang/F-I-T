# PROMPT_GUIDE — local CLI assistant (v0.4)

---

## Prompt 0 — guardrails (boundary + claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are **oracle labels** only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Use decision trace + one‑pager as the primary evidence.
5) If achieved FPR violates the cap materially, label the operating point invalid.

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
- one table: per policy final TPR@cap for PAE and MSA, final MAE(C3_hat), and joint_usable_round

---

## Prompt 1 — decision trace audit (EST hygiene)

Audit `decision_trace.csv`:

- deterministic ordering (same seed → same trace)
- no label leaks (labels only appear after queried)
- budgets respected per oracle
- no repeated (accession, oracle_type) queries

Output: pass/fail checklist.

---

## Prompt 2 — joint gate result

Using `round_metrics.json`, compute for each policy:

- `joint_usable_round` (first round both alarms usable at cap)
- if never achieved, report “NOT OPERATIONAL under this boundary + budget”.

No speculation; numbers only.

---

## Prompt 3 — next policy design (boundary‑preserving)

Suggest one improvement that stays within B0 features, e.g.:

- exploration/exploitation mixing per oracle
- diversity term in feature space (farthest‑first) within each oracle
- dynamic per‑oracle batch sizing to minimize `joint_usable_round`

If you add new policies, update prereg and treat as a new study.
