"""
Sweep script for systematic scaling law experiments
Runs multiple configurations to map the phase diagram
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from itertools import product
import math
import subprocess
import sys


def _ratios_for_M(M: int) -> list[float]:
    """
    Build a ratio grid that resolves the predicted boundary region.

    Li² Thm 4 (as used in this repo): n_crit ~ c * M log M.
    Since n = ratio * M^2, the implied critical ratio scales like:
        ratio_crit ~ c * log(M) / M

    To avoid only sampling the "safe zone" (high ratio), we include a band of
    ratios around log(M)/M plus a few coarse points for the broader phase map.
    """
    r0 = float(math.log(M) / M)
    band = [
        0.5 * r0,
        0.75 * r0,
        1.0 * r0,
        1.25 * r0,
        1.5 * r0,
        2.0 * r0,
        3.0 * r0,
    ]
    coarse = [0.01, 0.02, 0.03, 0.04, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]

    out: list[float] = []
    for r in (band + coarse):
        if r <= 0:
            continue
        if r >= 0.70:
            continue
        out.append(float(r))

    # De-dup + stabilize filenames (train.py prints ratio with 2 decimals by default)
    ratios = sorted(set(round(r, 3) for r in out))
    return ratios


def generate_sweep_configs():
    """
    Generate all configurations for the scaling law sweep
    
    Based on Li² paper Thm 4: critical boundary at n ~ M·log(M)
    """
    
    # Prime group sizes (to ensure cyclic group structure)
    M_values = [23, 41, 59, 71, 89, 101, 127]
    
    # Seeds for statistical significance
    seeds = list(range(5))  # 5 seeds per configuration
    
    configs = []
    for M in M_values:
        ratios = _ratios_for_M(M)
        for ratio, seed in product(ratios, seeds):
            configs.append({
                'M': M,
                'train_ratio': ratio,
                'seed': seed,
                'hidden_dim': 2048,
                'activation': 'quadratic',
                'lr': 1e-3,
                'weight_decay': 2e-4,
                'epochs': 50000,
                'log_interval': 100,
                'grad_log_interval': 1000,
            })
    
    return configs


def run_single_experiment(config, output_dir):
    """Run a single experiment using subprocess"""
    cmd = [
        sys.executable, 'train.py',
        '--M', str(config['M']),
        '--ratio', str(config['train_ratio']),
        '--seed', str(config['seed']),
        '--hidden_dim', str(config['hidden_dim']),
        '--activation', config['activation'],
        '--lr', str(config['lr']),
        '--weight_decay', str(config['weight_decay']),
        '--epochs', str(config['epochs']),
        '--log_interval', str(config.get('log_interval', 100)),
        '--grad_log_interval', str(config.get('grad_log_interval', 1000)),
        '--output_dir', output_dir,
    ]
    
    subprocess.run(cmd, check=True)


def run_sweep(output_dir, dry_run=False, max_jobs=None):
    """
    Run the full sweep
    
    Args:
        output_dir: directory to save results
        dry_run: if True, just print configs without running
        max_jobs: maximum number of jobs to run (for testing)
    """
    configs = generate_sweep_configs()
    
    print(f"Total configurations: {len(configs)}")
    print(f"Output directory: {output_dir}")
    
    if dry_run:
        print("\n[DRY RUN] Would run the following configurations:")
        for i, config in enumerate(configs[:10]):
            print(f"  {i}: M={config['M']}, ratio={config['train_ratio']}, seed={config['seed']}")
        if len(configs) > 10:
            print(f"  ... and {len(configs) - 10} more")
        return
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save sweep configuration
    sweep_meta = {
        'timestamp': datetime.now().isoformat(),
        'total_configs': len(configs),
        'configs': configs,
    }
    with open(Path(output_dir) / 'sweep_meta.json', 'w') as f:
        json.dump(sweep_meta, f, indent=2)
    
    # Run experiments
    if max_jobs:
        configs = configs[:max_jobs]
        
    for i, config in enumerate(configs):
        print(f"\n{'='*60}")
        print(f"Running experiment {i+1}/{len(configs)}")
        print(f"M={config['M']}, ratio={config['train_ratio']}, seed={config['seed']}")
        print(f"{'='*60}")
        
        try:
            run_single_experiment(config, output_dir)
        except Exception as e:
            print(f"Error running experiment: {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"Sweep complete! Results saved to {output_dir}")
    print(f"{'='*60}")


def estimate_time():
    """Estimate total sweep time"""
    configs = generate_sweep_configs()
    n_configs = len(configs)
    
    # Rough estimate: ~5 min per config on GPU, ~30 min on CPU
    gpu_time_per_config = 5  # minutes
    cpu_time_per_config = 30  # minutes
    
    print(f"Sweep configuration:")
    print(f"  Total experiments: {n_configs}")
    print(f"  Estimated time (GPU): {n_configs * gpu_time_per_config / 60:.1f} hours")
    print(f"  Estimated time (CPU): {n_configs * cpu_time_per_config / 60:.1f} hours")
    
    # Breakdown by M
    from collections import Counter
    m_counts = Counter(c['M'] for c in configs)
    print(f"\n  Experiments per M value:")
    for M, count in sorted(m_counts.items()):
        print(f"    M={M}: {count}")


def main():
    parser = argparse.ArgumentParser(description='Run scaling law sweep')
    parser.add_argument('--output_dir', type=str, default='results/sweep',
                        help='Output directory for results')
    parser.add_argument('--dry_run', action='store_true',
                        help='Print configs without running')
    parser.add_argument('--max_jobs', type=int, default=None,
                        help='Maximum number of jobs to run')
    parser.add_argument('--estimate', action='store_true',
                        help='Estimate sweep time without running')
    
    args = parser.parse_args()
    
    if args.estimate:
        estimate_time()
        return
    
    run_sweep(args.output_dir, args.dry_run, args.max_jobs)


if __name__ == "__main__":
    main()
