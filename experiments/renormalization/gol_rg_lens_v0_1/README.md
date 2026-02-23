# GoL RG Lens Repro Pack (v0.1)

Minimal reproducibility bundle for the `renormalization_lens` gate-aware claims.

This pack reproduces:

- multi-scheme x multi-estimator semigroup tests
- saturation-aware verdicts
- matrix summary (`SUPPORTED` vs `SCOPE_LIMITED_SATURATION`)
- route-B hard-gate summary (closure verdict for RG->FIT v2.x)

## Paper-ready Evidence (Route B)

- Matrix report (first-link): [`repro/route_b_v0.1/artifacts/scheme_matrix_v0_1.md`](repro/route_b_v0.1/artifacts/scheme_matrix_v0_1.md)
- Hard-gate summary: [`repro/route_b_v0.1/artifacts/route_b_hard_gate_summary.md`](repro/route_b_v0.1/artifacts/route_b_hard_gate_summary.md)
- Audit bundle entry: [`repro/route_b_v0.1/README.md`](repro/route_b_v0.1/README.md)

## Scope

- System: Conway's Game of Life
- Scales: `{1,2,4,8}`
- Schemes: `majority`, `threshold_low`, `threshold_high`, `average`
- Estimators: `C_frozen`, `C_activity`, `H`

## Quick Start

```powershell
cd experiments/renormalization/gol_rg_lens_v0_1
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\run_repro.ps1
```

Or (Linux/macOS):

```bash
cd experiments/renormalization/gol_rg_lens_v0_1
python -m pip install -r requirements.txt
bash ./run_repro.sh
```

## Smoke Test (fast)

```powershell
python src/generate_multiscale_dataset.py --seeds 2 --steps 400 --grid 64 --burn_in 50 --measure_interval 10 --window 20 --scales 1 2 4 8 --schemes majority threshold_low --out_csv out/smoke_multiscale.csv --summary_json out/smoke_run_summary.json
python src/semigroup_scale_map_test.py --input out/smoke_multiscale.csv --scheme majority --estimator C_frozen --outdir out/smoke_audit/majority_C_frozen --scales 1 2 4 8 --test_fraction 0.5 --random_state 0 --sat_near_bound_threshold 0.1 --sat_fraction_gate 0.9 --min_non_saturated_pairs 2
python src/build_scheme_matrix.py --out_root out/smoke_audit --schemes majority --estimators C_frozen --out_csv out/smoke_matrix.csv --out_md out/smoke_matrix.md
```

## Main Outputs

- `out/multiscale_scheme_audit.csv`
- `out/scheme_audit_full/<scheme>_<estimator>/semigroup_summary.json`
- `out/scheme_matrix_v0_1.csv`
- `out/scheme_matrix_v0_1.md`
- `out/route_b_hard_gate_summary.json`
- `out/route_b_hard_gate_summary.md`
- `out/run_summary.json`

## Strategy

- Execution plan: `ROUTE_B_HARD_GATE_PLAN.md`
- Recommended track: Route B (semigroup as hard gate), then stop at v2.x closure.
- Post-Route-B plan: `NEXT_VALIDATION_PLAN.md`

## Notes

- `C_activity` is derived as `1 - C_frozen` in this implementation; it is a consistency channel, not fully independent evidence.
- Saturation gate is mandatory. Saturated cells are reported as `SCOPE_LIMITED_SATURATION` (not PASS/FAIL).
- This pack is script-first for stable CI/replay. Notebook is intentionally omitted.
