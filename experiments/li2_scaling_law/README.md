# Li2 Scaling Law Verification Experiments

This directory contains experiments to verify the scaling laws proposed in Yuandong Tian's Li2 paper:
"Provable Scaling Laws of Feature Emergence From Learning Dynamics of Grokking"

## Paper Reference

- **arXiv**: https://arxiv.org/abs/2509.21519v5
- **Key Theorem**: Thm 4 predicts $n \gtrsim M \log M$ as the generalization/memorization boundary

## Experiment Goals

1. **Verify Scaling Law**: Measure the phase transition boundary in (M, sample_ratio) space
2. **Visualize Three Stages**: Confirm Lazy -> Independent -> Interactive dynamics
3. **Extend to Architectures**: Test if theory holds for deeper networks
4. **Extend to Tasks**: Test beyond modular addition

## Quick Start

```bash
# Install dependencies
pip install torch numpy matplotlib tqdm

# Run basic experiment
python train.py --M 71 --ratio 0.4 --seed 42

# Run quick sweep (smaller grid)
python quick_sweep.py

# Run full sweep (ratio grid is centered around log(M)/M per M)
python sweep.py --estimate
python sweep.py --output_dir results/sweep

# Analyze results (recursively scans `results/`)
python analyze.py --results_dir results --output_dir results/analysis
```

## Colab (one-click reproduction)

Notebook: `colab_li2_scaling_law.ipynb`

Open in Colab (replace `<OWNER>/<REPO>` if needed):
`https://colab.research.google.com/github/<OWNER>/<REPO>/blob/main/experiments/li2_scaling_law/colab_li2_scaling_law.ipynb`

## Baidu AI Studio (Paddle, Python 3.7)

If your cloud runtime only supports PaddlePaddle (and older Python), use:
`AISTUDIO_PADDLE_PY37.md`.

## Dense M sweep (beta vs M, exploratory)

This sweep targets the follow-up question: does the grok-speed sensitivity (beta) vary with M?

Summary note: `BETA_TRANSITION_FINDINGS.md`

```bash
# Resumable: skips existing JSON files in output_dir.
python dense_m_sweep.py --Ms 35,38,40,45,50 --output_dir results/dense_m_sweep

# Faster "beta-only" sweep: focus on ratios above r_crit_est (avoid very slow below-critical points).
# PowerShell tip: if the value starts with '-', use either --deltas=-0.02,... or quote it.
python dense_m_sweep.py --Ms 50 --deltas=-0.02,0.02,0.04,0.06 --output_dir results/dense_m_sweep

# Analyze beta transition curve
python analyze_beta_transition.py --results_dir results/dense_m_sweep --output_dir results/dense_m_sweep/analysis
```

## Multi-seed spot check (recommended before claims)

Single-seed beta fits can be misleading because r_crit is poorly estimated. Use a small multi-seed grid
around the boundary, then fit using probability-based r_crit:

```bash
# Targeted multi-seed runs (resumable)
python multiseed_fill.py --spec \"30:0.515,0.535,0.555,0.575;45:0.461,0.501,0.521,0.541\" --output_dir results/beta_multiseed

# Analyze (for 3 seeds, using >=2/3 as the fit-point filter)
python analyze_beta_transition.py --results_dir results/beta_multiseed --output_dir results/beta_multiseed/analysis_p0666 --min_prob 0.666 --min_points 3
```

## FIT validation protocol (one-command)

Protocol doc: `FIT_VALIDATION_README.md`

Unified runner:
```bash
python run_fit_validation.py --M 71 --ratios 0.38,0.40,0.42,0.44,0.46,0.48,0.50,0.52 --seeds 42,123,456
```

## Key Files

| File | Description |
|------|-------------|
| `train.py` | Training loop with metrics logging |
| `models/grok_net.py` | 2-layer network matching paper |
| `data/generate_data.py` | Modular arithmetic data generation |
| `analyze.py` | Scaling law fitting and analysis |
| `fit_scaling_law.py` | Simple n-space fit (hardcoded boundary points) |
| `plot_results.py` | Plot figures from boundary points (hardcoded) |
| `sweep.py` | Systematic sweep over (M, ratio, seed) |
| `quick_sweep.py` | Reduced sweep for iteration |
| `run_fit_validation.py` | Unified FIT validation entry point |
| `FIT_VALIDATION_README.md` | Protocol docs for FIT validation |

## Expected Results

According to Li2 theory:
- For $M = 71$: critical ratio ~ $\frac{\log 71}{71} \approx 0.06$
- Grokking should occur above this threshold
- Phase transition should sharpen with larger M

Practical note: empirical runs may require a constant factor $c>1$:
`ratio_crit ~ c * log(M)/M`.

## Logged signals (for stage diagnostics)

In each run JSON (`results/M{M}_ratio{...}_seed{...}.json`), `history.grad_norms` includes:
- `gf_norm`: a feature-level proxy for $\|G_F\|$ computed as the norm of `dL/dh` where `h` is the hidden activation vector
- per-parameter gradient norms (e.g., `embed.weight`, `output.weight`)

## PT-MSS phase-aligned plots (FIT-style audit)

To audit phase/milestone structure per-run, generate a phase-aligned plot that overlays:
train/test accuracy, train loss, `gf_norm`, and `gf_align_target_w_mean`, annotated with `mem_epoch` and `grok_epoch`.

```bash
python pt_mss_phase_plot.py --inputs "results/beta_multiseed/M30_ratio0.515_seed42.json" --write_md
```

## References

- Tian, Y. (2025). Provable Scaling Laws of Feature Emergence from Learning Dynamics of Grokking.
- Power et al. (2022). Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets.
