# Manuscript outline (suggested)

Working title: **Grokking hard indicators: a preregistered evaluation protocol and a weak baseline**

## 0) Abstract (1 paragraph)

- Problem: “hard indicators” are easy to claim and hard to validate because evaluation often becomes non-evaluable (no events).
- Contribution: a strict Explore -> Lock -> Evaluate pipeline and an event definition (jump/regime shift) that makes Phase B evaluable.
- Result: baseline estimator tuple is weak out-of-sample; report as negative/weak baseline.

## 1) Motivation & related work

- Grokking as a clean regime-shift phenomenon.
- Why online early warning is a useful benchmark.
- Prior indicators (loss/acc dynamics, sharpness, compression proxies, etc.).

## 2) Boundary (what is held fixed)

- Task (modular addition), model family, dataset, checkpoint cadence.

## 3) Event definitions

- E2 plateau (v0.1): often yields zero events in Phase B.
- E1 jump (v0.2): definition + parameters; why it increases event density.

## 4) Phase discipline (prereg logic)

- Phase A: choose event params (and score direction) once.
- Phase B: held-out seeds; no tuning allowed.
- “Not evaluable under boundary” vs “metric failure”.

## 5) Indicators & baseline score

- Estimator tuple definition and how the score is computed.
- Any allowed monotone transform/sign choice (chosen on Phase A only).

## 6) Metrics

- Ranking metrics: ROC-AUC, AP (per-run mean vs pooled).
- Alarm metrics: lead time + coverage at fixed FPR; how thresholds are chosen.
- **FPR feasibility / controllability check:** a “high AUC but infeasible low-FPR alarm” failure mode; show coverage–FPR tradeoff curves.

## 7) Results

### 7.1 Phase B evaluability and event density

- With v0.2 jump event (E1), Phase B is fully evaluable: **45/45** held-out seeds (`0–4`, `100–119`, `120–139`) exhibit a detectable jump.
- The jump yields a stable early-warning horizon: lead times on the order of **12–15k steps** (≈24–30 checkpoints at 500-step cadence).

### 7.2 FPR–coverage tradeoff (alarm feasibility)

- Sweep target FPR over `0.01–0.20`; report achieved FPR, coverage (runs with ≥1 TP trigger), and mean lead time.
- `score_sign=-1`: exhibits an **FPR floor** (achieved FPR ≈ **0.44** across targets), so low-FPR operation (e.g. `0.05`) is infeasible despite apparent ranking signal.
- `score_sign=+1`: achieved FPR tracks targets; coverage rises with FPR and lead time remains in the same 12–15k band.
  - At `FPR=0.05`, coverage ≈ **35%**.
  - At `FPR≈0.10`, coverage ≈ **65–70%**.

### 7.3 Ranking metrics vs alarm usability

- Show the concrete counterexample: higher mean AUC does **not** imply usable early-warning alarms if FPR is not controllable.
- Report per-run mean±std separately from pooled metrics (avoid conflating “ranking” with “operating point”).

### 7.4 Component-level diagnosis (v0.3 Phase A1)

- Decompose the score into `H_spec` and `CorrRate` terms; attribute seed-block effects:
  - seeds `100–119`: `H_spec` dominates and explains the sign-sensitive ranking improvements;
  - seeds `120–139`: both components weaken toward near-random discrimination.
- Crucially, even when a component yields ranking signal, it can still induce alarm infeasibility via an FPR floor.

## 8) Discussion / next steps

- Detector validity requires **FPR controllability** (alarm feasibility) in addition to ranking metrics.
- Practical operating points should be reported as tradeoff curves (not a single `FPR=0.05` point); `FPR≈0.10` is a plausible “usable” regime but reflects application-level risk tolerance.
- What would count as “validated hard indicator” under prereg discipline.
- Next steps: richer tuple, ablations, and system-level interventions that preserve monitorability (avoid FPR-floor regimes).

## 9) Reproducibility appendix

- Exact commands and seed blocks; pointers to released logs (avoid committing large logs to git).
