# GMB v0.5 runbook (CPU + single-GPU, repo-friendly)

**Goal**: produce a hold-out run that strengthens the GMB message for AI-safety practitioners:

- ranking metrics are not enough (Layer A);
- alarms must be *operational* under explicit risk budgets (Layer B);
- report abstention/coverage/lead-time at operating points (Layer C);
- quantify stability limits (Layer D), including effective-n collapse and tie dominance.

This runbook is written to be usable on:

- a **single-GPU** workstation (e.g., RTX 3090) for training new hold-out seeds, and
- a **CPU** machine for analysis + packaging.

---

## Phase order (do not reorder)

1) **CPU**: verify tooling works on existing runs (sanity check).  
2) **GPU**: train the hold-out seed range (logs-only).  
3) **CPU**: run diagnostics + FPR sweeps, then package a new GMB results folder.

---

## Prereqs (grokking workspace)

In your local `grokking/` workspace:

- Spec for hold-out seeds: `protocol/estimator_spec.v0_5_holdout.yaml`
  - eval seeds: `140–179`
  - `time.save_checkpoints: false` (logs-only)
- Diagnostics CLI:
  - `python -m grokking.analysis.gmb_v0_5_diagnostics`

---

## Common issue: it runs on CPU (not GPU)

If your progress bar shows `seed=... (cpu)`, the most common cause is a **CPU-only PyTorch** install in the Python you're using to run `grokking`.

Quick check:

```bash
python -c "import torch; print('torch', torch.__version__); print('cuda_available', torch.cuda.is_available()); print('device_count', torch.cuda.device_count())"
```

If you see `torch ... +cpu` or `cuda_available False`, training will fall back to CPU even if `nvidia-smi` can see your GPU.

### GPU setup (publish-safe guidance)

Use a Python version that reliably has CUDA wheels available (typically **Python 3.12 or 3.11**). Newer Python versions may end up with CPU-only wheels depending on the PyTorch release cadence.

Recommended workflow (OS-agnostic):

1) Create a clean virtual environment inside your `grokking/` workspace.  
2) Install a CUDA-enabled PyTorch build (follow the official PyTorch install command from `pytorch.org` for your CUDA version).  
3) Verify `torch.cuda.is_available()` is true.  
4) Run `grokking.runner.sweep` using that venv interpreter.

### Mac note

On Apple Silicon, the runner will prefer `mps` if available. On NVIDIA machines, it should pick `cuda` when `torch.cuda.is_available()` is true.

Local-only setup notes:

- If you keep machine-specific commands (paths, CUDA wheel URLs) as an internal lab memo, store them outside the public repo (e.g. under `chat-room/` in your local workspace).

## Step 1 (CPU, ~5–15 min): sanity check on existing eval runs

Run on an existing runs directory (any `runs/.../seed_*` directory you already have):

```bash
cd grokking
python -m grokking.analysis.gmb_v0_5_diagnostics \
  --runs_dir runs/eval \
  --event jump \
  --score_sign +1 \
  --out_dir results/v0_5_sanity/runs_eval_sign_plus1
```

Expected outputs:

- `diagnostics_per_run.csv`
- `tradeoff_with_abstain.csv`
- `summary.json`

If this step fails, fix tooling before training anything new.

---

## Step 2 (GPU, time varies): train hold-out seeds 140–179 (logs-only)

On the 3090 machine:

```bash
cd grokking
python -m grokking.runner.sweep \
  --spec protocol/estimator_spec.v0_5_holdout.yaml \
  --out runs_v0_5 \
  --phase eval
```

Notes:

- This writes to `runs_v0_5/eval/seed_<seed>/`.
- Checkpoints are disabled (logs-only) by default in the spec; this keeps artifacts small.
- If you want a quick smoke test first:

```bash
python -m grokking.runner.sweep \
  --spec protocol/estimator_spec.v0_5_holdout.yaml \
  --out runs_v0_5 \
  --phase eval \
  --limit 2
```

---

## Step 3 (CPU, ~10–30 min): evaluate FPR controllability + abstain + diagnostics

From the grokking workspace:

```bash
cd grokking

# sign=+1 (alarm-usable candidate)
python -m grokking.analysis.gmb_v0_5_diagnostics \
  --runs_dir runs_v0_5/eval \
  --event jump \
  --score_sign +1 \
  --out_dir results/v0_5_holdout/runs_v0_5_eval_sign_plus1

# sign=-1 (expected to show an FPR floor / invalid-as-alarm behavior in prior runs)
python -m grokking.analysis.gmb_v0_5_diagnostics \
  --runs_dir runs_v0_5/eval \
  --event jump \
  --score_sign -1 \
  --out_dir results/v0_5_holdout/runs_v0_5_eval_sign_minus1
```

Read the key rows:

- `tradeoff_with_abstain.csv`:
  - `fpr_target`, `fpr_achieved`, `coverage`, `abstain_rate`, `lead_time_mean_steps`
- `diagnostics_per_run.csv`:
  - `n_eff_ratio` (effective-n collapse)
  - `k_eff_neg` (effective negative support)
  - `tie_dom_topq` (top-quantile tie dominance)

---

## Step 4 (CPU, packaging): create a new GMB real-run folder

In the public FIT repo, create a new run folder (example id):

- `docs/benchmarks/gmb_v0_4/results/run_grokking_v0_5_holdout_140_179/`

and copy:

- `tradeoff_with_abstain.csv` (plus/minus sign variants, or a merged version)
- `diagnostics_per_run.csv` (plus/minus sign variants, or a merged version)
- optionally `summary.json` for provenance

Then fill `gmb_results_v0.4.<run_id>.yaml` using the v0.4 schema:

- label `SUPPORTED_FOR_ALARM` only if Layer B passes at the preregistered targets;
- label `RANK_ONLY` if ranking exists but FPR is uncontrollable (floor).

---

## Why this matters for AI safety (one sentence)

This hold-out run makes “monitorability under a risk budget” concrete: only scores that pass Layer B are admissible to trigger authority suspension (tool gating); everything else is diagnostic-only.
