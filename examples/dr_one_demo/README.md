# Dr.One Demo (Self-Edit Loop + Monitorability Gate)

This is a **minimal, model-agnostic** demo that shows how a self-modifying system can be wrapped in a **monitorability control loop**:

- proposals come with a scalar `score` (a proxy for "safety/quality confidence")
- acceptance is **threshold-based** under a target false-positive budget (FPR)
- if FPR cannot be controlled by any threshold, the score is **invalid as an alarm**

The demo is intentionally small and auditable. It runs on CPU and does not require a GPU.

## Quick start (no model required)

```bash
python dr_one_demo.py self-edit --backend stub
python dr_one_demo.py fpr-demo
python dr_one_demo.py policy-eval --backend stub
```

Outputs:
- `out/audit_log.jsonl`

## Optional: connect a real local model (Ollama)

1) Install and start Ollama, then pull a small model (example):

```bash
ollama pull qwen2.5:3b
```

2) Run:

```bash
python dr_one_demo.py self-edit --backend ollama --ollama_model qwen2.5:3b
```

You can also run a **policy-style jailbreak evaluation** (baseline vs controlled tool gating):

```bash
python dr_one_demo.py policy-eval --backend ollama --ollama_model qwen2.5:3b
```

By default it uses `data/policy_prompts.jsonl` and writes:

- `out/policy_eval_summary.json`
- `out/policy_eval.json`

## What the demo edits

`toy_repo/` contains a tiny Python module plus `unittest` tests. The agent proposes a patch; the gate runs tests and only keeps patches that pass.

## What this answers (Controlled Nirvana critique)

This demo is meant to make three claims *executable*:

- **Estimator implementation**: `policy-eval` computes \(\hat{F}\) and \(\hat{C}\) from an observable **output distribution** over actions (empirical sampling).
- **Adversarial comparison**: `policy-eval` runs a small jailbreak-style prompt suite and reports baseline vs controlled tool-call rates.
- **Automatic trigger / cutoff**: when \(\sigma^2(\hat{F})\) spikes, or when low-FPR alarms become infeasible (FPR floor), the controller can **disable tool/API actions**.

## Notes

- This demo uses a deliberately simplified notion of `score` to illustrate the *protocol* (thresholding + controllability), not to claim a good indicator.
- See also:
  - `docs/core/monitorability.md`
  - `docs/core/monitorability_control_loop.md`
