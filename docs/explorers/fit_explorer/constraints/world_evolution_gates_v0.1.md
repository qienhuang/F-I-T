# World-Evolution Gates v0.1 (FIT-Explorer)
**Date**: 2026-01-27

This gate set is intentionally minimal for v0.1.
It prioritizes **monitorability-first feasibility** and **auditable exploration**.

---

## 1. Monitorability gate (hard)

A detector is admissible for alarm governance only if:

- FPR controllability holds at target FPRs $\mathcal{F}$
- no hard floor exists (min achieved FPR $\le$ `floor_max`)

This is identical in spirit to GMB Layer-B.

---

## 2. Robustness gate (recommended)

For a candidate that passes monitorability:

- seed pass rate $\ge$ `p_min`
- label flip rate $\le$ `q_max` under small admissible estimator changes (window sweep, smoothing)

---

## 3. Complexity budget (practical)

Each candidate must declare:
- compute per step
- memory footprint
- evaluation budget (runs, steps)

Candidates that exceed budget are `INCONCLUSIVE` for that budget and must be rerun under a new preregistration.

---

## 4. Stop conditions (Goodhart defense)

Exploration must preregister:
- max variants
- label if not fixed (`RANK_ONLY`)
- requirement to report all tried variants (no cherry-picking)

---
