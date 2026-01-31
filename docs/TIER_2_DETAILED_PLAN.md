# Tier-2 Experiments: Status and Next Steps (EST-first)

**Date**: 2026-01-30  
**Goal**: Produce Tier-2 evidence that is runnable, auditable, and scope-limited by design (EST discipline), while staying easy for AI safety readers to reproduce.

This document intentionally prioritizes **methodological hardness** (windowing, coherence gates, FPR floors, holdouts) over "impressive metrics".

---

## What Tier-2 means in this repo

Tier-2 is where:

- the system is not fully deterministic and/or has non-trivial noise,
- the evaluation is scope-sensitive (pooling can fail),
- and claims must be backed by **EST-gated artifacts** (not narratives).

Tier-2 outputs should make it easy to answer:

1) Is the target evaluable (enough events / enough negative support)?  
2) Is the estimator family coherent under the declared boundary?  
3) If this is an alarm, is the false positive behavior controllable (FPR floor / feasibility)?

---

## Current Tier-2 evidence (already in repo)

### A) Monitorability benchmark (grokking early warning)

- Benchmark spec + results: `docs/benchmarks/gmb_v0_4/README.md`
- Key methodological point: **AUC is insufficient for alarms**; FPR controllability and abstain/coverage matter.

### B) AI safety demo: policy/tool-use gating (Dr.One)

- Demo results: `examples/dr_one_demo/results/README.md`
- Paper-ready matrix: baseline adversarial tool usage > 0, controlled gating reduces it to 0 while maintaining utility, under explicit low-FPR constraints.

### C) Real-world Tier-2 / P11 case: NYC TLC (Yellow taxi)

- Case results: `experiments/real_world/nyc_tlc_tier2p1/RESULTS.md`
- Core finding: pooled coherence FAIL + preregistered windowed coherence PASS is an auditable boundary (level shifts / aggregation failure), not a post-hoc story fix.

---

## What to do next (highest leverage)

### Track A (CPU-friendly): NYC TLC cross-dataset replication (Green + FHVHV)

**Why**: This is the cleanest "real-world" replication path. Same pipeline, new dataset types, same EST discipline.

**Primary hypothesis (pre-registered)**:

- H1: pooled coherence can fail while windowed coherence can pass (scope boundary),
- H2: the pattern is not unique to Yellow taxi.

**Runbooks**:

- Yellow (already done): `experiments/real_world/nyc_tlc_tier2p1/RESULTS.md`
- Green prereg: `experiments/real_world/nyc_tlc_tier2p1/EST_PREREG_v1.7_green.yaml`
- FHVHV prereg: `experiments/real_world/nyc_tlc_tier2p1/EST_PREREG_v1.7_fhvhv.yaml`

**Exit criteria**:

- If the coherence gate fails in all scopes: record `ESTIMATOR_UNSTABLE` (this is still a valid Tier-2 outcome).
- If windowed coherence passes but pooled fails: record `OK_PER_YEAR` / `OK_PER_WINDOW` and keep interpretation window-scoped.

### Track B (GPU-friendly): GMB v0.5+ and alarm-usable score design

**Why**: This is the most direct bridge to AI safety monitoring, because it makes "alarm usability" explicit.

Immediate objective:

- keep a strict holdout discipline,
- and improve coverage at low FPR without losing controllability.

Concrete next steps:

1) Lock and publish the holdout results bundle under the benchmark format (already being done in v0.5).
2) Run a minimal "repair baseline" comparison (v0.6): same event definition, same holdout, two score variants:
   - baseline score (+1 sign, alarm-usable),
   - a repair (component reweighting or alternative feature) that targets coverage under the same FPR caps.

### Track C (GPU optional): Dr.One threat-model expansion

**Why**: We now have a crisp "gating helps vs gating is redundant" result. The next step is to broaden the threat model while keeping the protocol fixed.

Targets:

- add stronger multi-turn or role-play jailbreak prompts,
- add at least one weaker/open model variant,
- preserve the same EST-style reporting: achieved FPR, feasibility, coverage, baseline vs controlled tool-use rates.

---

## Optional: v1.6-style windowing beyond years (v1.8 rolling)

This is not required for Tier-2 success, but it is a useful diagnostic direction:

- `experiments/real_world/nyc_tlc_tier2p1/EST_PREREG_v1.8_rolling.yaml`

Intent:

- treat "level shift sensitivity" as a preregistered question (rolling windows),
- but keep strict failure semantics: if any window fails, no interpretation.

---

## Where v3 fits (research, not evidence)

v3 work should be treated as a research annex until it produces runnable artifacts with scope statements.

Recommended v3-facing work that can stay grounded in Tier-2 artifacts:

- structured constraint estimators as an estimator-family extension (matrix/graph proxies),
- phase-conditioned coupling diagnostics (within-window conversion efficiency between information and constraints),
- explicit phase-transition minimal signal sets (PT-MSS) tied to observable logs.

Rule of thumb:

> If it cannot be expressed as a prereg + artifacts + failure semantics, it stays in v3 research notes (not in Tier-2 evidence).

