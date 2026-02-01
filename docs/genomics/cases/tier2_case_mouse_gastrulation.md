# Tier-2 case: Mouse gastrulation (E6.5–E8.5)
## Constraint coherence under explicit developmental staging (scRNA-seq)

**Tier**: Tier-2 (auditable, coherence-gated empirical case)  
**Domain**: developmental biology / scRNA-seq  
**Outcome label**: `OK_PER_WINDOW`

This case is a **scope-conditional** positive example: a preregistered constraint-family coherence gate passes when windows are defined by an **exogenous stage label** (`obs:stage`), rather than an inferred pseudotime.

## 1) Motivation

Gastrulation is a canonical developmental process with large-scale fate commitment and major reorganization. It is therefore a strong testbed for the claim that **constraint coherence is phase-conditional and boundary-dependent**.

## 2) Dataset and boundary

- Dataset: mouse gastrulation scRNA-seq (E6.5–E8.5) stored as `gastrulation_e75.h5ad`
- Windowing axis: `obs:stage` (experimental stage labels; not pseudotime)
- Windows: 17 (rolling-quantile windows over `obs:stage`)
- Mixing label: `obs:celltype`

Rationale: stage labels are exogenous and avoid estimator circularity.

## 3) Estimator family (constraint proxies)

Constraint proxy pair (C-hat):

1. `C_dim_collapse` — effective dimensional collapse (reachable-space reduction)
2. `C_label_purity` — label purity per window (stabilization of a dominant program)

Coherence gate:

- metric: Spearman rho
- expected sign: `+1`
- threshold: `rho >= 0.2`

## 4) Result (audit-facing)

Verdict: `OK_PER_WINDOW`

| Metric | Value |
|---|---:|
| rho (across windows) | 0.581 |
| p-value | 0.0145 |
| expected sign | +1 |

Interpretation is permitted **within the declared boundary** and under explicit-stage windowing. This is not a universal biological claim about commitment.

## 5) Portfolio context

For comparison runs and additional evidence bundles, see:

- `experiments/real_world/scrna_commitment_tier2p11/RESULTS.md`

## 6) Artifacts and reproduction

Prereg:

- `experiments/real_world/scrna_commitment_tier2p11/EST_PREREG_gastrulation_e75_purity.yaml`

Evidence bundle (ZIP):

- `experiments/real_world/scrna_commitment_tier2p11/outputs_runs/evidence_gastrulation_e75_purity.zip`

Reproduce:

```bash
cd experiments/real_world/scrna_commitment_tier2p11
python run_pipeline.py --prereg EST_PREREG_gastrulation_e75_purity.yaml
python package_evidence.py --main_dir outputs_runs/gastrulation_e75_purity --out outputs_runs/evidence_gastrulation_e75_purity.zip
```

