# Tier-2 case plan: T cell exhaustion (chronic infection / TME)
## Phase-conditional constraint coherence under exogenous timepoints (scRNA-seq)

**Tier**: Tier-2 (auditable, coherence-gated empirical case plan)  
**Domain**: immunology / scRNA-seq  
**Status**: protocol (to run)

Goal: replicate the “external stage beats inferred pseudotime” lesson in an immune setting with known non-stationarity (activation → dysfunction → exhaustion).

## 1) Why this case

T cell exhaustion has an intrinsically staged structure:

- early activation / expansion
- progressive dysfunction (exhaustion programs)
- reduced reversibility and altered responsiveness to perturbation (checkpoint blockade dependence)

This makes it a natural target for **phase-conditional** and **scope-limited** interpretation.

## 2) Dataset selection criteria (no lock-in)

Prefer datasets with:

- **exogenous timepoints** (day post infection / treatment day / longitudinal sampling)
- sufficient cells per timepoint to support windowed estimators
- clear annotation for cell identity (CD8 T, CD4 T, etc.)

## 3) Boundary + windowing

Boundary (minimal):

- include: CD8 T cells (or lineage-filtered T cells)
- exclude: unrelated cell types (unless multi-population modeling is preregistered)

Windowing axis:

- **Primary**: `obs:timepoint` (exogenous)
- **Secondary**: pseudotime (comparison only; not the primary scope gate)

Windows:

- per-timepoint windows, or
- adjacent bins (e.g., day 3–5, 6–8, …) if per-timepoint sample sizes are small

## 4) Estimator families (constraint proxy candidates)

Test at least two constraint-pair candidates:

**Pair A (global + geometric):** `C_dim_collapse` × `C_label_purity`

- `C_dim_collapse`: effective dimension collapse per window
- `C_label_purity`: purity of functional state labels per window (naive/effector/exhausted)

Hypothesis: should be coherent under exogenous timepoints if commitment stabilizes.

**Pair B (local + geometric):** `C_dim_collapse` × `C_mixing`

Hypothesis: may fail (`ESTIMATOR_UNSTABLE`) if local neighborhoods are sensitive to batch/activation noise, or may become coherent only in mid/late phase.

## 5) Coherence gate (EST)

- metric: Spearman rho
- expected sign: `+1` (preregistered)
- threshold: `rho_min = 0.2` (starter; tighten only after stable replication)
- output label:
  - `OK_PER_WINDOW` if coherence passes across windows
  - `SCOPE_LIMITED` if windowed PASS but pooled FAIL
  - `ESTIMATOR_UNSTABLE` if windowed coherence fails

## 6) What counts as a Tier-2 “win”

Tier-2 success is not “high performance”; it is an auditable claim:

1) under exogenous timepoints, at least one constraint proxy pair is coherent (PASS);  
2) pseudotime-only coherence is weaker or unstable (optional comparison);  
3) failures are labeled as scope-limited vs estimator-unstable (not explained away).

## 7) Artifacts to export (minimum)

- evidence pack ZIP (data hashes, configs, locked prereg)
- `coherence_report.json` (per-window)
- `tradeoff_onepage.png`
- `scope_labels.md` (SCOPE_LIMITED / INCONCLUSIVE / ESTIMATOR_UNSTABLE rationale)

