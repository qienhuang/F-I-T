# Tier-2 case: Mouse gastrulation (E6.5–E8.5) — EST-gated constraint coherence

This note records a **repo-runnable Tier-2 case** showing a passing coherence gate under an **explicit developmental-stage axis**.

## What is tested

**Boundary**

- Dataset: `experiments/real_world/scrna_commitment_tier2p11/data/raw/gastrulation_e75.h5ad`
- Windowing axis: `obs:stage` (explicit stage label; not inferred pseudotime)
- Mixing label: `obs:celltype`

**Constraint family (C-hat)**

- Estimator pair: `C_dim_collapse` vs `C_label_purity`
- Expected sign: `+1`
- Coherence threshold: `rho >= 0.2` (Spearman, across preregistered windows)

## Result (audit-facing)

Verdict: `OK_PER_WINDOW`

- `rho = 0.581` (across windows), `p = 0.0145`
- Interpretation is permitted **within the declared boundary** and **under the explicit-stage windowing**.

This case is intentionally narrow: it is evidence that the coherence gate can pass on a real developmental system when an external axis is available, not a general biological claim about fate commitment.

## Reproduce

Run:

```bash
cd experiments/real_world/scrna_commitment_tier2p11
python run_pipeline.py --prereg EST_PREREG_gastrulation_e75_purity.yaml
```

Evidence bundle:

```bash
cd experiments/real_world/scrna_commitment_tier2p11
python package_evidence.py --main_dir outputs_runs/gastrulation_e75_purity --out outputs_runs/evidence_gastrulation_e75_purity.zip
```

## Artifacts

- Prereg: `experiments/real_world/scrna_commitment_tier2p11/EST_PREREG_gastrulation_e75_purity.yaml`
- Run outputs: `experiments/real_world/scrna_commitment_tier2p11/outputs_runs/gastrulation_e75_purity/`
- Evidence ZIP: `experiments/real_world/scrna_commitment_tier2p11/outputs_runs/evidence_gastrulation_e75_purity.zip`
- Portfolio summary: `experiments/real_world/scrna_commitment_tier2p11/RESULTS.md`

