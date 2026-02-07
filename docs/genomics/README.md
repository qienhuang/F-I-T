# Genomics (Tier-2 cases + Tier-3 testbeds)

This folder contains:

- **Tier-2**: a repo-runnable, EST-gated real-world case (fate commitment in scRNA-seq).
- **Tier-3**: mapping notes and preregistration templates for genomic foundation models (structure-externalized testbeds).

Design goals:

- Keep claims **scope-conditional** and **artifact-backed**.
- Prefer systems that **externalize structure** (so constraints can be perturbed and audited).

## Tier-2 case: fate commitment (scRNA-seq)

- Short case note (mouse gastrulation, explicit stage axis): `tier2_mouse_gastrulation_case.md`
- Tier-2 case doc (mouse gastrulation): `cases/tier2_case_mouse_gastrulation.md`
- Case plans (protocols to run):
  - T cell exhaustion: `cases/tier2_caseplan_tcell_exhaustion.md`
  - Tumor therapy response: `cases/tier2_caseplan_tumor_therapy_response.md`
  - Prereg skeleton: `cases/tier2_prereg_biology_skeleton.yaml`
- Runnable case + results + evidence bundles:
  - `experiments/real_world/scrna_commitment_tier2p11/README.md`
  - `experiments/real_world/scrna_commitment_tier2p11/RESULTS.md`
  - Evidence ZIPs (gastrulation, within-boundary proxy comparison):
    - `experiments/real_world/scrna_commitment_tier2p11/evidence_gastrulation_e75_purity.zip`
    - `experiments/real_world/scrna_commitment_tier2p11/evidence_gastrulation_e75_mixing.zip`
    - `experiments/real_world/scrna_commitment_tier2p11/evidence_gastrulation_e75_purity_mixing.zip`

## Gengram (explicit motif memory + gating)

- `gengram_fit_mapping.md` — mapping Gengram primitives to FIT/EST concepts (research note).
- `explicit_motif_memory_fit_note.md` — short note motivating “structure externalization” as an audit shortcut.
- `gengram_tier3_prereg.yaml` — Tier-3 prereg template (protocol-level; no data included).

Primary reference:

- Huinan Xu et al. (2026-01-29). *Beyond Conditional Computation: Retrieval-Augmented Genomic Foundation Models with Gengram.* Preprint; code: `https://github.com/zhejianglab/Gengram`.
