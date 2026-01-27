# Budget Policy v0.1 (Successive Halving for FIT-Explorer)
**Date**: 2026-01-27

---

## Goal

Allocate compute to many candidates cheaply, then concentrate budget only on candidates that:

1) pass feasibility gates, and  
2) show non-trivial utility signals.

---

## Policy: 3-stage successive halving

Let initial candidate batch size be `N0`.

- Stage S0 (cheap): evaluate all `N0` at small budget (few steps / small seed set).
  - keep fraction `eta0` (e.g., 1/3)

- Stage S1 (gate): evaluate survivors at full gate budget (FPR controllability).
  - keep fraction `eta1` (e.g., 1/2)

- Stage S2 (utility+robustness): evaluate survivors at full utility budget (more seeds / longer horizon).
  - rank by utility and keep top-k.

This is compatible with:

- random search (candidates drawn each round)
- bandit sampling (eta-weighted arms)
- surrogate-guided sampling (sample near feasible frontier)

---

## Hard rule

Stage S2 is forbidden unless Stage S1 passed.

