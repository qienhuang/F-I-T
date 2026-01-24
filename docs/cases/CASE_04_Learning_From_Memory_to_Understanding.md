# Case 04 — Learning: From Memorization to Understanding

## Scope & Claims Notice

This case illustrates how the FIT framework can be *applied* under a specific
interpretive lens and estimator choice.

It does NOT constitute proof, prediction, or universal validation.
The analysis is structural, not normative.


## System Snapshot
Learners often experience sudden shifts from memorization
to genuine understanding.

## FIT Variable Mapping
- F: Practice, feedback
- I: Mental representations
- T: Learning time
- C: Cognitive capacity

## Boundary (what is in-scope)

In-scope boundary (a minimal, auditable version):

- One learner (or defined cohort), one skill domain, and a fixed curriculum/task family.
- A defined evaluation protocol (held-out items or transfer tasks), and a defined practice schedule.

Out of scope: broad claims about intelligence, personality, or motivation (not because they do not matter, but because they break boundary discipline for a short case).

## Oracle (what counts as "understanding" under this boundary)

To make this case falsifiable, "understanding" must be grounded in an external evaluation channel, e.g.:

- transfer performance (novel but structurally similar problems),
- explanation quality scored by a rubric,
- or robustness under perturbations (rewording, reordering, new contexts).

## Minimal estimator tuple (suggested)

Write down an explicit estimator tuple for your boundary:

`E = (S_t, B, {F_hat, C_hat, I_hat}, W)`

One workable choice for this case:

- `S_t` (state): practice logs + evaluation logs + current curriculum stage.
- `B` (boundary): the fixed curriculum/task family, evaluation protocol, and practice schedule you will not change mid-study.
- `F_hat` (force proxy): practice intensity and feedback pressure (e.g., attempts per day; spacing schedule; feedback latency).
- `C_hat` (constraint proxy): working-memory load proxies (time per item, error persistence, dependence on surface cues).
- `I_hat` (information proxy): transfer competence and representation compression (e.g., fewer rules needed; higher robustness under perturbations).
- `W` (window): a fixed aggregation window (e.g., last 50 attempts, or 7 days).

## Event definition (illustrative)

Define one event so the case is evaluable:

- Target event `E_transfer_jump`: entry into a stable transfer-capable regime.
- Example operationalization (choose thresholds and preregister them):
  - transfer accuracy increases by at least `delta` within window `W_jump`, and
  - remains above a floor for `K_hold` evaluations, and
  - the in-distribution score does not collapse (avoid "transfer-only" artifacts).

## Phase Map
Use Phi1/Phi2/Phi3 as a teaching shorthand.

Phi1 (Accumulation):
- Rote memorization

Phi2 (Crystallization):
- Pattern recognition

Phi3 (Coordination):
- Conceptual understanding

## PT-MSS
Look for co-occurring signals:

- Force redistribution: practice shifts from copying to testing / generation (different error gradients).
- Information re-encoding: rules become compressible abstractions (fewer special cases).
- Constraint reorganization: constraints move from surface cues (keywords) to structural invariants (concepts).

## Post-Phi3 Bifurcation
Path A:
- Overfitting to test formats

Path B:
- Meta-learning, transferable understanding

## Monitorability exercise (early warning)

Treat "transition into transfer competence" as an event and ask whether early-warning signals are usable:

- Candidate score: gap between in-distribution performance and transfer performance; or sharp drops in error under perturbations.
- Alarm criterion: can you set a threshold with controlled false positives (FPR), or do you get unstable alarms?

Related (toy but instructive): `examples/monitorability_grokking.md`.

## Minimal logging schema (practical)

If you want this case to connect to future demos, define a minimal log schema:

- `ts` (timestamp)
- `item_id`, `item_type` (`train`, `transfer`, `perturbation`)
- `is_correct`
- `response_seconds`
- `hint_used` (boolean)
- `attempt_index` (within item or within session)

From this schema you can compute: learning curves, transfer gaps, robustness drops, and candidate early-warning scores.

## One falsifiable claim (pick exactly one; illustrative)

Example protocol claim (not asserted here):

> Under a fixed curriculum boundary, introducing spaced retrieval practice increases transfer accuracy by at least X points without increasing total study time beyond Y%.

## Takeaways
- Understanding can resemble a phase transition (a discrete shift in generalization under a fixed protocol).
- Insight often appears when earlier shortcuts saturate and new abstractions become more compressive.

