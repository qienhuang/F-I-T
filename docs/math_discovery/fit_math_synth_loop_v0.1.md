# FIT-Math Synth Loop v0.1
**Date**: 2026-01-27

This loop makes “FIT as an explorer” concrete for mathematical discovery.

---

## 0. Core loop

1. **Generate** candidates (Explore)
2. **Diagnose** failure labels
3. **Select** admissible actuators (legal moves)
4. **Mutate** within actuators (budgeted)
5. **Lock** (preregister gates + budgets + stop conditions)
6. **Evaluate** (non-LLM validator)
7. **Record** (leaderboard + failure map)
8. Repeat

---

## 1. Admissible actuators (examples)

### Representation actuators
- change invariant family
- change scale parameters
- introduce a normalization / quotient
- change feature composition (evidence stack)

### Lemma actuators
- add lemma templates
- promote/demote lemmas by admission level
- add compositional regression tests

### Strategy actuators
- change tactic ordering
- cap branching factors
- change subgoal decomposition schemes

### Boundary actuators (restricted)
- boundary changes require a new preregistered experiment
- do not allow boundary edits to “save” a result

---

## 2. Stop conditions (Goodhart defense)

Preregister:
- maximum variants to try
- label to assign if not fixed (typically INCONCLUSIVE or SCOPE_LIMITED)
- requirement to report all variants

---

## 3. Outputs

- feasible leaderboard (SUPPORTED candidates)
- failure map (labels + evidence)
- provenance graph (candidate → mutations)

