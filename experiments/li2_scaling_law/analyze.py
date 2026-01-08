"""
Analysis script for scaling law verification
Fits phase boundary and compares with Li² theory
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import argparse


def load_results(results_dir):
    """Load all experiment results from directory"""
    results_dir = Path(results_dir)
    results = []
    
    for filepath in results_dir.rglob('*.json'):
        if filepath.name == 'sweep_meta.json':
            continue
        with open(filepath) as f:
            results.append(json.load(f))
    
    print(f"Loaded {len(results)} experiments")
    return results


def aggregate_by_config(results):
    """
    Aggregate results by (M, ratio)
    Returns dict: (M, ratio) -> list of results
    """
    aggregated = defaultdict(list)
    
    for r in results:
        config = r['config']
        # Robust bucketing: ratios are swept at ~1e-3 resolution and stored as floats.
        key = (int(config['M']), round(float(config['train_ratio']), 3))
        aggregated[key].append(r)
    
    return aggregated


def compute_grok_probability(results_list):
    """Compute grokking probability from list of results"""
    n_grok = sum(1 for r in results_list if r['grok_happened'])
    return n_grok / len(results_list) if results_list else 0


def compute_mean_grok_epoch(results_list):
    """Compute mean grokking epoch (for cases that grokked)"""
    grok_epochs = [r['grok_epoch'] for r in results_list if r['grok_happened']]
    return np.mean(grok_epochs) if grok_epochs else np.nan


def build_phase_matrix(aggregated):
    """
    Build phase diagram matrix
    
    Returns:
        M_values: sorted list of M values
        ratios: sorted list of ratios
        grok_probs: 2D array of grokking probabilities
        grok_epochs: 2D array of mean grokking epochs
    """
    M_values = sorted(set(key[0] for key in aggregated.keys()))
    ratios = sorted(set(key[1] for key in aggregated.keys()))
    
    grok_probs = np.zeros((len(M_values), len(ratios)))
    grok_epochs = np.full((len(M_values), len(ratios)), np.nan)
    
    for i, M in enumerate(M_values):
        for j, ratio in enumerate(ratios):
            key = (M, ratio)
            if key in aggregated:
                grok_probs[i, j] = compute_grok_probability(aggregated[key])
                grok_epochs[i, j] = compute_mean_grok_epoch(aggregated[key])
    
    return M_values, ratios, grok_probs, grok_epochs


def find_critical_ratio(M_values, ratios, grok_probs, threshold=0.5):
    """
    Find critical ratio (50% grokking probability) for each M
    
    Returns:
        critical_ratios: dict M -> critical ratio
    """
    critical_ratios = {}
    
    for i, M in enumerate(M_values):
        probs = grok_probs[i, :]
        
        # Find where probability crosses threshold
        above = probs >= threshold
        if not any(above):
            critical_ratios[M] = np.nan
            continue
        if all(above):
            critical_ratios[M] = ratios[0]
            continue
            
        # Linear interpolation
        for j in range(len(ratios) - 1):
            if probs[j] < threshold <= probs[j+1]:
                # Interpolate
                r1, r2 = ratios[j], ratios[j+1]
                p1, p2 = probs[j], probs[j+1]
                critical = r1 + (threshold - p1) * (r2 - r1) / (p2 - p1)
                critical_ratios[M] = critical
                break
    
    return critical_ratios


def _fit_through_origin(x, y):
    """
    Fit y ≈ c * x (no intercept) via OLS.

    Returns dict with c, c_std, r_squared, predicted.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape or x.size < 2:
        return None

    denom = float(np.sum(x * x))
    if denom <= 0:
        return None

    c_fit = float(np.sum(x * y) / denom)
    predicted = c_fit * x

    residuals = y - predicted
    sse = float(np.sum(residuals * residuals))
    sigma2 = sse / max(1, (int(x.size) - 1))
    c_var = sigma2 / denom
    c_std = float(np.sqrt(max(0.0, c_var)))

    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    r_squared = float(1 - (sse / ss_tot)) if ss_tot > 0 else float('nan')

    return {
        'c': c_fit,
        'c_std': c_std,
        'r_squared': r_squared,
        'predicted': predicted.tolist(),
    }


