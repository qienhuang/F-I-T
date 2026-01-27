# Monitorability gate (FIT-Explorer v0.1)

**Purpose**: Define the hard feasibility gate for alarm usage.

A detector is **admissible for governance** only if it passes **FPR controllability** at preregistered operating points.

---

## 1) Gate definition

Given target FPR set $\mathcal{F}$ and tolerance $\epsilon$:

1. Calibrate a threshold $\tau_f$ on negative windows for each $f \in \mathcal{F}$.
2. Compute achieved FPR $\hat{f}$ at $\tau_f$.

The detector is valid if:

- at least $m$ targets satisfy

$$
|\hat{f} - f| \le \epsilon
$$

- and no hard floor exists:

$$
\min_f \hat{f} \le f_{\mathrm{floor\_max}}
$$

If the gate fails, label the candidate `RANK_ONLY` and forbid alarm usage.

---

## 2) Required diagnostics (always report)

- achieved-vs-target table
- floor estimate
- negative support size (binned entropy or unique counts)
- tie/cluster dominance near top quantiles

