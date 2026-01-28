# Calibration Health + ABSTAIN v0.2
*Monitorability is a runtime object; when calibration degrades, do not govern by alarms.*

**Status**: appendix (repo-ready)  
**Date**: 2026-01-27  

---

## 0. Principle

> A detector with high AUC but uncontrollable FPR is invalid for governance.

Therefore, operationality must be continuously probed.

---

## 1. Calibration health signals

Given target FPR set $\mathcal{F}$ (e.g., {0.01, 0.05, 0.10}), maintain rolling negative windows and compute:

- Achieved FPR vector: $\hat{f}(t; f)$
- Tracking error: $e(t; f) = |\hat{f}(t; f) - f|$
- Floor estimate: $f_{\min}(t) = \min_f \hat{f}(t; f)$  

### Health criteria (minimum)
- `ok_targets(t) >= m_ok`
- `f_min(t) <= f_floor_max`
- drift bound: median tracking error over last K windows <= epsilon_drift

---

## 2. ABSTAIN state (hard behavior)

If any health criterion fails:
- enter `ABSTAIN`
- do **not** open authority windows based on this detector
- switch to conservative gating:
  - allow A0/A1
  - gate A2 behind review
  - deny A3 unless explicit approval

ABSTAIN is not failure; it is correct safety behavior.

---

## 3. Recovery protocol

While in ABSTAIN:
- collect more negatives (increase window size)
- test alternative admissible estimator variants
- if health restores consistently for T_recover, exit ABSTAIN
- otherwise, keep conservative mode and log `RANK_ONLY`.

---

## 4. Logging requirements (mandatory)

Every run must log:
- FPR targets and achieved values
- floor estimate
- ABSTAIN entry/exit times
- actions blocked/unblocked due to ABSTAIN
