# Φ₃ Stability Criteria (v2.4.1+)

Status: **core artifact**. Operationalizes late-phase stability (the engineering form of "nirvana") under EST.

Navigation: [`core index`](./README.md) | [`Core Card`](./fit_core_card.md) | [`Phase Algebra`](./phase_algebra.md) | [`v2.4.1 update`](../v2.4.1.md)

Notation: we write the phase as `Φ₃` (ASCII: `Phi3` in filenames/code, e.g. `phi3_stability.md`).

## Purpose

MCC-6 asserts that late-phase (Φ₃) systems exhibit irreversibility. But irreversibility is not binary; it admits degrees. This document defines a **stability-criterion family** that makes Φ₃ assessment operational under EST.

## The central question

> When is a system "in Φ₃"? How stable is "stable enough"?

Under EST, this is a measurement question: it depends on declared estimators, windows, and tolerances.

## Stability criterion family (SCF)

We define three tiers of stability criteria, ordered by stringency.

### SC-1: Structural persistence (weakest)

**Definition**: a system satisfies SC-1 if, under the declared estimator, the primary constraint structure persists for duration `tau_persist` without significant regression.

**Operational check (minimum form)**:

For an observation window `[t0, t0 + tau_persist]`, declare a constraint proxy `C(t)` and a tolerance `epsilon`.

SC-1 holds if:
- for all `t` in the window, `abs(C(t) - C(t0)) <= epsilon`

**Use case**: quick stability check; necessary but not sufficient for strong Φ₃.

### SC-2: Perturbation resilience (medium)

**Definition**: a system satisfies SC-2 if, after a bounded perturbation, it returns to a neighborhood of the original constraint structure within time `tau_recover`.

**Operational check (minimum form)**:

Declare:
- a perturbation budget `delta` (how large a shock counts as "bounded")
- a recovery time budget `tau_recover`
- a tolerance `epsilon` on the same constraint proxy `C(t)`

SC-2 holds if:
- after applying a perturbation with magnitude `<= delta`, there exists a recovery time `tr <= tau_recover` such that `abs(C(t0 + tr) - C(t0)) <= epsilon`

**Use case**: robustness assessment for systems under ongoing environmental variation.

### SC-3: Transfer stability (strongest)

**Definition**: a system satisfies SC-3 if its constraint structure can be transferred to a new substrate/context and still satisfy SC-1.

**Operational check (minimum form)**:

SC-3 holds if:
- SC-1 holds on substrate/context `S1`, and
- after transfer to `S2` (under a declared transfer protocol), SC-1 holds on `S2`

**Use case**: distinguish true coordination (Φ₃) from substrate-locked late Φ₂.

## Decision table

| Criterion | What it tests | Typical failure mode |
|----------|----------------|----------------------|
| SC-1 | Basic persistence | system is still in Φ₂ or earlier |
| SC-2 | Attractor strength | system is in shallow Φ₃ (fragile) |
| SC-3 | Transferability | system is in deep Φ₃ (robust) |

## Φ₃ sub-regimes (classification)

Based on the stability criteria:

| Sub-regime | Criteria satisfied | Description |
|-----------|---------------------|-------------|
| Φ₃- (marginal) | SC-1 only | just entered Φ₃; fragile |
| Φ₃ (standard) | SC-1 + SC-2 | stable attractor; bounded resilience |
| Φ₃+ (deep) | SC-1 + SC-2 + SC-3 | transferable stability; "nirvana-like" |

## Operational examples (illustrative)

### Example 1: Grokking (learning system)

- SC-1: test accuracy >= 95% persists for `tau_persist` epochs
- SC-2: after a bounded weight perturbation, accuracy recovers within `tau_recover`
- SC-3: learned features transfer to a related task and still satisfy SC-1

### Example 2: Institutional rule (social system)

- SC-1: rule persists across leadership changes
- SC-2: rule survives minor crises
- SC-3: rule transfers to other organizations

## Relationship to MCC-6

MCC-6 (late-phase irreversibility) can be assessed operationally as follows:

- Under a declared estimator suite, label a system as **Φ₃ (standard)** if it satisfies **SC-1 + SC-2**.
- Label it as **Φ₃+ (deep)** only if it also satisfies **SC-3**.

## Link to EST

See [`docs/est/diagnostics.md`](../est/diagnostics.md) for estimator/EST diagnostics and how to report scope/tolerance choices.
