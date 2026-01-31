# PROMPT_GUIDE — local CLI assistant (v0.9)

---

## Prompt 0 — guardrails (boundary + event claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Event claims must be grounded in `event_summary.json` and `round_metrics.json`.
5) Alpha/K claims must be grounded in `decision_trace.csv` and the policy spec string.

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
  - E_joint_usable_round
  - E_covjump_pae_round
  - E_covjump_msa_round
  - final PAE TPR@cap, final MSA TPR@cap
  - final fpr_floor_at_tpr_min (PAE holdout, MSA holdout)
  - final MAE(C3_hat)

---

## Prompt 1 — alpha ablation summary

Group policies by:
- basis: uK vs rK
- K: 5000

Within each group:
- compare alpha=0.0 vs 0.7 vs 1.0 on:
  - earliest joint usable
  - PAE covjump round
  - MSA covjump round
  - whether FPR floors block usability

Deliver:
- 1 short table per basis (uK/rK)
- 5‑line interpretation with falsifiable statements.

---

## Prompt 2 — K ablation summary

Group policies by:
- basis: uK vs rK
- alpha: 0.7

Compare K=1000 vs 5000 vs 20000 on:
- event rounds
- final TPR@cap
- final FPR floors

Deliver:
- one compact table
- one paragraph: “what K buys” vs “what K doesn’t buy”.

---

## Prompt 3 — candidate pool basis audit

Filter to composite policies:

- verify `candidate_pool_basis_used` matches uK/rK mapping
- compute per round:
  - mean novelty_norm
  - mean uncertainty_norm
- show whether rK loses uncertainty but retains novelty (or not)

Deliver: 10‑line audit summary + one minimal table.
