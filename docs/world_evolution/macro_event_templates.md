# Macro Event Templates v0.1
**Date**: 2026-01-27

Your results depend heavily on how the macro event $t^*$ is defined.
Event definitions must be preregistered.

---

## Template 1 — Threshold crossing (order parameter)

Given an order parameter $m(t)$:

- event time $t^*$ is the first time $m(t) \le \theta$

Use when:
- there is a meaningful monotone collapse (order -> disorder)

Report:
- threshold $\theta$
- smoothing/window used for $m(t)$
- handling of oscillations (first crossing vs sustained crossing)

---

## Template 2 — Absorbing-state / stabilization

Given activity $a(t)$ (fraction of changed micro sites per step):

- event time $t^*$ is the first time $a(t) = 0$ for $L$ consecutive steps

Use when:
- the system falls into an attractor

Report:
- $L$ (stability length)
- how noise is treated (stochastic systems may never reach exact 0)

---

## Template 3 — Regime change via variance explosion

Given macro observable $y(t)$:

- event time $t^*$ is the first time $\mathrm{Var}_W[y](t) \ge \theta$

Use when:
- instability manifests as rising variance

Report:
- window $W$
- whether you normalize by baseline variance

---

## Template 4 — Causal shock schedule (known intervention time)

If you control a parameter schedule and define an intervention time $t_s$:
- event $t^*$ may be defined relative to $t_s$ (e.g., first failure after shock)

Use when:
- you want to test early warning under controlled shifts

Report:
- schedule function
- why $t_s$ is valid as a reference

---

## FIT requirement

Every event template must specify:

- negative window: $t \le t^* - \Delta_{\text{safe}}$
- positive window: $t^* - H_{\text{pos}} \le t < t^*$

These define what "early warning" means operationally.
