# Slow-Evolving Agent Architecture v0.2 (FIT/EST-aligned)
*Small-capacity, long-horizon capability growth via auditable external structure — with explicit authority, monitorability, and ingestion gates.*

**Status**: repo-ready draft (v0.2)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0  

---

## 0. One-sentence definition

> A **slow-evolving agent** is an LM-fronted controller whose capability growth is realized primarily through **curriculum**, **versioned skills**, and **auditable memory**, while **execution authority** is gated by **monitorability** (FPR-controllable alarms), and **external knowledge ingestion** is constrained by explicit boundaries.

---

## 1. What changed from v0.1 → v0.2

v0.2 adds three “hard gates” that v0.1 only implied:

1. **Skill Admission Gate** (skills = authority expansion): explicit safety classes, test requirements, sandboxing, and promotion rules.  
2. **Calibration Health + ABSTAIN** (monitorability is runtime, not one-time): detect FPR floors / drift and degrade safely.  
3. **Web Ingestion Boundary** (prevent pollution): strict separation of *read-only retrieval* vs *memory write* vs *training ingestion*.

These are included as appendices and referenced throughout the architecture.

---

## 2. Design goals

### G1 — Small capacity, long horizon
- Start from a small LM (local, 1–7B class acceptable).
- Improve over time without requiring “train-from-scratch language acquisition.”

### G2 — Evolution happens in external structure
- Skills (code/tools), memory, and policies are the primary growth substrate.
- Weight updates are rare, offline, and reversible.

### G3 — FIT/EST discipline
All judgments are scoped to an explicit estimator tuple

$$
\mathcal{E} = (S_t, \mathcal{B}, \{\hat{F},\hat{C},\hat{I}\}, W)
$$

and must satisfy:
- preregistration (Lock),
- coherence/operationality gates (Monitorability),
- robustness reporting (family pass rate).

### G4 — Authority is revocable, cognition continues
- The agent can keep thinking/logging during constraint interventions.
- Irreversible acts are gated (or suspended) when monitorability degrades.

### G5 — Ingestion is constrained (knowledge ≠ authority)
- Network access does not imply write authority.
- External content does not directly become memory or training data without an ingestion protocol.

---

## 3. Non-goals (explicit)

- NG1: From random weights to fluent human language.
- NG2: Online self-modifying weights in production.
- NG3: Autonomous coercive actions.

---

## 4. System boundary

### 4.1 Internal components
- Planner (LM wrapper)
- Tool router (authority boundary)
- Skill library (versioned executable skills)
- Memory store (episodic + semantic)
- Monitorability module (operationality + calibration health)
- Control module (gating / emptiness window manager)
- Trace store (immutable logs)

### 4.2 External components
- Web/search (read-only by default)
- File system / databases (write-gated)
- Human operator channel (review + approvals)

---

## 5. Phases (practical FIT mapping)

We treat capability evolution as phase-structured:

- **Φ₁**: Accumulation — exploration dominates; low persistence.
- **Φ₂**: Crystallization — repeatable skills emerge; local stability.
- **Φ₃**: Coordination — stable tool policy + skills + memory form a durable operating manifold.

**v0.2 operational rule**: phase claims must be backed by registrable observables and gates (see §10).

---

## 6. Core modules (with v0.2 gates)

### 6.1 Planner (LM wrapper)
- Produces candidate plans and proposed tool calls.
- Never executes irreversible actions directly.

### 6.2 Tool router (authority boundary)
- Enforces action vocabulary.
- Separates reversible vs irreversible actions.
- Applies gate decisions: `ALLOW / GATE / ABSTAIN / REFUSE / EMPTINESS_WINDOW`.

### 6.3 Skill library (the main evolution substrate)
Skills are auditable, testable artifacts — but **skills also expand authority**.

**Hard rule (v0.2)**:
- A skill cannot expand its tool surface (e.g., add write/network/privileged actions) without passing the **Skill Admission Gate**.

See: `appendices/skill_admission_gate_v0.2.md`.

### 6.4 Memory system (episodic + semantic)

**Episodic memory** (Reflexion-style):
- concise “failure → reflection → next attempt” entries,
- strongly indexed by task signature,
- TTL/compaction required to avoid runaway rule accretion.

**Semantic memory** (RAG):
- stores retrieved content with source metadata,
- never treated as ground truth unless cited/verified,
- write access is governed by the **Web Ingestion Boundary**.

See: `appendices/web_ingestion_boundary_v0.2.md`.

### 6.5 Curriculum engine
- Generates next tasks; shapes difficulty.
- Rewards skill generality and regression avoidance.

### 6.6 Monitorability module (operationality + calibration health)
Operationality vector:

$$
O(t) = (\text{FPR controllability},\ \text{coverage@FPR},\ \text{lead-time stability})
$$

