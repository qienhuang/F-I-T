# PROMPT_GUIDE — Local Codex / Claude Code for MSA Deficit Proxy (v0.1)

---

## Prompt 0 — boundary and claims guardrail

You are assisting with a FIT/EST proxy‑estimator case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) Do not allow MSA fields as features; MSA is label/oracle only.
3) Report proxy quality as regression metrics + low‑FPR usability for `E_msa_sparse`.
4) If TPR is 0 at the target FPR, label the alarm unusable at that operating point.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/tradeoff_onepage.pdf

Outputs:
- safe claims (1 paragraph)
- unsafe claims (1 paragraph)
- a boundary summary (train vs deploy)

---

## Prompt 1 — numbers only

Report:

- MAE / RMSE / Spearman / R^2 (test)
- For each target FPR: achieved FPR, TPR, precision, flagged_per_10k, missed_per_10k

No explanations.

---

## Prompt 2 — how to use $ \widehat{C3} $ safely in FIT

Write a short note:
- how $ \widehat{C3} $ can be treated as an estimator channel under B0
- what coherence/monitorability checks must accompany it
- what would constitute boundary drift

Keep it protocol-level, not biology-level.
