#!/usr/bin/env python3
"""
Dense M-sweep to identify the critical M value where beta transitions.
Tests M ∈ {15, 18, 20, 23, 25, 28, 30, 32, 35, 38, 40, 45, 50}
For each M, uses 3 ratios around estimated r_crit to capture the transition precisely.
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict
import numpy as np
import sys

# Configuration
CONFIG_BASE = {
    "hidden_dim": 2048,
    "activation": "quadratic",
    "lr": 0.001,
    "weight_decay": 0.001,
    "epochs": 25000,
    "grok_threshold": 0.95,
}

# M values to test (denser sweep)
M_VALUES = [15, 18, 20, 23, 25, 28, 30, 32, 35, 38, 40, 45, 50]
SEEDS = [42]  # Single seed per config to save time (fewer total runs)

# Result directory
RESULTS_DIR = Path("results/dense_m_sweep")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def estimate_critical_ratio(M):
    """
    Estimate r_crit from observed pattern.
    
    From band_sweep:
    - M=23: r_crit ≈ 0.57
    - M=41: r_crit ≈ 0.49
    - M=59: r_crit ≈ 0.45
    
    Rough fit: r_crit ≈ 0.65 - 0.002 * M
    """
    # Linear interpolation based on observed points
    if M <= 23:
        # Linear from M=15 (est 0.59) to M=23 (0.57)
        r_crit = 0.61 - 0.0025 * (M - 15)
    elif M <= 41:
        # Linear from M=23 (0.57) to M=41 (0.49)
        r_crit = 0.57 - 0.005 * (M - 23)
    else:
        # Linear from M=41 (0.49) to M=59 (0.45)
        r_crit = 0.49 - 0.0022 * (M - 41)
    
    return r_crit

def design_ratios_for_M(M):
    """
    Design 5 ratio points around r_crit to capture transition precisely.
    
    Pattern:
      [r_crit - 0.04, r_crit - 0.02, r_crit, r_crit + 0.02, r_crit + 0.04]
    """
    r_crit = estimate_critical_ratio(M)
    ratios = [
        r_crit - 0.04,
        r_crit - 0.02,
        r_crit,
        r_crit + 0.02,
        r_crit + 0.04,
    ]
    # Clamp to valid range [0.1, 1.0]
    ratios = [max(0.1, min(1.0, r)) for r in ratios]
    return sorted(list(set(ratios)))  # Remove duplicates and sort

def run_experiment(M, ratio, seed):
    """Run a single training experiment."""
    # Build command with direct arguments
    cmd = [
        sys.executable, "train.py",
        "--M", str(M),
        "--ratio", str(ratio),
        "--seed", str(seed),
        "--hidden_dim", str(CONFIG_BASE["hidden_dim"]),
        "--activation", CONFIG_BASE["activation"],
        "--lr", str(CONFIG_BASE["lr"]),
        "--weight_decay", str(CONFIG_BASE["weight_decay"]),
        "--epochs", str(CONFIG_BASE["epochs"]),
        "--output_dir", str(RESULTS_DIR),
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0

def main():
    print("=" * 70)
    print("Dense M-Sweep: Locating β Phase Transition")
    print("=" * 70)
    print(f"\nM values to test: {M_VALUES}")
    print(f"Seeds per config: {len(SEEDS)}")
    print(f"Total experiments: ~{len(M_VALUES) * 5 * len(SEEDS)}")
    print()
    
    # Plan experiment
    experiment_plan = {}
    total_exps = 0
    
    for M in M_VALUES:
        ratios = design_ratios_for_M(M)
        experiment_plan[M] = ratios
        total_exps += len(ratios) * len(SEEDS)
        
        r_crit = estimate_critical_ratio(M)
        print(f"M={M:2d}: r_crit_est ≈ {r_crit:.4f}")
        print(f"  → Testing ratios: {[f'{r:.3f}' for r in ratios]}")
    
    print(f"\nTotal experiments planned: {total_exps}")
    print(f"Estimated time: ~{total_exps * 3.5 / 60:.1f} hours (at 3.5 min/exp)")
    
    # Run experiments
    print("\n" + "=" * 70)
    print("Running Dense M-Sweep")
    print("=" * 70)
    
    exp_count = 0
    for M in M_VALUES:
        for ratio in experiment_plan[M]:
            for seed in SEEDS:
                exp_count += 1
                print(f"\n[{exp_count}/{total_exps}] M={M}, ratio={ratio:.3f}, seed={seed}")
                
                success = run_experiment(M, ratio, seed)
                if not success:
                    print(f"  ⚠️  Experiment failed (continuing)")
    
    print("\n" + "=" * 70)
    print("✅ Dense M-Sweep Complete")
    print("=" * 70)
    print(f"\nResults directory: {RESULTS_DIR}")
    print(f"Next step: Run analyze_beta_transition.py to analyze β evolution")

if __name__ == "__main__":
    main()
