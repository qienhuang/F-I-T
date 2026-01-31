# PROMPT_GUIDE — local CLI assistant (v1.0)

---

## Prompt 0 — guardrails (boundary + event claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Event claims must be grounded in `event_summary.json` and `round_metrics.json`.
5) Regime claims must be grounded in `regime_timeline.csv` and `regime_summary.json`.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/event_summary.json
- out/<run_id>/regime_timeline.csv
- out/<run_id>/regime_summary.json
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv
- out/<run_id>/allocation_trace.csv
- out/<run_id>/round_metrics.json

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- one table: per policy
  - E_floor_resolved_pae_round
  - E_floor_resolved_msa_round
  - E_joint_usable_round
  - final PAE TPR@cap, final MSA TPR@cap
  - final FPR floors (PAE holdout, MSA holdout)
  - final MAE(C3_hat)

---

## Prompt 1 — regime timeline summary

Use `regime_timeline.csv` to answer:

- Which policies spend the longest time in `FPR_FLOOR`
- Which policies resolve floors early but still fail usability (remain `UNUSABLE`)

Deliver:
- 1 compact table (policy × first occurrence of each regime)
- 8 lines of interpretation with falsifiable claims.

---

## Prompt 2 — floor resolution vs joint usability

For each policy:

- compute `Δ = E_joint_usable_round - max(E_floor_resolved_pae_round, E_floor_resolved_msa_round)`

Interpret:
- small  Δ  means “once floors clear, usability arrives quickly”
- large  Δ  means “floors clear, but models still not good enough under cap”

Deliver:
- one ranked list by  Δ
- one paragraph of conclusions.
