#!/usr/bin/env python3
"""
FIT Markov Sandbox - Numerical Validation with Visualization

Generates plots demonstrating:
1. Entropy rate h(alpha) -> 0 as alpha -> 1
2. Constraint C(alpha) -> H(pi) as alpha -> 1
3. Relaxation time proxy (SLEM -> 1) as alpha -> 1

Output: fit_markov_validation.png for README/landing page
"""

import numpy as np
import matplotlib.pyplot as plt

from experiments import entropy, run_sweep, stationary_dist

def plot_single_run(ax1, ax2, ax3, data, P, seed, color, alpha=0.7):
    """Plot a single run on the three axes."""
    alphas = data[:, 0]
    h_vals = data[:, 1]
    C_vals = data[:, 2]
    slem_vals = data[:, 3]

    ax1.plot(alphas, h_vals, color=color, alpha=alpha, linewidth=1.5)
    ax2.plot(alphas, C_vals, color=color, alpha=alpha, linewidth=1.5)
    ax3.plot(alphas, slem_vals, color=color, alpha=alpha, linewidth=1.5)

    return h_vals, C_vals, slem_vals

def main():
    # Run multiple seeds for robustness
    n_states = 20
    n_seeds = 10
    alphas = np.linspace(0.0, 0.99, 100)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    ax1, ax2, ax3 = axes

    colors = plt.cm.viridis(np.linspace(0.2, 0.8, n_seeds))

    all_h = []
    all_C = []
    all_slem = []
    H_pi_values = []

    for i, seed in enumerate(range(n_seeds)):
        data, P = run_sweep(n=n_states, seed=seed, alphas=alphas)
        h_vals, C_vals, slem_vals = plot_single_run(
            ax1, ax2, ax3, data, P, seed, colors[i], alpha=0.5
        )
        all_h.append(h_vals)
        all_C.append(C_vals)
        all_slem.append(slem_vals)

        # Compute H(pi) for this chain (stationary dist of the base chain).
        pi = stationary_dist(P)
        H_pi_values.append(entropy(pi))

    # Plot means
    mean_h = np.mean(all_h, axis=0)
    mean_C = np.mean(all_C, axis=0)
    mean_slem = np.mean(all_slem, axis=0)
    mean_H_pi = np.mean(H_pi_values)

    ax1.plot(alphas, mean_h, 'k-', linewidth=2.5, label='Mean')
    ax2.plot(alphas, mean_C, 'k-', linewidth=2.5, label='Mean')
    ax3.plot(alphas, mean_slem, 'k-', linewidth=2.5, label='Mean')

    # Add reference lines
    ax1.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='h -> 0')
    ax2.axhline(y=mean_H_pi, color='red', linestyle='--', alpha=0.7, label=f'H(pi) = {mean_H_pi:.2f}')
    ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='SLEM -> 1')

    # Styling
    ax1.set_xlabel(r'Hardening parameter $\alpha$', fontsize=11)
    ax1.set_ylabel(r'Entropy rate $h(\alpha)$', fontsize=11)
    ax1.set_title('Information Production\n(tends to 0)', fontsize=12)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(bottom=0)

    ax2.set_xlabel(r'Hardening parameter $\alpha$', fontsize=11)
    ax2.set_ylabel(r'Mutual information $C(\alpha)$', fontsize=11)
    ax2.set_title(r'Constraint Accumulation\n(tends to $H(\pi)$)', fontsize=12)
    ax2.legend(loc='lower right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 1)

    ax3.set_xlabel(r'Hardening parameter $\alpha$', fontsize=11)
    ax3.set_ylabel('SLEM (relaxation proxy)', fontsize=11)
    ax3.set_title('Time Scale\n(SLEM -> 1, mixing slows)', fontsize=12)
    ax3.legend(loc='lower right', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1.05)

    # Overall title
    fig.suptitle('FIT Markov Sandbox: Constraint Accumulation via Lazy Hardening\n'
                 f'({n_seeds} random ergodic chains, n={n_states} states)',
                 fontsize=13, y=1.02)

    plt.tight_layout()

    # Save
    output_path = 'fit_markov_validation.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_path}")

    # Also save a smaller version for web
    plt.savefig('fit_markov_validation_small.png', dpi=100, bbox_inches='tight', facecolor='white')
    print("Saved: fit_markov_validation_small.png")

    plt.close()

    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"At alpha=0.00: h={mean_h[0]:.3f}, C={mean_C[0]:.3f}, SLEM={mean_slem[0]:.3f}")
    print(f"At alpha=0.99: h={mean_h[-1]:.3f}, C={mean_C[-1]:.3f}, SLEM={mean_slem[-1]:.3f}")
    print(f"Mean H(pi): {mean_H_pi:.3f}")
    print(f"h reduction: {(1 - mean_h[-1]/mean_h[0])*100:.1f}%")
    print(f"C increase: {(mean_C[-1]/mean_C[0]):.1f}x")

if __name__ == "__main__":
    main()
