# Self-Evolving Loop + FIT Control (v0.1)

Status: **exploratory scaffold**. v0.1 exists to make the loop runnable and falsifiable, not to claim robustness.

This folder is a direct response to the critique “is this only a philosophical framework?” It provides:

- a concrete estimator implementation that computes \(\hat{F}\) and \(\hat{C}\) from an observable output distribution,
- a minimal jailbreak-style adversarial comparison (baseline vs controlled),
- and an automatic trigger that can cut off tool/API usage when monitorability is lost.

## What is runnable today

- Code entry point: `code/run_demo.py`
- Estimator math: `code/src/sefit/estimators.py`
- Alarm feasibility / FPR controllability: `code/src/sefit/monitorability.py`
- Toy policy backend (output-distribution source-of-truth): `code/src/sefit/toy_backend.py`
- Jailbreak prompt suite: `code/data/jailbreak_prompts.jsonl`

Quick run (no dependencies):

```bash
cd github/F-I-T/experiments/self_evolving_fit_control_v0_1
PYTHONPATH=code/src python code/run_demo.py
```

Outputs:

- `out/demo_report.json` (headline rates)
- `out/jailbreak_eval.json` (per-prompt trace)

## Protocol / prereg

- Draft prereg: `PREREG_v0_1.md`

## v0.1 scope

v0.1 computes \(\hat{F}\) and \(\hat{C}\) from output distributions (toy policy). It does not yet hook gradients/activations.

The point is to validate pipeline pieces that the grokking work showed are mandatory for early warning:

- event evaluability (no "zero-event / NaN" Phase B),
- and alarm usability (explicit FPR feasibility / tradeoff), not just ranking metrics.

## Next step when the 3090 arrives (planned)

After the CPU-only pre-validator is stable, the next data-producing step is to add a real model backend and run multi-seed Phase B under a locked boundary:

- keep the same \(\hat{F}\)/\(\hat{C}\) interfaces, but source them from real outputs (and optionally activations/gradients),
- run a fixed jailbreak suite baseline vs controlled (tool gating) and report coverage at multiple target FPR operating points,
- log enough to reproduce FPR floors and volatility-trigger behavior, not only aggregate rates.
