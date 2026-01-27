# Gates and Failure Labels for Mathematical Discovery (v0.1)
**Date**: 2026-01-27

This document defines feasibility gates and canonical failure labels.

---

## 1. Gates (feasibility-first)

### Gate G1 — Checkability (hard)
A candidate must be expressible and checkable under the declared system.
If it cannot be encoded or the checker rejects it, the candidate is infeasible.

### Gate G2 — Budget (hard)
A candidate must be verifiable within preregistered limits:
- max search steps
- max memory
- max wall time
- max lemma/tactic calls

Budget failure is not “false”; it is “not operational under this budget”.

### Gate G3 — Robustness (recommended)
Candidate behavior should be stable under admissible transformations:
- equivalent definitions
- harmless reparameterizations
- small window/representation changes

Robustness is evaluated by preregistered sweeps.

### Gate G4 — Governance (system-level, optional)
If the discovery system is an agent with tools:
- skill/lemma library growth must pass Skill Admission Gate
- ingestion must respect Web Ingestion Boundary
- monitorability collapse triggers ABSTAIN / conservative mode

---

## 2. Canonical failure labels (standard taxonomy)

Use exactly one primary label per failure (secondary labels optional).

- **UNCHECKABLE**: cannot be formalized or fails proof-checker gate.
- **BUDGET_INCONCLUSIVE**: could be true, but not found/verified within budget.
- **REPRESENTATION_UNSTABLE**: success flips under admissible representation changes.
- **SCOPE_LIMITED**: depends on boundary choices; requires explicit scope statement.
- **HEURISTIC_FLOOR**: navigation heuristic provides no signal; search degenerates.
- **COMPOSITIONAL_HAZARD**: safe components compose into unsafe/invalid results.
- **INGESTION_POISON_RISK**: external content influences method library without provenance.
- **SUPPORTED**: passes gates and meets preregistered utility thresholds.

---

## 3. The HEURISTIC_FLOOR concept (math analog of FPR_FLOOR)

In empirical monitoring, an unusable detector may exhibit an FPR floor.

In math discovery, a navigation heuristic may exhibit a “floor” in a different sense:
- it repeatedly prioritizes unproductive branches,
- it fails to discriminate promising vs dead regions,
- increasing search effort does not improve success rate.

Operational test:
- success rate is flat across budget multipliers within a window,
- and the search tree statistics show no meaningful concentration of progress.

Label: **HEURISTIC_FLOOR**.

---

## 4. ABSTAIN semantics

- **ABSTAIN** is correct behavior when gates fail.
- ABSTAIN prevents post-hoc narratives from being treated as method improvements.
- ABSTAIN triggers conservative mode or scope restriction.

