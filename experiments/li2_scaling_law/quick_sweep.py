"""
Quick sweep for initial scaling law exploration
Uses fewer configs and shorter training for rapid iteration
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from itertools import product

# Add parent to path
sys.path.append(str(Path(__file__).parent))

from train import train, save_results


def run_quick_sweep():
    """
    Quick sweep with reduced configurations
    
    Target: Get rough phase diagram in ~2 hours on CPU
    """
    
    # Reduced M values (3 points for trend)
    M_values = [23, 59, 97]
    
    # Key ratios around theoretical boundary
    # Theory: critical ratio ~ log(M)/M
    # M=23: ~0.14, M=59: ~0.07, M=97: ~0.05
    ratios = [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
    
    # Fewer seeds
    seeds = [0, 1, 2]
    
    # Shorter training (may miss late grokking)
    epochs = 20000
    
    print("=" * 60)
    print("Quick Scaling Law Sweep")
    print("=" * 60)
    print(f"M values: {M_values}")
    print(f"Ratios: {ratios}")
    print(f"Seeds: {seeds}")
    print(f"Epochs: {epochs}")
    print(f"Total experiments: {len(M_values) * len(ratios) * len(seeds)}")
    print("=" * 60)
    
    output_dir = Path("results/quick_sweep")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save sweep config
    sweep_config = {
        'M_values': M_values,
        'ratios': ratios,
        'seeds': seeds,
        'epochs': epochs,
        'timestamp': datetime.now().isoformat(),
    }
    with open(output_dir / 'sweep_config.json', 'w') as f:
        json.dump(sweep_config, f, indent=2)
    
    results_summary = []
    
    total = len(M_values) * len(ratios) * len(seeds)
    i = 0
    
    for M in M_values:
        for ratio in ratios:
            for seed in seeds:
                i += 1
                print(f"\n[{i}/{total}] M={M}, ratio={ratio:.2f}, seed={seed}")
                
                config = {
                    'M': M,
                    'train_ratio': ratio,
                    'seed': seed,
                    'hidden_dim': 1024,  # Smaller for speed
                    'activation': 'quadratic',
                    'lr': 1e-3,
                    'weight_decay': 2e-4,
                    'epochs': epochs,
                    'log_interval': 500,  # Less frequent logging
                    'zero_init_output': False,
                    'timestamp': datetime.now().isoformat(),
                }
                
                try:
                    result = train(config)
                    save_results(result, output_dir)
                    
                    results_summary.append({
                        'M': M,
                        'ratio': ratio,
                        'seed': seed,
                        'grok': result['grok_happened'],
                        'grok_epoch': result['grok_epoch'],
                        'final_test_acc': result['final_test_acc'],
                    })
                    
                    status = "[GROK]" if result['grok_happened'] else "[no grok]"
                    print(f"  {status} | test_acc={result['final_test_acc']:.2%}")
                    
                except Exception as e:
                    print(f"  ERROR: {e}")
                    continue
    
    # Save summary
    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Quick Sweep Complete!")
    print("=" * 60)
    
    # Print summary table
    print("\nResults Summary:")
    print("-" * 50)
    
    for M in M_values:
        print(f"\nM = {M} (theory: ratio > {np.log(M)/M:.3f})")
        for ratio in ratios:
            entries = [r for r in results_summary 
                       if r['M'] == M and r['ratio'] == ratio]
            if entries:
                n_grok = sum(1 for e in entries if e['grok'])
                avg_acc = sum(e['final_test_acc'] for e in entries) / len(entries)
                print(f"  ratio={ratio:.2f}: {n_grok}/{len(entries)} grok, avg_test={avg_acc:.2%}")
    
    print(f"\nResults saved to {output_dir}")


if __name__ == "__main__":
    import numpy as np
    run_quick_sweep()
