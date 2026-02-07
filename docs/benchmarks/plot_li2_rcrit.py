import matplotlib.pyplot as plt
import numpy as np

# Data from four Ms
Ms = np.array([71, 97, 127, 159])
r_crits = np.array([0.415, 0.385, 0.350, 0.335])
lower_bounds = np.array([0.40, 0.36, 0.34, 0.32])
upper_bounds = np.array([0.44, 0.40, 0.36, 0.34])

# Compute error bars (symmetric for visualization)
errors_lower = r_crits - lower_bounds
errors_upper = upper_bounds - r_crits

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot with error bars
ax.errorbar(Ms, r_crits, yerr=[errors_lower, errors_upper], 
            fmt='o-', markersize=10, capsize=8, capthick=2, linewidth=2,
            color='#2E86AB', ecolor='#A23B72', label='r_crit with bounds')

# Styling
ax.set_xlabel('Modulus M', fontsize=14, fontweight='bold')
ax.set_ylabel('Critical Ratio (r_crit)', fontsize=14, fontweight='bold')
ax.set_title('Li² Grokking Phase Transition: r_crit vs Modulus M', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12)

# Annotate each point
for i, (m, r) in enumerate(zip(Ms, r_crits)):
    ax.annotate(f'M={m}\nr={r:.3f}', 
                xy=(m, r), xytext=(10, -15 if i % 2 == 0 else 15),
                textcoords='offset points', fontsize=10,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# Add trend annotation
ax.text(0.05, 0.95, 'Trend: r_crit decreases\nmonotonically with M', 
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('li2_rcrit_vs_M_benchmark.png', dpi=300, bbox_inches='tight')
plt.savefig('li2_rcrit_vs_M_benchmark.pdf', bbox_inches='tight')
print('Saved: li2_rcrit_vs_M_benchmark.png and .pdf')
plt.show()
