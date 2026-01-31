# PROMPT_GUIDE — local CLI assistant (v0.7)

---

## Prompt 0 — guardrails (boundary + claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Use decision trace + allocation trace + one‑pager as primary evidence.
5) Policy decisions must use labeled **val** diagnostics only (no holdout).

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv
- out/<run_id>/allocation_trace.csv
- out/<run_id>/round_metrics.json

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- one table: per policy final PAE TPR@cap, final MSA TPR@cap, joint_usable_round, final MAE(C3_hat)

---

## Prompt 1 — allocation audit (does joint‑gap behave)

Audit `allocation_trace.csv`:

- When PAE has larger `gap_pae` than `gap_msa`, does `q_pae` increase
- When both gaps are ~0, does policy fall back to uncertainty allocation
- Are there any rounds where holdout metrics appear in the allocation trace (Should be NO.)

Output: 10‑line diagnostic summary.

---

## Prompt 2 — decision trace diversity audit

For policies using `composite_batch_ff`:

- compute mean novelty per oracle per round
- compare to `uncertainty`

Goal: demonstrate batch diversity is measured behavior (not a label).
