# How to Reconstruct FIT from MCC

Status: **core artifact**. A guide for new readers to regenerate the full framework from the minimal core.

Navigation: [`core index`](./README.md) | [`Core Card`](./fit_core_card.md) | [`MCC`](./MCC.md) | [`MCC graph`](./MCC_graph.md) | [`Phase Algebra`](./phase_algebra.md) | [`Phi3 stability`](./phi3_stability.md) | [`v2.4 spec`](../v2.4.md)

## Audience

This document is for:
- researchers who want to understand FIT deeply (not just apply it),
- potential contributors who need to extend FIT consistently,
- critics who want to locate the exact points of disagreement.

## The reconstruction principle

> FIT is designed to be regenerable, not just readable.

If you accept the 6 MCC assertions and the EST discipline, you can derive the rest. This document shows one clean reconstruction path.

## Step 0: Accept the starting point

You need exactly one foundational commitment:

> **MCC-1 (Force propagation)**: in an evolving system, changes are triggered by a propagatable drive. If this drive cannot cross levels/subsystems, only surface changes occur.

If you reject this, FIT is not for you. If you accept it, proceed.

## Step 1: Derive Information and Constraint

From MCC-1, ask: "What happens when Force successfully propagates?"

Two consequences emerge:
1. Some structures get written and persist (MCC-2: Information persistence)
2. Some states become unreachable (MCC-3: Constraint accumulation)

These are not extra axioms; they are the operational unpacking of "Force reshapes structure".

## Step 2: Derive Phase structure

From MCC-2 + MCC-3, ask: "Is structure formation smooth over time?"

Empirically and theoretically, no. Systems exhibit qualitatively different dynamical types at different times. This motivates:
- MCC-4: Phase-structured evolution
- a minimal phase basis: Phi1/Phi2/Phi3 (see [`phase_algebra.md`](./phase_algebra.md))

## Step 3: Make phase transitions registrable

From MCC-4, ask: "How do we know a phase transition occurred?"

Under EST, the answer cannot be intuition. It must be operational. This yields MCC-5:
- PT-MSS: register a transition only when Force redistribution, Information re-encoding, and Constraint reorganization co-occur within a declared window `W`.

See [`phase_algebra.md`](./phase_algebra.md).

## Step 4: Derive late-phase irreversibility

From MCC-5, ask: "What happens after repeated transitions and coordination?"

Observation: systems that reach a coordinated late phase tend to become resistant to reversal. This yields MCC-6:
- irreversibility is probabilistic (regressions become rare), not absolute.

See [`phi3_stability.md`](./phi3_stability.md) for an operational stability family that makes "late-phase" testable.

## Step 5: Expand to the proposition registry

The MCC skeleton expands into the proposition set in [`docs/v2.4.md`](../v2.4.md).

Important:
- proposition numbering and categorization are defined in [`docs/v2.4.md`](../v2.4.md),
- this guide does not attempt a 1:1 mapping of "MCC -> P#",
- propositions are estimator-scoped expansions, not new axioms.

Practical connection procedure:
1. use MCC to decide what kind of claim you are making (F / I / C / Phase / irreversibility),
2. pick the relevant proposition family in [`docs/v2.4.md`](../v2.4.md),
3. state estimator scope (EST) and admissibility/robustness checks.

## Step 6: Apply EST discipline

Every claim in FIT must be:
1. estimator-scoped (declare what you're measuring),
2. admissibility-checked (confirm estimator meets FIT criteria),
3. coherence-gated (reject estimates outside coherence bounds),
4. robustness-reported (show sensitivity to parameter choices).

See [`docs/est/diagnostics.md`](../est/diagnostics.md).

## Step 7: Generate domain applications

With MCC + EST, you can analyze any evolving system:
1. identify what counts as Force in this domain,
2. define estimators for Information and Constraint,
3. classify the current phase (Phi1/Phi2/Phi3),
4. look for PT-MSS signals,
5. evaluate stability with SC-1/SC-2/SC-3 (for late phases).

The evidence layer lives in `experiments/` and domain-specific docs.
