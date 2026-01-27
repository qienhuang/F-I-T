# Roadmap: From Toy Worlds to Proof Assistants (v0.1)
**Date**: 2026-01-27

This roadmap connects your world-evolution experiments to formal mathematical discovery.

---

## Stage 0 — Establish the discipline (now)
Goal: make exploration auditable and feasibility-first.

Deliverables:
- candidate schemas
- hard gates
- failure map reports
- budget policies

---

## Stage 1 — Toy worlds: discover effective variables (fast, compute-cheap)
Goal: learn how to discover invariants and operational early-warning signals under constraints.

Method:
- define a macro event  t*  (preregistered)
- define negative/positive windows
- search coarse-grainings  $ g(x) $  and detectors
- produce a phase diagram (failure map)

Success criteria:
- stable feasible region across seeds and schedules
- interpretable effective variable candidates

---

## Stage 2 — Formalize invariants (medium)
Goal: translate effective variables/invariants into a strict language.

Approach:
- choose a formal system boundary (Lean/Coq/Isabelle)
- implement invariants as definitions and prove simple properties:
  - boundedness
  - invariance under admissible transformations
  - monotonicity (if claimed)

Gate:
- checkability gate (must compile / type-check)
- budget gate (must finish within limits)

---

## Stage 3 — Lemma library growth under admission gates (slow)
Goal: turn repeated proof patterns into reusable skills.

Rules:
- versioned lemma/tactic artifacts
- regression suites (proof replay)
- promotion requires prereg tests

This is directly analogous to skill admission in your slow-evolving agent work.

---

## Stage 4 — Strategy search and scaling (very slow)
Goal: budgeted proof plan search with failure maps.

Key discipline:
- success rate vs budget curves
- detect HEURISTIC_FLOOR regions
- do not mistake “search luck” for robust method improvement

---

## Risk notes (honest)

- A proof assistant changes the unit of “feasibility” dramatically (excellent!)
- But formalization cost is real; start with small invariants and replayable proofs.
- The most valuable output is often the failure map and boundary dependence statements.

