# PROMPT_GUIDE — using a local CLI assistant for the PAE Proxy Alarm case

Use these prompts to keep the analysis **EST‑disciplined**.

---

## Prompt 0 — boundary and claims guardrail (always first)

You are assisting with a FIT/EST alarm case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) Do not allow PAE fields as features; PAE is label/oracle only.
3) Report alarm usability only at low FPR operating points.
4) If TPR is 0 at target FPR, label the alarm unusable at that FPR.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/tradeoff_onepage.pdf

Outputs:
- 1 paragraph: what is safe to claim
- 1 paragraph: what is unsafe to claim
- 1 paragraph: the boundary split (train vs deploy)

---

## Prompt 1 — “numbers only” audit

Compute:
- test ROC‑AUC, PR‑AUC
- for each target FPR: achieved FPR, TPR, precision, flagged_per_10k, missed_per_10k

Do not explain why; only report values.

---

## Prompt 2 — interpretability (bounded)

Given the feature coefficients (logistic regression):
- list top positive and negative coefficients
- explain them only as “proxy correlations” under the locked boundary
- do not claim causal structure

---

## Prompt 3 — next experiment design

Suggest one extension that preserves boundary discipline, e.g.:
- add geometric features derived from coords (declare as boundary expansion)
- add active acquisition loop: choose which accessions to retrieve PAE for next
