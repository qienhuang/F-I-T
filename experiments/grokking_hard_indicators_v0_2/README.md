# Grokking Hard Indicators (v0.2)

## What changed from v0.1

v0.1 was often **not evaluable** in Phase B because the event definition relied on an absolute plateau threshold (e.g. `test_acc >= 0.95`), which can yield zero events.

v0.2 switches the **primary event** to a **jump / regime-shift** event (E1) so Phase B has sufficient event density to evaluate predictors.

## Boundary

- Task: modular addition `(a + b) mod p`
- Model: small transformer
- Dataset: synthetic (generated)
- Logging: checkpoint-level metrics and estimator tuple values

## Primary event (E1): Jump / regime shift

Defined on checkpointed `test_acc`:

- Smooth with trailing moving average of length `W_jump` checkpoints.
- Jump if smoothed accuracy increases by at least `delta_jump` over the last `W_jump` checkpoints,
  is above `theta_floor`, and does not backslide by more than `delta_back` over the next `hold_k` checkpoints.

Default parameters are in `code/protocol/estimator_spec.v0_2.yaml` and `code/protocol/prereg_v0_2.md`.

## Results (current takeaway)

This experiment family is **evaluable and reproducible** (dense jump events on held-out seeds), but the baseline score is **not yet a stable hard indicator** under strict low-FPR alarm constraints.

See:

- `RESULTS_v0.2_v0.2.1.md`
- `results/v0.3_A1_component_diagnosis.md`
- `results/v0.3_A2_fpr_tradeoff.md`

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r code/requirements.txt
pip install -e code

# Phase A (explore; not evidence)
python -m grokking.runner.sweep --spec code/protocol/estimator_spec.v0_2.yaml --out runs --phase explore
python -m grokking.analysis.evaluate_suite --runs_dir runs/explore --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign 1
python -m grokking.analysis.evaluate_suite --runs_dir runs/explore --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign -1
python -m grokking.analysis.report_table --runs_dir runs/explore --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign 1 --out runs/phase_a_table.md

# Phase B (eval; only evidence if v0.2 prereg is locked beforehand)
python -m grokking.runner.sweep --spec code/protocol/estimator_spec.v0_2.yaml --out runs --phase eval
python -m grokking.analysis.evaluate_suite --runs_dir runs/eval --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign 1
python -m grokking.analysis.evaluate_suite --runs_dir runs/eval --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign -1
python -m grokking.analysis.report_table --runs_dir runs/eval --event jump --w_jump 2 --delta_jump 0.04 --theta_floor 0.85 --delta_back 0.03 --hold_k 5 --score_sign 1 --out runs/phase_b_table.md
```

## Notes

- If you want to report the old plateau event (E2), run evaluation with `--event plateau --theta_grok 0.92 --hold_k 5`.
- PyTorch is not pinned; install it per your platform (e.g. Apple Silicon `mps`).

## Status / write-up

- Current claim scope and next steps: `STATUS.md`
- Suggested paper structure (if writing this up): `MANUSCRIPT_OUTLINE.md`

## Example results (one internal run)

Using the default v0.2 jump event parameters (`W_jump=2`, `delta_jump=0.04`, `theta_floor=0.85`, `delta_back=0.03`, `hold_k=5`, `N_steps=20000`):

- Event rate (E1): Phase A `5/5`, Phase B `20/20`.
- Score orientation tradeoff:
  - Ranking metrics: with `score_sign=-1`, Phase B pooled `ROC_AUC=0.5635`, pooled `AP=0.0799`.
  - Low-FPR alarm (lead time @ `FPR=0.05`): with `score_sign=-1`, coverage `0/20` (no triggers); with `score_sign=+1`, per-run mean lead time `14550` steps with coverage `10/20`.

Interpretation: v0.2 makes Phase B reliably evaluable (dense events). The current baseline shows a real but unresolved tradeoff between ranking (AUC/AP) and low-FPR alarm coverage; v0.2.1 re-runs on fresh seeds with a locked choice.
