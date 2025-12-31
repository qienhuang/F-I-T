# Tier-2 Predictions Register (EN)

This document is a **pre-registrable Tier-2 prediction register** for FIT/EST-style work.

Core rule: every Tier-2 case study must pass the **A/B/C novelty filter**:
- **A**: How does the field describe the phenomenon today (without FIT)?
- **B**: How does FIT translate it (state / force / constraint / tempo)?
- **C**: What new, quantitative, falsifiable prediction follows that is not already contained in (A)?

If (C) is missing, the case study is a demo, not a Tier-2 validation.

## Practical notes

- Prefer *operational definitions* over algebra where possible. Many platforms render math inconsistently.
- When you do need math, use robust forms (e.g., `t_1^{\ast}` not `t^*_1`).
- Pre-register estimator choices and thresholds before looking at results.

---

## T2-1: Tempo mismatch → IO accumulation changes shape (linear → accelerating)

### A / B / C

- **A (baseline)**: The field warns about “shipping faster than evaluation”, “lack of rollback”, “approval delays”, etc., usually as qualitative risk management.
- **B (FIT translation)**: Define a tempo mismatch ratio and treat governance cadence and rollback feasibility as constraints shaping the reachable option space.
- **C (new prediction)**: There exists a critical mismatch threshold `r_c` such that when `r > r_c`, IO accumulation shifts from roughly linear to accelerating growth, and `r_c` can be detected earlier via estimator coherence degradation.

### Definitions (operational)

- Tempo mismatch ratio:
  - `r := tau_update / tau_gov`
  - `tau_update`: average interval between impactful updates (training or deployment)
  - `tau_gov`: evaluation / audit / approval closure cycle time
- IO event rate: `lambda_IO(t)` (IO events per unit time)
- Provisional “danger zone” starting point: `r > 5` (illustrative; must be calibrated per domain)

### Testable predictions

1. As `r` crosses `r_c`, the fitted shape of `lambda_IO(t)` changes (e.g., linear-ish to accelerating).
2. Before obvious failures, estimator coherence for governance/constraint proxies degrades (P10-style gate).

### Candidate data sources

- Real-world: CI/CD approval logs, incident tickets, rollback drills, model card update pipelines
- Proxy systems: a controlled “ship/eval” simulator with pre-defined gates and rollback costs

---

## T2-2: Coherence collapse as early warning (P10-style)

### A / B / C

- **A (baseline)**: Teams track individual metrics (incidents, evaluation scores), but metric drift and metric gaming are common.
- **B (FIT translation)**: Use an admissible estimator family and require task-appropriate coherence as an audit gate.
- **C (new prediction)**: Coherence degradation occurs before incident spikes and predicts loss of intervention feasibility.

### Operational sketch

Define an “intervention viability” proxy `V(t)` using an estimator family (3+ estimators):

- `V_hat_1`: rollback success probability (rolling window)
- `V_hat_2`: auditability / override latency proxy
- `V_hat_3`: dependency / single-point reliance proxy

Coherence:

- `coh(t) := median_{i<j} rho(V_hat_i, V_hat_j)`

Prediction:

- `coh(t)` drops below a pre-registered `rho_min` before IO rate spikes or major incidents.

---

## T2-3: Boundary = constraint in real pipelines (governance lag as boundary)

### A / B / C

- **A (baseline)**: “Approval delays” are treated as process friction, not a structural variable.
- **B (FIT translation)**: Treat governance cadence as a boundary condition that induces an evolving approval constraint.
- **C (new prediction)**: When `tau_gov >> tau_update`, the reachable correction option space collapses (topological/event-structure change), detectable via task-typed coherence gates.

---

## T2-N1 (negative prediction): coherence does NOT drop, and P10 still holds

Purpose: this is a deliberate “negative prediction” that can falsify common interpretations.

### Setup

- `coh(t)` remains above `rho_min` even under fast update cycles
- IO rate remains bounded (no acceleration)

### What it would imply

If T2-N1 holds, then:
1. The chosen `rho_min` is too low/high (miscalibrated gate), or
2. The estimator family is not admissible (scope/robustness failures), or
3. The claimed causal link “coherence collapse → irreversibility” is not generally valid and needs scope refinement.

---

## Reporting schema (recommended)

Use a machine-readable record per prediction:

- `prediction_id`
- `system`
- `state_representation`
- `boundary_conditions`
- `task_type`: ordinal | metric | topological
- `estimators`: family + version + scope
- `coherence_gate`: type + threshold
- `success_criteria` / `failure_criteria`
- `data_source`
- `timeline`

