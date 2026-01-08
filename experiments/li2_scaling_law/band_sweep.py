"""
Multi-seed band sweep for Li² scaling law verification
GPT constraints:
1. Config locked: hidden_dim/activation/lr/weight_decay/epochs/grok_threshold fixed
2. Only multi-seed boundary: M={23,41,59}, 4-6 ratios around critical, 3 seeds
3. Report in n-space (n_crit ~ M log M)
"""

import os
import subprocess
import sys
from pathlib import Path

# Locked configuration (DO NOT CHANGE)
CONFIG = {
    "hidden_dim": 2048,
    "activation": "quadratic",
    "lr": 0.001,
    "weight_decay": 0.001,
    "epochs": 25000,  # Enough for grokking
    "grok_threshold": 0.95,
}

# Band sweep configuration
SEEDS = [42, 123, 456]

# Ratios around critical points (from seed=42 experiments)
BANDS = {
    23: [0.54, 0.56, 0.58, 0.60],   # critical ~0.565
    41: [0.46, 0.48, 0.50, 0.52],   # critical ~0.49
    59: [0.42, 0.44, 0.46, 0.48],   # critical ~0.445
}

def run_experiment(M, ratio, seed, output_dir="results/band_sweep"):
    """Run a single experiment"""
    cmd = [
        sys.executable, "train.py",
        "--M", str(M),
        "--ratio", str(ratio),
        "--seed", str(seed),
        "--epochs", str(CONFIG["epochs"]),
        "--weight_decay", str(CONFIG["weight_decay"]),
        "--output_dir", output_dir,
    ]
    
    print(f"\n{'='*60}")
    print(f"Running: M={M}, ratio={ratio}, seed={seed}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    total = sum(len(ratios) * len(SEEDS) for ratios in BANDS.values())
    completed = 0
    failed = []
    
    print(f"Multi-seed band sweep: {total} experiments")
    print(f"Seeds: {SEEDS}")
    print(f"Config: {CONFIG}")
    print()
    
    for M, ratios in BANDS.items():
        for ratio in ratios:
            for seed in SEEDS:
                success = run_experiment(M, ratio, seed)
                completed += 1
                
                if not success:
                    failed.append((M, ratio, seed))
                
                print(f"Progress: {completed}/{total} ({100*completed/total:.1f}%)")
    
    print(f"\n{'='*60}")
    print(f"Completed: {completed - len(failed)}/{total}")
    if failed:
        print(f"Failed: {failed}")
    print(f"{'='*60}")
    
    print("\nNext step: run analyze.py to generate report")
    print("  python analyze.py --results_dir results/band_sweep --output_dir results/band_sweep/analysis")


if __name__ == "__main__":
    main()
