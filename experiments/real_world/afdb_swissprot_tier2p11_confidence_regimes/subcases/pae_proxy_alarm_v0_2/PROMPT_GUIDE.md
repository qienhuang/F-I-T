# PROMPT_GUIDE — local CLI assistant for v0.2 Active Acquisition

---

## Prompt 0 — boundary and claims guardrail

You are assisting with a FIT/EST active acquisition case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE is label/oracle only; PAE must not be used as a feature.
3) Compare policies only under the primary FPR cap.
4) Prefer “budgeted learning” claims (TPR vs queried labels), not storytelling.
5) If achieved FPR violates the cap materially, label the comparison invalid.

Inputs:
- README.md
- out/<run_id>/PREREG.locked.yaml
- out/<run_id>/eval_report.md
- out/<run_id>/tradeoff_onepage.pdf
- out/<run_id>/decision_trace.csv

Outputs:
- 1 paragraph: what is safe to claim
- 1 paragraph: what is unsafe to claim
- 1 paragraph: whether the event E_covjump occurred (and at which round) per policy

---

## Prompt 1 — numbers-only policy comparison

Produce a table:

- policy
- final queried labels
- final TPR@primaryFPR
- AUTC
- E_covjump_round (or None)

No explanations.

---

## Prompt 2 — decision trace audit (EST hygiene)

From `decision_trace.csv` verify:

- deterministic behavior (same seed → same trace)
- no label leaks (only queried items show revealed label at time of query)
- query budget matches the prereg

Output: a short audit checklist with pass/fail.

---

## Prompt 3 — next protocol improvement

Suggest one boundary‑preserving improvement:

- class‑balanced initial seed
- exploration/exploitation mix policy
- diversity term (feature-space farthest-first)

If you add a new policy family, update prereg and treat as a new study.
