# Status (v0.2)

As of 2026-01-20, **v0.2 is complete as a reproducible, held-out evaluation pipeline**, but it is **not yet a validated “hard indicator”** in the strong sense.

## What is “done” (strong claim we can make)

- **Protocol/pipeline success:** Explore -> Lock -> Evaluate works end-to-end on held-out seeds.
- **Evaluability fixed:** the primary event is **E1 (jump/regime shift)**, which yields dense events in Phase B (25/25 runs had an E1 under the current boundary), so Phase B is not “NaN / no-event” anymore.
- **Reproducibility materials exist:** this folder contains a runnable snapshot (`code/`) plus a locked-ish protocol draft.

## What is *not* done yet (claim we should not make)

- **Hard-indicator validation (strong):** the baseline shows a **tradeoff**:
  - `score_sign=-1` improves ranking (Phase B pooled ROC-AUC ~0.56), but yields **0/20** coverage for lead-time alarms at `FPR=0.05`.
  - `score_sign=+1` yields non-zero alarm coverage, but ranking metrics are <0.5.
  This is not yet a clean “hard indicator verified” story.

## What can be published now (low-risk)

- A clean **v0.2 technical report / reproducibility note**:
  - the prereg-style evaluation setup;
  - why plateau events are often not evaluable;
  - why jump events improve evaluability;
  - baseline results reported honestly as modest/early signal.

## What to do next (v0.3 direction)

- Lock a single **alarm policy** on Phase A (including score orientation + trigger rule), then rerun Phase B on fresh seeds (v0.2.1).
- Improve the estimator tuple (still preregistered): add 1–3 cheap-to-log indicators and re-evaluate on held-out seeds.
- Keep Phase discipline strict: no threshold or model changes on eval seeds.
