# Monitorability Boundary — Toy Proposition + Diagnostics (GMB v0.4 companion)

**Status**: draft-final (paper-ready)  
**Version**: v0.4  
**Date**: 2026-01-27

---

## 1. Problem statement

In early-warning settings, an indicator score may contain **ranking information** (e.g., AUC > 0.5) while being **operationally unusable** as an alarm under low-FPR budgets.

This note provides:

1) a toy proposition explaining **FPR floors** as a structural calibration failure, and  
2) practical diagnostics that map cleanly to GMB v0.4 failure semantics (`RANK_ONLY`, `ESTIMATOR_UNSTABLE`, `INCONCLUSIVE`).

---

## 2. Definitions (alarm view)

Let each evaluation unit be a window ending at time `t` with label \(y(t) \in \{0,1\}\) (negative/positive).  
An indicator produces a scalar score \(s(t)\).

For a threshold \(\tau\), define the alarm decision:

\[
a(t) = \mathbf{1}[s(t) \ge \tau]
\]

Define the achieved false positive rate (FPR):

\[
\mathrm{FPR}(\tau) := \Pr(a(t)=1 \mid y(t)=0).
\]

Define AUC as the ranking-based discriminative content (it does not require a fixed operating point).

GMB’s core claim: **alarm usability** requires controllability at a specified operating point, not just ranking.

---

## 3. Toy proposition (sufficient condition for an FPR floor)

### Proposition (two-level negative support ⇒ discrete achievable FPR)

Assume that on **negative windows**, the score takes only two values:

- \(s(t) \in \{s_L, s_H\}\) with \(s_H > s_L\), and
- \(p := \Pr(s(t)=s_H \mid y(t)=0)\).

Then for any threshold \(\tau\):

- If \(\tau > s_H\), \(\mathrm{FPR}(\tau)=0\),
- If \(s_L < \tau \le s_H\), \(\mathrm{FPR}(\tau)=p\),
- If \(\tau \le s_L\), \(\mathrm{FPR}(\tau)=1\).

Therefore the achievable FPR set is discrete: \(\{0,p,1\}\). Unless \(p\) is already below your risk budget, **no threshold can achieve low target FPR**: the detector has an **FPR floor** at \(p\).

#### Interpretation

- AUC can still be > 0.5 if positives tend to score higher.
- But alarm usability collapses if \(p\) is large (e.g., \(p \approx 0.44\)), producing a monitorability boundary: “ranking exists, but alarm does not.”

This is the minimal formal skeleton behind the common failure mode “high AUC, unusable at low-FPR.”

---

## 4. Practical diagnostics for real (non-binary) scores

Real scores are not exactly two-valued, but FPR floors often arise from **effective quantization / saturation** in the negative class, sometimes amplified by time-correlation.

### Diagnostic D1 — effective negative support size

Compute the number of unique score values (or bins) on negatives:

- \(K_{\mathrm{eff}} = \exp(H_{\mathrm{bin}})\) where \(H_{\mathrm{bin}}\) is entropy of binned negative scores.

Very small \(K_{\mathrm{eff}}\) implies discrete achievable FPR steps and a high risk of floors.

### Diagnostic D2 — achieved-FPR vs target-FPR curve (the Layer-B gate)

For targets \(f \in \{0.01, 0.05, 0.10\}\) (or your preregistered set), select thresholds \(\tau_f\) and report achieved \(\hat f\).

Practical floor signatures:

- \(\hat f\) is nearly constant across targets (flat curve).
- \(\min_f \hat f\) is far above the risk budget (alarm objective is ill-posed).

This is the most direct operational test: **if Layer B fails, the score is not an alarm**.

### Diagnostic D3 — tie / cluster dominance near the top quantiles

Compute the fraction of negative samples within the top-quantiles that share the same score (ties), or (if the score comes from a model) within-cluster variance near the decision boundary.

High tie dominance means threshold movement cannot smoothly control alarm rate.

### Diagnostic D4 — effective-n collapse (time correlation)

If windows are highly autocorrelated, the number of *effectively independent* negative samples can collapse, making calibration unstable and floors more likely.

A lightweight check:

- estimate an effective sample size \(n_{\mathrm{eff}}\) from the negative score autocorrelation (any standard ESS estimator is acceptable if declared), and
- report \(n_{\mathrm{eff}}/n\) alongside Layer-B results.

If \(n_{\mathrm{eff}} \ll n\), treat “apparently smooth calibration” as fragile and prefer conservative claims.

### Diagnostic D5 — quantify ABSTAIN explicitly

If a detector cannot operate at target FPR (floor), the correct operational behavior is often to **abstain** (do not gate, do not alarm, or fall back to a safe policy).

Do not hide abstention inside ranking metrics; report it as an explicit rate (e.g., “alarm never triggers at target FPR”).

---

## 5. Failure semantics (what to label)

Suggested mapping to GMB v0.4 labels:

- `SUPPORTED_FOR_ALARM`: Layer B passes (controllable), and Layer C is non-trivial at the preregistered operating point(s).
- `RANK_ONLY`: ranking is non-trivial (AUC/AP may be > baseline) but Layer B fails (floor / uncontrollable).
- `ESTIMATOR_UNSTABLE`: conclusions flip under small preregistered perturbations (e.g., window size, mild relabeling, seed range) or effective-n collapses in a way that changes admissibility.
- `INCONCLUSIVE`: missing artifacts, too few events, or insufficient negative support to evaluate the operating point.

Key rule: **a high AUC cannot override a Layer-B failure**.

---

## 6. Repair patterns (what counts as a real fix)

A fix is only real if it **restores Layer-B controllability**, not merely improves ranking.

Typical repair strategies (benchmark-neutral):

1. **Minimal repair baselines**: reweight / clip / discretize one problematic component and re-evaluate under the same Layer-B gate.
2. **Window redefinition**: adjust windowing to reduce pathological autocorrelation in negatives (then re-check \(n_{\mathrm{eff}}\)).
3. **Calibration health + ABSTAIN**: detect calibration collapse and explicitly abstain rather than force a threshold.
4. **Trajectory control**: keep the system in a monitorable regime (increase observation resolution, slow hardening, etc.).

---

## 7. Concrete repo example (optional)

GMB ships with a real run demonstrating this exact failure mode:

- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/`

Key takeaway:

- `score_sign = -1` exhibits an FPR floor at ~0.44 (uncontrollable) → `RANK_ONLY`.
- `score_sign = +1` is controllable; at FPR=0.10 coverage is ~65–70% with stable lead times → `SUPPORTED_FOR_ALARM`.

See:

- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/tables/gate_summary.csv`
- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_3_A2_tradeoff/tables/utility_at_fpr.csv`

