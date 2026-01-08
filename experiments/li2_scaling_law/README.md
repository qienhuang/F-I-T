# Li² Scaling Law Verification Experiments

This directory contains experiments to verify the scaling laws proposed in Yuandong Tian's Li² paper:
"Provable Scaling Laws of Feature Emergence From Learning Dynamics of Grokking"

## Paper Reference

- **arXiv**: https://arxiv.org/abs/2509.21519v5
- **Key Theorem**: Thm 4 predicts $n \gtrsim M \log M$ as the generalization/memorization boundary

## Experiment Goals

1. **Verify Scaling Law**: Measure the phase transition boundary in (M, sample_ratio) space
2. **Visualize Three Stages**: Confirm Lazy → Independent → Interactive dynamics
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

## Expected Results

According to Li² theory:
- For $M = 71$: critical ratio ≈ $\frac{\log 71}{71} \approx 0.06$
- Grokking should occur above this threshold
- Phase transition should sharpen with larger M

Practical note: empirical runs may require a constant factor $c>1$:
`ratio_crit ≈ c * log(M)/M`.

## Logged signals (for stage diagnostics)

In each run JSON (`results/M{M}_ratio{...}_seed{...}.json`), `history.grad_norms` includes:
- `gf_norm`: a feature-level proxy for $\|G_F\|$ computed as the norm of `dL/dh` where `h` is the hidden activation vector
- per-parameter gradient norms (e.g., `embed.weight`, `output.weight`)

## References

- Tian, Y. (2025). Provable Scaling Laws of Feature Emergence from Learning Dynamics of Grokking.
- Power et al. (2022). Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets.
