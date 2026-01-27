# Actuator Selection Policy v0.1.1
*Turning the Synth Loop into an executable control policy: failure label → admissible actuators → priority → budgets → stop.*

**Status**: repo-ready patch (v0.1.1)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0  

---

## 0. Purpose

Feedback correctly identified a missing piece:

- We had “actuators” and “failure labels”.
- We did not specify **how to choose actuators** (so the loop risks degenerating into random mutation).

This policy is a minimal, deterministic, *budget-aware* chooser.

---

## 1. Principles

1. **Feasibility first**: fix gate failures before optimizing utility.  
2. **Minimal change first**: prefer the smallest actuator that can plausibly address the diagnosed failure.  
3. **Budgeted escalation**: increase budgets only after structural fixes fail.  
4. **Auditability**: every actuator application must cite its triggering label(s).  
5. **Stop conditions**: avoid infinite tweaking; preregister max variants per label.

---

## 2. Actuator classes

### A — Representation actuators
- A1: rename / reparameterize (sweep-level)
- A2: change invariant family
- A3: add normalization / quotient / canonicalization
- A4: multi-scale augmentation (compose coarse-grainings)

### B — Lemma actuators
- B1: add lemma template (bounded)
- B2: promote/demote lemma by admission level
- B3: add regression replay suite for lemma

### C — Strategy actuators
- C1: reorder tactics
- C2: cap branching / depth
- C3: change decomposition scheme

### D — Budget actuators
- D1: increase proof-search steps tier
- D2: increase wall time tier
- D3: increase lemma library max

### E — Boundary actuators (restricted)
- E1: tighten scope statement (make boundary explicit)
- E2: expand boundary (NEW preregistration only)

---

## 3. Decision table (primary label → policy)

| Primary label | What it means | First-line actuator priority | Budget escalation allowed? | Stop label if unresolved |
|---|---|---|---|---|
| `UNCHECKABLE` | cannot formalize / kernel rejects encoding | A2 → A3 → B1 (proof-friendly lemma) | **No** (don’t throw compute at uncheckable) | `UNCHECKABLE` |
| `BUDGET_INCONCLUSIVE` | checkable, but budget-limited | C1 → C2 → B1 → D1 → D2 | **Yes** (tiered) | `BUDGET_INCONCLUSIVE` |
| `REPRESENTATION_UNSTABLE` | flips under allowed sweeps | A3 → A2 → A4 → B3 | **Limited** (only after stability improves) | `REPRESENTATION_UNSTABLE` |
| `HEURISTIC_FLOOR` | heuristic provides no discriminative guidance | A2 → C3 → B1 (new lemma cues) | **Yes**, but only after changing heuristics | `HEURISTIC_FLOOR` |
| `SCOPE_LIMITED` | depends on boundary choices | E1 (explicit scope) → A2 (seek boundary-robust invariant) | **No** unless scope is tightened | `SCOPE_LIMITED` |
| `COMPOSITIONAL_HAZARD` | safe parts compose into failure | B3 → C2 → governance gates | **No** until regression suite passes | `COMPOSITIONAL_HAZARD` |
| `INGESTION_POISON_RISK` | provenance violated | governance: freeze ingestion, demote, audit | n/a | `INGESTION_POISON_RISK` |

Notes:
- This policy assumes representation sweeps exist (see `representation_sweeps_v0.1.1.md`).
- `INGESTION_POISON_RISK` and `COMPOSITIONAL_HAZARD` are “governance failures”; do not optimize utility until resolved.

---

## 4. Budget schedule (tiers)

Use discrete tiers (example):
- steps: 10k → 50k → 200k
- lemma_library_max: 50 → 200 → 1000
- time: 10s → 60s → 300s

**Hard rule**: do not escalate budget twice in a row without a structural actuator in between (prevents “compute laundering”).

---

## 5. Logging requirements

Every mutation record must include:

```yaml
mutation:
  parent_candidate_id: "math:..."
  child_candidate_id: "math:..."
  trigger_label: "BUDGET_INCONCLUSIVE"
  actuator_applied: "C2"
  justification: "cap branching to reduce search explosion"
  budgets_before: {steps: 50000}
  budgets_after: {steps: 50000}
```

If budgets change, record it explicitly and cite the tier schedule.

---

## 6. Minimal “chooser” pseudocode

1) Identify primary label.  
2) Select first-line actuator not yet tried.  
3) Apply once; re-evaluate.  
4) If still fails and label is budget-eligible, escalate one tier.  
5) Stop at `max_variants` and assign stop label.

