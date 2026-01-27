# Gates and Failure Labels for Mathematical Discovery (v0.1.1)
**Date**: 2026-01-27

This replaces/updates v0.1 to address two clarifications:
1) “FPR=0” must be stated precisely (kernel soundness vs discovery reliability).  
2) Explorer vs Verifier must be separated conceptually, even if coupled in one system.

---

## 1. Gates (feasibility-first)

### Gate G1 — Checkability (hard)
A candidate must be expressible and checkable under the declared system.

- Pass condition: the verifier accepts the artifact (type-check / kernel-check).  
- Fail label: `UNCHECKABLE`.

### Gate G2 — Budget (hard)
A candidate must verify within preregistered resource limits:
- max search steps
- max memory
- max wall time
- max lemma/tactic calls

Budget overrun is not “false”; it is “not operational under this budget”.

- Fail label: `BUDGET_INCONCLUSIVE`.

### Gate G3 — Robustness (recommended)
Behavior should be stable under preregistered representation sweeps.

- Evaluate flip rate under sweeps (see `representation_sweeps_v0.1.1.md`).  
- Fail label: `REPRESENTATION_UNSTABLE`.

### Gate G4 — Governance (system-level, optional but recommended for agents)
If discovery is performed by an agent with tools:
- lemma/skill growth requires admission gates
- ingestion must respect provenance boundaries
- monitorability collapse triggers ABSTAIN

Governance failures are not “lower utility”; they block optimization.

---

## 2. Canonical failure labels (standard taxonomy)

Use exactly one primary label per failure (secondary labels optional).

- **SUPPORTED**: passes feasibility gates and meets preregistered utility thresholds, with an evidence chain to verifier artifacts.
- **UNCHECKABLE**: cannot be formalized or fails the verifier gate.
- **BUDGET_INCONCLUSIVE**: could be true, but not verified within budget.
- **REPRESENTATION_UNSTABLE**: outcome flips under admissible representation sweeps above bound.
- **SCOPE_LIMITED**: depends on boundary choices; requires explicit scope statement.
- **HEURISTIC_FLOOR**: the explorer heuristic provides no discriminative guidance; success rate is flat across budget multipliers.
- **COMPOSITIONAL_HAZARD**: safe components compose into invalid/unsafe behavior.
- **INGESTION_POISON_RISK**: external content influences method library without provenance.

---

## 3. The “FPR≈0” nuance (precise statement)

- **Verifier layer**: under a sound kernel and correct encoding, false accept probability is treated as approximately 0.  
- **Explorer layer**: proposals and heuristics can still be wrong, brittle, or non-reproducible.

Therefore:
- FIT-Math is about **discovery reliability** (heuristics, representation stability, budgets), not redefining proof correctness.
- A `SUPPORTED` label requires a verifier-linked evidence chain (see `explorer_verifier_interface_v0.1.1.md`).

---

## 4. HEURISTIC_FLOOR: operational definition

A heuristic is considered to have a floor if, over a preregistered evaluation window:

1) success rate is flat across budget tiers (e.g., 10k → 50k → 200k steps), and  
2) search statistics show no concentration of progress (no measurable discrimination).

Interpretation:
- The heuristic is not usable for navigation under this boundary and representation.
- Required response is not “more compute”, but an actuator on representation/strategy.

---

## 5. ABSTAIN semantics

ABSTAIN is correct behavior when gate validity is compromised (or governance fails).

- ABSTAIN prevents “narrative rescue” from being counted as progress.  
- ABSTAIN triggers conservative mode:
  - stop claiming SUPPORT
  - tighten scope or relock experiments
  - require new preregistration for boundary changes

---

## 6. Scope discipline (avoid overclaiming)

This framework does **not** claim to “unify mathematics”.
It claims to provide:
- an auditable exploration protocol,
- feasibility-first gates,
- failure maps as first-class outputs.

Any historical analogy must be framed as:
- a workflow metaphor,
- not a complete explanation of mathematical progress.

