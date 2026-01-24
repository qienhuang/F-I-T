# Case 05 Addendum: A FIT-Disciplined Research Pitch (Computational Phase Transition)

This addendum turns the "design phase transitions" intuition into a preregisterable, falsifiable protocol for FIT readers.

It assumes you are comfortable with the estimator-tuple framing and basic monitorability discipline:

- `docs/core/how_to_falsify_fit.md`
- `docs/core/monitorability.md`

## 0) Scope

Target class: data-driven inverse design loops that look like:

generate -> oracle evaluate -> accept/reject -> curate dataset -> retrain -> repeat

Example inspiration: bicontinuous multiscale microstructure inverse design with:

- a hard boundary mask (interface contract),
- a feasibility filter (bicontinuity/connectivity/manufacturability),
- a physics oracle (FEA / CFD / experiments),
- and an AL loop that expands coverage in a property space.

Concrete anchor (optional):

- Nature Communications paper (2026): https://www.nature.com/articles/s41467-025-68089-2
- L-BOM project repo (if available): https://github.com/llwang91/L-BOM/

This pitch does not claim FIT “explains” the domain. It only claims FIT can impose discipline on what you measure and what would count as a phase-like transition.

## 1) The claim (pick exactly one primary claim)

Primary claim H1 (phase-like event in the design loop):

> Under a locked boundary mask family and a locked oracle, the loop exhibits a discrete “coverage jump” event E_jump: within a short window, feasible coverage in a target property region increases by at least delta_cov, while feasibility (constraint satisfaction) does not degrade beyond delta_fail.

This is intentionally modest:

- it is about the loop dynamics (not physics),
- it is measurable,
- and it can fail cleanly.

## 2) Boundary (lock before Phase B)

You must lock:

- mask family: which boundary masks are in-scope (and which are held out),
- oracle definition: which simulator/FEA settings, meshing, solver tolerances,
- feasible microstructure definition: bicontinuity/connectivity checks + manufacturability checks,
- target region definition: the property space region you are trying to cover (and how distance is computed),
- compute budget: number of AL rounds, candidates per round, and retraining schedule.

Boundary-discipline rule:

If you change any of the above after seeing results, treat it as a new study (not a rescue of H1).

## 3) Estimator tuple (declare the minimum you will log)

Declare an estimator tuple:

E = (S_t, B, {F_hat, C_hat, I_hat}, W)

One practical choice:

- S_t: dataset state + model state at AL iteration t
- F_hat(t): selection pressure proxy
  - e.g., average penalty-weighted distance to target among selected candidates
- C_hat(t): constraint accumulation proxy
  - e.g., feasibility rate, interface defect rate, connectivity failure rate
- I_hat(t): library / manifold proxy
  - e.g., diversity of feasible microstructures (entropy over bins), effective coverage volume in property space
- W: fixed window size(s) for smoothing, declared in advance

Important: do not claim "I increased" unless you define I_hat.

If you want a fill-in worksheet for this domain, see:

- `docs/cases/CASE_05_LBOM_Workbook.md`

## 4) Event definition (E_jump)

Define a scalar coverage statistic cov(t). Examples:

- cov(t) = fraction of the target region covered by feasible samples (bin coverage),
- or cov(t) = volume of the convex hull (or KDE mass) of feasible samples inside the target region.

Define E_jump at the first t where:

- cov(t) - cov(t - W_jump) >= delta_cov
- and fail_rate(t) - fail_rate(t - W_jump) <= delta_fail

This is a “phase-like” event only in the weak sense that it is a discrete regime-shift observable under a fixed protocol.

## 5) PT-MSS-style diagnostics (optional, but must be operational)

If you want to use “phase transition” language, require a minimal co-occurrence check.

Operationalize three signals:

1) Force redistribution:
   - e.g., AL acquisition shifts from mostly rejecting to mostly accepting, or the accepted set moves sharply in target-distance space.
2) Information re-encoding:
   - e.g., generator latent clustering changes; reconstruction error distribution shifts; or a simple manifold proxy changes discontinuously.
3) Constraint reorganization:
   - e.g., boundary/interface defect rate drops sharply without sacrificing target match.

If you cannot measure these, do not use PT-MSS framing; report only H1.

## 6) A monitorability gate (the grokking lesson)

Do not report only ranking metrics.

Pick an alarm target event and ask whether alarms are usable under low false positives.

Example early-warning task:

- Target event: interface failure at assembly or connectivity defect spike.
- Score candidate: any scalar model score used to select candidates (quality score, uncertainty score, novelty score).

Report:

- achieved FPR vs target FPR under thresholding,
- coverage vs FPR sweep,
- and whether an FPR floor exists (degenerate score).

If an indicator cannot operate at low FPR, it is invalid as an alarm even if AUC is high.

See: `docs/core/monitorability.md`.

## 7) Phase A / Phase B discipline (same spirit as grokking protocol)

Phase A (explore):

- allowed to choose delta_cov, delta_fail, W_jump, and the estimator definitions,
- must demonstrate E_jump has sufficient event density under the locked boundary.

Phase B (evaluate):

- held-out masks (or held-out target regions),
- no changes to definitions,
- report the same metrics and the monitorability gate.

If Phase B has no events, label as NOT EVALUABLE UNDER BOUNDARY (not “success” or “failure”).

## 8) What would count as a strong negative result (publishable)

A strong negative result is not “we didn’t get a better structure”.

A strong negative result is one of:

- H1 fails under locked boundary despite sufficient budget (no coverage jump),
- E_jump exists but monitorability fails (FPR floors make alarms unusable),
- or PT-MSS diagnostics cannot be satisfied with any reasonable operationalization (so “phase transition” language is unjustified).

These are exactly the kinds of results that keep the protocol falsifiable and interpretable.

## 9) Optional: a FIT-aware inverse design protocol (minimal)

If you want to operationalize the “FIT as design discipline” idea without expanding scope, the minimal protocol is:

1) Lock the boundary contracts (mask/interface constraints) and publish them as artifacts.
2) Lock the oracle definition (solver settings, tolerances, failure handling) and publish it.
3) Declare the estimator tuple and the admissible family (small, finite, preregistered).
4) Define one event (E_jump or a failure event) and one operating point family (FPR targets).
5) Report both ranking metrics and alarm usability (FPR floor / coverage-vs-FPR).
6) Publish the decision trace (what was generated, what the oracle returned, why it was accepted/rejected).

If any step is skipped, do not claim “phase design” results; report it as an exploratory pilot.
