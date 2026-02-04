# 3-Block Boot Protocol (LLM Session Initialization)

**Purpose**: Force any LLM session to re-enter a stable conceptual coordinate system without relying on memory.

This protocol is **model-agnostic** and **session-stateless**.

---

## Block 1 — Identity & Red Lines (Immutable)

Include verbatim at the start of every session.

- Author attribution and licensing
- Non-authority clause
- Explicit misuse boundaries (no moral arbitration, no coercive justification)
- Versioning discipline (no silent scope expansion)

> This block must never be edited mid-session.

---

## Block 2 — Compressed Core State

Provide the **smallest possible** set of artifacts that define the current theory state:

Typical contents:
- FIT Core Card
- MCC (or equivalent minimal core)
- Any phase algebra or estimator discipline required

**Hard rule**:
> If it does not fit in ~1–2 pages, it is not a core state.

---

## Block 3 — Task-Local Spec Lock

Define what *this session* is allowed to do.

Must include:
- Target output type (card / essay / protocol / experiment plan)
- Explicit exclusions ("do not discuss X")
- Required format and location (file path, naming)

---

## Failure handling

If the LLM:
- violates Block 1 → session invalid
- drifts outside Block 2 → re-inject Block 2
- ignores Block 3 → discard output

---

## Rationale

This protocol replaces:
- reliance on model memory
- prompt accumulation
- hidden context

with **explicit structural reload**.

It is intentionally repetitive.

---
