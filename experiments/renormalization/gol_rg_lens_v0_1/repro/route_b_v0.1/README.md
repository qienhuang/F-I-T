# Route B Audit Bundle (v0.1)

This folder is a publish-ready audit bundle for the RG -> FIT Route B hard gate.

## What it contains

- `run_repro.ps1` / `run_repro.sh`: one-command rerun for the full 4x3 matrix.
- `summarize_route_b.py`: hard-gate summarizer.
- `artifacts/`: locked outputs copied from `out/` after a run.

## How to run

From this folder:

```powershell
python -m pip install -r ../../requirements.txt
powershell -ExecutionPolicy Bypass -File .\run_repro.ps1
```

or

```bash
python -m pip install -r ../../requirements.txt
bash ./run_repro.sh
```

## Locked outputs for this run

- `artifacts/scheme_matrix_v0_1.md`
- `artifacts/scheme_matrix_v0_1.csv`
- `artifacts/route_b_hard_gate_summary.md`
- `artifacts/route_b_hard_gate_summary.json`
- `artifacts/PREREG.locked.yaml`

## Hard-gate interpretation

- `CHALLENGED` present -> `NONCLOSURE_OR_CHALLENGED`
- no `CHALLENGED` and >=1 `SUPPORTED` -> `SUPPORTED` (or `SUPPORTED_WITH_SCOPE_LIMITS` if saturation-limited cells exist)
- otherwise -> `INCONCLUSIVE`

