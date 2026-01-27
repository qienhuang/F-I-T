# Toy World Menu v0.1 (for FIT-Explorer)
**Date**: 2026-01-27

This menu prioritizes worlds where:
- you can generate many runs cheaply,
- you can define a clean macro-event $t^*$,
- you can create controlled distribution shifts,
- you can validate feasibility gates.

---

## A. Discrete "particle-ish" worlds

### A1. Stochastic Majority Cellular Automaton (included demo)
- micro: binary grid
- update: majority-of-neighbors with noise probability $p(t)$
- macro: order parameter (magnetization) collapses as noise increases
- event $t^*$: first time magnetization < threshold

Pros:
- cheap, controllable phase-like transition
- rich multi-scale structure (good for coarse-graining search)

Practical note:
- Use an *ordered* initial condition (high magnetization) so the event is not triggered at $t=0$.

### A2. Game of Life with perturbation schedule
- micro: classic GoL
- macro: activity decays to attractors
- event: "stabilization" (activity -> 0) or "explosion" (activity above bound)

Pros:
- fast; clear attractors
- cons: event depends strongly on initial conditions (good for robustness stress)

---

## B. Continuous worlds (still cheap)

### B1. Logistic map with slowly varying parameter
- micro: scalar $x_t$
- macro: periodic -> chaotic transition
- event: Lyapunov proxy crosses threshold

Pros:
- analytically understood; perfect sanity check
- cons: may be too simple for representation search

### B2. Kuramoto-like phase oscillators (small N)
- micro: phases on a graph
- macro: synchronization order parameter
- event: desynchronization under noise schedule

Pros:
- natural multi-scale coarse-graining (communities)
- cons: more compute than CA but still cheap

---

## C. Agent worlds (bridging to your agent work)

### C1. Simple resource economy (stocks/flows)
- micro: agents with inventories; trading
- macro: crash/illiquidity event $t^*$
- event: price volatility or default cascade

Pros:
- connects to governance/monitorability
- cons: requires more careful boundary preregistration

---

## Recommendation

Start with A1 (included). Once gates and failure maps behave as expected, move to B2 or C1.
