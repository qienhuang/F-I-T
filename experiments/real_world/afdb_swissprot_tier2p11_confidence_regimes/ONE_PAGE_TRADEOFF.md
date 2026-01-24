# ONE_PAGE_TRADEOFF — AFDB Swiss‑Prot Confidence Regimes (Tier2P11)

This file defines the mandatory **one-page** figure output for every run.

**Output path:** `out/<run_id>/tradeoff_onepage.pdf`  
**Rule:** exactly one page, 4 panels.

---

## Panel A — Information vs length

- x: length-bin midpoint (aa)
- y: `I1_hi_conf_frac` (and optionally `I2_mean_plddt`)

Interpretation allowed: local confidence coverage changes with length.

---

## Panel B — Constraint proxies vs length (boundary-sensitive)

- Always: `C1_low_conf_frac`
- If boundary provides PAE: normalized `C2_pae_offdiag`
- If boundary provides MSA: normalized `C3_msa_deficit`
- Optionally: `C_primary` (the composite used in `R_primary`)

Interpretation allowed: agreement / disagreement across constraint estimators; boundary switch visibility.

---

## Panel C — Regime score and detected event

- y: `R_primary`
- vertical line at detected `t*` (if any), labeled `E_regime`
- shaded persistence window (if implemented)

Interpretation allowed: regime-shift signature under preregistered rules.

---

## Panel D — Trade-off geometry

Scatter:
- x: `C_primary` (or `C1_low_conf_frac` if boundary is B0)
- y: `I1_hi_conf_frac`
- point size: bin count (`bin_n`)
- color: length-bin midpoint

Interpretation allowed: empirical feasible geometry under this boundary.

---

## Footer (mandatory)

A footer text block containing:
- case id, run id
- boundary mode
- AFDB release label
- sample size N
- bin width + smoothing bins
