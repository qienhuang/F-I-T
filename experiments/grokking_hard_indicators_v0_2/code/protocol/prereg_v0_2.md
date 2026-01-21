# Prereg (Draft) - Grokking Hard Indicators v0.2

Status: draft (unlocked). Do not treat Phase B outputs as evidence until this document and the spec are locked.

## 1) Boundary

- Task: modular addition `(a+b) mod p`
- Dataset sizes: train/test as specified in `protocol/estimator_spec.v0_2.yaml`
- Model family: transformer (small)
- Checkpoint cadence: every `checkpoint_every_steps`

## 2) Event Definition (LOCKED IN v0.2)

Primary event **E1: Jump / regime shift** (defined on checkpointed `test_acc`).

Let checkpoints be indexed by `i = 0,1,2,...` with step `s_i`.
Let `m_i := test_acc(s_i)`.

Define trailing moving average:

- `m_bar_i := (1/W_jump) * sum_{j=0..W_jump-1} m_{i-j}` (only defined when `i >= W_jump-1`)

Define jump delta:

- `delta_i := m_bar_i - m_bar_{i-W_jump}` (only defined when `i >= 2*W_jump-1`)

Event time `t_E1` is the earliest step `s_i` such that:

1) `delta_i >= delta_jump`
2) `m_bar_i >= theta_floor`
3) stability: for the next `K_hold` checkpoints, `m_bar` does not drop by more than `delta_back`, i.e.
   `min_{k=1..K_hold} m_bar_{i+k} >= m_bar_i - delta_back`

Default v0.2 parameters (must be fixed before Phase B):

- `W_jump = 2` checkpoints
- `delta_jump = 0.04`
- `theta_floor = 0.85`
- `delta_back = 0.03`
- `K_hold = 5`

Secondary event **E2: Plateau** (reported, not primary):

- `t_E2 :=` earliest step such that `test_acc >= theta_plateau` for `K_hold` consecutive checkpoints
- default `theta_plateau = 0.92`, `K_hold = 5`

## 3) Labeling (prediction target)

At checkpoint step `s`, label:

- `y(s) = 1` iff `0 <= t_E1 - s <= N_steps`, else `0`.

`N_steps` is declared in the spec (`prediction_horizon_N_steps`).

## 4) Indicators (Estimator tuple) (LOCKED AFTER Phase A)

Estimator tuple is the v0.1 baseline:

- `H_spec(unembed.weight)` (normalized)
- `Correction_Rate` on corrupted subset

Raw decision score is computed by `grokking.analysis.score.compute_scores`.

**Score direction lock:** because the score may be monotone-increasing or monotone-decreasing with risk, we allow choosing a single global sign `sign ∈ {+1, -1}` on Phase A only, then lock it for Phase B:

- `score := sign * raw_score`

## 5) Phase Discipline

Phase A (explore):

- allowed (once): tune E1 parameters to achieve adequate event density (evaluable)
- allowed: choose `sign` for the score direction
- lock criterion: E1 event rate is non-trivial on explore seeds (e.g., >= 60%)

Phase B (eval):

- forbidden: changing any of `W_jump`, `delta_jump`, `theta_floor`, `delta_back`, `K_hold`, `N_steps`, `sign`, or the score definition
- if Phase B has insufficient E1 events: classify as **not evaluable under boundary**, not as "metric failure"

## 6) Metrics

Primary:

- ROC-AUC for predicting "E1 within next N steps"
- Average Precision (same label)
- Mean lead time at fixed FPR (e.g. 5%)

Secondary:

- E2 plateau reporting
- Per-seed event time distribution

## 7) Success Criteria (interpretation policy)

v0.2 is a baseline intended to validate the *evaluation protocol*.

- Protocol success: Phase B is evaluable (non-trivial E1 event rate) and the scripts run end-to-end on held-out seeds.
- Indicator success (stronger claim, optional): Phase B achieves both non-trivial lead time at `FPR=0.05` and ROC-AUC meaningfully above 0.5.

If indicator success is not met, we still report v0.2 as a clean weak/negative baseline without retroactively changing thresholds.

## 8) Post-hoc correction note (score orientation)

The v0.2 baseline score is defined by `grokking.analysis.score.compute_scores`. Empirically, on the initial v0.2 runs, the raw score was oriented opposite to the event label (i.e., larger raw scores were *less* likely to be followed by E1 within the horizon).

Policy:
- We treat selecting `score_sign ∈ {+1,-1}` as part of the Phase A lock (a monotone transform), and require fresh held-out evaluation seeds if the sign choice was discovered after inspecting Phase B.

Practical note:
- In v0.2, `score_sign=-1` improves ranking metrics (ROC-AUC/AP), but yields zero coverage for the low-FPR lead-time alarm metric at `FPR=0.05` under the current alarm rule (trigger on high score). This tradeoff must be resolved (and locked) before treating Phase B as evidence for the “hard indicator” claim.
