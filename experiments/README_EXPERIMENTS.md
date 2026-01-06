# FIT Framework v2.3 Experiment Programs Guide

## Scope & Claims Notice

These experiments illustrate how the FIT framework can be *applied* under specific estimator choices and system configurations.

They do **not** constitute:
- proof of FIT,
- validation of universal claims,
- or generalization beyond the stated scope.

Any observed behavior is conditional on the chosen estimators and phase context. These artifacts should be interpreted as *reproducibility infrastructure*, not as theoretical evidence.

---

## Overview

These two Python programs fully automate the validation experiments defined in FIT Framework v2.3:

1. **conway_fit_experiment.py** - Conway's Game of Life validation
2. **langton_fit_experiment.py** - Langton's Ant validation

## Features

✓ **Fully Automated** - No human intervention required
✓ **Detailed Reports** - Automatically generates report.txt files
✓ **Configurable Parameters** - Adjustable experiment scale and thresholds
✓ **Statistical Validation** - Multiple runs ensure result reliability
✓ **Progress Display** - Real-time experiment progress

## System Requirements

- Python 3.7+
- NumPy

Install dependencies:
```bash
pip install numpy
```

## Usage

### 1. Conway's Game of Life Experiment

```bash
python conway_fit_experiment.py
```

**Tested Propositions:**
- P1: Nirvana Irreversibility
- P2: Late-Stage Constraint Non-Decrease
- P4: Plateau Detection Criterion
- P7: Entropy Capacity Bound
- P10: Constraint Estimator Equivalence

**Expected Runtime:** 5-10 minutes

**Output Files:**
- `conway_report.txt` - Detailed experiment report
- `conway_data/` - Numerical data directory

### 2. Langton's Ant Experiment

```bash
python langton_fit_experiment.py
```

**Tested Propositions:**
- P1: Attractor Persistence (highway analogy)
- P3: Force Variance Decay Family
- P11: Phase Transition Signal
- P18: Timescale Separation

**Expected Runtime:** 10-20 minutes (waiting for highway emergence)

**Output Files:**
- `langton_report.txt` - Detailed experiment report
- `langton_data/` - Numerical data directory

## Configuration Options

Both programs define an `ExperimentConfig` class at the beginning for adjustable parameters:

### Conway Configuration Example
```python
@dataclass
class ExperimentConfig:
    grid_size: int = 50           # Grid size
    num_runs: int = 20            # Number of independent runs
    max_steps: int = 2000         # Maximum steps per run
    window_W: int = 50            # Measurement window
    epsilon_force: float = 0.01   # Force variance threshold
```

### Langton Configuration Example
```python
@dataclass
class ExperimentConfig:
    grid_size: int = 200          # Grid size (needs to be large to observe highway)
    num_runs: int = 10            # Number of independent runs
    max_steps: int = 15000        # Maximum steps per run
    highway_start: int = 8000     # Expected highway emergence window
```

## Experiment Report Format

Reports contain the following sections:

1. **Configuration** - Experiment parameters
2. **Executive Summary** - Overall pass rate and statistics
3. **Proposition Details** - Test results for each proposition
4. **Interpretation** - FIT framework analysis of results
5. **Recommendations** - Directions for follow-up experiments

## Quick Validation Mode

For quick testing (approximately 1-2 minutes), modify configuration:

```python
# Conway quick mode
num_runs: int = 5
max_steps: int = 500

# Langton quick mode
num_runs: int = 3
max_steps: int = 10000
```

## Estimator Description

### Force (F) Estimators
- **Conway**: Based on neighbor count deviation from stable values
- **Langton**: Based on step direction alignment

### Constraint (C) Estimators
- **Frozen Fraction**: Proportion of unchanged cells within window
- **Compression Ratio**: Based on run-length encoding
- **Intrinsic Dimension**: Based on covariance matrix

### Information (I) Estimators
- **Shannon Entropy**: Based on block patterns
- **Predictive Information**: Based on trajectory sequences
- **Complexity Proxy**: Based on grid state standard deviation

## Interpreting Results

### Proposition Pass Criteria

- **P1**: < 10% escape rate from nirvana states
- **P2**: < 5% late-stage violation rate
- **P3**: > 50% of runs show exponential decay
- **P4**: Plateau regions detected
- **P7**: < 1% violation rate
- **P10**: Estimator correlation > 0.5
- **P11**: > 50% detect phase transition within expected range
- **P18**: > 50% show timescale separation (ratio > 2)

### Success Rate Interpretation

- **≥ 80%**: Strong support for FIT framework
- **50-80%**: Moderate support, some propositions need improvement
- **< 50%**: Significant challenges, revision needed

## FAQ

**Q: Can the program be interrupted?**
A: Yes, use Ctrl+C to interrupt. Completed run data will be preserved.

**Q: How to run only specific propositions?**
A: Comment out unwanted tests in the `run_all_tests()` method.

**Q: What if out of memory?**
A: Reduce `grid_size` or `num_runs` parameters.

**Q: Results unstable?**
A: Increase `num_runs` for better statistical stability.

## Literature Reference

These experiments correspond to FIT Framework v2.3 documentation:

- **Section 5**: Falsifiable Propositions Overview
- **Section 7**: Validation Roadmap
- **Appendix A**: Proposition Registry

## Extended Experiments

Based on these two programs, you can further:

1. **Parameter Sweeps**: Systematically vary `grid_size`, `window_W`, etc.
2. **Comparative Analysis**: Compare performance of different estimators
3. **Visualization**: Add graphical output of trajectories, entropy curves
4. **New Propositions**: Add tests for P5, P6, and other propositions

## Technical Details

### Random Number Seed
Conway program uses run index as seed to ensure reproducibility.

### Boundary Conditions
Both systems use periodic boundaries (toroidal grid).

### Numerical Stability
All logarithmic and division operations include small constants to prevent numerical errors.

## Contact & Feedback

If you discover bugs or have suggestions for improvements, please refer to the contact information in the FIT Framework v2.3 documentation.

---

**Version**: 1.0
**Date**: 2025-12-25
**Compatible**: FIT Framework v2.3
