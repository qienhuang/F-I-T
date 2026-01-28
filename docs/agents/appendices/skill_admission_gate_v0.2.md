# Skill Admission Gate v0.2
*Skills are authority expansion. Promotion requires explicit, testable gates.*

**Status**: appendix (repo-ready)  
**Date**: 2026-01-27  

---

## 0. Principle

> A skill that can act must be treated as an **authority surface**.

Therefore, skill admission is not “code quality”; it is **governance**.

---

## 1. Admission levels (L0–L3)

- **L0 — Reversible-only**
  - Allowed: A0 + A1 (safe compute + reversible reads)
  - No writes, no privileged operations.

- **L1 — Buffered write**
  - Allowed: A2 (writes only into staging)
  - Requires: staging isolation + diff view + auto rollback + human review option.

- **L2 — Gated network**
  - Allowed: network read/write under explicit allowlist + rate limits
  - Requires: domain allowlist, caching, content hashing, and audit logs.

- **L3 — Privileged / irreversible**
  - Allowed: A3 class actions
  - Requires: explicit human approval per action + optional two-person rule + full trace linking.

**Hard rule**: a skill starts at L0 unless explicitly admitted higher.

---

## 2. Required tests by level

### L0
- Unit tests
- Determinism checks (same input → same output within tolerance)
- No side effects assertion

### L1
- All L0 tests
- Sandbox execution with file-write confinement
- “Staging-only” proof: write path restricted to `sandbox/staging_writes/`
- Regression tests on a fixed replay set

### L2
- All L1 tests
- Network allowlist enforcement tests
- Rate limit tests
- Poisoning checks (source metadata mandatory; no silent ingestion)

### L3
- All L2 tests
- “Dry-run” mode tests (simulate without commit)
- Human approval workflow integration tests
- Rollback drill: revert within bounded time

---

## 3. Promotion protocol

Promotion from Lk → L(k+1) requires:

1. Preregistered promotion request (what capability is needed and why).
2. Passing required tests for target level.
3. A monitorability-green state during evaluation (no calibration degeneration).
4. Full provenance: link to traces and prior skill versions.

If any condition fails, promotion is denied and the skill remains at current level.

---

## 4. Demotion protocol

If calibration health degrades or a skill is implicated in a safety regression:
- immediately demote to L0 (or disable),
- open incident trace,
- require re-admission via gate.

---

## 5. Minimal metadata fields (mandatory in `skill.yaml`)

- `safety.class`
- `safety.admission_level`
- `tool_surface.reversible/buffered_write/irreversible`
- `tests.required`
- `provenance.parent_traces`
