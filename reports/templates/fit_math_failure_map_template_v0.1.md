# FIT-Math Failure Map Template v0.1
**Date**: 2026-01-27

Use this template to report method-space phase diagrams for math discovery.

---

## 1. Boundary (locked)
- system: (Lean/Coq/Isabelle/…)
- axioms / theory fragment:
- object domain:
- admissible transformations (equivalences/isomorphisms):

---

## 2. Axes (method space parameterization)

Choose up to 3 axes:
- representation family
- lemma template set size
- strategy policy
- budget tier (proof steps)

---

## 3. Labels (primary)

- `SUPPORTED`
- `UNCHECKABLE`
- `BUDGET_INCONCLUSIVE`
- `REPRESENTATION_UNSTABLE`
- `SCOPE_LIMITED`
- `HEURISTIC_FLOOR`

---

## 4. Evidence per region (required)

For each region:
- sample count
- gate pass rates
- budget success curve (success vs steps)
- flip rate under representation sweeps
- example candidates (ids + params)

---

## 5. Interpretation (required)

Write 3 paragraphs:
1) feasible frontier geometry (where success lives)
2) dominant failure mechanism bounding the frontier
3) suggested actuators to move the frontier (new invariants, lemmas, strategies)

---

## 6. Negative results (required)

List at least 3 “dead regions” with evidence.  
Do not omit failures; the failure map is part of the contribution.

