# FIT/EST Core Contract (One Pager)

This is the minimum contract to keep an analysis auditable and falsifiable.
If any item is missing, default stance is **INCONCLUSIVE** and collect the missing artifacts.

## 1) Boundary (what is fixed vs what varies)

Write down:

- System / dataset / model family in scope
- What is allowed to change (seeds, prompts, configs, sampling)
- What is forbidden (post-hoc threshold changes, new data mixed into an evidence run)
- Real-world data note: record license/permission + time boundary

## 2) Window (what counts as a decision/event; cadence)

Define:

- Unit of time: steps / checkpoints / requests / days
- Window length `W`
- Event definition (how you detect the thing you care about from logs)
- What is "in-scope" vs "out-of-scope" inside the window

## 3) Estimator tuple (EST discipline)

Declare a small tuple, not a single metric:

- `E_state`: what you measure as state
- `E_constraint`: what you measure as constraints / friction / lock-in
- `E_force`: what you measure as pressure / drive / drift
- Optional: a small **estimator family** (two to three alternatives) to test robustness

Hard rule: if the conclusion flips across the estimator family, label it **estimator-dependent**.

## 4) Operating point (alarms / monitorability)

If the goal is an alarm, report at a fixed operating point:

- Target FPR (e.g., 0.05 or 0.10)
- Achieved FPR
- `fpr_floor` (minimum reachable FPR under thresholding)
- `feasible` (can we operate at the target FPR?)
- Coverage (fraction of runs that ever trigger)
- Lead time (when it triggers relative to the event)

Ranking metrics (AUC/AP) are not sufficient for alarms.
If AUC improves but FPR is not controllable, the score is **invalid as an alarm**.

## 5) Failure semantics (write them before running)

- **NON-EVALUABLE**: event density too low (no events in Phase B)
- **NON-MONITORABLE**: FPR floor too high / FPR not controllable
- **WEAK BASELINE**: feasible but low coverage at target FPR
- **INCONCLUSIVE**: missing boundary/window/estimator declaration or missing artifacts

## 6) Phase context (avoid phase-mixed claims)

Before trusting monotone proxies, ask:

- Does the data span multiple phases (pre/post transition)?
- If yes, segment analysis by phase (or label runs by phase) before aggregating.

