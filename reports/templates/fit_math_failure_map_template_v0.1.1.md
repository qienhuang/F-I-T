# FIT-Math Failure Map Template v0.1.1
**Date**: 2026-01-27

This template reports **method-space phase diagrams** for math discovery with mandatory evidence-chain fields.

---

## 1. Boundary (locked)
- system:
- axioms / theory fragment:
- object domain:
- admissible transformations (equivalences/isomorphisms):

---

## 2. Explorer–Verifier interface (required)
- verifier kernel + version:
- evidence artifacts:
  - verdict ids
  - proof object hashes (for `SUPPORTED`)
  - log hashes

---

## 3. Axes (method space parameterization)
Choose up to 3 axes:
- representation family
- lemma template set size
- strategy policy
- budget tier (proof steps)

---

## 4. Labels (primary)
- `SUPPORTED`
- `UNCHECKABLE`
- `BUDGET_INCONCLUSIVE`
- `REPRESENTATION_UNSTABLE`
- `SCOPE_LIMITED`
- `HEURISTIC_FLOOR`

---

## 5. Evidence per region (required)
For each region:
- sample count
- gate pass rates
- success vs budget curve
- flip rate under representation sweeps
- example candidates (ids + params)
- for any `SUPPORTED`: verdict id + proof hash + kernel/version

---

## 6. Interpretation (required)
Write 3 paragraphs:
1) feasible frontier geometry
2) dominant failure mechanism bounding the frontier
3) suggested actuators to move the frontier (cite actuator policy doc)

---

## 7. Negative results (required)
List at least 3 dead regions with evidence.
Do not omit failures; failure maps are part of the contribution.

---

## 8. Scope statement (required)
Explicitly state what this report *does not claim*:
- no “unifying mathematics” claim
- results are scoped to the locked boundary
- improvements are discovery-method improvements, not truth claims

