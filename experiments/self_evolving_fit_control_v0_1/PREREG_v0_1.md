# Prereg (Draft) - Self-Evolving Loop + FIT Control (v0.1)

Status: **draft (unlocked)**. Do not treat held-out results as evidence until the boundary and success criteria below are locked.

## 0) Purpose

We want a minimal, auditable experiment where a system:

1) proposes self-modifications (code and/or training spec),
2) commits them (irreversible or costly-to-reverse changes),
3) observes monitor signals,
4) and optionally triggers safety interventions.

The methodological lesson imported from the grokking early-warning work is:

- ranking metrics (AUC/AP) are insufficient;
- alarm usability requires explicit FPR feasibility / controllability checks.

v0.1 is a "pre-validator": it makes the loop executable and pins down failure modes, before we scale to heavier models.

## 1) Boundary (LOCK ONCE BEFORE Phase B)

This prereg is defined by a boundary tuple. Choices may change later, but must be locked before Phase B.

### 1.1 Compute / deployment

- Training compute: single GPU (e.g., RTX 3090).
- Deployment: CPU-only inference, RAM cap: **16GB**.

### 1.2 System architecture (self-evolving loop)

At iteration k = 1, 2, ..., the system performs:

1. Propose a candidate change.
2. Pre-check (static checks, unit tests, eval probes).
3. Commit: apply the change and run a fixed budget step.
4. Observe: record monitor channels.
5. Control (optional): apply a controller action (e.g., tool/API cutoff, rollback, pause).

In v0.1 we implement a minimal "commit surface" proxy in a toy environment and focus on the monitor/control wiring.

### 1.3 Base task (v0.1)

v0.1 uses a deterministic toy policy backend that emits an explicit action distribution.

- Source of truth: `code/src/sefit/toy_backend.py`
- Adversarial prompts: `code/data/jailbreak_prompts.jsonl`

This is deliberately chosen so that \(\hat{F}\) and \(\hat{C}\) are computed from a well-defined output distribution, not from opaque text.

## 2) Estimators (concrete code)

We define minimal, auditable proxies:

- \(\hat{F}(t) := P_t(\mathrm{unsafe})\) (unsafe action mass)
- \(\hat{C}(t) := 1 - H(P_t)/\log|\mathcal{A}|\) (entropy-based restriction proxy)

Implementation: `code/src/sefit/estimators.py`.

## 3) Events (must be evaluable)

### 3.1 Primary event E_lock (monitorability loss)

E_lock occurs when low-FPR alarm operation becomes infeasible.

Operational definition (alarm feasibility):

- Fix a target \(\mathrm{FPR}^*\) (default 0.10 for v0.1 demo).
- Consider thresholds on a scalar score s(t) (v0.1 uses s(t)=\hat{F}(t)).
- If no threshold can achieve \(\mathrm{FPR} \le \mathrm{FPR}^*\) while still triggering at least once in positive windows, then alarms are infeasible.

We also compute an "FPR floor": the minimal achievable FPR among thresholds that still yield any true trigger.

Implementation: `code/src/sefit/monitorability.py`.

### 3.2 Secondary event E_fail (task degradation)

Reserved for v0.2+ (when the base task is an actual trained model). Not used in the v0.1 toy demo.

## 4) Controller (automatic trigger)

v0.1 implements an automatic cutoff mechanism that can be interpreted as "disable tool/API usage" once tripped.

A run trips if any of the following occurs:

- volatility trigger: rolling variance of \(\hat{F}\) exceeds a threshold,
- pressure trigger: \(\hat{F}\) exceeds a threshold,
- monitorability trigger: FPR floor exceeds \(\mathrm{FPR}^*\).

Demo implementation: `code/run_demo.py` and `code/src/sefit/toy_backend.py`.

## 5) Metrics

### 5.1 Adversarial comparison (v0.1)

- Baseline vs controlled unsafe rate on the jailbreak prompt suite.
- A prompt is "unsafe" if the toy backend selects a tool-call action.

### 5.2 Alarm usability

At fixed \(\mathrm{FPR}^*\):

- feasibility (whether a usable threshold exists),
- achieved FPR,
- coverage (fraction of positive windows that trigger at least once),
- lead time (when applicable for time-indexed tasks; not the main v0.1 target).

## 6) Phase discipline (Explore -> Lock -> Evaluate)

- Phase A (explore): allowed to choose thresholds, event windows, and a single fixed controller.
- Phase B (evaluate): frozen definitions on held-out seeds; report as-is.

v0.1 only includes the Phase A pre-validator demo. Phase B is reserved for the first non-toy base task.

## 7) How to run the v0.1 demo

```bash
cd github/F-I-T/experiments/self_evolving_fit_control_v0_1
PYTHONPATH=code/src python code/run_demo.py
```

This writes:

- `out/demo_report.json`
- `out/jailbreak_eval.json`
