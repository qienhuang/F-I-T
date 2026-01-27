# Mini Case Study: Toy World → Effective Variables → "Math-like" Invariants (v0.1)
**Date**: 2026-01-27

This case study shows what "math discovery" looks like in the toy world setting.

---

## 1. World

World A1: stochastic majority cellular automaton.

- micro state: binary grid $x_t$
- schedule: noise $p(t)$ increases over time
- macro observable: magnetization $m(t) = |2\,\mathrm{density}(t) - 1|$

We define event $t^*$ as the first time $m(t) \le \theta$.

---

## 2. Representation candidates (effective variables)

We treat a representation as $z_t = g(x_t)$.
In the demo, $z_t$ are coarse statistics like:
- magnetization
- activity
- rolling variance
- lag-1 autocorrelation

In a richer run, you would add multi-scale block statistics:
- block density variance at scales 2/4/8
- entropy of block means

---

## 3. FIT-Explorer search target

We do not "predict everything". We search for an operational early-warning pipeline that:

1) passes the monitorability gate (low-FPR controllability),
2) yields non-trivial coverage in the positive window,
3) provides usable lead time.

---

## 4. Output: phase diagram

The run produces:
- feasible leaderboard: candidates that are operational
- failure map: where candidates fail and why

Interpretation:
- the feasible region corresponds to "effective variables" that expose a stable signal
- failure regions correspond to "bad abstractions" (noise-dominated or unstable)

This is the compute analogue of mathematical progress:
- a good invariant collapses complexity into a stable signal
- a bad invariant fails under robustness checks or becomes non-operational

---

## 5. What would count as a real "math step" here?

A real step is when you can state a stable, replayable property, e.g.:

- "Under schedule class $S$ and initialization family $I$, the effective variable $z(t)$ satisfies monotone drift prior to $t^*$."

Then you can try to formalize it:
- define $S$, $I$, $z$ precisely
- prove monotonicity or concentration bounds (even partial)

FIT discipline helps you avoid claiming "theorems" from fragile empirical patterns:
- you treat boundary dependence explicitly,
- and you record failure maps as part of the result.
