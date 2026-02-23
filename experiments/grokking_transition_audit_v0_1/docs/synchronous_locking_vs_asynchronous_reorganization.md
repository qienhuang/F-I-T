# Synchronous Locking vs Asynchronous Reorganization in Grokking

## 1. From "does transition occur?" to "what kind of transition?"

Classical grokking analysis often treats generalization jumps as a single
transition type.

Phase I audit shows a stratified structure across 40 seeds:

- baseline registers performance jump in `40/40`
- structural proxy activity appears broadly
- synchronized triple-signal locking appears in `2/40`

This motivates a distinction:

- asynchronous reorganization
- synchronous structural locking

## 2. Asynchronous multi-peak reorganization

Definition (within this prereg):

- each proxy signal (F, I, C) crosses threshold multiple times
- no sampled timepoint satisfies PT-MSS triple co-window condition

Empirical frequency: `35/40` seeds.

Interpretation:

- structural adjustments occur
- representation reshaping occurs
- constraint proxies fluctuate
- dynamics remain temporally distributed rather than synchronized

## 3. Synchronous structural locking

Definition:

- force redistribution, information re-encoding, and constraint restructuring
  jointly exceed locked thresholds within PT-MSS window

Empirical frequency: `2/40` seeds (`seed_159`, `seed_168`).

These cases show:

- high-amplitude tri-signal peaks
- estimator-family alignment
- replay label stability

Interpretation:

- coordinated structural event on the sampled grid

## 4. Why the distinction matters

This framework avoids an overclaim:

- not "most grokking transitions are false"
- but "most trajectories do not satisfy synchronized structural locking under
  this PT-MSS gate"

So:

- performance jump != synchronized structural locking
- baseline is permissive by design
- FIT gate is restrictive by design

This is a classification difference, not a blanket correctness claim.

## 5. Provisional taxonomy from Phase I

| Regime | Description | Frequency |
|---|---|---:|
| Asynchronous reorganization | distributed structural changes without locking | 35/40 |
| Synchronous locking | temporally aligned global restructuring | 2/40 |
| Measurement ambiguity | estimator families disagree on dominant event | 3/40 |

The taxonomy is produced by preregistered gates, not post hoc labeling.

## 6. Theory-facing implication

If this pattern holds across tasks:

- grokking is not a single dynamical mode
- synchronized locking may be rare
- performance gains can occur without global structural locking

This motivates Phase II questions about robustness and recoverability linkage.

## Scope boundary

Supported claim:

- FIT PT-MSS adds a reproducible gate that separates synchronized locking from
  permissive performance jumps.

Not claimed:

- baseline transitions are false
- grokking lacks structural change
- synchronous locking is the only valid transition notion

