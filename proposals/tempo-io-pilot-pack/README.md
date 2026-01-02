# Tempo & IO 2‑Week Pilot — Starter Pack (Templates + Example Data)

This folder is a **copy/paste starter pack** for running the two‑week pilot in `proposals/tempo-io-pilot.md`.

The goal is not to predict incidents. The goal is to produce **auditable outputs** that measure whether your system retains **corrective capacity** under real update tempo.

## What you get (deliverables)

By the end of the pilot, a team should be able to produce:

1. A metrics snapshot:
   - **Validation Lag (VL)**
   - **Rollback Drill Pass Rate (RDPR)**
   - **Gate Bypass Rate (GBR)**
2. A minimal **IO register** (classified, not blame-framed)
3. One rollback (or purge) **drill** logged as pass/fail with declared RTO/RPO
4. A short report (1–2 pages): what failed operationally, proposed thresholds, next actions

## Files

- `pilot_report_template.md` — fill‑in report template
- `io_register.template.yaml` — IO register schema (copy/paste)
- `io_register.example.yaml` — example entries (self‑eval gate, memory write‑back)
- `changes.example.csv` — example change log (VL + IO tag + bypass)
- `rollback_drills.example.csv` — example drill log (RDPR)
- `compute_metrics.py` — computes VL/RDPR/GBR from the example CSVs (stdlib only)

## How to run (demo)

From repo root:

1. Run the example metrics computation:

   `python proposals/tempo-io-pilot-pack/compute_metrics.py`

2. Replace the example CSVs with your own exported logs:
   - same column names
   - timestamps in ISO 8601 (UTC recommended)

## Notes (privacy + friction)

- You can run this pilot in **shadow mode**. You do not need to publish logs.
- If you only share one thing externally, share:
  - aggregated VL percentiles,
  - RDPR (with your declared RTO/RPO),
  - GBR,
  - counts by IO category (no internal IDs).

## Related (core artifacts)

- 2‑week pilot proposal: `proposals/tempo-io-pilot.md`
- Self‑Referential IO Control Standard (S‑RIOCS): `docs/ai_safety/self_referential_io.md`
- IO‑SR mapping table: `docs/ai_safety/io_sr_mapping.md`
- Runnable demo notebook: `examples/self_referential_io_demo.ipynb`