def fit_scaling_law_n(M_values, critical_ratios):
    """
    Fit scaling law (Li² Thm4 form): n = c * M * log(M)
    
    Since n = ratio * M^2, we have:
    ratio = c * log(M) / M
    
    Fit c from data
    """
    # Filter out NaN values
    valid_M = []
    valid_ratios = []
    for M in M_values:
        if M in critical_ratios and not np.isnan(critical_ratios[M]):
            valid_M.append(M)
            valid_ratios.append(critical_ratios[M])
    
    if len(valid_M) < 2:
        return None, None
    
    valid_M = np.array(valid_M, dtype=float)
    valid_ratios = np.array(valid_ratios, dtype=float)

    # Use the interpolated critical ratio to compute critical n (continuous).
    valid_n = valid_ratios * (valid_M ** 2)
    valid_x = valid_M * np.log(valid_M)  # M log M

    fit = _fit_through_origin(valid_x, valid_n)
    if not fit:
        return None

    return {
        'c': fit['c'],
        'c_std': fit['c_std'],
        'r_squared': fit['r_squared'],
        'valid_M': valid_M.astype(int).tolist(),
        'critical_ratio': valid_ratios.tolist(),
        'critical_n': valid_n.tolist(),
        'predicted_n': fit['predicted'],
    }


def fit_scaling_law_ratio(M_values, critical_ratios):
    """
    Fit ratio_crit ≈ c * log(M)/M (same constant c, but a different loss weighting).
    This can behave differently from the n-space fit; keep as a secondary diagnostic.
    """
    valid_M = []
    valid_ratios = []
    for M in M_values:
        if M in critical_ratios and not np.isnan(critical_ratios[M]):
            valid_M.append(M)
            valid_ratios.append(critical_ratios[M])

    if len(valid_M) < 2:
        return None

    valid_M = np.array(valid_M, dtype=float)
    valid_ratios = np.array(valid_ratios, dtype=float)

    x = np.log(valid_M) / valid_M
    fit = _fit_through_origin(x, valid_ratios)
    if not fit:
        return None

    return {
        'c': fit['c'],
        'c_std': fit['c_std'],
        'r_squared': fit['r_squared'],
        'valid_M': valid_M.astype(int).tolist(),
        'critical_ratio': valid_ratios.tolist(),
        'predicted_ratio': fit['predicted'],
    }


def plot_phase_diagram(M_values, ratios, grok_probs, output_path=None, show=False):
    """Plot phase diagram heatmap"""
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    im = plt.imshow(grok_probs, aspect='auto', cmap='RdYlGn',
                    origin='lower', vmin=0, vmax=1)
    
    # Labels
    plt.xticks(range(len(ratios)), [f'{r:.2f}' for r in ratios], rotation=45)
    plt.yticks(range(len(M_values)), M_values)
    plt.xlabel('Training Ratio')
    plt.ylabel('Group Size M')
    plt.title('Grokking Phase Diagram\n(Green = Grok, Red = No Grok)')
    
    plt.colorbar(im, label='Grokking Probability')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Phase diagram saved to {output_path}")

    if show:
        plt.show()
    plt.close()


