# Tier-2 case plan: Tumor therapy response (pre/on/post)
## Constraint coherence under exogenous intervention stages (scRNA-seq)

**Tier**: Tier-2 (auditable, coherence-gated empirical case plan)  
**Domain**: oncology / scRNA-seq  
**Status**: protocol (to run)

Goal: test whether intervention stages (pre/on/post/relapse) yield coherent constraint signatures and scope-limited validity.

## 1) Why this case

Therapy is a natural **external shock**:

- pre-treatment baseline regime
- acute response / stress regime
- post-treatment adaptation (resistance / remodeling)

This supplies exogenous phase boundaries and directly tests phase-conditional interpretation.

## 2) Dataset selection criteria (no lock-in)

Prefer datasets with:

- clear stage labels: pre / on-treatment / post / relapse
- enough cells per stage to compute windowed estimators
- annotations for tumor vs immune compartments (optional multi-population extension)

## 3) Boundary + windowing

Boundary (minimal):

- option A (clean): tumor cells only  
- option B (richer): tumor + immune, but then multi-population estimators must be preregistered

Windowing axis:

- **Primary**: `obs:stage` (pre/on/post/relapse)
- Windows: stage-based (as in the gastrulation Tier-2 anchor)

## 4) Estimator families (constraint proxy candidates)

**Pair A:** `C_dim_collapse` × `C_label_purity` (tumor-state purity)

Expected pattern:

- acute response windows may show coherence instability (diagnostic)
- later resistance regime may show renewed coherence (new stable program)

**Pair B:** `C_dim_collapse` × `C_mixing`

May capture mixing during remodeling; may fail if label structure is unstable.

## 5) PT-MSS (optional Tier-2+)

If sufficient signals exist, preregister a minimal PT-MSS check:

- S1: shock-induced redistribution (stage boundary)
- S2: information re-encoding (predictive gain for relapse / resistance)
- S3: constraint reorganization (non-smooth change in C proxies)

Primary Tier-2 objective remains: coherence gating + scope labeling.

## 6) What counts as a Tier-2 “win”

1) at least one C-proxy pair is coherent under stage windowing;  
2) pooled analysis across all stages is weaker (`SCOPE_LIMITED`) or unstable (diagnostic);  
3) interpretation is explicitly stage-scoped (e.g., “valid pre/post but not through acute shock”).

## 7) Artifacts to export (minimum)

- evidence pack ZIP
- `coherence_report.json`
- `tradeoff_onepage.png`
- `scope_labels.md`

