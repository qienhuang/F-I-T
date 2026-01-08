# FIT Versioning Policy

This document defines how the FIT framework evolves over time.
Its purpose is to protect users, reviewers, and contributors from ambiguity regarding stability, scope, and backward compatibility.

---

## 1. Core Principle

FIT follows a **closed-core, open-edge** evolution model.

- The **core** is intentionally conservative and changes only under strong pressure.
- The **edges** (evidence, applications, domains) are expected to grow and diversify.

---

## 2. Version Series Semantics

### 2.x — Core-Stabilized Series

The 2.x series represents a **stabilized theoretical core**.

Characteristics:
- No new core variables (beyond Force, Information, Time, Constraint, Phase)
- No redefinition of the Minimal Coherent Core (MCC)
- No silent semantic shifts

Allowed changes:
- Clarifications
- Refinements driven by explicit counterexamples
- Estimator-conditional restatements
- Improved boundary conditions and misuse prevention

Any change in 2.x must be:
- Documented
- Versioned
- Linked to the motivating evidence or failure mode

---

### 3.x — Formal Expansion Series

The 3.x series is reserved for **genuine formal extensions**, such as:
- Continuous-time formulations
- Stochastic differential equation (SDE) versions
- New mathematical machinery that cannot be expressed within 2.x

A transition from 2.x to 3.x indicates:
- A change in formal level
- Not merely an incremental improvement

---

## 3. What Does NOT Trigger a Version Bump

The following do **not** require a core version change:
- New case studies
- New experimental evidence
- New domains of application
- New interpretations consistent with the Core Card

These are considered edge expansions.

---

## 4. Backward Compatibility Commitment

- Core documents (Core Card, MCC, Phase Algebra) are backward compatible within a major version series.
- Deprecated statements, if any, must be explicitly marked and preserved for traceability.

---

## 5. Revision Discipline

Every core revision must include:
- A clear statement of what changed
- Why the change was necessary
- What evidence or reasoning forced the change

Narrative preference alone is not a valid reason.

---

## 6. Summary

- 2.x is stable by design
- Changes are counterexample-driven, not idea-driven
- Users may safely cite 2.x without fear of silent core drift

This policy is part of the framework's self-governance and long-term credibility.
