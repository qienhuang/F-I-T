# Runbook: AFDB B1 expanded (CPU)

This runbook stages a deterministic accession set and runs the B1 pipeline (coords + PAE) at a larger scale.

Scope notes:

- This case is designed for **auditability**, not biological claims.
- The local caches under `data/runs/...` and run outputs under `out/...` are **local-only** and should not be pushed.

## 0) Environment

- Python 3.11+ recommended
- Install deps:

```bash
pip install -r requirements.txt
```

## 1) Stage a deterministic accession set + download AFDB artifacts

Two preregistered sizes are supported:

- **Quick**: N=100 (`EST_PREREG.B1_taxon9606_N100.yaml`)
- **Expanded**: N=1000 (`EST_PREREG.B1_taxon9606_N1000.yaml`)

They differ only in target N, seed string, and the staging path under `data/runs/`.

Example A (quick; reviewed UniProt subset; taxon=9606; N=100):

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python scripts/stage_b1_uniprot_reviewed.py \
  --run_name B1_taxon9606_N100 \
  --query "(reviewed:true) AND (taxonomy_id:9606)" \
  --seed_string FIT_AFDB_B1_taxon9606_N100_v1 \
  --n 100 \
  --sleep_s 0.2
```

Example B (expanded; reviewed UniProt subset; taxon=9606; N=1000):

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python scripts/stage_b1_uniprot_reviewed.py \
  --run_name B1_taxon9606_N1000 \
  --query "(reviewed:true) AND (taxonomy_id:9606)" \
  --seed_string FIT_AFDB_B1_taxon9606_N1000_v1 \
  --n 1000 \
  --sleep_s 0.2
```

This creates (for the chosen run name):

- `data/runs/<run_name>/accessions_input.txt`
- `data/runs/<run_name>/coords/` (AF-<acc>-*.cif)
- `data/runs/<run_name>/pae/` (`<acc>.json`)

## 2) Run the case (B1)

Quick:

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python run_case.py --prereg EST_PREREG.B1_taxon9606_N100.yaml --run_id B1_taxon9606_N100
```

Expanded:

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python run_case.py --prereg EST_PREREG.B1_taxon9606_N1000.yaml --run_id B1_taxon9606_N1000
```

Outputs:

- `out/B1_taxon9606_N1000/regime_report.md`
- `out/B1_taxon9606_N1000/tradeoff_onepage.pdf`
- `out/B1_taxon9606_N1000/boundary_snapshot.json`
- `out/B1_taxon9606_N1000/metrics_per_bin.parquet`

## 2b) Optional: run the same accession set under B2 (adds MSA)

This is the minimal "boundary switch" test:

- B1: coords + PAE
- B2: coords + PAE + MSA

First, ensure the MSA channel is available for the staged accession set:

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python scripts/download_pae_msa_for_accessions.py \
  --accessions out/B1_taxon9606_N1000/accessions_selected.txt \
  --out_pae_dir data/runs/B1_taxon9606_N1000/pae \
  --out_msa_dir data/runs/B1_taxon9606_N1000/msa
```

Then run B2:

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python run_case.py --prereg EST_PREREG.B2_taxon9606_N1000.yaml --run_id B2_taxon9606_N1000
```

## 3) Package a repo-safe evidence zip (optional)

```bash
cd github/F-I-T/experiments/real_world/afdb_swissprot_tier2p11_confidence_regimes

python scripts/package_run_dir.py \
  --run_dir out/B1_taxon9606_N1000 \
  --out_zip evidence_B1_taxon9606_N1000.zip
```

By default this excludes `metrics_per_protein.parquet`. Add `--include_per_protein` if needed.
