# PROMPT_GUIDE — local CLI assistant (v0.8)

---

## Prompt 0 — guardrails (boundary + event claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Event claims must be grounded in `event_summary.json` and `round_metrics.json`.
5) Candidate pool ablation claims must be grounded in `decision_trace.csv`.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/event_summary.json
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv
- out/<run_id>/allocation_trace.csv
- out/<run_id>/round_metrics.json

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- one table: per policy
  - `E_joint_usable_round`
  - `E_covjump_pae_round`
  - `E_covjump_msa_round`
  - final PAE TPR@cap, final MSA TPR@cap, final MAE(C3_hat)

---

## Prompt 1 — candidate pool ablation audit

From `decision_trace.csv`:

- filter to policies with `ranking_policy` in {`composite_batch_ff_uK`, `composite_batch_ff_rK`}
- compare:
  - mean novelty per round
  - mean uncertainty_norm per round
- check the `candidate_pool_basis_used` column is correct and stable.

Deliver: 10‑line audit summary + one minimal table.

---

## Prompt 2 — event‑centric narrative

Use `event_summary.json`:

- identify which policy achieves `E_joint_usable` earliest
- identify which policy achieves PAE covjump earliest
- identify if MSA covjump occurs at all under the budget

Then cross‑check with the one‑page PDF.

Deliver: 1‑page narrative with explicit falsifiable statements.
