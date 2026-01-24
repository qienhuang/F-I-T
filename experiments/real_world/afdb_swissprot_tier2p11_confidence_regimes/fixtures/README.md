# Fixtures (tiny synthetic)

This folder contains a tiny, synthetic dataset intended only for a **pipeline smoke test**:

- `fixtures/coords/`: three PDB files with pLDDT encoded in B-factor
- `fixtures/pae/`: three PAE JSON files, one per accession (compact constant-matrix fixture encoding)

It is **not** biological data and supports no biology claims.

Use:

- `EST_PREREG.fixture_B0.yaml` (coords only)
- `EST_PREREG.fixture_B1.yaml` (coords + PAE)
