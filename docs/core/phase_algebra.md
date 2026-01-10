# Phase Algebra + PT-MSS (v2.4.1+)

Status: **core artifact**. This document introduces a phase language that is compatible with EST and operationalizes "phase transition" as a registrable object via PT-MSS.

Navigation: [`core index`](./README.md) | [`Core Card`](./fit_core_card.md) | [`MCC`](./MCC.md) | [`Φ₃ stability`](./phi3_stability.md) | [`v2.4.1 update`](../v2.4.1.md)

Notation: phases are written as `Φ₁/Φ₂/Φ₃` (ASCII: `Phi1/Phi2/Phi3` in filenames/code).

## Why a Phase Algebra

Before v2.4.1, "phase/stage" could be read as narrative segmentation.
Phase Algebra makes Phase a first-class object that:
- is **estimator-scoped** (EST compliant),
- is **composable** (nested / parallel / restart),
- supports phase-conditional refinements (e.g., P2 in [`docs/v2.4.1.md`](../v2.4.1.md)).

## Definition: Phase (EST-scoped)

Under an explicit estimator specification (EST), a **Phase** is a set of states where:
1. the **Force propagation topology** remains (approximately) invariant,
2. the primary **Information storage substrate** does not undergo a structural jump,
3. the primary **Constraint growth mechanism** remains consistent.

A Phase change implies at least one of these conditions is broken (under the declared estimators and windowing).

## Canonical phase generators (minimal basis)

We use three canonical phase generators as a minimal basis:

### Φ₁ - Accumulation

- Force exists but cannot stably write structure.
- Information is mostly short-lived or superficial correlations.
- Constraint growth relies on external injection rather than internal coordination.

### Φ₂ - Crystallization

- Local structures stabilize.
- Subsystems evolve relatively independently.
- Constraints grow rapidly locally but remain globally inconsistent.

### Φ₃ - Coordination

- Substructures are modulated by global constraints.
- Redundant structures are suppressed.
- The system enters a durable, transferable stability regime.

## Composition rules (minimal)

Legal composition patterns include:
- **Nesting**: `Φ₃(Φ₂(Φ₁))`
- **Parallelism**: `Φ₂ || Φ₂` (multiple subsystems crystallize in parallel)
- **Restart**: `Φ₃ -> Φ₁` (new Force injection re-opens exploration)

## PT-MSS: Phase Transition Minimal Signal Set

Purpose: make "phase transition" registrable under EST, instead of a narrative label.

A Phase Transition is registered only when, within a declared window `W`, signals from all three classes occur together:

### (S1) Force redistribution

Evidence that Force propagation pathways changed (e.g., gradients begin entering a representation layer; external shocks rewrite internal weights).

### (S2) Information re-encoding

Evidence that the information carrier/representation changed (e.g., surface memory -> abstract feature; individual knowledge -> institutional rule).

### (S3) Constraint reorganization

Evidence that constraint proxies undergo a non-smooth reorganization (e.g., sudden dimension drop, correlation re-wiring, suppression of previously stable structures).

Decision rule (minimum form):

`register_transition := (S1 && S2 && S3) within W`

## Link to propositions

- P11 (existence of transitions) becomes operationally interpretable with PT-MSS.
- P13 (predictability of transitions) becomes measurable: "early vs synchronous detection" is evaluated relative to PT-MSS + EST estimator scope.

See also:
- [`docs/v2.4.md`](../v2.4.md) for the proposition registry (including phase-transition propositions).
- [`docs/est/diagnostics.md`](../est/diagnostics.md) for estimator/EST diagnostics and scope reporting.
