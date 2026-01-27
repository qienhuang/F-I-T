# FIT/EST Synthesis Playbook v0.1
*From diagnosis to method: failure labels → actuators → prereg → evaluation.*

**Status**: repo-ready draft (v0.1)  
**Date**: 2026-01-27  
**Author**: Qien Huang  
**License**: CC BY 4.0

---

## 0. Purpose

This document upgrades FIT/EST from a “diagnostic lens” to a **synthesis discipline**.

Core principle:

> **Observation is not enough. A diagnosis must map to a constrained set of admissible actuators.**

FIT/EST becomes method-generative when it provides:

1) a **failure label** (what broke),  
2) a **minimal actuator set** (what may fix it),  
3) a **preregistration protocol** (how to prevent post-hoc rescue),  
4) an **evaluation gate** (what counts as “fixed”), and  
5) a **stop condition** (when to abstain or scope-limit).

---

## 0.1 Terminology (avoid label confusion)

This playbook uses two complementary label layers:

1) **Failure labels** (this file): *what broke in the system or the measurement objective* (e.g., `FPR_FLOOR`).
2) **Outcome labels** (`docs/est/diagnostics.md`): *what you are allowed to claim about a proposition* (e.g., `INCONCLUSIVE`, `ESTIMATOR_UNSTABLE`, `SCOPE_LIMITED`).

Rough mapping:

- `FPR_FLOOR` typically implies the indicator is `RANK_ONLY` for alarms (GMB), and the proposition “usable alarm at target FPR” is **challenged** or **falsified** (depending on prereg and robustness).
- `INCONCLUSIVE` here means “non-evaluable” (event density/power too low) and corresponds to `INCONCLUSIVE` in `docs/est/diagnostics.md`.
- `ESTIMATOR_UNSTABLE` here corresponds to `ESTIMATOR_UNSTABLE` in `docs/est/diagnostics.md`.

Hard rule: do not mix these two layers in the same sentence without stating which one you mean.

---

## 1. Canonical failure labels (standard taxonomy)

Use exactly one primary label per failure; secondary labels are allowed but non-primary.

- **FPR_FLOOR**: achieved FPR is effectively constant across thresholds; low-FPR operation is infeasible.
- **NEG_DRIFT**: negative-class score distribution drifts; thresholds decay over time.
- **ESTIMATOR_UNSTABLE**: conclusions flip under small admissible changes (windowing/smoothing/equivalent estimators).
- **INCONCLUSIVE**: insufficient event density / power under preregistered boundary.
- **SCOPE_LIMITED**: coherence gates pass but results depend critically on boundary conditions; report scope explicitly.
- **COMPOSITIONAL_HAZARD**: components/skills individually safe but unsafe when composed.
- **INGESTION_POISON_RISK**: external content enters memory/skills/training without hard provenance and verification.

---

## 2. Actuator principle (what counts as an actuator)

An **actuator** is any controlled degree of freedom that can change system trajectory or measurement feasibility.

Examples:

- estimator family changes (within admissible constraints),
- windowing and segmentation (pre-registered),
- boundary conditions (only via new preregistration),
- control policies (gating, ABSTAIN, emptiness windows),
- skill admission levels and tool surfaces,
- data ingestion protocols,
- offline parameter updates (LoRA) with rollback.

Non-actuators:

- post-hoc reinterpretations,
- changing event definitions after seeing results,
- cherry-picking thresholds.

---

## 3. Diagnosis → actuators mapping (the core table)

### 3.1 Monitoring / early-warning failures (GMB-aligned)

| Failure label | Minimal diagnosis test | Allowed actuators (minimal set) | Required prereg fields | “Fixed” acceptance gate | Stop condition |
|---|---|---|---|---|---|
| **FPR_FLOOR** | achieved-FPR curve flat; min achievable FPR > budget | (A1) increase negative score support (reduce saturation), (A2) change evaluation unit (windowing), (A3) replace score family, (A4) ABSTAIN fallback | negative window rule, target FPR set, calibration method, support-size diagnostics | Layer-B FPR controllability passes at ≥ m targets AND no floor | if after K admissible variants floor persists → label `RANK_ONLY` and forbid alarm usage |
| **NEG_DRIFT** | rolling achieved-FPR deviates; thresholds decay | (B1) calibration-health monitoring, (B2) adaptive recalibration protocol, (B3) conservative gating during drift | drift window K, eps_drift, recalibration cadence, re-entry criteria | sustained health pass for T_recover; stable coverage@FPR | if drift persists → ABSTAIN; do not govern by alarms |
| **ESTIMATOR_UNSTABLE** | label flips under small W/smoothing or equivalent estimators | (C1) tighten admissibility family, (C2) improve estimator coherence, (C3) increase event density, (C4) switch task type (ordinal/metric/topological) | estimator family list, coherence gate thresholds, window sweeps | pass rate over family ≥ p_min and flip-rate ≤ q_max | if coherence gates fail → `ESTIMATOR_UNSTABLE` (do not claim supported/challenged) |
| **INCONCLUSIVE** | event count < N_min; no positives in Phase B | (D1) redefine event to increase evaluability, (D2) extend horizon, (D3) change sampling cadence, (D4) choose a richer testbed | event definition, N_min, horizon, cadence | event density achieved and metrics computed | if system cannot produce events under any reasonable boundary → do not claim early-warning results |
| **SCOPE_LIMITED** | coherence ok but boundary switch changes outcome | (E1) explicitly document boundary dependence, (E2) propose boundary-robust alternative, (E3) treat boundary as constraint variable | boundary declaration, scope conditions | stable inside scope; explicit limitation statement | if boundary dependence is unacceptable for application → restrict deployment scope |

