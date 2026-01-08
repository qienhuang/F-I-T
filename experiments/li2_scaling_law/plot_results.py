"""
Visualize Scaling Law verification results
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Create output directory
Path("results/analysis").mkdir(parents=True, exist_ok=True)

# Experimental data
data = [
    {"M": 23, "ratio_lower": 0.56, "ratio_upper": 0.57},
    {"M": 41, "ratio_lower": 0.48, "ratio_upper": 0.50},
    {"M": 59, "ratio_lower": 0.44, "ratio_upper": 0.45},
]

Ms = np.array([d["M"] for d in data])
ratio_crits = np.array([(d["ratio_lower"] + d["ratio_upper"])/2 for d in data])
n_crits = ratio_crits * Ms * Ms
M_logMs = Ms * np.log(Ms)

# Fitted constant
c_fit = 6.02

# Figure 1: n_critical vs M*log(M)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left plot: Scaling Law
ax1 = axes[0]
ax1.scatter(M_logMs, n_crits, s=100, c='red', zorder=5, label='Experimental')
M_range = np.linspace(0, 300, 100)
ax1.plot(M_range, c_fit * M_range, 'b--', label=f'Fit: n = {c_fit:.1f} · M·log(M)', linewidth=2)
ax1.set_xlabel('M · log(M)', fontsize=12)
ax1.set_ylabel('Critical n (training samples)', fontsize=12)
ax1.set_title('Scaling Law: n_critical ~ M·log(M)', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 280)
ax1.set_ylim(0, 1800)

# Add labels
for i, M in enumerate(Ms):
    ax1.annotate(f'M={M}', (M_logMs[i]+5, n_crits[i]+30), fontsize=10)

# Right plot: Critical ratio vs M
ax2 = axes[1]
ax2.scatter(Ms, ratio_crits, s=100, c='red', zorder=5, label='Experimental')
M_range2 = np.linspace(20, 130, 100)
# Theoretical: ratio ~ log(M)/M (normalized)
c_ratio = 4.82
ax2.plot(M_range2, c_ratio * np.log(M_range2) / M_range2, 'g--', 
         label=f'Theory: ratio ~ log(M)/M', linewidth=2)
ax2.set_xlabel('M (modulus)', fontsize=12)
ax2.set_ylabel('Critical ratio', fontsize=12)
ax2.set_title('Critical Ratio Decreases with M', fontsize=14)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Add labels
for i, M in enumerate(Ms):
    ax2.annotate(f'M={M}', (Ms[i]+1, ratio_crits[i]+0.01), fontsize=10)

plt.tight_layout()
plt.savefig('results/analysis/scaling_law.png', dpi=150, bbox_inches='tight')
print("Saved: results/analysis/scaling_law.png")

# Figure 2: Grokking time vs ratio (for M=23)
fig2, ax3 = plt.subplots(figsize=(8, 5))

grok_data_M23 = [
    (0.57, 14700),
    (0.58, 15600),
    (0.60, 10900),
    (0.62, 7300),
    (0.65, 1000),
    (0.70, 300),
]

ratios = [d[0] for d in grok_data_M23]
epochs = [d[1] for d in grok_data_M23]

ax3.semilogy(ratios, epochs, 'bo-', markersize=10, linewidth=2)
ax3.set_xlabel('Training Data Ratio', fontsize=12)
ax3.set_ylabel('Grokking Epoch (log scale)', fontsize=12)
ax3.set_title('Grokking Time vs Data Ratio (M=23)', fontsize=14)
ax3.grid(True, alpha=0.3)

# Add annotations
for r, e in grok_data_M23:
    ax3.annotate(f'{e}', (r+0.005, e*1.1), fontsize=9)

plt.tight_layout()
plt.savefig('results/analysis/grok_time.png', dpi=150, bbox_inches='tight')
print("Saved: results/analysis/grok_time.png")

# Figure 3: Phase diagram
fig3, ax4 = plt.subplots(figsize=(10, 6))

# All experimental points
all_points = [
    # M=23
    (23, 0.30, False), (23, 0.50, False), (23, 0.55, False), (23, 0.56, False),
    (23, 0.57, True), (23, 0.58, True), (23, 0.60, True), (23, 0.62, True),
    (23, 0.65, True), (23, 0.70, True),
    # M=41
    (41, 0.40, False), (41, 0.45, False), (41, 0.48, False),
    (41, 0.50, True), (41, 0.60, True),
    # M=59
    (59, 0.40, False), (59, 0.42, False), (59, 0.44, False),
    (59, 0.45, True),
]

grok_points = [(p[0], p[1]) for p in all_points if p[2]]
no_grok_points = [(p[0], p[1]) for p in all_points if not p[2]]

ax4.scatter([p[0] for p in grok_points], [p[1] for p in grok_points], 
            s=80, c='green', marker='o', label='Grok', alpha=0.7)
ax4.scatter([p[0] for p in no_grok_points], [p[1] for p in no_grok_points], 
            s=80, c='red', marker='x', label='No Grok', alpha=0.7)

# Phase boundary
M_boundary = np.linspace(20, 65, 100)
ratio_boundary = c_ratio * np.log(M_boundary) / M_boundary
ax4.plot(M_boundary, ratio_boundary, 'k--', linewidth=2, label='Phase boundary (fitted)')

ax4.set_xlabel('M (modulus)', fontsize=12)
ax4.set_ylabel('Training Data Ratio', fontsize=12)
ax4.set_title('Grokking Phase Diagram', fontsize=14)
ax4.legend(loc='upper right')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0.25, 0.75)

plt.tight_layout()
plt.savefig('results/analysis/phase_diagram.png', dpi=150, bbox_inches='tight')
print("Saved: results/analysis/phase_diagram.png")

print("\nAll plots saved!")
