# Agents (FIT/EST-aligned architectures)

This folder contains **agent architecture specifications** that apply FIT/EST discipline to LM-fronted controllers.

---

## Index

| Architecture | Purpose | Status |
|--------------|---------|--------|
| [Slow-Evolving Agent v0.2](slow_evolving_agent_architecture_v0.2.md) | Small-capacity, long-horizon capability growth via auditable external structure | repo-ready |

### Appendices

| Appendix | Purpose |
|----------|---------|
| [Skill Admission Gate v0.2](appendices/skill_admission_gate_v0.2.md) | L0–L3 authority levels + promotion rules |
| [Calibration Health + ABSTAIN v0.2](appendices/calibration_health_and_abstain_v0.2.md) | Runtime monitorability + graceful degradation |
| [Web Ingestion Boundary v0.2](appendices/web_ingestion_boundary_v0.2.md) | Retrieval vs ingestion separation |

---

## Key concepts

| Concept | Description |
|---------|-------------|
| **Slow-evolving** | Capability growth via skills/memory/curriculum, not weight updates |
| **Authority gating** | Skills expand what an agent can do; promotion requires explicit tests |
| **Monitorability** | FPR-controllable alarms gate irreversible actions |
| **ABSTAIN** | When calibration degrades, stop governing by alarms |
| **Ingestion boundary** | Read ≠ write ≠ train; prevent web pollution |

---

## Related entry points

- FIT/EST core: [docs/v2.4.md](../v2.4.md)
- Monitorability gate: [docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md](../benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md)
- Dr.One demo: [examples/dr_one_demo/README.md](../../examples/dr_one_demo/README.md)
- AI Safety Index: [docs/ai_safety/README.md](../ai_safety/README.md)

---

## Minimal runnable evidence (recommended)

These documents are architecture specs. For an executable, repo-runnable pre-validator of the key claims (low-FPR alarm feasibility → authority gating; and infeasible alarms → conservative posture), start here:

- `docs/agents/DEMO_CHECKLIST.md`

## Background

These architectures synthesize ideas from:

- **ReAct** (Yao et al., 2023): Reasoning + Acting interleaved
- **Reflexion** (Shinn et al., 2023): Episodic self-reflection
- **Voyager** (Wang et al., 2023): Skill library + curriculum

The key difference: we add **FIT/EST governance** to make these patterns safe and auditable.