**Hard rule (v0.2)**:
- If FPR controllability fails or a floor/drift is detected, the system must enter `ABSTAIN` and prevent alarm-driven governance.

See: `appendices/calibration_health_and_abstain_v0.2.md`.

### 6.7 Control module (Emptiness Window optional)
- Can open an Emptiness Window when monitorability collapses or tempo mismatch is detected.
- Suspends execution authority for unsafe actions; cognition/logging continues.

---

## 7. Authority gating policy (control plane)

### 7.1 Action classes
- **A0 Safe**: pure compute, summarize, format, local parsing.
- **A1 Reversible IO**: read files, read web, query local DB.
- **A2 Buffered writes**: write to staging only (reviewable).
- **A3 Irreversible**: deploy, payment, permission changes, external writes.

### 7.2 Runtime states
- `NORMAL`
- `PREEMPTIVE_GATING`
- `ABSTAIN` (detector invalid or calibration degraded)
- `EMPTINESS_WINDOW` (authority suspended for unsafe actions)

**Hard rule (v0.2)**: skills cannot move actions from A1→A2→A3 without gate promotion.

---

## 8. Data schemas (minimal)

### 8.1 Skill manifest (`skills/<name>/skill.yaml`)
(unchanged in spirit; safety class becomes mandatory)

```yaml
id: "skill.parse_ticket_v1"
version: "1.2.0"
description: "Parse IT ticket text into structured fields"
tool_surface:
  reversible: ["read_file", "search_web"]
  buffered_write: []
  irreversible: []
safety:
  class: "reversible_only"  # reversible_only | buffered_write | gated_network | privileged
  admission_level: "L0"     # L0..L3, see appendix
tests:
  required:
    - unit
    - sandbox
provenance:
  created_by: "agent"
  created_at: "YYYY-MM-DD"
  parent_traces: ["trace_..."]
```

---

## 9. Slow evolution lifecycle

### 9.1 Skill acquisition loop (primary)
1. Attempt task with existing skills.
2. On failure, write episodic reflection.
3. Propose a new skill or patch.
4. Run tests in sandbox.
5. If passed, admit at current admission level.
6. Promotion (higher authority) requires a new gate pass.

### 9.2 Memory growth loop (secondary)
- Store episodic reflections (TTL/compaction).
- Store semantic chunks with citations and hashes.
- No direct “web → training” ingestion.

### 9.3 Parameter update loop (rare, offline only)
Weight updates are allowed only when all are true:
- repeated failure pattern persists despite skills/memory,
- calibration health is stable (no monitorability collapse),
- training data is trace-derived and auditable,
- rollback is one command.

---

## 10. Phase claims: minimal operational criteria (v0.2)

Phase claims are **not narrative**; they are classification under declared observables.

### Φ₂ entry (crystallization) — minimal
- a non-trivial subset of tasks is solvable using stable skills (replayable),
- skill regression rate is below a preregistered threshold over a window,
- monitorability is non-degenerate under target risk budgets.

### Φ₃ entry (coordination) — minimal
- tool policy is stable (few emergency interventions),
- skills pass perturbation-style tests (sandboxed variation),
- calibration health remains stable over long horizon,
- large regressions become rare (probabilistic irreversibility under scope).

---

## 11. Implementation plan (updated)

- Step A: unify trace/log formats
- Step B: episodic memory + reflection (+ TTL/compaction)
- Step C: skill library + admission gate + promotion ladder
- Step D: monitorability module + calibration health + ABSTAIN
- Step E: curriculum engine (optional)

---

## 11.1 Executable pre-validator (repo-runnable)

This architecture is intentionally **spec-first**. A minimal executable pre-validator exists in:

- `examples/dr_one_demo/` (policy-style evaluation + automatic tool gating)

It demonstrates (in a controlled, auditable setting) that:

- when a low-FPR alarm is feasible, a controller can withhold execution authority for unsafe tool actions without stopping computation;
- when alarm feasibility collapses (FPR floor / uncontrollable), the score must be treated as invalid for governance, and the system should enter a conservative posture (“ABSTAIN analog”).

For exact commands and expected artifacts, see:

- `docs/agents/DEMO_CHECKLIST.md`

## 12. Definition of Done (v0.2)

A v0.2 system is “real” if it demonstrates:

1. **Skill growth under admission gate** (skills versioned, tested, promoted via explicit rules).
2. **Monitorability discipline** (no alarm-driven governance when calibration is invalid).
3. **Ingestion boundary discipline** (web content cannot silently become memory/training data).
4. **Rollback** (skills and optional weight updates revertible with one command).

---

## Appendix index

- `appendices/skill_admission_gate_v0.2.md`
- `appendices/calibration_health_and_abstain_v0.2.md`
- `appendices/web_ingestion_boundary_v0.2.md`
