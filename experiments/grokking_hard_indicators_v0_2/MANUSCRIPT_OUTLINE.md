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

- ROC-AUC, AP, lead time @ fixed FPR; how lead time is computed.

## 7) Results

- Event-rate summary (E1 density in A/B).
- Baseline predictive performance (reported neutrally).
- Failure analysis: why baseline is weak (hypotheses).

## 8) Discussion / next steps

- What would count as “validated hard indicator”.
- v0.3: richer tuple, ablations, larger Phase B, robustness across boundaries.

## 9) Reproducibility appendix

- Exact commands; pointers to released logs (avoid committing large logs to git).

