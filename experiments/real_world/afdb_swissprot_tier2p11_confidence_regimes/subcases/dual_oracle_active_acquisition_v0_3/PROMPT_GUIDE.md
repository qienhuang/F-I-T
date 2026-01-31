# PROMPT_GUIDE — local CLI assistant for Dual‑Oracle Active Acquisition (v0.3)

---

## Prompt 0 — guardrails (boundary + claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `out/<run_id>/PREREG.locked.yaml` as the spec.
2) PAE/MSA are **oracle labels** only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Use decision trace + one‑pager as the primary evidence, not narrative.
5) If achieved FPR violates the cap materially, label that comparison invalid.

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
- one table: per policy final TPR@cap for PAE and MSA + AUTC totals

---

## Prompt 1 — decision trace audit (EST hygiene)

Audit `decision_trace.csv`:

- deterministic ordering (same seed → same trace)
- no label leaks (labels only appear after queried)
- budgets respected per oracle
- no repeated queries for the same (accession, oracle_type) pair

Output: pass/fail checklist.

---

## Prompt 2 — coverage jump events

Using `round_metrics.json`, detect for each policy:

- whether `E_covjump_pae` occurred and at which round
- whether `E_covjump_msa` occurred and at which round

Do not speculate why; report only.

---

## Prompt 3 — next policy design (boundary‑preserving)

Suggest one improvement that stays within B0 features, e.g.:

- exploration/exploitation mixing for each oracle
- per‑oracle diversity term (farthest‑first in feature space)
- adaptive per‑oracle batch sizing to satisfy a joint usability criterion

If you add new policies, update prereg and treat as a new study.
