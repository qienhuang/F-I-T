# PROMPT_GUIDE — Local Codex / Claude Code (v0.5)

This guide assumes you are reading a completed run directory:

- `out/<run_id>/PREREG.locked.yaml`
- `out/<run_id>/eval_report.md`
- `out/<run_id>/tradeoff_onepage.pdf`
- `out/<run_id>/decision_trace.csv`
- `out/<run_id>/round_metrics.json`

---

## Prompt 0 — guardrails (boundary + claims)

You are assisting with a FIT/EST protocol case.

Rules:
1) Treat `PREREG.locked.yaml` as the spec.
2) PAE/MSA are **oracle labels** only; they must not be used as features.
3) Compare policies under the **primary FPR cap**, not just AUC.
4) Use decision trace + one‑pager as the primary evidence.
5) If achieved FPR violates the cap materially, label the operating point invalid.

Output:
- safe claims (numbers only)
- unsafe claims (common failure modes)
- one table: per policy final TPR@cap (PAE and MSA), `joint_usable_round`, final MAE(  $ \widehat{C3} $  )

---

## Prompt 1 — decision trace audit (EST hygiene)

Audit `decision_trace.csv`:

- deterministic ordering (same seed → same trace)
- no label leaks (labels only appear after queried)
- budgets respected per oracle
- no repeated `(accession, oracle_type)` queries

Output: pass/fail checklist with evidence lines.

---

## Prompt 2 — ranking policy explanation (composite vs uncertainty)

For policies with `__composite`, explain concretely:

- what `uncertainty` means (distance to 0.5),
- what `novelty` means (min distance to labeled set in z‑scored B0 space),
- how `composite_score` is computed from prereg alpha.

Then verify from trace that top picks have higher composite scores than median picks.

---

## Prompt 3 — design a new policy without expanding boundary

Suggest one new preregisterable policy that stays inside B0 features, e.g.:

- exploration/exploitation mixing per oracle
- diversity term using farthest‑first (sequential novelty) rather than batch novelty
- allocation that directly optimizes `joint_usable_round` under fixed per‑round budget

If you add new policies, update prereg and treat as a new study.
