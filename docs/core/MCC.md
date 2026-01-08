# FIT Minimal Coherent Core (MCC) - v2.4.1+

Status: **core artifact** (compressed theory entry). This is not an evidence document.

MCC goal: compress FIT into a minimal self-consistent skeleton such that an external reader can reconstruct the rest (propositions, EST layer, and domain case studies) without relying on the author.

Navigation: [`core index`](./README.md) | [`Core Card`](./fit_core_card.md) | [`MCC graph`](./MCC_graph.md) | [`Phase Algebra`](./phase_algebra.md) | [`Phi3 stability`](./phi3_stability.md) | [`Reconstruction guide`](./reconstruction_guide.md)

## Design constraints

1. **No new terms**: only uses `F / I / T / Phase / Constraint`.
2. **No case dependence**: cases are optional expansions, not the definition.
3. **No proposition-list dependence**: propositions are expansions; MCC is the core.

## MCC-1 - Force propagation

In an evolving system, changes are triggered by a **propagatable drive** (Force). If Force cannot propagate across levels/subsystems, the system exhibits only surface/local changes.

## MCC-2 - Information persistence

Only structures that can be **stably preserved across time** count as Information in the system. Short-term fit or transient patterns are not "learned structure" by default.

## MCC-3 - Constraint accumulation

Stable structure formation is accompanied by a **contraction of the reachable state-space**, induced by accumulated Constraints. Constraints are not external rules; they emerge as a byproduct of stabilized information.

## MCC-4 - Phase-structured evolution

Evolution is not globally smooth; it is segmented into **Phases** defined by distinct dynamical types under a given constraint structure.

## MCC-5 - Phase transition signals

A Phase Transition is registered only when **Force propagation**, **Information encoding**, and **Constraint structure** reorganize together (within an explicit observation window and estimator scope).

## MCC-6 - Late-phase irreversibility

Once a system enters a coordinated late phase (Phi3-style), large-scale structural regressions become rapidly unlikely over time. Irreversibility is probabilistic ("regressions become rare"), not "no change".

## Reconstruction notes (how MCC expands)

Given MCC, the rest of FIT can be reconstructed as:
- **Primitives + notation** (see [`docs/v2.4.md`](../v2.4.md))
- **EST discipline**: admissibility, equivalence/coherence gates, robustness reporting (see [`docs/v2.4.md`](../v2.4.md) and [`docs/est/diagnostics.md`](../est/diagnostics.md))
- **Proposition registry**: P1-P18 as expansions under explicit scope + estimators
- **Domain case studies**: auditable evidence layers (e.g., `experiments/`)

See also:
- [`MCC_graph.md`](./MCC_graph.md) (dependency graph)
- [`reconstruction_guide.md`](./reconstruction_guide.md) (step-by-step regeneration guide)
