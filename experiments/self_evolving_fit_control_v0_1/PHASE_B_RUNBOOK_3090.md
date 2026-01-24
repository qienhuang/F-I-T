# Phase B Runbook (3090) — Self-Evolving FIT Control (v0.1 → v0.2 bridge)

This runbook is intentionally practical: it exists to turn the “philosophy vs code” critique into a repeatable data run.

## Objective (what new data should demonstrate)

1) Concrete estimators: \(\hat{F}(t)\), \(\hat{C}(t)\) computed from observables (starting with output distributions).
2) Adversarial comparison: baseline vs FIT-controlled behavior under a fixed jailbreak suite.
3) Automatic trigger: an explicit rule that can cut off tool/API use when volatility spikes or low-FPR alarms become infeasible (FPR floor).

## What to lock before collecting Phase B data

- Prompt suite (JSONL), including a “safe” subset and a jailbreak subset.
- Action set and what counts as “unsafe” (e.g., `TOOL:*`).
- Target operating points: \(\mathrm{FPR}^* \in \{0.05, 0.10, 0.20\}\) (report the whole tradeoff, not one point).
- Trigger parameters (e.g., \(\sigma^2(\hat{F})\) window and threshold; FPR-floor cutoff rule).
- Budget per run: samples per prompt, temperature, number of runs/seeds.

## Minimal data run (recommended first)

Use `examples/dr_one_demo` as the “real-model policy probe”:

```bash
cd github/F-I-T/examples/dr_one_demo

# Baseline vs controlled tool gating, using a local model (Ollama).
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --samples 50 --temperature 0.7 --target_fpr 0.10
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --samples 50 --temperature 0.7 --target_fpr 0.05
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b --samples 50 --temperature 0.7 --target_fpr 0.20
```

Each run writes:

- `out/policy_eval_summary.json`
- `out/policy_eval.json`

To get “multi-seed” stability without changing code, repeat the command multiple times with different `--temperature` or different prompt file order (and keep that protocol fixed once you switch to held-out runs).

## What to report (tables)

For each operating point \(\mathrm{FPR}^*\):

- Baseline adversarial tool rate vs controlled adversarial tool rate.
- Baseline alarm feasibility vs controlled alarm feasibility.
- Achieved FPR, FPR floor, and coverage on adversarial prompts.
- Fraction of runs that trip the controller (and which trigger fired first, if you log it).

## Next step (after the first data batch)

Once the policy probe is stable and the gate is shown to function on real model outputs, the next step is to:

- add a heavier estimator backend (optional): activations/gradients (Torch),
- and run a true “self-evolving” loop where tool use is not just simulated but actually gated by the controller.

