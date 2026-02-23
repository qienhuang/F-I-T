# Route B Hard-Gate Plan (RG -> FIT)

Status: executable and in progress.

Goal: make semigroup closure a hard gate so this is a structural asset, not a one-off experiment.

## Scope

- Keep inside FIT v2.x discipline.
- Do not add v3 primitives.
- Focus on:
  - semigroup closure gate
  - scheme-family audit
  - saturation gate

## Decision of Record

Route selected: **B (recommended)**.

Reason:
- Q1 map existence alone is not enough.
- Need composition consistency to support flow-like interpretation.

## Deliverables

1. Reproducible 4x3 matrix run (4 schemes x 3 estimators)
1. Per-cell semigroup summary JSON
1. Matrix verdict table
1. Route-B hard-gate summary (`SUPPORTED`, `SUPPORTED_WITH_SCOPE_LIMITS`, `NONCLOSURE_OR_CHALLENGED`, `INCONCLUSIVE`)

## Commands

```powershell
cd experiments/renormalization/gol_rg_lens_v0_1
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\run_repro.ps1
```

Outputs:
- `out/scheme_matrix_v0_1.csv`
- `out/scheme_matrix_v0_1.md`
- `out/route_b_hard_gate_summary.json`
- `out/route_b_hard_gate_summary.md`

## Hard-Gate Rule (v0.1)

- Any `CHALLENGED` cell -> `NONCLOSURE_OR_CHALLENGED`.
- No `CHALLENGED` and >=1 `SUPPORTED` cell -> `SUPPORTED` (or `SUPPORTED_WITH_SCOPE_LIMITS` if saturation-limited cells exist).
- Otherwise -> `INCONCLUSIVE`.

## Stop Condition for v2.x

You can stop after Route B when all are true:

- Q1 map existence confirmed.
- Triviality excluded.
- L4 robustness claim retained.
- Saturation gate enforced.
- Semigroup hard-gate concludes either:
  - `SUPPORTED` / `SUPPORTED_WITH_SCOPE_LIMITS`, or
  - `NONCLOSURE_OR_CHALLENGED` (explicitly documented).

That is a complete v2.x closure. Cross-system validation is next phase.

