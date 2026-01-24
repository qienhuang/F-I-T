# FIT Core Card (v2.4.1+)

Status: **core artifact** (one-page operational entry). For the full specification and EST details, see [`docs/v2.4.md`](../v2.4.md) and the update note [`docs/v2.4.1.md`](../v2.4.1.md).

Navigation: [`core index`](./README.md) | [`MCC`](./MCC.md) | [`Phase Algebra`](./phase_algebra.md) | [`Φ₃ stability`](./phi3_stability.md) | [`How to falsify FIT`](./how_to_falsify_fit.md) | [`Reconstruction guide`](./reconstruction_guide.md)

Notation: phases are written as `Φ₁/Φ₂/Φ₃` (ASCII: `Phi1/Phi2/Phi3` in filenames/code).

## 1) One-sentence definition

> **FIT is a phase-structured framework for analyzing how structure forms, stabilizes, and becomes effectively irreversible in evolving systems, via the interaction of Force, Information, Time, and emergent Constraints (under explicit estimator scope).**

## 2) Minimal variables (F / I / T / C)

### Force (F)

Propagatable drive that can cross levels/subsystems and reshape structure. If Force cannot propagate, the system exhibits only local perturbations.

### Information (I)

Structure that can be stably preserved across time. Short-term fit or transient patterns do not count by default.

### Time (T)

Tempo/direction of evolution that defines irreversibility and waiting cost. Time is not just a parameter; it acts as a stability filter.

### Constraint (C)

Reachable-state-space contraction induced by stabilized information. Constraints are not external rules; they are byproducts of stable structure.

## 3) Phase (Phi) as a first-class object

> A Phase is not a time segment; it is a dynamical type under a given constraint structure (EST-scoped).

Canonical phase labels (the minimal basis used in the core docs):
- **Φ₁ (Accumulation)**: Force exists but cannot stably write structure.
- **Φ₂ (Crystallization)**: local structures stabilize; subsystems remain weakly coordinated.
- **Φ₃ (Coordination)**: global constraints modulate substructures; stability becomes transferable.

See [`phase_algebra.md`](./phase_algebra.md) for the operational definition and composition rules.

## 4) PT-MSS (minimum phase-transition criterion)

Register a phase transition only when, within a declared observation window `W`, all three signal classes co-occur:
1. **Force redistribution** (propagation pathways change)
2. **Information re-encoding** (representation/carrier changes)
3. **Constraint reorganization** (non-smooth re-wiring of constraint proxies)

See [`phase_algebra.md`](./phase_algebra.md) for the operational definition.

## 5) Minimal coherent core (MCC)

If a reader accepts the six MCC assertions, they have the minimal FIT skeleton; everything else is an expansion under estimator scope.

See [`MCC.md`](./MCC.md) and [`MCC_graph.md`](./MCC_graph.md).

## 6) Red lines (what FIT is not)

- Not a value-judgment framework.
- Not a guarantee of "progress" or "improvement".
- Not a predictor of specific events/trajectories in complex systems.
- Not a replacement for domain theories (it is a meta-language).
