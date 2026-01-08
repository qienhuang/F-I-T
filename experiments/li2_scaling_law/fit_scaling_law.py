"""
Fit the Scaling Law: n_critical = c * M * log(M)
Using experimental data from grokking experiments
"""

import numpy as np

# Experimental results: (M, critical_ratio_lower, critical_ratio_upper)
# Lower: highest ratio that doesn't grok
# Upper: lowest ratio that groks
data = [
    # M=23: ratio 0.56 doesn't grok, 0.57 groks
    {"M": 23, "ratio_lower": 0.56, "ratio_upper": 0.57},
    # M=41: ratio 0.48 doesn't grok, 0.50 groks
    {"M": 41, "ratio_lower": 0.48, "ratio_upper": 0.50},
    # M=59: ratio 0.44 doesn't grok, 0.45 groks
    {"M": 59, "ratio_lower": 0.44, "ratio_upper": 0.45},
]

print("=" * 60)
print("Li² Scaling Law Verification")
print("n_critical = c * M * log(M)")
print("=" * 60)
print()

# Calculate critical n and theoretical M*log(M)
print("Data Summary:")
print("-" * 60)
print(f"{'M':>5} | {'ratio_crit':>12} | {'n_critical':>12} | {'M*log(M)':>12} | {'c':>8}")
print("-" * 60)

Ms = []
n_criticals = []
M_logMs = []

for d in data:
    M = d["M"]
    # Use midpoint of the range as critical ratio
    ratio_crit = (d["ratio_lower"] + d["ratio_upper"]) / 2
    n_crit = ratio_crit * M * M  # n = ratio * M^2
    M_logM = M * np.log(M)
    c = n_crit / M_logM
    
    print(f"{M:>5} | {ratio_crit:>12.3f} | {n_crit:>12.1f} | {M_logM:>12.1f} | {c:>8.2f}")
    
    Ms.append(M)
    n_criticals.append(n_crit)
    M_logMs.append(M_logM)

print("-" * 60)
print()

# Fit n_critical = c * M * log(M)
Ms = np.array(Ms)
n_criticals = np.array(n_criticals)
M_logMs = np.array(M_logMs)

# Simple linear regression: n = c * M*log(M) + intercept
# But the theory predicts intercept = 0
c_fit = np.sum(n_criticals * M_logMs) / np.sum(M_logMs**2)

# R-squared
n_predicted = c_fit * M_logMs
ss_res = np.sum((n_criticals - n_predicted)**2)
ss_tot = np.sum((n_criticals - np.mean(n_criticals))**2)
r_squared = 1 - ss_res / ss_tot

print("Scaling Law Fit:")
print("-" * 60)
print(f"  n_critical = {c_fit:.2f} * M * log(M)")
print(f"  R^2 = {r_squared:.4f}")
print()

# Alternative: fit ratio_critical = c * log(M) / M
ratio_crits = np.array([(d["ratio_lower"] + d["ratio_upper"])/2 for d in data])
log_M_over_M = np.log(Ms) / Ms

c_ratio = np.sum(ratio_crits * log_M_over_M) / np.sum(log_M_over_M**2)
ratio_predicted = c_ratio * log_M_over_M
ss_res_r = np.sum((ratio_crits - ratio_predicted)**2)
ss_tot_r = np.sum((ratio_crits - np.mean(ratio_crits))**2)
r_squared_ratio = 1 - ss_res_r / ss_tot_r

print("Alternative formulation (ratio space):")
print("-" * 60)
print(f"  ratio_critical = {c_ratio:.2f} * log(M) / M")
print(f"  R^2 = {r_squared_ratio:.4f}")
print()

# Predictions for other M values
print("Predictions for untested M values:")
print("-" * 60)
print(f"{'M':>5} | {'Predicted ratio':>15} | {'Predicted n':>15}")
print("-" * 60)
for M_test in [71, 97, 127]:
    ratio_pred = c_ratio * np.log(M_test) / M_test
    n_pred = c_fit * M_test * np.log(M_test)
    print(f"{M_test:>5} | {ratio_pred:>15.3f} | {n_pred:>15.0f}")
print("-" * 60)
print()

# Conclusion
print("=" * 60)
print("Conclusion:")
print("=" * 60)
if r_squared > 0.95:
    print("OK: Strong evidence for scaling law: n ~ M * log(M)")
elif r_squared > 0.8:
    print("NOTE: Moderate evidence (more data needed)")
else:
    print("NOTE: Weak evidence (need more experiments)")
print()
print(f"Fitted constant: c ≈ {c_fit:.1f}")
print(f"This means grokking requires about {c_fit:.0f}x more samples")
print(f"than the bare M*log(M) scaling would suggest.")