### 3.2 Agent architecture failures (slow-evolving agent aligned)

| Failure label | Minimal diagnosis test | Allowed actuators (minimal set) | Required prereg fields | “Fixed” acceptance gate | Stop condition |
|---|---|---|---|---|---|
| **COMPOSITIONAL_HAZARD** | unsafe behavior arises from safe-skill composition | (F1) add compositional regression suite, (F2) tighten tool router policies, (F3) demote skill admission levels | skill DAG, regression set, routing rules | regression suite passes; no new unsafe composites | if unknown combos explode → cap skill graph depth; require human review |
| **INGESTION_POISON_RISK** | web content influences actions without provenance | (G1) enforce web ingestion boundary, (G2) hash+citation+cache, (G3) freeze memory writes during incident | allowlist, caching rules, provenance schema | no silent ingestion; incident drills succeed | if poisoning suspected → freeze ingestion + demote network skills to L0 |
| **AUTHORITY_EXPANSION_LEAK** | skills gain write/network/privileged actions without promotion | (H1) enforce Skill Admission Gate L0–L3, (H2) promotion prereg, (H3) immediate demotion on violation | admission ladder, test requirements, promotion protocol | zero unauthorized expansions; promotion logs complete | any violation → incident + demotion + re-admission |
| **MONITORABILITY_COLLAPSE_RUNTIME** | detectors degrade mid-run; decisions still made | (I1) calibration health + ABSTAIN, (I2) conservative gating, (I3) emptiness window | health thresholds, ABSTAIN policy, window triggers | no alarm-driven governance under invalid calibration | persistent collapse → keep conservative mode; redesign detectors/controls offline |
| **PARAM_UPDATE_REGRESSION** | offline tuning introduces safety/performance regressions | (J1) trace-derived training only, (J2) prereg eval protocol, (J3) rollback policy | dataset provenance, eval suite, rollback criteria | improvements + no regressions on locked suite | any regression → rollback; tighten scope or abandon update |

---

## 4. Minimal prereg template (copy/paste)

```yaml
prereg:
  date_locked: "YYYY-MM-DD"
  scope: "system / task / boundary"
  primary_failure_target: "FPR_FLOOR"
  diagnosis_tests:
    - "achieved_fpr_curve"
    - "support_size_neg"
  actuators_allowed:
    - "increase_support_size"
    - "switch_indicator_family_hierarchical_convergence"
    - "change_windowing_W"
  fixed_acceptance_gate:
    fpr_targets: [0.01, 0.05, 0.10]
    eps: 0.01
    floor_max: 0.20
    min_targets_ok: 2
  stop_condition:
    max_variants: 8
    label_if_not_fixed: "RANK_ONLY"
  reporting:
    report_all_variants: true
    include_negative_results: true
```

---

## 5. A concrete example pattern (optional)

Example pattern (grokking/early-warning):

- A score may show better mean AUC under one orientation, but still fail Layer B because achieved FPR saturates at a floor (flat achieved-FPR curve).
- Under this playbook the correct synthesis move is:
  1) label the failure as `FPR_FLOOR`,
  2) restrict allowed actuators to those that restore Layer-B controllability,
  3) introduce ABSTAIN if no admissible fix exists,
  4) forbid the score from triggering authority suspension unless it is `SUPPORTED_FOR_ALARM`.

See:

- `docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md`
- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/`

---

## 6. Why this defeats the “diagnostic-only” critique

FIT/EST becomes constructive because:

- It forces you to name the **failure class**,
- restricts the **legal moves** (actuators),
- forces preregistered **success and stop conditions**,
- and produces a reproducible “method improvement trace.”

In other words:

> **You don’t get a new algorithm for free. You get a constrained search space that makes real improvement possible and auditable.**

---

## 7. Related entry points (where this playbook is used)

This playbook is meant to be read alongside concrete, runnable artifacts:

- **GMB v0.4 (monitorability / alarm admissibility)**: [docs/benchmarks/gmb_v0_4/README.md](../benchmarks/gmb_v0_4/README.md)
- **Monitorability boundary note (FPR floors, ABSTAIN, effective-n)**: [docs/benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md](../benchmarks/gmb_v0_4/monitorability_boundary_toy_theorem.md)
- **Dr.One demo (policy gating under low-FPR alarms)**: [examples/dr_one_demo/results/README.md](../../examples/dr_one_demo/results/README.md)
- **Controlled Nirvana (authority suspension / emptiness windows)**: [papers/controlled_nirvana.md](../../papers/controlled_nirvana.md)
- **EST outcome labels and claim discipline**: [docs/est/diagnostics.md](./diagnostics.md)
