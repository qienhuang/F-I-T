# PROMPT_GUIDE — local CLI assistant (v1.9)

This guide assumes you have completed a run and you are reading artifacts under `out/<run_id>/`.

---

## Prompt 0 — guardrails (boundary + event claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are oracle labels only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Event claims must be grounded in `event_summary.json` and `round_metrics.json`.
5) Regime claims must be grounded in `regime_timeline.csv` and `regime_summary.json`.
6) Any validity claim must reference `leakage_audit.json`.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/event_summary.json
- out/<run_id>/regime_timeline.csv
- out/<run_id>/regime_summary.json
- out/<run_id>/leakage_audit.json
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv
- out/<run_id>/allocation_trace.csv
- out/<run_id>/round_metrics.json

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- one table: per policy
  - r_floor_pae, r_floor_msa, r_floor=max, r_joint
  - delta_lag
  - final PAE TPR@cap, final MSA TPR@cap
  - final FPR floors (PAE holdout, MSA holdout)
  - final MAE(C3_hat)
  - leakage_audit status

---

## Prompt 1 — regime timeline summary

Use `regime_timeline.csv` to answer:

- Which policies spend the longest time in `FPR_FLOOR`
- Which policies resolve floors early but still fail usability (remain `UNUSABLE`)

Deliver:
- 1 compact table (policy × first occurrence of each regime)
- 8 lines of interpretation with falsifiable claims.

---

## Prompt 2 — Δ‑lag ranking (floor‑clear → joint‑usable)

For each policy:

- compute  $ \Delta = r\_{joint} - \max(r^{pae}\_{floor}, r^{msa}\_{floor}) $

Interpret:
- small  $ \Delta $  means “once floors clear, usability arrives quickly”
- large  $ \Delta $  means “floors clear, but models still not good enough under cap”

Deliver:
- one ranked list by  $ \Delta $
- one paragraph of conclusions.

---

## Prompt 3 — leakage audit summary

Read `leakage_audit.json` and report:

- whether any holdout IDs were queried
- whether any duplicate (accession, oracle_type) queries exist
- whether any oracle features were used

If any fail: **invalidate** the run and stop interpretation.


---

## Prompt X — joint coverage jump (E_covjump_joint) interpretation

Read:

- `event_summary.json`
- `policy_table.csv`
- `policy_cards_index.md`
- one policy card under `policy_cards/`

Tasks:

1) For each policy, report whether `E_covjump_joint` is found and at which round.
2) Compare  `E_covjump_joint.round_index`  vs  `E_joint_usable.round_index` :
   - if equal (or within 1 round), the “jump” is mostly a boundary/monitorability phase transition
   - if delayed, explain what changed (TPR growth vs floor/failure signals) while staying within the prereg boundary
3) Use the policy card’s joint coverage plot as primary evidence.

Rules:

- Do not infer mechanistic claims beyond what is logged.
- Treat any policy with `leakage_pass=false` as non-interpretable.

