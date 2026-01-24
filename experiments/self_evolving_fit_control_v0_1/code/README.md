# Self-Evolving FIT Control (v0.1) - Code

This folder provides a minimal, auditable implementation of:

- an estimator layer that produces concrete \(\hat{F}(t)\) and \(\hat{C}(t)\) proxies from observable signals,
- an automatic "monitorability controller" that can cut off tool/API usage when an alarm becomes infeasible,
- a small jailbreak-style prompt suite for baseline vs controlled comparisons.

It is a v0.1 scaffold: the goal is to make the protocol executable and falsifiable, not to claim broad robustness.

## Quick start (CPU, no model; no dependencies)

```bash
cd /path/to/F-I-T/experiments/self_evolving_fit_control_v0_1
PYTHONPATH=code/src python code/run_demo.py
```

This runs a deterministic toy backend and produces:

- `out/demo_report.json`
- `out/jailbreak_eval.json`
 
## Notes

- v0.1 focuses on wiring and falsifiability; the toy backend is the source-of-truth for the estimator math.
- `code/requirements.txt` is intentionally empty for the demo. Future backends may add optional deps.
