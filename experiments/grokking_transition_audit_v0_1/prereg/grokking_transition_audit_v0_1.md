# Prereg: Grokking Transition Audit v0.1

## Claim under test

Relative to empirical baseline detectors, `PT-MSS + topological coherence gate`
should provide incrementally distinguishable labels for transition claims:

- `REGISTERED_TRANSITION`
- `NO_TRANSITION`
- `ESTIMATOR_UNSTABLE`
- `INCONCLUSIVE`

This claim is falsifiable and allowed to fail (`SCOPE_LIMITED`).

## Boundary

- Task: modular arithmetic grokking (single fixed task)
- Model: fixed small transformer architecture
- Train setup: fixed optimizer/schedule/batch size
- Probe set: fixed batch and seed
- Seeds: prereg lock at full evaluation size before evidence phase

## Estimator tuple

- S1 (force proxy): gradient energy redistribution (`D_F`)
- S2 (information proxy): representation shift (`D_I`, e.g. CKA-delta)
- S3 (constraint proxy): effective-dimension shift (`D_C`)

PT-MSS event is registered only if S1/S2/S3 events co-occur within a locked
window radius.

## Coherence gate (topological task)

- Family alignment tolerance: `|T_j - T_k| <= Delta_t`
- Order consistency: no family-dependent event order flip for `(S1,S2,S3)`

If PT-MSS passes but gate fails, the label is `ESTIMATOR_UNSTABLE`.

## Primary outcome

`C1` incremental distinguishability is evaluated as divergence rate between
baseline transition label and FIT transition label on valid seeds.

Pass rule (locked in YAML):

- divergence rate >= `c1_min_divergence_rate`
- divergence count >= `c1_min_replay_count`

Else verdict is `SCOPE_LIMITED_GROKKING_TRANSITION_DETECTION`.

## Failure semantics

- Frequent `NO_TRANSITION`: under this scope, no tri-signal co-window evidence.
- Frequent `ESTIMATOR_UNSTABLE`: estimator family disagreement; interpretation blocked.
- Frequent `INCONCLUSIVE`: instrumentation/density issue; run quality insufficient.

## Artifacts

- Per-seed JSON (schema-validated structure)
- Diagnostics CSV (seed-level gate status)
- Aggregate summary JSON
- Markdown report

