# Conceptual Diagram: Synchronous Locking vs Asynchronous Reorganization

This note provides a structural interpretation guide for the Grokking
Transition Audit.

The conceptual figure uses four aligned panels, each representing one
dynamical regime.

## Panel A: Baseline performance jump

- x-axis: training step
- y-axis: test accuracy

Shape:

- long plateau
- sudden jump
- high-performance stabilization

This is the classical grokking signature as registered by the permissive
baseline detector. It does not by itself establish structural synchronization.

## Panel B: Asynchronous multi-peak reorganization

Three stacked signal tracks:

- force proxy `D_F(t)`
- information proxy `D_I(t)`
- constraint proxy `D_C(t)`

Observed pattern:

- each signal crosses threshold multiple times
- peaks are staggered in time
- no sampled timepoint satisfies triple-signal co-window condition

Interpretation:

- structural activity is present
- reorganization is distributed in time
- no synchronized locking event is registered by PT-MSS

This is the dominant regime in Phase I (`35/40` seeds).

## Panel C: Synchronous structural locking

Same three stacked tracks, but at one sampled step:

- `D_F`, `D_I`, and `D_C` all exceed locked thresholds
- primary and alt estimator families align on event timing/order

Interpretation:

- coordinated structural reconfiguration
- registered as `REGISTERED_TRANSITION`

This regime is rare in Phase I (`2/40` seeds).

## Panel D: Measurement ambiguity (optional inset)

- both families detect candidate events
- dominant event localization differs beyond alignment tolerance
- label: `ESTIMATOR_UNSTABLE`

Interpretation:

- competing structural interpretations, not structural absence

## Structural summary

The diagram separates three different objects:

1. performance-level transition
2. structural activity
3. structural synchronization

These are not equivalent.

## Why this framing matters

Without this distinction, one might overread:

> "FIT rejects most baseline transitions, so baseline transitions are false."

The audit does not support that claim.
What it supports is:

- many trajectories have structural activity
- few trajectories satisfy synchronized triple-signal locking under
  preregistered PT-MSS criteria

This is a dynamical taxonomy, not a truth judgment.

## Suggested caption

Figure X: Conceptual distinction between performance jumps, asynchronous
structural reorganization, and synchronous structural locking. Most trajectories
show staggered structural proxy peaks without temporal alignment. Only a small
subset show synchronized triple-signal locking under preregistered PT-MSS
criteria.

