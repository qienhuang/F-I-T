# CASE_07 — Motor-Imagery BCI: monitorability under low-FPR budgets

**Status:** draft-final (repo-ready)  
**What this is:** a FIT reading exercise that treats motor-imagery BCI as a **low-FPR early-warning / actuation-admissibility** problem.  
**What this is not:** a new MI decoder, and not a medical claim.

## 0) Why this case matters (one paragraph)

Motor-imagery (MI) BCIs are one of the clearest real-world settings where **offline ranking metrics can look acceptable** while **deployment still fails**. The reason is rarely a single “accuracy number.” It is usually **monitorability**: drift, nonstationarity, autocorrelation, and score saturation can make a decision threshold **unreliable** under the low false-positive rates required for safe actuation. FIT’s contribution here is not new neuroscience; it is a disciplined way to declare boundaries, define events, select estimators, and report failure semantics without drifting into narrative.

## 1) System snapshot (FIT grammar)

We describe an MI-BCI pipeline as an evolving system:

- **State (S):** sensor streams + latent state proxies (EEG bandpower features, CSP projections, classifier scores, signal-quality metrics).
- **Force (F):** learning + adaptation (decoder training, user learning, feedback shaping, online recalibration).
- **Information (I):** model parameters + feature geometry (CSP filters, classifier weights, score distributions).
- **Time (T):** trials, blocks, sessions, days (the key is that *the system changes across T*).
- **Constraints (C):** hardware limits, attention/fatigue, artifact rejection, calibration protocol, clinical safety constraints, and “do no harm” actuation constraints.

The practical question is not “can we decode MI at all?” but:

> Can we **grant actuation authority** (e.g., move a cursor / trigger a device) only when the system is **monitorable** at a predeclared low-FPR budget?

## 2) Boundary (what varies vs what is held fixed)

BCI results are extremely boundary-sensitive. A repo-ready boundary declaration should be explicit:

**Held fixed (examples):**
- task protocol (MI classes, cue timing, rest windows)
- feature pipeline (e.g., bandpass + log-variance + CSP)
- classifier family (e.g., LDA / logistic regression)
- decision cadence (trial-level or sliding window)

**Allowed to vary (examples):**
- subject (cross-subject vs subject-specific)
- session/day (cross-session generalization)
- electrode subset / channel dropout
- artifact contamination level (blink/muscle)
- recalibration frequency (none vs periodic)

**Out of scope by default (unless declared):**
- clinical performance claims
- invasive BCIs
- real-time stimulation safety

## 3) Target events (what “failure” looks like)

To make evaluation non-handwavy, define events from observables:

### Event E_actuate_false (primary safety event)

An actuation is “unsafe” if it occurs during a **no-actuation** regime (e.g., REST or “do nothing” periods) or produces a command when the user is not attempting MI.

Operationally this is a standard “negative class” definition.

### Event E_drift (monitorability loss)

Drift is present when the score distribution or feature geometry shifts enough that:

- thresholds calibrated earlier no longer achieve target FPR, or
- the system enters a high-ABSTAIN regime at low FPR (coverage collapses), or
- achieved FPR saturates at a floor (cannot be reduced by thresholding).

E_drift is not “the model got worse”; it is “the system is no longer monitorable under the declared operating point.”

## 4) Estimator families (what to measure)

This case is intentionally conservative: we prefer **families** to a single metric.

### 4.1 Decoding score family (task-facing)

- classifier score / logit
- calibrated probability (only if calibration is itself monitored)

### 4.2 Signal-quality family (precondition for interpretability)

- per-channel noise / saturation flags
- bandpower outliers and artifact proxies
- missing-channel patterns (hardware constraint shocks)

### 4.3 Distribution-shift / geometry family (monitorability-facing)

- score distribution shift (e.g., quantile drift)
- feature covariance drift (e.g., CSP-space covariance distance)
- **effective-n collapse**: negative-window autocorrelation reduces effective independent support

### 4.4 Decision health family (actuation-facing)

- ABSTAIN rate (explicit)
- tie dominance / score quantization near the boundary
- achieved-FPR vs target-FPR curve (controllability)

## 5) Mapping to GMB / monitorability language (why this transfers to AI safety)

If you view MI-BCI as an alarm/actuation gate, you can report it using the same layers used in grokking/Dr.One:

- **Layer A (ranking):** AUC/AP are useful, but do not imply deployability.
- **Layer B (gate):** achieved FPR must track target; detect floors.
- **Layer C (utility):** coverage (non-abstain fraction) and latency/lead-time under the operating point.
- **Layer D (robustness):** stability across sessions/subjects and mild boundary perturbations.

The key cross-domain principle:

> Only scores that pass Layer B are admissible to trigger “authority” (actuation). Everything else is diagnostic-only.

## 6) Minimal runnable study (what to do first)

This is a suggested skeleton for a repo-ready evaluation (no claims until artifacts exist):

1) Pick a public MI dataset with session structure (subject-specific recommended first).
2) Define a negative class that corresponds to “no-actuation allowed” (REST or explicit no-command trials).
3) Train a baseline decoder on Session A; evaluate on Session B.
4) Calibrate thresholds on Session A to a preregistered target FPR grid (e.g., 0.01/0.05/0.10/0.20).
5) On Session B, report:
   - achieved FPR curve (Layer B)
   - coverage + ABSTAIN rate at the operating point(s) (Layer C)
   - effective-n ratio on negatives (Layer D diagnostic)
6) If Layer B fails (floor), label the decoder `RANK_ONLY` for actuation (even if AUC is high).

## 7) What FIT adds (and what it does not)

FIT does not “solve MI decoding.” Its value is to turn common MI-BCI arguments into auditable claims:

- “It works offline but not online” → boundary + monitorability failure semantics.
- “Calibration broke” → Layer B floor / effective-n collapse / tie dominance.
- “We should be conservative” → explicit ABSTAIN + authority suspension rule.

## 8) Cross-domain takeaway

Motor-imagery BCI is a clean real-world analog of AI-safety tool gating:

- **actuation authority** in BCI ↔ **tool authority** in agents,
- low-FPR constraints are non-negotiable in both,
- the hard part is often not accuracy, but **monitorability under a risk budget**.

