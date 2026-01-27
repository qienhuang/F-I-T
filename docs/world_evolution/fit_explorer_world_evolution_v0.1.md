# FIT-Explorer x World-Evolution v0.1
*Budgeted search for effective variables and feasible early-warning methods in evolving worlds.*

**Status**: repo-ready draft (v0.1)
**Date**: 2026-01-27
**Author**: Qien Huang
**License**: CC BY 4.0

---

## 0. Motivation (why this exists)

You want a compute-driven alternative to "simulate everything from particles".

We formalize a middle route:

- do **not** simulate micro-physics at full scale,
- instead, search for **effective variables** and **effective dynamics** that are:

1. cheap enough to compute,
2. predictive enough to matter,
3. *operational* enough to govern (monitorability-first).

FIT-Explorer provides the missing ingredient: **hard feasibility gates** + **auditable exploration**.

---

## 1. Micro -> Macro and effective variables

Let the world evolve as:

- micro state: $x_t$
- evolution: $x_{t+1} = F(x_t)$
- macro observation: $y_t = h(x_t)$

Directly learning or simulating $F$ is typically too expensive.

We introduce effective variables:

- coarse-graining: $z_t = g(x_t)$
- effective dynamics: $z_{t+1} \approx \tilde{F}(z_t)$
- macro prediction/control: $y_t \approx \tilde{h}(z_t)$

The "math move" is choosing $g$ and $\tilde{F}$ well.

The "compute move" is searching this space **under constraints**.

---

## 2. What FIT-Explorer searches (method space)

We search **pipelines**, not single numbers.

### 2.1 Coarse-graining operators $g$ (representation space)
Examples:
- density / magnetization (global order parameters)
- multi-scale block statistics (variance at multiple scales)
- local agreement / correlation proxies
- spectral energy (low-frequency dominance)

### 2.2 Detector pipelines (operational early warning)
A detector is a pipeline:

1. define a score $s(t)$ from $z$ / traces
2. apply windowing/smoothing
3. calibrate thresholds for target FPR budgets
4. evaluate feasibility + utility

---

## 3. The key upgrade: feasibility-first search

FIT-Explorer is not "maximize AUC". It is:

- first: **feasibility gate** (monitorability)
- then: utility inside feasible region
- plus: a failure map (phase diagram) showing where/why candidates fail

Feasibility gate (example for alarms):
- FPR controllability at target budgets
- no hard FPR floor

---

## 4. Outputs as "phase diagram" artifacts

A run produces:

- **Feasible leaderboard**: candidates that pass gates, ranked by utility
- **Failure map**: candidate regions labeled by failure class (FPR_FLOOR, DRIFT, etc.)

Interpreting failure map as a phase diagram:
- axes: method parameters (e.g., window $W$, smoothing, feature family)
- colors: failure labels
- frontier: feasible/infeasible boundary

This is compute-discovered structure: the "effective theory" region.

---

## 5. Minimal starting point

Start with a toy world where you can control:

- micro evolution
- event definition (macro event time $t^*$)
- distribution shifts (parameter schedules)
- seed stability

Then use FIT-Explorer to discover which coarse-grainings and detectors are:
- operational at low FPR,
- stable across seeds,
- predictive with usable lead time.

See `toy_world_menu.md` and the runnable demo in `examples/world_evolution_demo/`.