def plot_scaling_law_n(M_values, critical_ratios, fit_result, output_path=None, show=False):
    """Plot scaling law fit in n-space: n_crit vs M log M"""
    plt.figure(figsize=(10, 6))
    
    # Data points
    x_plot = []
    n_plot = []
    for M in M_values:
        if M in critical_ratios and not np.isnan(critical_ratios[M]):
            ratio_crit = float(critical_ratios[M])
            x_plot.append(float(M) * float(np.log(M)))
            n_plot.append(ratio_crit * float(M) * float(M))
    
    plt.scatter(x_plot, n_plot, s=100, c='blue', label='Observed (interpolated)', zorder=3)
    
    # Theoretical curve
    if fit_result:
        x_theory = np.linspace(min(x_plot) * 0.9, max(x_plot) * 1.1, 100)
        n_theory = fit_result['c'] * x_theory
        plt.plot(
            x_theory,
            n_theory,
            'r-',
            linewidth=2,
            label=f"Fit: n = {fit_result['c']:.2f} * (M log M) (R^2={fit_result['r_squared']:.3f})",
        )
    
    plt.xlabel('M log(M)')
    plt.ylabel('Critical n (train samples)')
    plt.title('Scaling Law Verification (Li2 Thm4 form): n_crit ~ M log(M)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Scaling law plot saved to {output_path}")

    if show:
        plt.show()
    plt.close()


def generate_report(M_values, ratios, grok_probs, critical_ratios, fit_result, output_path):
    """Generate analysis report"""
    report = []
    report.append("# Li² Scaling Law Verification Report")
    report.append(f"\nGenerated: {np.datetime64('now')}")
    report.append("\n## Summary")
    report.append(f"- M values tested: {M_values}")
    report.append(f"- Ratio range: {min(ratios):.2f} to {max(ratios):.2f}")
    
    report.append("\n## Critical Ratios (50% Grokking Probability)")
    report.append("| M | Critical Ratio | Critical n (≈ ratio·M²) | M·log(M) | c_implied (= n / (M log M)) |")
    report.append("|---|----------------|------------------------|----------|-----------------------------|")
    for M in M_values:
        ratio = critical_ratios.get(M, np.nan)
        if np.isnan(ratio):
            report.append(f"| {M} | nan | nan | {float(M*np.log(M)):.1f} | nan |")
            continue
        n_crit = float(ratio) * float(M) * float(M)
        mlogm = float(M * np.log(M))
        c_implied = n_crit / mlogm if mlogm > 0 else float('nan')
        report.append(f"| {M} | {ratio:.4f} | {n_crit:.1f} | {mlogm:.1f} | {c_implied:.2f} |")
    
    if fit_result:
        report.append("\n## Scaling Law Fit")
        report.append(f"- Fitted constant c: {fit_result['c']:.3f} ± {fit_result['c_std']:.3f}")
        report.append(f"- R^2 score (n-space): {fit_result['r_squared']:.4f}")
        report.append("\nFitted model: `n = c * M * log(M)` (Li2 Thm 4 form)")
    
    report.append("\n## Conclusion")
    if fit_result and fit_result['r_squared'] > 0.9:
        report.append("OK: Strong support for Li2 scaling law (R^2 > 0.9 in n-space).")
    elif fit_result and fit_result['r_squared'] > 0.7:
        report.append("NOTE: Moderate support for Li2 scaling law (0.7 < R^2 < 0.9 in n-space).")
    else:
        report.append("NOTE: Weak support for Li2 scaling law (R^2 < 0.7 in n-space).")
    
    report_text = '\n'.join(report)
    
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"Report saved to {output_path}")
    print("\n" + report_text)


def main():
    parser = argparse.ArgumentParser(description='Analyze scaling law experiment results')
    parser.add_argument('--results_dir', type=str, default='results',
                        help='Directory containing experiment results')
    parser.add_argument('--output_dir', type=str, default='results/analysis',
                        help='Directory for analysis outputs')
    parser.add_argument('--show', action='store_true',
                        help='Show plots (default: save only; useful on headful setups)')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and aggregate results
    results = load_results(args.results_dir)
    aggregated = aggregate_by_config(results)
    
    # Build phase matrix
    M_values, ratios, grok_probs, grok_epochs = build_phase_matrix(aggregated)
    
    print(f"\nM values: {M_values}")
    print(f"Ratios: {ratios}")
    print(f"Grok probability matrix shape: {grok_probs.shape}")
    
    # Find critical ratios
    critical_ratios = find_critical_ratio(M_values, ratios, grok_probs)
    print(f"\nCritical ratios (50% grok):")
    for M, ratio in critical_ratios.items():
        print(f"  M={M}: ratio={ratio:.4f}")
    
    # Fit scaling law
    fit_result = fit_scaling_law_n(M_values, critical_ratios)
    fit_ratio = fit_scaling_law_ratio(M_values, critical_ratios)
    if fit_result:
        print(f"\nScaling law fit:")
        print(f"  c = {fit_result['c']:.3f} ± {fit_result['c_std']:.3f}")
        print(f"  R^2 (n-space) = {fit_result['r_squared']:.4f}")
    if fit_ratio:
        print(f"\nSecondary fit (ratio-space; different weighting):")
        print(f"  c = {fit_ratio['c']:.3f} ± {fit_ratio['c_std']:.3f}")
        print(f"  R^2 (ratio-space) = {fit_ratio['r_squared']:.4f}")
    
    # Generate plots
    plot_phase_diagram(M_values, ratios, grok_probs, 
                       output_dir / 'phase_diagram.png',
                       show=args.show)
    plot_scaling_law_n(M_values, critical_ratios, fit_result,
                       output_dir / 'scaling_law_n.png',
                       show=args.show)
    
    # Generate report
    generate_report(M_values, ratios, grok_probs, critical_ratios, fit_result,
                    output_dir / 'report.md')


if __name__ == "__main__":
    main()
