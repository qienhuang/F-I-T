# FIT as a Mathematical Discovery Engine v0.1
*Turning FIT/EST + FIT-Explorer into a constraint-driven, auditable discovery workflow for definitions, invariants, lemmas, and proof strategies.*

**Status**: repo-ready draft (v0.1)
**Date**: 2026-01-27
**Author**: Qien Huang
**License**: CC BY 4.0

---

## 0. Why this document exists

You observed a deep analogy:

- The physical world "evolves" from micro variables $x_t$ via layered aggregation.
- Full micro-simulation is computationally intractable.
- Mathematics is a human-discovered compression: it invents **effective variables** and **direct mappings**.

This document makes that analogy operational:

> FIT/EST is not only for empirical evaluation.
> It can be used as a **discovery discipline**: a budgeted, constraint-first explorer that searches for *effective representations* and *effective proof structure*.

---

## 1. What FIT means in mathematics (the key translation)

Mathematics is different from empirical science:

- Truth is not probabilistic once formalized and proof-checked.
- But *discovery* (finding the right definitions/lemmas/strategies) is a search problem under constraints.

So FIT in math should target the **discovery process**, not "truth itself".

### 1.1 Micro → Macro mapping (world-evolution view)

We use a generic structure:

- micro state: $x_t$
- micro evolution: $x_{t+1} = F(x_t)$
- macro quantity: $y_t = h(x_t)$

The "math move" introduces effective variables:

- coarse-graining: $z_t = g(x_t)$
- effective dynamics: $z_{t+1} \approx \tilde{F}(z_t)$
- macro prediction/control: $y_t \approx \tilde{h}(z_t)$

The discovery question is: how to find good $g, \tilde{F}, \tilde{h}$ **under constraints**.

### 1.2 Proof discovery as a constrained search

Replace "prediction" by "proof construction":

- objects: definitions, invariants, lemmas, tactics, proof plans
- validator: a proof checker kernel (or a strict verifier)
- budget: proof search time/steps, lemma library size, tactic complexity
- output: not just a proof, but a **failure map** (what regions of method space systematically fail)

---

## 2. FIT-Explorer for mathematics: the core loop

The loop is:

1. **Explore**: generate candidate "methods" (representation + lemma + strategy).
2. **Gate**: reject candidates that fail *hard constraints*.
3. **Optimize**: within feasible region, improve utility (compression, reuse, stability).
4. **Map**: record failure regions as a "phase diagram" of method space.

This is analogous to constrained architecture search (BioArc-style) but for mathematical method primitives.

---

## 3. What is a "candidate method" in this setting?

A candidate is not "a theorem". It is a pipeline.

### 3.1 Candidate types

- **Representation candidate**: proposes a new variable/invariant family $g(x)$
- **Lemma candidate**: proposes intermediate statements that reduce proof depth
- **Strategy candidate**: proposes a proof plan / tactic graph
- **Composite candidate**: (representation + lemma library + strategy policy)

### 3.2 Candidate must declare scope (boundary)

Every candidate must specify:
- formal system boundary (axioms / theory / type discipline)
- domain of objects (structures, operations)
- admissible transformations (equivalences/isomorphisms)

Boundary changes are **not allowed post hoc**; they are a new preregistered trial.

---

## 4. Hard gates (feasibility-first)

In empirical monitorability, you use "FPR controllability" as an alarm admissibility gate.

In math discovery, use analogous gates:

1. **Checkability gate**: the candidate is formalizable and checkable under the chosen system.
2. **Budget gate**: proof/verification fits within declared compute limits.
3. **Robustness gate**: conclusions are stable under admissible equivalences / small representation changes.
4. **Governance gate** (system-level): candidate does not introduce untracked authority expansion (if running agents).

Details are in:
- `docs/math_discovery/gates_and_labels_v0.1.md`

---

## 5. Utility metrics (only after feasibility passes)

Utility is allowed to be multi-objective, but must be preregistered.

Typical utilities:
- **Compression**: shorter proofs, smaller lemma basis
- **Reuse**: lemma/invariant used across many targets
- **Stability**: little sensitivity to representation changes
- **Constructivity**: produces executable objects when required
- **Search cost**: fewer steps / lower branching factor

---

## 6. Failure map = "method phase diagram"

A core output is a phase-diagram-like artifact:

- axes: method parameters (representation family, lemma depth, tactic budget, etc.)
- colors: failure labels (UNCHECKABLE, BUDGET_INCONCLUSIVE, HEURISTIC_FLOOR, …)
- frontier: feasible/infeasible boundary

This provides the same kind of knowledge mathematics accumulates historically:
- where certain techniques work,
- where they systematically fail,
- and what new abstractions are required to move the frontier.

Use:
- `reports/templates/fit_math_failure_map_template_v0.1.1.md` (preferred)
- `reports/templates/fit_math_failure_map_template_v0.1.md` (legacy)

---

## 7. Relationship to "math discovery" in the human sense

Human mathematical progress often looks like:
- inventing a definition that collapses a complex family of instances into one invariant,
- discovering a lemma that shortens proof depth,
- creating a reusable technique that shifts the feasible frontier.

FIT-as-discovery makes this explicit and auditable:
- it logs why a technique was tried,
- which gate it failed,
- and which actuator was allowed next.

---

## 8. Minimal integration plan (practical)

Start in three phases:

### Phase A — Toy-world invariant discovery (fast)
- Use a controllable evolving world.
- Search for coarse-grainings $g$ that yield stable early warning under low false positive budgets.
- Output: "effective variable candidates" + failure map.

### Phase B — Formalization interface (medium)
- Translate best invariants into a formal language (Lean/Coq/Isabelle).
- Gate by checkability + budget + robustness.

### Phase C — Proof search scaling (slow)
- Add lemma library growth under admission gates.
- Add tactic search under budgets.
- Treat "library growth" as authority expansion: versioned, tested, rollbackable.

Roadmap in:
- `docs/math_discovery/roadmap_to_proof_assistants_v0.1.md`

---

## Appendix index

- `docs/math_discovery/mapping_table_v0.1.md`
- `docs/math_discovery/gates_and_labels_v0.1.md`
- `docs/math_discovery/search_spaces_v0.1.md`
- `docs/math_discovery/fit_math_synth_loop_v0.1.md`
- `docs/math_discovery/roadmap_to_proof_assistants_v0.1.md`
- `docs/math_discovery/examples/mini_case_study_toy_world_to_invariants.md`
