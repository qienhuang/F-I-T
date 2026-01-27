# Failure Map as Phase Diagram — Report Template v0.1
**Date**: 2026-01-27

This template standardizes how to report “method phase diagrams” discovered by FIT-Explorer.

---

## 1. Axes (what parameterizes the method space)

Choose up to 3 axes (examples):
- window length  W  
- smoothing  \alpha  
- feature family (categorical)  
- calibration method (categorical)  
- coarse-graining scale  s  

---

## 2. Labels (colors)

Use primary failure labels:
- `SUPPORTED_FOR_ALARM`
- `RANK_ONLY` (e.g., FPR_FLOOR)
- `ESTIMATOR_UNSTABLE`
- `INCONCLUSIVE`
- `SCOPE_LIMITED`

Also report sublabels:
- `FPR_FLOOR`
- `NEG_DRIFT`
- `SUPPORT_COLLAPSE`
- etc.

---

## 3. Evidence per region

For each labeled region, record:
- achieved FPR min
- ok_targets count
- support size (neg)
- tie dominance
- utility metrics (if gate passed)
- seed pass rate

---

## 4. Interpretation

Write 3 paragraphs:
1) where the feasible region lives
2) the dominant failure mechanism that bounds it
3) what actuator(s) are suggested by the frontier geometry

---

## 5. “New math” claim discipline

A discovered feasible region is not automatically a “theory”.
A theory claim requires:
- boundary stability
- estimator coherence
- robustness across seeds/schedules
- and a clear mapping to interpretable effective variables.

