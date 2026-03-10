# civilization_dynamics_v0_1

Minimal reproducibility pack for the essay:
`essays/governance-longform/civilization_as_a_dynamical_system.v2.md`.

This package adds numeric evidence for:

- phase portrait under slow-manifold reduction (`x-R` plane),
- transcritical threshold scan (`N_flip`),
- collapse-time distribution across system scale `N`.

## Model

The ODE is the same three-variable system from the essay:

$$
\dot{x} = x(1-x)(dR - P\gamma),\quad
\dot{R} = rR\left(1 - \frac{R}{K}\right)\left(\frac{R}{A} - 1\right) - hxR,\quad
\dot{\gamma} = aR - bN - c\gamma.
$$

Integration uses explicit RK4 (implemented locally in `model.py`).

## Quick Start

```bash
cd experiments/civilization_dynamics_v0_1
python -m pip install -r requirements.txt
python scripts/run_all.py
```

Artifacts are written to `results/`.

## Individual Commands

```bash
python scripts/simulate.py --out results --N 30
python scripts/plot_phase_portrait.py --out results --N 30
python scripts/plot_bifurcation.py --out results
python scripts/collapse_time_scan.py --out results --n_grid_points 20 --trials_per_n 30
```

## Outputs

- `results/trajectory.csv`
- `results/trajectory.png`
- `results/phase_portrait.png`
- `results/bifurcation_scan.csv`
- `results/bifurcation_mu_vs_N.png`
- `results/collapse_time_scan.csv`
- `results/collapse_time_summary_by_N.csv`
- `results/collapse_time_scan.png`

## Notes

- This is a toy calibration scaffold, not a historical fit.
- Parameters in `model.py` are intentionally transparent and editable.
- For paper use, treat these as qualitative structure checks, then run domain-specific calibration in a separate preregistered package.

